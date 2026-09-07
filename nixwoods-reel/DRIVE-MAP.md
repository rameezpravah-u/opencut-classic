# Google Drive — where NixWoods creative lives

Root: **`nixwoods`** — `1CzQKZ9EHRY5ITfZlPCjAABb8kR4nXo91`

| Folder | What is in it |
|---|---|
| `00-OS` | operating docs |
| `10-Brand` | brand guidelines, logo |
| `20-Products` | **empty.** Created 6 Sep 2026, nothing moved in yet. Product photos are in the raw creative folder below. |
| `30-Creative` | **most photos and videos** — the working folder |
| `40-Content` · `50-Ads` · `60-Email` · `70-SEO` · `80-Customers` | by function |
| `90-Archive` | superseded material, including the watermarked shoot below |

## The two that matter

**Product photos, sorted per product** — `1nXp-iE61A0lIgidTFZhFTdKlMelz3qvS`
Per-product subfolders (`nixwoods-aurora-linear-wall-light`, `general-pendant-lights`, `wooden-floor-lamp-minimalist-standing-light`, `rubiks-cube-table-lamp-sheesham-wood`, `linear-pendant`, …) holding the renamed shoot files:

```
NW-CREATIVE-IMG-{YYYYMMDD}-{product-handle}-{originalFrame}-v{n}.JPG
NW-CREATIVE-VID-{YYYYMMDD}-{product-handle}-{shot description}-{ratio}-v{n}.mp4
```

**Unsorted creative** — `1ukKuObS93sg0VHhXteNHKFNMOhAMVKjk` — 9 files not yet filed, named `…-UNSORTED-…`.

## Do not use: the watermarked shoot

`90-Archive / photoshoot-20260805-WATERMARKED-do-not-use` is the **same 5 Aug shoot** as the clean `NW-CREATIVE-IMG-20260805-*` files. Its filenames are bare camera names (`AC4I9586.JPG`), so it is easy to grab one by mistake.

**Never pull from it.** No watermark removal is needed or wanted: a clean original of every frame already exists under the sorted product folders — match on the frame number (`AC4I9835` → `NW-CREATIVE-IMG-20260805-rubiks-cube-table-lamp-sheesham-wood-AC4I9835-v1.JPG`). If a frame ever turns out to exist *only* watermarked, that is a rights question for the photographer, not an editing task — ask before using it.

## What a session can and cannot pull from Drive (corrected 7 Sep)

**Files up to 10 MB download fine.** `download_file_content` returns base64; when the result is
too big for the conversation the harness writes it to a file under
`~/.claude/projects/<project>/tool-results/` and hands back the path. Decode it there and the
bytes never touch context:

```python
import json, base64
d = json.load(open(saved_path))          # {content, id, mimeType, title}
open(dest, "wb").write(base64.b64decode(d["content"]))
```

Verified 7 Sep: a 1.5 MB mp4 came through and decoded to a clean 10 s, 720×1280 h264 file.

**Over 10 MB the connector refuses**, with "File too large for download, over limit of 10 MB.
For downloading larger files, use the standard Google Drive API." That is a hard cap in the
connector, not a context limit.

What that means for this library:

| | |
|---|---|
| **The 18 raw shoot clips** (19–25 MB each) | **out of reach** — every one is over the cap |
| Brand-film exports, the Aurora hallway cinematic, the Gemini clips, the finished reels (1.5–9 MB) | **downloadable** |
| The two wall-light ad exports (28 MB, 62 MB) | out of reach |
| Product photographs (4–7 MB) | **downloadable** |
| Drive metadata — search, titles, structure | always readable |

So the raw shoot is the one thing a session cannot fetch, and it is exactly the material the reels
want most. Three ways round it, cheapest first:

1. **Copy the clip into the repo** (`<product>-reels/src/`) and commit it. `system/sources.py`
   registers its colour states automatically.
2. **Export a smaller version to Drive** — a 9:16 H.264 under 10 MB is plenty for a reel, since
   the renders top out at 1080×1920 anyway.
3. Use the standard Drive API with an OAuth token, which has no such cap.

Photography for the reels still comes from the **public Shopify product CDN**
(`cdn.shopify.com/s/files/1/0650/8488/3079/files/…`) — it needs no credentials, and it is the same
imagery the PDP shows. See each product's `hf/README.md`.

## Naming, if you add files

Keep the `NW-CREATIVE-{IMG|VID}-{date}-{handle}-{description}-{ratio}-v{n}` convention: it is what makes a product's assets findable by title search, since the Drive API here cannot list a folder by parent id.
