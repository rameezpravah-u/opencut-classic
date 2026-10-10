"""OpenMontage run nixline-one-line-of-light: idea (approved) + script (awaiting approval)."""
import json
from pathlib import Path
from lib.checkpoint import init_project, write_checkpoint, PROJECTS_DIR

PID = "nixline-one-line-of-light"
B = 0.8357  # music6-corners beat; music starts at its first beat (0.396 s) so beat n lands at n*B
t = lambda n: round(n * B, 3)

init_project(PID, title="NixLine: One line of light", pipeline_type="hybrid")

brief = {
    "version": "1.0",
    "title": "NixLine: One line of light",
    "hook": "It starts as one line.",
    "key_points": [
        "A raw solid-teak bar becomes a line of warm light",
        "Solid teak, made by hand in Uttar Pradesh",
        "NixLine warms one corner of a real room",
        "₹999 (was ₹1,599), cash on delivery, free delivery",
    ],
    "core_message": "One line of teak, lit warm, changes a corner.",
    "cta": "nixwoods.com — ₹999, COD, free delivery",
    "tone": "warm, calm, honest; the light does the selling, the type stays quiet",
    "style": "custom: NixWoods MOTION.md Dusk look (atelier composition)",
    "target_audience": "Indian home-makers 25-65 who live with a white tubelight",
    "target_platform": "instagram",
    "target_duration_seconds": 10,
    "reference_material": [
        "nixwoods-reel/MOTION.md", "nixwoods-reel/brand.md",
        "floor-reels/src/nx0*.mp4 (real NixLine workshop footage)",
        "drive-pull/shoot-20260805/...AC4I9815 (NixLine, clean 5 Aug shoot)",
    ],
    "selected_angle": "One line of light",
    "metadata": {
        "anchor_medium": "broll_footage",
        "source_inventory": [
            "floor-reels/src/nx06-7921.mp4: unlit teak bar on carpet (4.8 s), lit bar held vertical (8.6 s)",
            "floor-reels/src/nx03-7926.mp4: bundle of lit bars, vertical",
            "floor-reels/src/nx07-7922.mp4: lit bar vertical (0.3 s)",
            "AC4I9815: NixLine upright on its teak block in a room",
        ],
        "support_layers": [
            "glowing line (cream core #FFEED2, amber halo #E8A24A): draws down the unlit bar, then hands off to the real lit channel across cuts",
            "quiet type (Fraunces 600 / Inter), on scrims, never across the lit channel",
            "end card: logo, NixLine, ₹999 / ₹1,599, chips",
            "music6-corners (cleared for paid), cut on its beat",
        ],
        "deliverable_mix": ["9:16 1080x1920 hero, 30 fps, ~10 s (organic + ad length)"],
        "missing_capabilities": [
            "no image/video generation keys: none needed, every frame is real footage or the real photo",
            "no TTS used: music-only by choice",
        ],
        "fallback_policy": "No generated frames, so no AI label. Any substitution of runtime or footage goes back to the user first.",
        "brand_rules": "MOTION.md sections 1-7; banned-word list in brand.md; lamp always upright",
    },
}

def opt(i, label, score, reason, rej=None):
    o = {"option_id": i, "label": label, "score": score, "reason": reason}
    if rej:
        o["rejected_because"] = rej
    return o

decisions = {"version": "1.0", "project_id": PID, "decisions": [
    {"decision_id": "d-001", "stage": "idea", "category": "pipeline_selection", "subject": "Pipeline",
     "options_considered": [
         opt("hybrid", "hybrid", 0.9, "real footage anchor + designed line/type support"),
         opt("cinematic", "cinematic", 0.6, "mood edit, but built around generated clips", "no video generation available"),
         opt("documentary-montage", "documentary-montage", 0.4, "stock-corpus montage", "our own footage, not stock")],
     "selected": "hybrid", "reason": "Footage-led with one support layer (the line) and quiet type.",
     "user_visible": True, "user_approved": False, "confidence": 0.85},
    {"decision_id": "d-002", "stage": "idea", "category": "concept_selection", "subject": "Concept",
     "options_considered": [
         opt("one-line", "One line of light", 0.9, "the brand's own moving element as the idea"),
         opt("tubelight", "Tubelight vs teak", 0.7, "proven V1 story", "user picked One line of light"),
         opt("five-cuts", "Made by hand, in 5 cuts", 0.6, "honest process", "user picked One line of light")],
     "selected": "one-line", "reason": "User choice.", "user_visible": True, "user_approved": True, "confidence": 0.9},
    {"decision_id": "d-003", "stage": "idea", "category": "render_runtime_selection", "subject": "Composition runtime",
     "options_considered": [
         opt("hyperframes", "HyperFrames", 0.85, "GSAP line drawing and kinetic type in our fonts; footage as <video class=clip>"),
         opt("remotion", "Remotion", 0.7, "React + OffthreadVideo, word captions", "user picked HyperFrames; springs risk bounce"),
         opt("ffmpeg", "FFmpeg", 0.3, "cuts only", "cannot draw the line or set type")],
     "selected": "hyperframes", "reason": "User choice; best fit for a self-drawing line.",
     "user_visible": True, "user_approved": True, "confidence": 0.85},
    {"decision_id": "d-004", "stage": "idea", "category": "composition_mode", "subject": "Authoring mode",
     "options_considered": [
         opt("atelier", "Atelier (hand-authored)", 0.9, "brand hero piece; MOTION.md look"),
         opt("templated", "Templated scene types", 0.4, "fast", "stock look, off-brand")],
     "selected": "atelier", "reason": "Brand hero work; every value comes from MOTION.md.",
     "user_visible": True, "user_approved": False, "confidence": 0.85},
    {"decision_id": "d-005", "stage": "idea", "category": "voice_selection", "subject": "Narration",
     "options_considered": [
         opt("none", "No voice, music only", 0.9, "matches shipped NixWoods reels"),
         opt("piper", "Piper TTS", 0.4, "free offline", "user chose music only; synthetic sound")],
     "selected": "none", "reason": "User choice.", "user_visible": True, "user_approved": True, "confidence": 0.9},
    {"decision_id": "d-006", "stage": "idea", "category": "music_source", "subject": "Music track",
     "options_considered": [
         opt("music6", "music6-corners (our library, cleared for paid)", 0.85, "calm, 71.8 bpm, beat 0.8357 s; 12 beats = 10.03 s"),
         opt("music3", "music3-design (our library)", 0.6, "99.4 bpm with a drop", "busier than the calm brief"),
         opt("pixabay", "Pixabay search", 0.3, "free", "unmeasured, licence per track")],
     "selected": "music6", "reason": "Calm tempo fits a line that warms up; already measured and cleared.",
     "user_visible": True, "user_approved": False, "confidence": 0.8},
]}

