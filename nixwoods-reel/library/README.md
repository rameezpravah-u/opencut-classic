# The NixWoods Drive library: how a session reaches all of it

Set up 16 Oct 2026 at the owner's request: "figure out a way to use all the NixWoods content that is there on the
Drive."

## What is there (16 Oct listing)
**Size:** 6,707 photos and videos under the `nixwoods` Drive root, 32 GB in all.
- **Unique:** 4,846 files (3,908 photos and 938 videos).
- **Duplicates:** the other 1,861 are byte-identical copies.

**Status of the unique files:**

| Status | Files | Meaning |
|---|---|---|
| OK | 2,137 | Usable once the product is confirmed. Includes 295 videos over 10 MB. |
| CHECK | 2,141 | In holding folders such as "to be tagged" or quarantine. Look at them before use. |
| AI-LABEL | 434 | Generated. Use only with the AI label. |
| ASK | 17 | Customer testimonial pictures. |
| DO-NOT-USE | 117 | The watermarked 5 Aug shoot and other brands' reference material. |

**Left out:** the other ~13,000 files in the Drive, which sit outside the `nixwoods` root (WhatsApp backups, sent
items, icons).

## Where things are kept
This repository is **public**, so nothing that names or shows unreleased files lives here.

| What | Where |
|---|---|
| The index, one row per file: id, name, folder, kind, size, dimensions, duration, product guess, use status, duplicate-of, md5 | private repo **nixwoods-os**, `30-Creative/library/INDEX.tsv` |
| Product tags confirmed by eye or by the owner | nixwoods-os, `30-Creative/library/TAGS.tsv` |
| The scripts | here: `build_index.py` and `fetch.py` |
| Downloaded files | here, `library/cache/`, which is never committed. They are re-fetched on demand. |

## How to reach a file of any size
The Google Drive connector built into a session refuses files over 10 MB (DRIVE-MAP.md). The **Composio Google
Drive** connection, authorised by the owner on 16 Oct, does not.

1. Find the file in `INDEX.tsv`, by product, folder or name.
2. Call the Composio tool `GOOGLEDRIVE_DOWNLOAD_FILE` with `fileId` = its `drive_id`. It returns
   `downloaded_file_content.s3url`, a signed link that is valid for an hour.
3. Run `python3 nixwoods-reel/library/fetch.py <drive_id> '<s3url>'`. It downloads to `library/cache/`, refuses
   DO-NOT-USE rows, and checks the file's md5 against Drive's.

Checked 16 Oct: a 24.3 MB raw shoot clip (the Aurora "hook switch-on", 1080×1920, 19 s) came down whole. Its md5
matched Drive's and it decoded cleanly.

## Rebuilding the index
In the Composio workbench, page `GOOGLEDRIVE_FIND_FILE` over all image and video files with
`fields=nextPageToken,files(id,name,mimeType,size,parents,createdTime,md5Checksum,imageMediaMetadata(width,height),videoMediaMetadata(width,height,durationMillis))`,
plus all folders (`id,name,parents`). Save the JSON, then run `build_index.py <json> <nixwoods-os INDEX.tsv>`.

## Before anything goes into a reel
These rules still apply:
- **Product:** name it with the PRODUCT-ID.md tells, or ask the owner. Folder and filename guesses are guesses, and
  several shoot filenames are wrong.
- **Faces:** none without a release.
- **AI:** generated material carries the AI label.
- **Watermarks:** never pull from the watermarked archive.
