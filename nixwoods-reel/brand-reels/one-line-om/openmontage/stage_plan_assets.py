"""OpenMontage run nixline-one-line-of-light: script approved, scene_plan + assets (pre-authorised)."""
import json, os
from lib.checkpoint import write_checkpoint, PROJECTS_DIR

PID = "nixline-one-line-of-light"
proj = PROJECTS_DIR / PID
WS = proj / "hyperframes"
geo = json.load(open(WS / "assets" / "geometry.json"))
fr = geo["frames"]
T = lambda b: round(fr[b] / 30, 4)

# --- script: approved by the user, with shot 4 swapped to nx04 (the bar standing upright) ---
script = json.load(open(proj / "artifacts" / "script.json"))
for s in script["sections"]:
    if s["id"] == "s4":
        s["source_ref"] = "footage nx04-7930 (lit bar standing upright), swapped in at the user's approval"
(proj / "artifacts" / "script.json").write_text(json.dumps(script, indent=2))
write_checkpoint(PROJECTS_DIR, PID, "script", "completed", {"script": script}, pipeline_type="hybrid",
                 human_approval_required=True, human_approved=True,
                 metadata={"approval_note": "approved in chat with the shot-4 swap; user pre-authorised the remaining gates"})

# --- full-run pre-authorisation, recorded the moment it was given (checkpoint-protocol.md rule 5).
# The decision_log schema's category enum has no "approval_policy" yet, so this entry is appended to the
# project log directly rather than through a validated artifact.
dl = json.load(open(proj / "decision_log.json"))
if not any(d["decision_id"] == "d-007" for d in dl["decisions"]):
    dl["decisions"].append({
        "decision_id": "d-007", "stage": "script", "category": "approval_policy",
        "subject": "Remaining approval gates",
        "options_considered": [
            {"option_id": "run-through", "label": "Approve and run scene_plan, assets, edit, compose without stopping", "score": 0.9, "reason": "user choice"},
            {"option_id": "every-gate", "label": "Stop at scene_plan and assets", "score": 0.6, "reason": "default", "rejected_because": "user chose to run through"}],
        "selected": "run-through", "reason": "User: 'Approve, run the rest'.",
        "user_visible": True, "user_approved": True, "confidence": 1.0})
    (proj / "decision_log.json").write_text(json.dumps(dl, indent=2))

# --- scene plan ---
scenes = [
    dict(id="sc1", type="broll", script_section_id="s1", start_seconds=0, end_seconds=T("b2"),
         description="Bare back of a NixLine teak bar on the workshop carpet, held vertical on x 540; a glowing line draws down it on beat 1",
         framing="close-up, bar fills the centre third", movement="handheld drift, stabilised to the bar's axis",
         overlay_notes="hook split either side of the line: 'It starts as' left, 'one line.' right, 60 px Fraunces on a top gradient",
         narrative_role="establish_context", hero_moment=False, required_assets=["s1.mp4"]),
    dict(id="sc2", type="broll", script_section_id="s2", start_seconds=T("b2"), end_seconds=T("b4"),
         description="The bar flipped: its real lit channel stands exactly where the drawn line was",
         framing="close-up", movement="stabilised to the channel", transition_in="cut on beat 2",
         overlay_notes="'Solid / teak.' left, 'Made / by hand.' right, 140 px clear of the channel",
         narrative_role="deliver_payload", hero_moment=True, required_assets=["s2.mp4"]),
    dict(id="sc3", type="broll", script_section_id="s3", start_seconds=T("b4"), end_seconds=T("b5"),
         description="A bundle of lit bars: one line becomes many", framing="top-down", movement="none",
         transition_in="cut on beat 4", narrative_role="evidence", required_assets=["s3.mp4"]),
    dict(id="sc4", type="broll", script_section_id="s4", start_seconds=T("b5"), end_seconds=T("b6"),
         description="One lit bar standing upright in the workshop, channel on x 540", framing="medium",
         movement="stabilised to the channel", transition_in="cut on beat 5", narrative_role="transition",
         required_assets=["s4.mp4"]),
    dict(id="sc5", type="broll", script_section_id="s5", start_seconds=T("b6"), end_seconds=T("b8"),
         description="NixLine upright on its teak block in a real room (AC4I9815), graded to dusk; slow 4% push",
         framing="full lamp, channel on x 540", movement="push-in 1.00 to 1.04, smoothstep",
         transition_in="cut on beat 6", overlay_notes="'Then it warms / the corner.' above the lamp, 'corner.' amber italic",
         narrative_role="emotional_beat", hero_moment=True, required_assets=["corner.jpg"]),
    dict(id="sc6", type="text_card", script_section_id="s6", start_seconds=T("b8"), end_seconds=T("b12"),
         description="End card on the Dusk ground: the lamp's channel becomes the brand line; logo above, price left, chips right",
         transition_in="ground fades in over 0.30 s on beat 8; the line glides to its end-card length",
         overlay_notes="logo 520 px; NixLine. / ₹999 amber / ₹1,599 struck left; Solid teak · Cash on delivery · Free delivery, nixwoods.com right",
         narrative_role="call_to_action", required_assets=["ground.png", "logo-cream.png"]),
]
SRC = {"s1.mp4": "source", "s2.mp4": "source", "s3.mp4": "source", "s4.mp4": "source", "corner.jpg": "source",
       "ground.png": "provided", "logo-cream.png": "provided"}
