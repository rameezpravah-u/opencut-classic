# 3D installation video → nixwoods.com/pages/installation-video

Status: **ready, not published** — Shopify's connector was signed out when this was prepared.

| file | what |
|---|---|
| `../out/motion/NX-MOTION-teak-pendant-install-v1.mp4` | the video, 18.4 s, 3.0 MB |
| `install-3d-poster.jpg` | poster: the hook frame at 1.25 s ("before you drill, watch this.") |
| `install-3d-section.html` | the block to add, styled to match the page's existing video block |

## Publishing (additive only)

1. Upload the mp4 and the poster to Shopify Files (staged upload → `fileCreate`, `contentType: FILE`
   for the mp4 so it gets a plain `cdn.shopify.com/s/files/...mp4` URL that a `<video>` tag plays).
2. Read the page body by handle `installation-video` and **save it here as `page-body-before.html`**
   before changing anything, so the edit can be reverted exactly.
3. Insert `install-3d-section.html` (with `VIDEO_URL` / `POSTER_URL` filled) immediately after the
   closing `</div>` of the existing video block - the one whose `<source>` is
   `566717c3c65a40cbbfc4705bb766c51a...`. Nothing else in the body changes.
4. `pageUpdate` with the new body, then fetch the live page and confirm the new `<source>` URL is present
   and returns `200 video/mp4`.

## Notes for whoever approves it

- The page's existing workshop video shows a **round** canopy; this 3D video shows the Double Arm Teak's
  **rectangular** canopy, as on its product page. The copy says "shown on the Double Arm Teak pendant"
  so the difference reads as intended rather than as an error.
- Canopy screw positions in the 3D model are placed by eye - the guide does not document them. Step 1
  has the customer mark through the canopy's own holes, so the drawing does not set where anyone drills.
