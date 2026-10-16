"""Land one Drive file in library/cache/ at full size and check it against the index.

A session gets a signed download link for any Drive file, of any size, by calling the Composio Google Drive tool
GOOGLEDRIVE_DOWNLOAD_FILE with the file's drive_id (from the private index, nixwoods-os
30-Creative/library/INDEX.tsv). The link is downloaded here, and its md5 must equal the index's (Drive's own
checksum). The cache is not committed: this repository is public.

    python3 nixwoods-reel/library/fetch.py <drive_id> '<signed url>'
"""
import csv, hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(os.path.dirname(os.path.dirname(HERE)), "..", "nixwoods-os", "30-Creative",
                     "library", "INDEX.tsv")
CACHE = os.path.join(HERE, "cache")


def row(drive_id):
    for r in csv.DictReader(open(INDEX), delimiter="\t"):
        if r["drive_id"] == drive_id:
            return r
    sys.exit(f"{drive_id} is not in {INDEX}")


def main(drive_id, url):
    r = row(drive_id)
    if r["use"] == "DO-NOT-USE":
        sys.exit(f"refused: {r['name']} is DO-NOT-USE ({r['why']})")
    os.makedirs(CACHE, exist_ok=True)
    dest = os.path.join(CACHE, f"{drive_id}-{r['name']}")
    if not os.path.exists(dest):
        subprocess.run(["curl", "-sSL", "--fail", "-o", dest + ".part", url], check=True)
        os.replace(dest + ".part", dest)
    md5 = hashlib.md5(open(dest, "rb").read()).hexdigest()
    if r["md5"] and md5 != r["md5"]:
        os.remove(dest)
        sys.exit(f"md5 mismatch for {r['name']}: got {md5}, Drive says {r['md5']}")
    print(dest, f"{r['size_mb']} MB", r["use"], r["product_guess"] or "(product not tagged)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