proj = PROJECTS_DIR / PID
(proj / "artifacts" / "brief.json").write_text(json.dumps(brief, indent=2))
write_checkpoint(PROJECTS_DIR, PID, "idea", "completed", {"brief": brief, "decision_log": decisions},
                 pipeline_type="hybrid", human_approval_required=True, human_approved=True,
                 metadata={"approval_note": "concept, runtime and voice chosen by the user in chat, 10 Oct 2026"})

script = {
    "version": "1.0",
    "title": "NixLine: One line of light",
    "total_duration_seconds": t(12),
    "sections": [
        {"id": "s1", "label": "hook / unlit teak", "text": "It starts as / one line.", "start_seconds": 0, "end_seconds": t(2),
         "speaker_directions": "on-screen only; Fraunces 600 96 px cream on a top scrim, readable by 0.17 s",
         "enhancement_cues": [{"type": "animation", "description": "glowing line draws down the unlit bar, expo-out over 0.6 s, from beat 1", "timestamp_seconds": t(1)}],
         "source_ref": "footage nx06-7921 @4.8 s"},
        {"id": "s2", "label": "the line is real light", "text": "Solid teak. / Made by hand.", "start_seconds": t(2), "end_seconds": t(4),
         "speaker_directions": "on-screen only; Fraunces 600 88 px, split either side of the lit channel",
         "enhancement_cues": [{"type": "animation", "description": "drawn line hands off to the real lit channel on the cut", "timestamp_seconds": t(2)}],
         "source_ref": "brand.md: solid teak, handmade in Uttar Pradesh"},
        {"id": "s3", "label": "many lines", "text": "", "start_seconds": t(4), "end_seconds": t(5),
         "speaker_directions": "no text; one beat", "source_ref": "footage nx03-7926"},
        {"id": "s4", "label": "one line again", "text": "", "start_seconds": t(5), "end_seconds": t(6),
         "speaker_directions": "no text; one beat", "source_ref": "footage nx07-7922"},
        {"id": "s5", "label": "the corner", "text": "Then it warms / the corner.", "start_seconds": t(6), "end_seconds": t(8),
         "speaker_directions": "on-screen only; 'corner.' in Fraunces 500 italic amber; slow push into the lamp",
         "source_ref": "photo AC4I9815"},
        {"id": "s6", "label": "end card", "text": "NixLine. ₹999 ₹1,599 · Solid teak · COD · Free delivery", "start_seconds": t(8), "end_seconds": t(12),
         "speaker_directions": "logo 520 px, price Inter 600 112 px amber, was-price struck, chips; holds 4 beats; music fades last 0.8 s",
         "source_ref": "brand.md: ₹999 (compare-at ₹1,599), COD, free delivery"},
    ],
    "metadata": {
        "anchor_sections": ["s1", "s2", "s3", "s4", "s5"],
        "support_sections": ["s1 line draw", "s6 end card"],
        "narration_sections": [],
        "required_support_assets": ["Fraunces/Inter fonts (nixwoods-reel/assets)", "logo.png", "music6-corners.mp3"],
        "beat_grid": "music6-corners from 0.396 s; beat n at n*0.8357 s; cuts on beats 2, 4, 5, 6, 8",
        "words_per_screen_max": 12,
    },
}
(proj / "artifacts" / "script.json").write_text(json.dumps(script, indent=2))
write_checkpoint(PROJECTS_DIR, PID, "script", "awaiting_human", {"script": script},
                 pipeline_type="hybrid", human_approval_required=True)
print("ok", proj)
