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

## Access constraint (read this before planning around Drive)

Drive files here are private, so an agent session **cannot download them**. The API returns file bytes as base64 through the conversation, and these are 4–7 MB photographs and 20–28 MB videos — far past what fits. `https://drive.google.com/uc?export=download` hits a login wall.

What this means in practice:

- **Drive is the source of truth for people, not the pipeline.** Humans pull from it; sessions cannot.
- **The working image source for reels is the Shopify product CDN** (`cdn.shopify.com/s/files/1/0650/8488/3079/files/…`), which is public, free and is the same photography the PDP shows. That is where `aurora-reels/hf/`, `rosewood-reels/hf/` and `teak-reels/hf/` came from — see each product's `hf/README.md`.
- **To get a Drive asset into the system**, a person copies it into the product folder in this repo (`<product>-reels/src/` for footage, `hf/` for stills) and commits it. `system/sources.py` then registers a video's colour states automatically.
- Drive *metadata* — search, titles, folder structure — is fully readable, which is how this map was verified.

## Naming, if you add files

Keep the `NW-CREATIVE-{IMG|VID}-{date}-{handle}-{description}-{ratio}-v{n}` convention: it is what makes a product's assets findable by title search, since the Drive API here cannot list a folder by parent id.
