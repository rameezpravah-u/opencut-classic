"""qa.py — fidelity review: every generated still and clip next to the real reference frames, with its status.

    python3 qa.py --root <asset root> [--product rubik] [--out qa-sheet.jpg]

Prints the status table (approved / rejected / pending / unreviewed) and writes one sheet: each generated asset
(first frame for clips) beside the nearest real reference frame (rubik-reels/ref/), so approval is a one-look job.
Approve or reject by editing presets.json → products.<key>.assets.status / clip_status; the mechanisms refuse
anything marked rejected and fall back to the real footage.
"""
import argparse, glob, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
PRESETS = json.load(open(os.path.join(HERE, "presets.json"), encoding="utf-8"))


def first_frame(path):
    if path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        return Image.open(path).convert("RGB")
    out = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "1.0", "-i", path, "-frames:v", "1",
                          "-f", "image2pipe", "-vcodec", "mjpeg", "-"], capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(out)).convert("RGB")


def status_of(assets, kind, key):
    table = assets.get("status" if kind == "stills" else "clip_status", {})
    s = str(table.get(key, "")).lower()
    return "rejected" if s.startswith("rejected") else "approved" if s.startswith("approved") else "pending" if s.startswith("pending") else "unreviewed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--product", default="rubik")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if not a.root:
        a.root = os.path.abspath(os.path.join(os.path.dirname(HERE), PRESETS["products"][a.product]["root"]))
    assets = PRESETS["products"][a.product]["assets"]
    refs = sorted(glob.glob(os.path.join(a.root, "ref", "ref-*.jpg")) + glob.glob(os.path.join(os.path.dirname(HERE), "rubik-reels", "ref", "ref-*.jpg")))
    ref_img = first_frame(refs[len(refs) // 2]) if refs else None
    rows = []
    for kind in ("stills", "clips"):
        for key, rel in assets.get(kind, {}).items():
            p = os.path.join(a.root, rel)
            st = status_of(assets, kind, key)
            rows.append((kind, key, rel, st, os.path.exists(p)))
    counts = {}
    print(f"{'kind':6s} {'key':14s} {'status':10s} {'file':34s} present")
    for kind, key, rel, st, ok in rows:
        counts[st] = counts.get(st, 0) + 1
        print(f"{kind:6s} {key:14s} {st:10s} {rel:34s} {'yes' if ok else 'MISSING'}")
    print("summary:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if a.out:
        w, h = 300, 533
        font = ImageFont.truetype(os.path.join(os.path.dirname(HERE), "assets", "DM_Sans-600.ttf"), 22)
        cols = 4
        n = len([r for r in rows if r[4]])
        sheet = Image.new("RGB", (cols * (w * 2 + 20), ((n + cols - 1) // cols) * (h + 40)), (12, 12, 12))
        d = ImageDraw.Draw(sheet)
        i = 0
        for kind, key, rel, st, ok in rows:
            if not ok:
                continue
            x = (i % cols) * (w * 2 + 20); y = (i // cols) * (h + 40)
            im = first_frame(os.path.join(a.root, rel)).resize((w, h))
            sheet.paste(im, (x, y + 34))
            if ref_img is not None:
                sheet.paste(ref_img.resize((w, h)), (x + w, y + 34))
            col = {"approved": (90, 205, 140), "rejected": (232, 90, 80), "pending": (242, 180, 78)}.get(st, (200, 200, 200))
            d.text((x + 6, y + 6), f"{key} · {st}", font=font, fill=col)
            d.text((x + w + 6, y + 6), "reference", font=font, fill=(200, 200, 200))
            i += 1
        sheet.save(a.out, quality=85)
        print("sheet:", a.out)


if __name__ == "__main__":
    main()
