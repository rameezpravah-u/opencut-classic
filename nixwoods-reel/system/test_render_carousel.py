"""Tests for render_carousel.py. Run from nixwoods-reel/: python3 -m unittest system.test_render_carousel -v"""
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def make_carousel(src, status="APPROVED"):
    from PIL import Image
    Image.new("RGB", (1080, 1350), (120, 100, 80)).save(src / "REAL-026-wall.jpg")
    Image.new("RGB", (2000, 2000), (60, 60, 60)).save(src / "REAL-027-alt.jpg")
    return {
        "id": "NW-CREATIVE-CAROUSEL-20261118-test-x-v1", "type": "carousel", "status": status, "handle": "test",
        "slides": [
            {"headline": "Down only, or up and down?", "body": "", "image": "REAL-026"},
            {"headline": "Down only", "body": "A warm pool of light below. The wall above stays dark.", "image": "REAL-027", "crop": [0, 0, 1, 0.6]},
            {"headline": "Which wall is yours?", "body": "nixwoods.com", "image": "REAL-026"},
        ],
    }


class CarouselRenderTests(unittest.TestCase):
    def setUp(self):
        import render_carousel as rc
        self.rc = rc
        self.tmp = tempfile.TemporaryDirectory()
        self.d = pathlib.Path(self.tmp.name)
        (self.d / "src").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_renders_one_4x5_slide_and_one_9x16_story_per_slide(self):
        from PIL import Image
        c = make_carousel(self.d / "src")
        out = self.rc.render(c, self.d / "src", self.d / "out")
        slides = sorted((out).glob("slide-*.jpg"))
        stories = sorted((out).glob("story-*.jpg"))
        self.assertEqual(len(slides), 3)
        self.assertEqual(len(stories), 3)
        self.assertEqual(Image.open(slides[0]).size, (1080, 1350))
        self.assertEqual(Image.open(stories[0]).size, (1080, 1920))

    def test_only_an_approved_carousel_renders(self):
        c = make_carousel(self.d / "src", status="AWAITING-OWNER")
        with self.assertRaises(ValueError):
            self.rc.render(c, self.d / "src", self.d / "out")

    def test_preview_renders_an_unapproved_carousel_for_review(self):
        c = make_carousel(self.d / "src", status="AWAITING-OWNER")
        out = self.rc.render(c, self.d / "src", self.d / "out", preview=True)
        self.assertEqual(len(list(out.glob("slide-*.jpg"))), 3)
        self.assertTrue((out / "PREVIEW.txt").exists())

    def test_missing_image_is_named(self):
        c = make_carousel(self.d / "src")
        c["slides"][1]["image"] = "REAL-099"
        with self.assertRaises(FileNotFoundError) as e:
            self.rc.render(c, self.d / "src", self.d / "out")
        self.assertIn("REAL-099", str(e.exception))

    def test_text_stays_inside_the_safe_width(self):
        lines = self.rc.wrap("A warm pool of light below. The wall above stays dark.", 40, self.rc.F_BODY, 1080 - 2 * self.rc.MARGIN)
        self.assertTrue(all(self.rc.width(l, 40, self.rc.F_BODY) <= 1080 - 2 * self.rc.MARGIN for l in lines))
        self.assertGreater(len(lines), 1)


if __name__ == "__main__":
    unittest.main()