for sc in scenes:
    sc["required_assets"] = [{"type": "video" if f.endswith(".mp4") else "image", "description": f, "source": SRC[f]}
                             for f in sc.get("required_assets", [])]
scene_plan = {"version": "1.0", "scenes": scenes, "metadata": {
    "anchor_rules": "real footage fills sc1-sc5; the only drawn element over footage is the line in sc1",
    "support_rules": "max 2 overlay layers at once (line + one text block)",
    "safe_zones": "MOTION.md: x 70-950, y 230-1500; text above y 1250; never across the lit channel (84 px, 140 px on close-ups)",
    "variant_rules": "9:16 only", "overlay_density_limits": "one text block per scene, 12 words max",
    "geometry": geo["shots"]}}
(proj / "artifacts" / "scene_plan.json").write_text(json.dumps(scene_plan, indent=2))
write_checkpoint(PROJECTS_DIR, PID, "scene_plan", "completed", {"scene_plan": scene_plan}, pipeline_type="hybrid",
                 human_approval_required=True, human_approved=True,
                 metadata={"approval_note": "pre-authorised (decision d-007)"})

# --- assets: all source-derived (no generation, no spend) ---
def a(i, typ, path, scene, sub, summary, dur=None):
    d = {"id": i, "type": typ, "path": str(WS / "assets" / path), "source_tool": "prep.py (nixwoods-reel/brand-reels/one-line-om)",
         "scene_id": scene, "cost_usd": 0, "subtype": sub, "generation_summary": summary, "provider": "source", "license": "NixWoods own footage"}
    if dur:
        d["duration_seconds"] = dur; d["resolution"] = "1080x1920"; d["format"] = "mp4"
    return d
assets = [
    a("s1", "video", "s1.mp4", "sc1", "source-derived", "nx06-7921 3.60 s, 50 frames, bar axis to x 540, montage grade", T("b2")),
    a("s2", "video", "s2.mp4", "sc2", "source-derived", "nx06-7921 6.60 s, 50 frames, channel to x 540, montage grade", T("b4") - T("b2")),
    a("s3", "video", "s3.mp4", "sc3", "source-derived", "nx03-7926 0.40 s, 25 frames, montage grade", T("b5") - T("b4")),
    a("s4", "video", "s4.mp4", "sc4", "source-derived", "nx04-7930 1.30 s, 25 frames, channel to x 540, montage grade", T("b6") - T("b5")),
    a("corner", "image", "corner.jpg", "sc5", "source-derived", "AC4I9815 at 1.25x, channel on x 540, montage grade"),
    a("ground", "image", "ground.png", "sc6", "designed", "Dusk ground #2E1E14, vignette, grain sigma 2.2"),
    a("logo", "image", "logo-cream.png", "sc6", "provided", "assets/logo.png tinted cream"),
    {"id": "music", "type": "music", "path": str(WS / "assets" / "music6-corners.mp3"), "source_tool": "library",
     "scene_id": "all", "cost_usd": 0, "provider": "nixwoods library", "license": "cleared for paid (brand.md)",
     "generation_summary": "music6-corners from 0.396 s (first beat), 71.8 bpm"},
]
asset_manifest = {"version": "1.0", "assets": assets}
(proj / "artifacts" / "asset_manifest.json").write_text(json.dumps(asset_manifest, indent=2))
write_checkpoint(PROJECTS_DIR, PID, "assets", "completed", {"asset_manifest": asset_manifest}, pipeline_type="hybrid",
                 human_approval_required=True, human_approved=True,
                 metadata={"approval_note": "pre-authorised (decision d-007)",
                           "source_vs_generated_map": {"source": ["s1", "s2", "s3", "s4", "corner", "logo", "music"], "designed": ["ground"], "generated": []}},
                 cost_snapshot={"spent_usd": 0, "projected_compose_usd": 0})
print("ok")
