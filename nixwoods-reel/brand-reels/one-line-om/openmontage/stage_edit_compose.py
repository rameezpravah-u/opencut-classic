"""OpenMontage run nixline-one-line-of-light: edit (edit_decisions) + compose through video_compose."""
import glob, json, os
from lib.checkpoint import write_checkpoint, PROJECTS_DIR
from tools.video.video_compose import VideoCompose

PID = "nixline-one-line-of-light"
proj = PROJECTS_DIR / PID
WS = proj / "hyperframes"
shell = sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell"))
if shell:
    os.environ.setdefault("HYPERFRAMES_BROWSER_PATH", shell[-1])   # the CLI's own Chrome download is blocked here
os.environ["HYPERFRAMES_SKIP_SKILLS"] = "1"
os.environ["DO_NOT_TRACK"] = "1"

A = lambda p: str(WS / "assets" / p)
edit = {
    "version": "1.0",
    "render_runtime": "hyperframes",
    "composition_mode": "atelier",
    "bespoke": {"entry": str(WS / "index.html"), "composition_id": "main",
                "art_direction": "nixwoods-reel/MOTION.md Dusk look; the line holds on x 540 across cuts"},
    "cuts": [
        {"id": "c1", "source": A("s1.mp4"), "in_seconds": 0, "out_seconds": 1.6667, "layer": "primary", "reason": "hook; the line draws on beat 1"},
        {"id": "c2", "source": A("s2.mp4"), "in_seconds": 0, "out_seconds": 1.6667, "layer": "primary", "reason": "the real channel on beat 2"},
        {"id": "c3", "source": A("s3.mp4"), "in_seconds": 0, "out_seconds": 0.8334, "layer": "primary", "reason": "many lines, beat 4"},
        {"id": "c4", "source": A("s4.mp4"), "in_seconds": 0, "out_seconds": 0.8333, "layer": "primary", "reason": "standing upright, beat 5"},
        {"id": "c5", "source": A("corner.jpg"), "in_seconds": 0, "out_seconds": 5.0333, "layer": "primary", "reason": "the corner, beat 6, 5% push"},
        {"id": "c6", "source": A("ground.png"), "in_seconds": 0, "out_seconds": 3.3333, "layer": "overlay", "reason": "end card, beat 8"},
    ],
    "metadata": {"music": "music6-corners from 0.396 s, fade over the last 0.8 s", "fps": 30, "duration_seconds": 10.0333},
}
(proj / "artifacts" / "edit_decisions.json").write_text(json.dumps(edit, indent=2))
write_checkpoint(PROJECTS_DIR, PID, "edit", "completed", {"edit_decisions": edit}, pipeline_type="hybrid")

out = proj / "renders" / "final.mp4"
res = VideoCompose().execute({
    "operation": "render", "edit_decisions": edit,
    "asset_manifest": json.load(open(proj / "artifacts" / "asset_manifest.json")),
    "workspace_path": str(WS), "output_path": str(out), "fps": 30, "quality": "high",
    "proposal_packet": {"production_plan": {"render_runtime": "hyperframes"}},
})
print("success:", res.success)
print("error:", res.error)
d = res.data or {}
print(json.dumps({k: d[k] for k in d if k in ("final_review_status", "final_review", "output_path", "duration_seconds")}, indent=1, default=str)[:4000])
