#!/usr/bin/env python3
"""Loopback speech-timing service speaking Hypit's `hypit.whisperx-service@1` protocol, backed by
local faster-whisper (no WhisperX/torch). Used through the whisperx.local Endpoint's `serviceCommand`.

It honestly reports `whisperxVersion: "none (faster-whisper <ver>)"`; the Profile's
`expectedWhisperXVersion` is set to the same string so the Provider's identity check passes only
for this service. Word times come from faster-whisper's word_timestamps on the canonical 16 kHz
mono WAV the Provider stages (no ffmpeg here). No network: the model is loaded local-files-only.
"""
import json, os, sys, threading, wave, logging, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import faster_whisper
from faster_whisper import WhisperModel
import numpy as np

PORT = int(os.environ.get("HYPIT_WHISPERX_PORT", "8765"))
MODEL = os.environ.get("HYPIT_WHISPERX_MODEL", "small.en")
DEVICE = os.environ.get("HYPIT_WHISPERX_DEVICE", "cpu")
COMPUTE = os.environ.get("HYPIT_WHISPERX_COMPUTE", "int8")
BATCH = int(os.environ.get("HYPIT_WHISPERX_BATCH_SIZE", "8"))
ROOTS = [os.path.realpath(r) for r in os.environ.get("HYPIT_FW_INPUT_ROOTS", tempfile.gettempdir()).split(os.pathsep) if r]
IDENT = {
    "ok": True, "protocol": "hypit.whisperx-service@1", "serviceVersion": "0.1.0",
    "whisperxVersion": f"none (faster-whisper {faster_whisper.__version__})",
    "model": MODEL, "device": DEVICE, "compute": COMPUTE, "batchSize": BATCH,
}
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [fw-service] %(message)s")
log = logging.getLogger()
log.info("loading faster-whisper %s on %s/%s (local files only)", MODEL, DEVICE, COMPUTE)
model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE, local_files_only=True)
lock = threading.Lock()
log.info("model ready")


def transcribe(path, language):
    real = os.path.realpath(path)
    if not os.path.isabs(path) or not any(real == r or real.startswith(r + os.sep) for r in ROOTS):
        raise ValueError("audio_path must be absolute and inside the allowed roots")
    with wave.open(real, "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2 or w.getframerate() != 16000:
            raise ValueError("audio input must be 16 kHz mono PCM s16 WAV")
        pcm = w.readframes(w.getnframes())
    samples = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768.0
    log.info("transcribing %.2fs, language=%s", len(samples) / 16000, language)
    segs, info = model.transcribe(samples, language=language, word_timestamps=True, vad_filter=False, beam_size=5)
    # Whisper's cross-attention word times drift around pauses (a pause gets absorbed into a
    # neighbouring word: "Books, [pause] candle" gave candle 1.38-1.38 when it is spoken at
    # 0.95-1.5). Refine deterministically on the same samples: find silences >= 150 ms in the
    # 10 ms RMS envelope and assign each to the word boundary (k | k+1) whose whisper end/start
    # are closest to the silence's edges; that word k then ends at the silence and k+1 starts
    # where speech resumes. Words never reorder; boundaries far from any silence are untouched.
    hop = 160
    n = len(samples) // hop
    rms = np.sqrt(np.mean(samples[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    voiced = db > (np.percentile(db, 95) - 35.0)
    gaps, k = [], 0
    while k < n:
        if not voiced[k]:
            j = k
            while j < n and not voiced[j]:
                j += 1
            if (j - k) >= 15 and k > 0 and j < n:
                gaps.append((k / 100.0, j / 100.0))
            k = j
        else:
            k += 1

    def refine(words):
        timed = [w for w in words if "start" in w]
        used = set()
        for g0, g1 in gaps:
            best, cost = None, 1.0
            for i in range(len(timed) - 1):
                c = abs(timed[i]["end"] - g0) + abs(timed[i + 1]["start"] - g1)
                if c < cost and i not in used:
                    best, cost = i, c
            if best is None:
                continue
            used.add(best)
            left, right = timed[best], timed[best + 1]
            left["end"] = max(min(left["end"], g0) if left["end"] > g0 else g0, left["start"] + 0.02)
            right["start"] = g1
            right["end"] = max(right["end"], g1 + 0.05)
        for i in range(len(timed) - 1):  # keep the sequence monotone
            if timed[i + 1]["start"] < timed[i]["start"]:
                timed[i + 1]["start"] = timed[i]["start"]
            timed[i]["end"] = max(timed[i]["start"], min(timed[i]["end"], timed[i + 1]["end"]))
        return words

    out = []
    for s in segs:
        words = []
        for wd in (s.words or []):
            t = wd.word.strip()
            if not t:
                continue
            item = {"text": t}
            if wd.start is not None and wd.end is not None and 0 <= wd.start <= wd.end:
                item.update(start=float(wd.start), end=float(wd.end))
            if wd.probability is not None and 0 <= wd.probability <= 1:
                item["score"] = float(wd.probability)
            words.append(item)
        if words:
            out.append({"text": s.text.strip(), "start": float(s.start), "end": float(s.end), "words": words})
    flat = [w for seg in out for w in seg["words"]]
    refine(flat)
    for seg in out:
        ts = [w for w in seg["words"] if "start" in w]
        if ts:
            seg["start"], seg["end"] = min(seg["start"], ts[0]["start"]), max(seg["end"], ts[-1]["end"])
    log.info("pause refinement: %d silences", len(gaps))
    log.info("word timing ready: %d segments, %d words", len(out), sum(len(s["words"]) for s in out))
    return {"language": info.language or language, "segments": out}


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, value):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, IDENT)
        else:
            self._send(404, {"error": {"code": "NOT_FOUND", "message": "not found"}})

    def do_POST(self):
        if self.path != "/transcribe":
            return self._send(404, {"error": {"code": "NOT_FOUND", "message": "not found"}})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
            lang = req.get("language") or None
            if not lock.acquire(blocking=False):
                return self._send(503, {"error": {"code": "BUSY", "message": "busy"}})
            try:
                self._send(200, transcribe(req["audio_path"], lang))
            finally:
                lock.release()
        except (ValueError, KeyError, wave.Error) as e:
            self._send(400, {"error": {"code": "INVALID_INPUT", "message": str(e)}})
        except Exception as e:  # noqa: BLE001
            log.exception("inference failed")
            self._send(500, {"error": {"code": "INFERENCE_FAILED", "message": str(e)}})

    def log_message(self, fmt, *args):
        log.info(fmt, *args)


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    log.info("ready on http://127.0.0.1:%d", PORT)
    srv.serve_forever(poll_interval=0.25)
