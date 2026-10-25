# Hypit at NixWoods: house rules (read with SKILL.md)

The skill files in this folder are copied unchanged from github.com/hypit-ai/hypit at tag v0.3.1 (commit `8efbac0`).
The licence is in `../_licenses/hypit-LICENSE.txt`: a modified Apache-2.0, free for our own organisation's
commercial work, with no reselling or hosting it for others. Its name and logo stay in its CLI and reports.

**What it gives us:** a reel rebuilt as a workflow anchored to the spoken words. Change a line, the hook, the
product, the language or the aspect ratio, and the timing re-flows, so one working reel becomes many variants.
The owner sent this on 25 Oct (instagram.com/reel/De0xibcTMkE).

## Rules that win over SKILL.md
- **The code-only path.** Captions, motion graphics, our own footage (`source/`, `*-reels/src`) and our own stills. No
  generation models unless the owner approves the spend. Higgsfield credits and ElevenLabs credits need the owner's
  OK.
- **No hosted services and no credentials.** Never sign up for HypiHub or any provider, and never paste a key. A
  service needs the owner's go-ahead first.
- **MOTION.md wins** for colour, type and timing. Product facts come only from `nixwoods-reel/PRODUCT-FACTS.md` and
  `PRODUCT-ID.md`. Banned words, the AI label and the OS filing rules all apply as for any reel.
- **No faces without a release.** A "new host" means synthetic or the owner's own footage.
- **Word timing:** use our faster-whisper (as in `.claude/skills/effects/scripts/words.py`). Prepare WhisperX only if
  it is cheap.

## Status
- **Installed on 25 Oct** (owner: "Install both"): `bash .claude/skills/hypit/setup.sh` installs
  `@hypit/hypit@0.3.1` globally. Global npm does not persist, so re-run it in each new cloud session.
- A project is a folder with a `package.json` carrying `"hypit": {"project": true}`. Run commands from there, or pass
  `--project`.
