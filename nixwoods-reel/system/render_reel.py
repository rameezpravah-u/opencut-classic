#!/usr/bin/env python3
"""render_reel.py — an approved reel-engine script + its clips + a style -> a finished 9:16 reel.

The NixWoods equivalent of a "script -> render" server step: no per-reel build script.

Inputs
  script   nixwoods-os 40-Content/reel-engine/scripts/<id>.json  (status must be APPROVED or RENDERED)
  cut      <product>-reels/cuts/<id>.json  — edit decisions the script does not carry:
           {"product_dir": "aurora-reels", "beats": [{"in": 1.8, "speed": 1.5}, {}, ...],
            "music": "audio/music2-meaning.mp3", "speak": {"3000K": "three thousand K"},
            "voice": "EXAVITQu4vr4xnSDxMaL"}
  style    bone-serif | amber-key | quiet-bar   (NixWoods brand only: Fraunces, Bone, Signal Amber)

What it does
  1. Voice-over per beat with word timestamps (ElevenLabs /with-timestamps), cached next to the clips;
     a cached take is reused while its text is unchanged, so a re-render spends nothing.
  2. Cuts each beat from its clip: video trimmed + slow push-in; a still kept whole (contain) on a
     blurred fill with a push-in (a linear fixture is never centre-cropped).
  3. Draws the hook on beat 1 (on screen by 0.3 s), word-timed captions on the later beats in the
     chosen style, and the closing question with nixwoods.com.
  4. Mixes voice (+ music for the -music cut), loudnorm -16 LUFS; writes -vo-only and -music mp4s,
     cover.jpg and sheet.jpg.

Run from nixwoods-reel/:
  python3 system/render_reel.py <script.json> --style bone-serif [--out DIR]
"""
import argparse
import base64
import json
import os
import pathlib
import re
import shutil
import subprocess
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
BONE, MUTED, AMBER = (246, 241, 231), (215, 208, 197), (245, 165, 36)
F_HEAD = str(ROOT / "assets" / "Fraunces-600.ttf")
F_BODY = str(ROOT / "assets" / "DM_Sans-600.ttf")
GRADE = "eq=contrast=1.05:saturation=1.06,vignette=angle=PI/5:mode=forward"
STYLES = ("bone-serif", "amber-key", "quiet-bar")
STOP = {"a", "an", "the", "and", "or", "of", "to", "in", "on", "it", "is", "so", "your", "you", "one", "two", "up", "down"}
CTA_SECS = 1.8
HOOK_AT = 0.3


# ---------- timing (pure) ----------
def words_from_alignment(al):
    """ElevenLabs character alignment -> [(word, start, end)] split on whitespace."""
    out, cur, s, e = [], "", None, None
    for ch, cs, ce in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                out.append((cur, s, e))
            cur, s, e = "", None, None
            continue
        if not cur:
            s = cs
        cur, e = cur + ch, ce
    if cur:
        out.append((cur, s, e))
    return out


def _core(tok):
    return re.sub(r"[^\w']", "", tok)


def spoken_text(display, speak_map):
    """Text for TTS (numbers spelled for the voice) + how many spoken words each display word becomes."""
    toks, spans = [], []
    for tok in display.split():
        core = _core(tok)
        if core in speak_map:
            exp = speak_map[core].split()
            exp[-1] += tok[len(tok.rstrip(".,!?:;")):]   # keep trailing punctuation
            toks += exp
            spans.append(len(exp))
        else:
            toks.append(tok)
            spans.append(1)
    return " ".join(toks), spans


def display_words(display, spans, words):
    """Map spoken-word timings back to the words shown on screen."""
    disp = display.split()
    if sum(spans) == len(words):
        out, i = [], 0
        for tok, n in zip(disp, spans):
            out.append((tok, words[i][1], words[i + n - 1][2]))
            i += n
        return out
    # TTS added or dropped a word: spread the shown words evenly over the spoken span
    t0, t1 = (words[0][1], words[-1][2]) if words else (0.0, 1.0)
    step = (t1 - t0) / max(1, len(disp))
    return [(tok, t0 + k * step, t0 + (k + 1) * step) for k, tok in enumerate(disp)]


