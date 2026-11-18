"""Tests for render_reel.py (pure parts: timing, captions, clip lookup, gates).
Run from nixwoods-reel/:  python3 -m unittest system.test_render_reel -v"""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def align(text, t0=0.0, per_char=0.05):
    """A fake ElevenLabs alignment: one char every 50 ms, spaces included."""
    chars = list(text)
    starts = [round(t0 + i * per_char, 3) for i in range(len(chars))]
    ends = [round(s + per_char, 3) for s in starts]
    return {"characters": chars, "character_start_times_seconds": starts, "character_end_times_seconds": ends}


SCRIPT = {
    "id": "NW-CREATIVE-SCRIPT-20261116-test-lamp-x-v1", "handle": "test-lamp", "status": "APPROVED",
    "chosen_hook_index": 0, "hooks": [{"text": "Same bed. One bar of teak.", "frame0": "x"}],
    "beats": [
        {"vo": "Same wall, two lights.", "on_screen": "Same bed. One bar of teak.", "clip": "VEO-002", "secs": 3},
        {"vo": "Solid teak, warm white 3000K.", "on_screen": "Solid teak · warm 3000K", "clip": "VEO-007", "secs": 4},
    ],
    "cta": "Where would yours go?",
}


class WordTimingTests(unittest.TestCase):
    def setUp(self):
        import render_reel as rr
        self.rr = rr

    def test_words_from_alignment_splits_on_spaces_and_keeps_punctuation(self):
        w = self.rr.words_from_alignment(align("Same wall, two."))
        self.assertEqual([x[0] for x in w], ["Same", "wall,", "two."])
        self.assertAlmostEqual(w[0][1], 0.0)
        self.assertAlmostEqual(w[1][1], 0.25)   # "wall" starts at char 5
        self.assertAlmostEqual(w[2][2], 0.75)   # "two." ends after char 15

    def test_speak_map_expands_for_tts_and_display_word_spans_the_expansion(self):
        spoken, spans = self.rr.spoken_text("warm 3000K.", {"3000K": "three thousand K"})
        self.assertEqual(spoken, "warm three thousand K.")
        words = self.rr.words_from_alignment(align(spoken))
        disp = self.rr.display_words("warm 3000K.", spans, words)
        self.assertEqual([d[0] for d in disp], ["warm", "3000K."])
        self.assertAlmostEqual(disp[1][1], words[1][1])   # starts with "three"
        self.assertAlmostEqual(disp[1][2], words[3][2])   # ends with "K."

    def test_word_count_mismatch_falls_back_to_even_spread(self):
        spoken, spans = self.rr.spoken_text("one two three", {})
        words = self.rr.words_from_alignment(align("one two"))   # TTS dropped a word
        disp = self.rr.display_words("one two three", spans, words)
        self.assertEqual(len(disp), 3)
        self.assertTrue(all(a[2] <= b[1] + 1e-9 for a, b in zip(disp, disp[1:])))


class CaptionTests(unittest.TestCase):
    def setUp(self):
        import render_reel as rr
        self.rr = rr
        self.words = [("Solid", 0.0, 0.3), ("teak,", 0.3, 0.6), ("warm", 0.7, 1.0), ("white", 1.0, 1.3), ("3000K.", 1.3, 2.0)]

    def test_bone_serif_groups_two_words_max_and_breaks_after_comma(self):
        g = self.rr.group_words(self.words, "bone-serif")
        self.assertEqual([[w[0] for w in x["words"]] for x in g], [["Solid", "teak,"], ["warm", "white"], ["3000K."]])

    def test_groups_do_not_overlap_in_time(self):
        for style in ("bone-serif", "amber-key", "quiet-bar"):
            g = self.rr.group_words(self.words, style)
            self.assertTrue(all(a["end"] <= b["start"] + 1e-9 for a, b in zip(g, g[1:])), style)

    def test_line_styles_show_the_whole_line_as_one_group(self):
        for style in ("amber-key", "quiet-bar"):
            self.assertEqual(len(self.rr.group_words(self.words, style)), 1, style)

    def test_key_words_come_from_the_on_screen_text(self):
        keys = self.rr.key_words("Solid teak · warm 3000K")
        self.assertIn("teak", keys)
        self.assertIn("3000k", keys)
        self.assertNotIn("·", keys)

    def test_at_most_one_highlighted_word_per_group_and_it_is_the_last_key(self):
        g = self.rr.group_words(self.words, "amber-key")[0]
        hi = self.rr.highlight(g, {"solid", "teak", "warm", "3000k"})
        self.assertEqual(hi, {4})   # "3000K." only

    def test_unknown_style_is_refused(self):
        with self.assertRaises(ValueError):
            self.rr.group_words(self.words, "neon-3d")


