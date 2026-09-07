#!/usr/bin/env python3
"""file_for_os.py — give a render its NixWoods OS identity.

The pipeline names renders after their brief (`A1-aurora-transformation-music.mp4`) because that
is what regenerates them. The OS names every asset
`NW-CREATIVE-VID-<YYYYMMDD>-<shopify-handle>-<slug>-v#` (OPERATING_MANUAL §6, FILE_CONSOLIDATION §2.3
and §2.7). Both are needed, so this maps one to the other instead of renaming in place.

    python3 system/file_for_os.py --date 20260907                 # write the OS copies + manifest
    python3 system/file_for_os.py --date 20260907 --rows          # also print ASSET_REGISTRY rows

Renames the mp4s in place (git mv) — copying them would duplicate ~300 MB against a repo already
near the size ceiling in README. Covers, contact sheets and timelines keep their brief names: they
are working artefacts, not filed assets. The manifest in system/os-manifest.tsv is the mapping.
"""
import argparse, csv, json, os, shutil, subprocess, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRESETS = json.load(open(os.path.join(HERE, "presets.json"), encoding="utf-8"))

# brief prefix -> (product key, slug for the OS name)
BRIEFS = {
 "A1-aurora-transformation":      ("aurora",  "transformation"),
 "A2-aurora-before-after":        ("aurora",  "before-after"),
 "A3-aurora-sizes":               ("aurora",  "size-guide"),
 "A4-aurora-listicle":            ("aurora",  "three-reasons"),
 "A5-aurora-price":               ("aurora",  "price-reveal"),
 "R1-rosewood-transformation":    ("rosewood","transformation"),
 "R2-rosewood-vo":                ("rosewood","voice-over"),
 "R3-rosewood-spec":              ("rosewood","spec-card"),
 "R4-rosewood-loop":              ("rosewood","evening-loop"),
 "R5-rosewood-price":             ("rosewood","price-reveal"),
 "T1-teak-kinetic":               ("teak",    "kinetic-two-lines"),
 "T2-teak-transformation":        ("teak",    "transformation"),
 "T3-teak-triptych":              ("teak",    "three-rooms"),
 "T4-teak-spec":                  ("teak",    "spec-card"),
 "T5-teak-price":                 ("teak",    "price-reveal"),
 "K1-rubik-11pm":                 ("rubik",   "transformation-11pm"),
 "K2-rubik-mood":                 ("rubik",   "mood-loop"),
 "K3-rubik-listicle":             ("rubik",   "three-moods"),
 "K4-rubik-kinetic":              ("rubik",   "kinetic-no-switch"),
 "K5-rubik-price":                ("rubik",   "price-reveal"),
}
VARIANTS = {"-music.mp4": "music", "-clean.mp4": "clean"}


def probe(path):
    """duration in seconds. imageio-ffmpeg ships ffmpeg but not ffprobe, so parse ffmpeg's own report."""
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    for line in o.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return round(int(h) * 3600 + int(m) * 60 + float(s), 1)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y%m%d"))
    ap.add_argument("--version", default="v1")
    ap.add_argument("--rows", action="store_true", help="print ASSET_REGISTRY markdown rows")
    a = ap.parse_args()

    manifest, rows = [], []
    for brief, (pkey, slug) in BRIEFS.items():
        prod = PRESETS["products"][pkey]
        handle, gid = prod["shopify_handle"], prod["shopify_gid"]
        src_dir = os.path.join(ROOT, prod["root"], "out", "system")
        for suffix, variant in VARIANTS.items():
            asset = f"NW-CREATIVE-VID-{a.date}-{handle}-{slug}-{variant}-{a.version}"
            src, dst = os.path.join(src_dir, brief + suffix), os.path.join(src_dir, asset + ".mp4")
            if os.path.exists(src) and not os.path.exists(dst):
                if subprocess.run(["git", "mv", src, dst], cwd=ROOT, capture_output=True).returncode:
                    os.rename(src, dst)          # not tracked yet
            if not os.path.exists(dst):
                print("MISSING", src, file=sys.stderr); continue
            manifest.append(dict(asset_id=asset, brief=brief, product=handle, product_id=gid,
                                 variant=variant, orientation="9:16",
                                 duration_s=probe(dst), size_mb=round(os.path.getsize(dst) / 1048576, 1),
                                 repo_path=os.path.relpath(dst, os.path.dirname(ROOT))))
    with open(os.path.join(HERE, "os-manifest.tsv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(manifest[0]), delimiter="\t")
        w.writeheader(); w.writerows(manifest)
    print(f"{len(manifest)} assets -> system/os-manifest.tsv")
    if a.rows:
        for m in manifest:
            print(f"| {m['asset_id']} | {m['brief']} {m['variant']} cut | VID | com | opencut-classic `{m['repo_path']}` | "
                  f"code-cloud | {a.date[:4]}-{a.date[4:6]}-{a.date[6:]} | reel | SOCIAL, ADS, PIN | — | STAGED | "
                  f"— | CREATIVE tab | {m['product']} | {m['product_id']} | reel | {m['orientation']} | {m['duration_s']}s |")


if __name__ == "__main__":
    main()
