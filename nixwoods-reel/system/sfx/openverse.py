#!/usr/bin/env python3
"""openverse.py: search and download free sound effects from the Openverse API (api.openverse.org, 5M+ openly
licensed audio files, mostly Freesound), with the licence recorded for every file used.

    python3 system/sfx/openverse.py search "wood knock" [--n 10] [--allow-by] [--max-dur 3]
    python3 system/sfx/openverse.py get <openverse-id> [--allow-by]        # downloads into the cache, logs the credit

Rules (FREE-TOOLS.md "Sound"):
- CC0 / public domain by default: nothing to credit. --allow-by also admits CC-BY, which then needs the credit line
  from SFX-CREDITS.tsv in the caption. NC (non-commercial) and ND licences are never used: our reels are commercial.
- Anonymous API: no key, no account. Files land in ~/.cache/nixwoods-sfx/openverse (not the repo); a reel that uses
  one copies it next to its script, and the credit row travels with it.
"""
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://api.openverse.org/v1/audio/"
CACHE = os.path.expanduser("~/.cache/nixwoods-sfx/openverse")
CREDITS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "brand-reels", "audio", "SFX-CREDITS.tsv")
FREE = {"cc0", "pdm"}
BY = {"by"}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "nixwoods-reel/1.0 (sound search)"})
    for k in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception:
            if k == 3:
                raise
            time.sleep(2 ** k)


def allowed(lic, allow_by):
    return lic in FREE or (allow_by and lic in BY)


def search(q, n=10, allow_by=False, max_dur=None):
    lic = "cc0,pdm" + (",by" if allow_by else "")
    params = {"q": q, "license": lic, "page_size": min(50, n * 3), "category": "sound_effect"}
    d = json.loads(_get(API + "?" + urllib.parse.urlencode(params)))
    out = []
    for r in d.get("results", []):
        dur = (r.get("duration") or 0) / 1000
        if not allowed(r.get("license"), allow_by) or (max_dur and dur > max_dur):
            continue
        out.append({"id": r["id"], "title": r.get("title"), "creator": r.get("creator"), "license": r["license"],
                    "license_version": r.get("license_version"), "duration_s": round(dur, 2),
                    "provider": r.get("provider"), "url": r["url"], "page": r.get("foreign_landing_url")})
        if len(out) >= n:
            break
    if not out and params["category"]:                     # many good effects carry no category: retry without it
        params.pop("category")
        d = json.loads(_get(API + "?" + urllib.parse.urlencode(params)))
        for r in d.get("results", []):
            dur = (r.get("duration") or 0) / 1000
            if allowed(r.get("license"), allow_by) and not (max_dur and dur > max_dur):
                out.append({"id": r["id"], "title": r.get("title"), "creator": r.get("creator"),
                            "license": r["license"], "license_version": r.get("license_version"),
                            "duration_s": round(dur, 2), "provider": r.get("provider"), "url": r["url"],
                            "page": r.get("foreign_landing_url")})
            if len(out) >= n:
                break
    return out


def get(oid, allow_by=False):
    """download one file into the cache (once) and log its credit row; returns the local path"""
    r = json.loads(_get(API + oid + "/"))
    if not allowed(r.get("license"), allow_by):
        raise SystemExit(f"openverse: {oid} is {r.get('license')}; only CC0/PDM (or CC-BY with --allow-by)")
    os.makedirs(CACHE, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(r["url"]).path)[1] or ".mp3"
    path = os.path.join(CACHE, oid + ext)
    if not os.path.exists(path):
        try:
            data = _get(r["url"])
        except urllib.error.HTTPError as e:
            if e.code == 403 and "freesound" in r["url"]:
                raise SystemExit("openverse: the Freesound CDN refuses this machine (403; it does from cloud sessions, "
                                 "it works from the Mac). Fetch it there, or use place.py's synthesized sound.")
            raise
        with open(path + ".part", "wb") as f:
            f.write(data)
        os.replace(path + ".part", path)
    row = "\t".join([oid, (r.get("title") or "").replace("\t", " "), (r.get("creator") or "").replace("\t", " "),
                     f"{r['license']} {r.get('license_version') or ''}".strip(), r.get("foreign_landing_url") or r["url"],
                     time.strftime("%Y-%m-%d")])
    have = open(CREDITS).read() if os.path.exists(CREDITS) else ""
    if oid not in have:
        with open(CREDITS, "a") as f:
            if not have:
                f.write("# Openverse sounds used in NixWoods reels: id, title, creator, licence, source, date fetched.\n"
                        "# CC0/PDM need no credit; a CC-BY row needs 'Sound: <title> by <creator> (CC BY)' in the caption.\n")
            f.write(row + "\n")
    return path


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--n", type=int, default=10)
    s.add_argument("--allow-by", action="store_true")
    s.add_argument("--max-dur", type=float)
    s.add_argument("--json", action="store_true")
    g = sub.add_parser("get")
    g.add_argument("id")
    g.add_argument("--allow-by", action="store_true")
    a = ap.parse_args()
    if a.cmd == "search":
        res = search(a.query, a.n, a.allow_by, a.max_dur)
        if a.json:
            print(json.dumps(res, indent=1))
        else:
            for r in res:
                print(f"{r['id']}  {r['duration_s']:5.2f}s  {r['license']:4}  {r['title'][:60]}  ({r['creator']})")
    else:
        print(get(a.id, a.allow_by))


if __name__ == "__main__":
    sys.exit(main())