class PlanTests(unittest.TestCase):
    def setUp(self):
        import render_reel as rr
        self.rr = rr

    def test_beat_starts_are_cumulative(self):
        self.assertEqual(self.rr.beat_starts(SCRIPT), [0.0, 3.0])

    def test_only_an_approved_script_renders(self):
        s = dict(SCRIPT, status="AWAITING-OWNER")
        with self.assertRaises(ValueError):
            self.rr.check_renderable(s)

    def test_clip_lookup_finds_file_by_id_and_refuses_missing_or_unshot(self):
        with tempfile.TemporaryDirectory() as d:
            src = pathlib.Path(d)
            (src / "VEO-002-aurora-flip-9x16-clean.mp4").write_bytes(b"x")
            self.assertEqual(self.rr.find_clip(src, "VEO-002").name, "VEO-002-aurora-flip-9x16-clean.mp4")
            with self.assertRaises(FileNotFoundError):
                self.rr.find_clip(src, "VEO-099")
            with self.assertRaises(ValueError):
                self.rr.find_clip(src, "needs-shoot")


if __name__ == "__main__":
    unittest.main()


class SegmentFilterTests(unittest.TestCase):
    """Cut options for stills and short clips (built 2026-11-18 for the NixLine/Rubik's renders)."""

    def setUp(self):
        import render_reel as rr
        self.rr = rr

    def test_still_contain_height_follows_the_image_aspect(self):
        f = self.rr.still_filter({}, 4.0, 1080, 1920)        # a 9:16 photo fills the frame
        self.assertIn("s=1080x1920", f)
        f = self.rr.still_filter({}, 4.0, 1080, 1350)        # a 4:5 photo is contained
        self.assertIn("s=1080x1350", f)

    def test_still_crop_is_applied_before_scaling(self):
        f = self.rr.still_filter({"crop": [0.5, 0.45, 0.78, 0.95]}, 4.0, 3324, 3324)
        self.assertIn("crop=iw*0.28", f)
        self.assertLess(f.index("crop=iw*0.28"), f.index("scale="))

    def test_cold_to_warm_grade_changes_over_time(self):
        f = self.rr.still_filter({"effect": "cold-to-warm"}, 3.0, 1080, 1920)
        self.assertIn("colortemperature", f)
        self.assertIn("enable=", f)

    def test_short_video_holds_its_last_frame(self):
        f = self.rr.video_filter({}, 3.0, clip_secs=1.0)
        self.assertIn("tpad=stop_mode=clone", f)
        f = self.rr.video_filter({}, 3.0, clip_secs=10.0)
        self.assertNotIn("tpad", f)


class HeadlineTests(unittest.TestCase):
    def test_long_hook_wraps_inside_the_safe_width(self):
        import render_reel as rr
        lines = rr.headline_lines("Your dark corner needs one line.", size=78)
        self.assertGreaterEqual(len(lines), 2)
        self.assertTrue(all(rr.text_width(l, 78) <= rr.W - 160 for l in lines))

    def test_two_sentence_hook_keeps_one_sentence_per_line(self):
        import render_reel as rr
        self.assertEqual(rr.headline_lines("Same bed. One bar of teak.", size=78), ["Same bed.", "One bar of teak."])