def key_words(on_screen):
    return {w for w in (_core(t).lower() for t in on_screen.split()) if w and w not in STOP}


def highlight(group, keys):
    """Index (within the group) of the one word to emphasise: the last key word, or none."""
    idx = [i for i, w in enumerate(group["words"]) if _core(w[0]).lower() in keys]
    return {idx[-1]} if idx else set()


def group_words(words, style):
    """Caption groups [{words, start, end}] that never overlap. bone-serif: <=2 words, break after
    punctuation. amber-key / quiet-bar: the whole line as one group."""
    if style not in STYLES:
        raise ValueError(f"unknown style {style!r}; one of {STYLES}")
    if not words:
        return []
    if style == "bone-serif":
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) == 2 or w[0][-1] in ".,!?:;":
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
    else:
        groups = [list(words)]
    out = []
    for k, g in enumerate(groups):
        end = groups[k + 1][0][1] if k + 1 < len(groups) else g[-1][2] + 0.35
        out.append({"words": g, "start": g[0][1], "end": max(end, g[0][1] + 0.2)})
    for a, b in zip(out, out[1:]):
        a["end"] = min(a["end"], b["start"])
    return out


def beat_starts(script):
    t, out = 0.0, []
    for b in script["beats"]:
        out.append(t)
        t += float(b["secs"])
    return out


def check_renderable(script):
    if script.get("status") not in ("APPROVED", "RENDERED"):
        raise ValueError(f"{script.get('id')}: status {script.get('status')!r}; only an owner-approved script renders")


def find_clip(src, clip_id):
    if not clip_id or clip_id in ("needs-shoot", "ai"):
        raise ValueError(f"beat clip is {clip_id!r}: shoot or generate it first")
    hits = sorted(p for p in pathlib.Path(src).iterdir() if p.name.startswith(clip_id + "-") or p.stem == clip_id)
    if not hits:
        raise FileNotFoundError(f"no file for clip {clip_id} in {src}")
    return hits[0]


# ---------- voice ----------
def tts_with_timestamps(text, voice, mp3, js):
    if js.exists() and mp3.exists():
        d = json.loads(js.read_text())
        if d.get("text") == text and d.get("voice") == voice:
            return d["alignment"], False
    body = json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
                                 data=body, headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy"), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    mp3.write_bytes(base64.b64decode(d["audio_base64"]))
    al = d.get("alignment") or d.get("normalized_alignment")
    js.write_text(json.dumps({"text": text, "voice": voice, "alignment": al}))
    return al, True


# ---------- drawing ----------
def _font(path, size):
    from PIL import ImageFont
    return ImageFont.truetype(path, size)


def _wrap(draw, words, font_for, max_w):
    lines, cur, cur_w = [], [], 0
    for w in words:
        f = font_for(w)
        ww = draw.textlength(w + " ", font=f)
        if cur and cur_w + ww > max_w:
            lines.append(cur)
            cur, cur_w = [], 0
        cur.append(w)
        cur_w += ww
    if cur:
        lines.append(cur)
    return lines


def _shadowed(layer):
    from PIL import Image, ImageFilter
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.5))
    base = Image.merge("RGBA", (Image.new("L", layer.size, 0),) * 3 + (a,))
    base.alpha_composite(layer)
    return base


def scrim():
    from PIL import Image
    import numpy as np
    a = np.zeros((H, W), dtype=np.uint8)
    ys = np.arange(1120, H)
    a[1120:, :] = (255 * 0.55 * ((ys - 1120) / (H - 1120)) ** 0.85)[:, None].astype(np.uint8)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.putalpha(Image.fromarray(a))
    return im


def text_width(text, size, path=None):
    from PIL import Image, ImageDraw
    return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=_font(path or F_HEAD, size))


def headline_lines(text, size=78, max_w=W - 160):
    """One sentence per line, and any line wider than the safe width wrapped by words."""
    out = []
    for sent in [x.strip() + "." for x in text.split(".") if x.strip()] or [text]:
        cur = ""
        for w in sent.split():
            t = (cur + " " + w).strip()
            if cur and text_width(t, size) > max_w:
                out.append(cur)
                cur = w
            else:
                cur = t
        out.append(cur)
    if text.strip() and not text.strip().endswith("."):
        out[-1] = out[-1].rstrip(".")
    return out


