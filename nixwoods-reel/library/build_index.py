"""Build library/INDEX.tsv: every photo and video under the `nixwoods` Drive root, one row each.

Input: a JSON listing made through the Composio Google Drive connection (see library/README.md): every media file
with its id, name, mime type, size, md5, parent folder and image/video dimensions, plus every folder (to rebuild
paths). Files outside the `nixwoods` root (WhatsApp backups, sent items, icons) are left out.

Each row says what the file is, which product it most likely shows, and whether it may be used:
  OK            usable once its product is confirmed (PRODUCT-ID.md: names in folders and filenames are guesses)
  AI-LABEL      generated (Veo, Sora, Kling, Gemini, Higgsfield…): only with the Meta/Instagram AI label
  ASK           customer pictures (testimonials): needs the owner's and the customer's OK
  CHECK         in a quarantine or "to be tagged" holding folder: look before use
  DO-NOT-USE    the watermarked 5 Aug shoot, or another brand's material kept as a reference
  DUPLICATE     a byte-identical copy (same md5) of an earlier row; use that one

    python3 nixwoods-reel/library/build_index.py <drive_index.json> [out.tsv]

The index goes to the private nixwoods-os repo (30-Creative/library/INDEX.tsv), never to this public repo: it
holds every Drive file name, id and folder.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_ID = "1CzQKZ9EHRY5ITfZlPCjAABb8kR4nXo91"                     # Drive folder "nixwoods" (DRIVE-MAP.md)

# Shopify handles (live catalogue, 14 Oct 2026). A handle in a path or filename is the strongest guess we have.
HANDLES = [
    "nix-line-solid-wood-floor-lamp", "solid-wood-led-wall-light-30-inch", "nixwoods-aurora-linear-wall-light",
    "luma-pillar-ambient-lamp", "luminous-spiral-sculptural-sheesham-wood", "wooden-floor-lamp-minimalist-standing-light",
    "solid-wooden-floor-lamp-standing-light", "tall-teak-wood-rectangular-floor", "rosewood-pendant-light-360",
    "scandinavian-rosewood-round-pendant-light", "teak-wood-hollow-bowl-pendant-light",
    "pine-wood-pendant-light-clean-rectangular-design-for-home-office", "bedside-dimmer-lamp-soft-adjustable",
    "compact-wooden-wall-light", "teak-wood-minimalist-led-ceiling-light", "nordic-teak-wood-pendant-light-curved",
    "wooden-compact-table-lamp-subtle-charm-with-small-hollow", "rosewood-wooden-pendant-light-hollow",
    "handcrafted-wood-pendant-light-30-scandinavian-linear-design", "rosewood-frame-table-lamp",
    "teak-wood-vintage-fat-table-lamp-edison-bulb", "vertical-wooden-wall-light",
    "rosewood-pendant-light-hollow-curved-hanging", "double-arm-teak-pendant-light-sculptural-led",
    "rosewood-vertical-pendant-lamp-3ft-dimmable", "minimal-teak-wood-floor-lamp-india", "floating-wall-sconce-light",
    "wooden-wall-light-with-shelf", "wood-floating-wall-light-shelf-modern-led-wall-sconce-lighting",
    "rubiks-cube-table-lamp-sheesham-wood", "nixwoods-teak-linear-wall-light",
    "teak-amp-rosewood-led-wall-sconce-30-modern-minimalist-design",
    "curve-pine-solid-wood-floating-wall-light-minimal-wall-sconce", "aure-wood-linear-wall-light",
    "arden-12-inch-rosewood-wooden-wall-light", "arcline-14-inch-solid-wood-led-wall-light",
    "aura-drum-solid-wood-pendant-light", "24-inch-circular-hole-wooden-wall-light",
]
# folder words that point at one product (the per-product "produced" folders)
FOLDER_PRODUCT = {
    "rubiks-cube": "rubiks-cube-table-lamp-sheesham-wood", "glass-cube-lamp": "rubiks-cube-table-lamp-sheesham-wood",
    "nixline-floor-lamp": "nix-line-solid-wood-floor-lamp", "aurora": "nixwoods-aurora-linear-wall-light",
    "vertical-curved-wall-light": "vertical-wooden-wall-light",
    "rosewood-linear-pendant": "handcrafted-wood-pendant-light-30-scandinavian-linear-design",
    "compact-wall-light": "compact-wooden-wall-light", "bedside-dimmer-lamp": "bedside-dimmer-lamp-soft-adjustable",
    "minimalist-floor-lamp": "wooden-floor-lamp-minimalist-standing-light", "luma": "luma-pillar-ambient-lamp",
    "sculpted-glow": "luminous-spiral-sculptural-sheesham-wood", "table-lamp-edison": "edison (bedside or globe?)",
    "nixline": "nixline (floor lamp or wall light?)", "pendant": "pendant (which?)", "wall-light": "wall light (which?)",
}
AI_WORDS = re.compile(r"(?i)(^|[/_\-\s])(veo|sora|kling|gemini|higgsfield|hf_\d|chatgpt|dall-?e|midjourney|runway|"
                      r"ai-gen|generated|tool-outputs|mac-regen)")


def paths(folders):
    by = {f["id"]: f for f in folders}
    cache = {}

    def walk(fid):
        if fid in cache:
            return cache[fid]
        parts, cur, seen = [], fid, set()
        while cur and cur in by and cur not in seen:
            seen.add(cur)
            if cur == ROOT_ID:
                cache[fid] = "/".join(["nixwoods"] + parts[::-1])
                return cache[fid]
            parts.append(by[cur]["name"])
            cur = (by[cur].get("parents") or [None])[0]
        cache[fid] = None
        return None
    return walk


def product_of(path, name):
    hay = (path + "/" + name).lower()
    for h in sorted(HANDLES, key=len, reverse=True):
        if h in hay:
            return h, "handle in name/path"
    segs = path.lower().split("/")
    for seg in segs[::-1]:
        for k, v in FOLDER_PRODUCT.items():
            if seg == k or seg.endswith("-" + k) or seg.startswith(k + "-") or (k in seg and len(k) > 8):
                return v, "folder"
    return "", ""


def use_of(path, name):
    p = path.lower()
    if "watermarked" in p:
        return "DO-NOT-USE", "the watermarked 5 Aug shoot; the clean copy is under the sorted product folders"
    if "reference" in p and "competitor" in p:
        return "DO-NOT-USE", "another brand's material, kept only as a reference"
    if "testimonial" in p:
        return "ASK", "a customer's picture: needs the owner's and the customer's OK"
    if AI_WORDS.search(path + "/" + name):
        return "AI-LABEL", "generated: post only with the AI label"
    if "quarantine" in p or "_to-be-tagged" in p or "unsorted" in p:
        return "CHECK", "holding folder: look at it (faces, watermarks, product) before use"
    return "OK", ""


def main(src, out=None):
    d = json.load(open(src))
    walk = paths(d["folders"])
    rows, first = [], {}
    for m in sorted(d["media"], key=lambda x: x.get("createdTime") or ""):
        path = walk((m.get("parents") or [None])[0])
        if not path:
            continue
        name = m["name"]
        kind = "video" if m["mimeType"].startswith("video") else "photo"
        im, vm = m.get("imageMediaMetadata") or {}, m.get("videoMediaMetadata") or {}
        w, h = vm.get("width") or im.get("width") or "", vm.get("height") or im.get("height") or ""
        dur = round(int(vm["durationMillis"]) / 1000, 2) if vm.get("durationMillis") else ""
        prod, how = product_of(path, name)
        use, why = use_of(path, name)
        md5 = m.get("md5Checksum") or ""
        dup = ""
        if md5 and md5 in first:
            dup, use, why = first[md5], "DUPLICATE", "byte-identical copy"
        elif md5:
            first[md5] = m["id"]
        rows.append([m["id"], name, path, kind, m["mimeType"], round(int(m.get("size") or 0) / 1e6, 2), w, h, dur,
                     prod, how, use, why, dup, md5, (m.get("createdTime") or "")[:10]])
    out = out or os.path.join(os.path.dirname(os.path.dirname(HERE)), "..", "nixwoods-os",
                              "30-Creative", "library", "INDEX.tsv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        wr.writerow(["drive_id", "name", "folder", "kind", "mime", "size_mb", "width", "height", "duration_s",
                     "product_guess", "guess_from", "use", "why", "duplicate_of", "md5", "created"])
        wr.writerows(rows)
    print("wrote", out, len(rows), "rows")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