def draw_headline(lines, size=78, y_top=1340, sub=None):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = _font(F_HEAD, size)
    y = y_top
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=BONE)
        y += int(size * 1.18)
    if sub:
        fs = _font(F_BODY, 30)
        d.text(((W - d.textlength(sub, font=fs)) / 2, y + 18), sub, font=fs, fill=MUTED)
    return _shadowed(im)


def draw_caption(group, t, style, keys):
    """One caption group at time t, in the style."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    words = group["words"]
    hi = {words[i][0] for i in highlight(group, keys)}
    is_key = lambda w: w in hi
    if style == "bone-serif":
        fn = lambda w: _font(F_HEAD, 96 if is_key(w) else 76)
        lines = _wrap(d, [w[0] for w in words], fn, W - 180)
        y = 1360
        for ln in lines:
            tw = sum(d.textlength(w + " ", font=fn(w)) for w in ln) - d.textlength(" ", font=fn(ln[-1]))
            x = (W - tw) / 2
            for w in ln:
                f = fn(w)
                d.text((x, y + (0 if is_key(w) else 14)), w, font=f, fill=BONE)
                x += d.textlength(w + " ", font=f)
            y += 112
        return _shadowed(im)
    if style == "amber-key":
        f = _font(F_HEAD, 64)
        lines = _wrap(d, [w[0] for w in words], lambda _: f, W - 160)
        said = {i for i, w in enumerate(words) if w[1] <= t}
        y, idx = 1340, 0
        for ln in lines:
            tw = d.textlength(" ".join(ln), font=f)
            x = (W - tw) / 2
            for w in ln:
                col = AMBER if is_key(w) else BONE
                alpha = 255 if idx in said else 90
                d.text((x, y), w, font=f, fill=col + (alpha,))
                x += d.textlength(w + " ", font=f)
                idx += 1
            y += 80
        return _shadowed(im)
    # quiet-bar
    f = _font(F_BODY, 46)
    lines = _wrap(d, [w[0] for w in words], lambda _: f, W - 240)
    lh, pad = 62, 26
    bw = max(d.textlength(" ".join(ln), font=f) for ln in lines) + 2 * pad
    bh = lh * len(lines) + 2 * pad - 8
    x0, y0 = (W - bw) / 2, 1380
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=14, fill=(20, 16, 14, 170))
    for k, ln in enumerate(lines):
        s = " ".join(ln)
        d.text(((W - d.textlength(s, font=f)) / 2, y0 + pad + k * lh), s, font=f, fill=BONE)
    return im


# ---------- render ----------
def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def still_filter(opts, dur, iw, ih):
    """filter_complex for a still: optional crop, kept whole (contain) on a blurred fill, or filling the frame when
    it is already 9:16 or taller; slow push-in; optional cold-to-warm switch (ad-formula style D, a grade on a real photo)."""
    crop, cw, ch = "", float(iw), float(ih)
    if opts.get("crop"):
        x0, y0, x1, y1 = opts["crop"]
        crop = f"crop=iw*{round(x1 - x0, 4)}:ih*{round(y1 - y0, 4)}:iw*{x0}:ih*{y0},"
        cw, ch = iw * (x1 - x0), ih * (y1 - y0)
    n = max(1, int(dur * FPS))
    if ch / cw >= H / W - 1e-6:
        fg_h, fg_scale = H, f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    else:
        fg_h = int(round(W * ch / cw / 2) * 2)
        fg_scale = f"scale={W}:{fg_h}"
    z = opts.get("zoom", 0.05)
    eff = ""
    if opts.get("effect") == "cold-to-warm":
        sw = round(dur * 0.45, 2)
        eff = (f",colortemperature=temperature=9500:enable='lt(t,{sw})'"
               f",eq=brightness=-0.10:saturation=0.55:enable='lt(t,{sw})'")
    return (f"[0]{crop}split[a][b];"
            f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.12[bg];"
            f"[b]{fg_scale},zoompan=z='1+{z}*on/{n}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{fg_h}:fps={FPS}[fg];"
            f"[bg][fg]overlay=0:(H-h)/2,fps={FPS},{GRADE}{eff},format=yuv420p")


def video_filter(opts, dur, clip_secs):
    speed, t_in, push = float(opts.get("speed", 1.0)), float(opts.get("in", 0.0)), opts.get("push", 0.0006)
    hold = ",tpad=stop_mode=clone:stop_duration=" + str(dur) if clip_secs - t_in < dur * speed - 0.02 else ""
    zp = f",zoompan=z='1+{push}*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS}" if push else ""
    return f"setpts=PTS/{speed},scale={W}:{H}:flags=lanczos,fps={FPS}{hold}{zp},{GRADE},format=yuv420p"


def _probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = d["streams"][0]
    return int(st["width"]), int(st["height"]), float(d.get("format", {}).get("duration") or 0)


def cut_segments(script, cut, src, tmp):
    paths = []
    for i, (b, c) in enumerate(zip(script["beats"], cut["beats"])):
        dur = float(b["secs"])
        clip = find_clip(src, c.get("clip") or b["clip"])
        out = tmp / f"s{i + 1}.mp4"
        iw, ih, secs = _probe(clip)
        if clip.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            ff("-loop", "1", "-t", str(dur), "-i", str(clip), "-filter_complex", still_filter(c, dur, iw, ih), "-t", str(dur), "-an", str(out))
        else:
            speed, t_in = float(c.get("speed", 1.0)), float(c.get("in", 0.0))
            ff("-ss", str(t_in), "-t", str(dur * speed), "-i", str(clip), "-vf", video_filter(c, dur, secs), "-an", "-t", str(dur), str(out))
        paths.append(out)
    (tmp / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in paths))
    ff("-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(tmp / "base.mp4"))


def build_cues(script, cut, vo_dir, spent):
    """Voice per beat with word timings -> list of (start, end, kind, payload)."""
    starts, lead = beat_starts(script), float(cut.get("lead", 0.25))
    voice, speak = cut.get("voice", "EXAVITQu4vr4xnSDxMaL"), cut.get("speak", {})
    vo_files, captions = [], []
    for i, (b, t0) in enumerate(zip(script["beats"], starts)):
        text, spans = spoken_text(b["vo"], speak)
        mp3, js = vo_dir / f"beat-{i + 1}.mp3", vo_dir / f"beat-{i + 1}.json"
        al, new = tts_with_timestamps(text, voice, mp3, js)
        if new:
            spent.append(len(text))
        at = t0 + lead
        vo_files.append((mp3, at))
        if i == 0:
            continue  # beat 1 carries the hook headline instead of captions
        words = [(w, s + at, e + at) for w, s, e in display_words(b["vo"], spans, words_from_alignment(al))]
        captions.append((words, key_words(b.get("on_screen", ""))))
    return vo_files, captions


def overlay_frames(script, captions, style, tmp):
    from PIL import Image
    total = sum(float(b["secs"]) for b in script["beats"])
    hook = script["hooks"][script.get("chosen_hook_index", 0)]["text"]
    hook_lines = headline_lines(hook, size=78)
    end1 = beat_starts(script)[1] if len(script["beats"]) > 1 else total
    cta_at = total - CTA_SECS
    sc = scrim()
    groups = [(g, keys) for words, keys in captions for g in group_words(words, style)]
    cache, fr = {}, tmp / "ov"
    fr.mkdir(exist_ok=True)
    for n in range(int(round(total * FPS))):
        t = n / FPS
        if t >= cta_at:
            key = ("cta",)
        elif HOOK_AT <= t < end1 - 0.1:
            key = ("hook",)
        else:
            gi = next((k for k, (g, _) in enumerate(groups) if g["start"] <= t < g["end"]), None)
            said = sum(1 for w in groups[gi][0]["words"] if w[1] <= t) if gi is not None and style == "amber-key" else 0
            key = ("cap", gi, said) if gi is not None else ("none",)
        if key not in cache:
            im = sc.copy()
            if key[0] == "cta":
                cta = [l2 for l in _split_cta(script["cta"]) for l2 in headline_lines(l, size=62)]
                im.alpha_composite(draw_headline(cta, size=62, y_top=1300, sub="nixwoods.com"))
            elif key[0] == "hook":
                im.alpha_composite(draw_headline(hook_lines, size=78))
            elif key[0] == "cap":
                g, keys = groups[key[1]]
                im.alpha_composite(draw_caption(g, t, style, keys))
            p = tmp / f"state-{len(cache)}.png"
            im.save(p, compress_level=1)
            cache[key] = p
        dst = fr / f"{n:05d}.png"
        if dst.exists():
            dst.unlink()
        os.link(cache[key], dst)
    return fr, total


def _split_cta(cta):
    if ":" in cta:
        a, b = cta.split(":", 1)
        return [a.strip() + ":", b.strip()]
    words = cta.split()
    return [" ".join(words[: len(words) // 2]), " ".join(words[len(words) // 2:])] if len(words) > 5 else [cta]


def mix(tmp, frames, total, vo_files, music, out_mp4):
    inputs = ["-i", str(tmp / "base.mp4"), "-framerate", str(FPS), "-i", str(frames / "%05d.png")]
    fc = ["[0][1]overlay=0:0:shortest=1[v]"]
    amix = []
    for j, (mp3, at) in enumerate(vo_files):
        inputs += ["-i", str(mp3)]
        ms = int(at * 1000)
        fc.append(f"[{2 + j}]adelay={ms}|{ms}[a{j}]")
        amix.append(f"[a{j}]")
    if music:
        inputs += ["-i", str(music)]
        fc.append(f"[{2 + len(vo_files)}]atrim=0:{total},volume=-13dB,afade=t=in:d=0.5,afade=t=out:st={total - 1.5}:d=1.5[m]")
        amix.append("[m]")
    fc.append(f"{''.join(amix)}amix=inputs={len(amix)}:normalize=0,atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11[a]")
    ff(*inputs, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", str(total),
       "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out_mp4))


def render(script_path, style, out_dir=None):
    script = json.loads(pathlib.Path(script_path).read_text())
    check_renderable(script)
    if style not in STYLES:
        raise ValueError(f"unknown style {style!r}; one of {STYLES}")
    cut_path = next(ROOT.glob(f"*-reels/cuts/{script['id']}.json"), None)
    if not cut_path:
        raise FileNotFoundError(f"no cut file <product>-reels/cuts/{script['id']}.json")
    cut = json.loads(cut_path.read_text())
    pdir = ROOT / cut["product_dir"]
    if len(cut["beats"]) != len(script["beats"]):
        raise ValueError("cut file and script have a different number of beats")
    name = script.get("render_name") or script["id"].replace("NW-CREATIVE-SCRIPT-", "NW-CONTENT-RENDER-")
    out = pathlib.Path(out_dir) if out_dir else pdir / "out" / "render_reel" / f"{name}-{style}"
    tmp = out / "_build"
    tmp.mkdir(parents=True, exist_ok=True)
    vo_dir = pdir / "audio-vo" / script["id"]
    vo_dir.mkdir(parents=True, exist_ok=True)
    spent = []
    cut_segments(script, cut, pdir / "src", tmp)
    vo_files, captions = build_cues(script, cut, vo_dir, spent)
    frames, total = overlay_frames(script, captions, style, tmp)
    mix(tmp, frames, total, vo_files, None, out / "vo-only.mp4")
    mix(tmp, frames, total, vo_files, pdir / cut["music"] if cut.get("music") else None, out / "music.mp4")
    ff("-ss", str(max(0, total - CTA_SECS - 2.5)), "-i", str(out / "music.mp4"), "-frames:v", "1", "-q:v", "2", str(out / "cover.jpg"))
    ff("-i", str(out / "music.mp4"), "-vf", "fps=1,scale=216:-1,tile=8x2", "-frames:v", "1", "-q:v", "3", str(out / "sheet.jpg"))
    shutil.rmtree(tmp)
    return out, sum(spent)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("--style", required=True, choices=STYLES)
    ap.add_argument("--out")
    a = ap.parse_args()
    o, chars = render(a.script, a.style, a.out)
    print(f"{o}  (new voice characters spent: {chars})")
