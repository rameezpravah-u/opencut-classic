"""mechanisms.py — the twelve reel mechanisms from PLAYBOOK §6.

Each mechanism is a function that takes a *resolved* brief (product + style presets merged in)
and returns a reelkit.Reel ready to render. Use build():

    from mechanisms import build
    reel = build(brief_dict, root="dir with src/ audio/ hf/", out="out/system")
    reel.render("-music")

Every mechanism follows the same grammar: shots get a virtual camera move (2x supersampled
zoompan), text is auto-placed off the product with reelkit.auto_slot, the hook is on screen by
0.3 s, colour words take the lamp's real colour, and the price gets its own screen.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rubik-reels"))
import reelkit as rk
from reelkit import text_layer as T, merge_layers as M, logo_layer, solid_card, rule_layer, TRANS, SLOTS, SAFE

PRESETS = json.load(open(os.path.join(HERE, "presets.json"), encoding="utf-8"))
CAM = PRESETS["camera"]
COL = {k: tuple(v) for k, v in PRESETS["colors"].items()}
MECHANISMS = {}


def mechanism(name, funnel, note):
    def deco(fn):
        fn.mech = dict(name=name, funnel=funnel, note=note)
        MECHANISMS[name] = fn
        return fn
    return deco


def cam(name, **over):
    d = dict(CAM[name]); d.update(over); return d


def _wrap(text, maxc=20):
    """greedy wrap to max characters per line (headline sizes: ~18 chars at 66 px, ~22 at 54 px)"""
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > maxc:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# style: fonts / palette / case for one audience (presets.json → styles)
# --------------------------------------------------------------------------
class Style:
    def __init__(self, d):
        self.d = d
        self.pal = {k: tuple(v) for k, v in d["palette"].items()}

    def _case(self, lines):
        c = self.d.get("case", "as-is")
        return [l.lower() if c == "lower" else l.upper() if c == "upper" else l for l in lines]

    def headline(self, lines, y_top, size=None, color=None, colors=None, **kw):
        d = self.d
        lines = [lines] if isinstance(lines, str) else lines
        args = dict(y_top=y_top, size=size or d["headline_size"], fontfile=d["headline_font"],
                    color=color or self.pal["text"], align=d.get("align", "center"), x_left=d.get("x_left", 90),
                    tracking=d.get("tracking", 0), shadow_blur=d.get("shadow_blur", 12), line_gap=d.get("line_gap", 10))
        if d.get("box"):
            args["box"] = tuple(d["box"]); args["box_pad"] = (28, 16)
        if colors:
            args["colors"] = {k: tuple(v) for k, v in colors.items()}
        args.update(kw)
        return T(self._case(lines), **args)

    def support(self, lines, y_top, size=None, color=None, **kw):
        d = self.d
        lines = [lines] if isinstance(lines, str) else lines
        args = dict(y_top=y_top, size=size or d["support_size"], fontfile=d["support_font"], color=color or self.pal["accent"],
                    align=d.get("align", "center"), x_left=d.get("x_left", 90), tracking=d.get("support_tracking", 1), shadow_blur=10)
        args.update(kw)
        return T(lines, **args)

    def kicker(self, text, y_top, **kw):
        args = dict(y_top=y_top, size=self.d.get("kicker_size", 30), fontfile=self.d.get("kicker_font", "DM_Sans-600.ttf"),
                    color=self.pal["accent"], tracking=6, align=self.d.get("align", "center"), x_left=self.d.get("x_left", 90), shadow_blur=10)
        args.update(kw)
        return T([text.upper()], **args)

    def price(self, text, y_top, size=None, **kw):
        """Archivo Black has no ₹ glyph, so styles name a price_font"""
        args = dict(y_top=y_top, size=size or self.d["headline_size"], fontfile=self.d.get("price_font", self.d["headline_font"]),
                    color=self.pal.get("price", self.pal["text"]), align="center", shadow_blur=8)
        if self.d.get("price_box"):
            args["box"] = tuple(self.d["price_box"]); args["box_pad"] = (34, 18)
        args.update(kw)
        return T([text], **args)

    def endcard(self, path, lines, sub):
        card = solid_card(self.pal["card"], glow=self.pal["accent"], glow_cy=820)
        lines = [w for l in lines for w in _wrap(l, 24)]
        size = min(self.d["headline_size"], 66)
        card = M(card, logo_layer(300, 800),
                 T(self._case(lines), y_top=1010, size=size, fontfile=self.d["headline_font"],
                   color=self.pal.get("on_card", self.pal["text"]), shadow_blur=0, align="center", line_gap=8),
                 T(_wrap(sub, 40), y_top=1010 + len(lines) * int(size * 1.25) + 50, size=40, fontfile=self.d["support_font"],
                   color=self.pal["accent"], shadow_blur=0, align="center"))
        card.save(path)
        return path


# --------------------------------------------------------------------------
# Build: a running timeline of shots, cues and sounds → reelkit.Reel
# --------------------------------------------------------------------------
class Build:
    VIDEO_ONLY = ("slow", "speed", "reverse")

    def __init__(self, b):
        self.b = b; self.st = b["_style"]; self.sd = b["_style"].d
        self.out = b["_out"]; self.name = b["name"]
        self.shots, self.cues, self.sounds, self.t = [], [], [], 0.0

    # --- assets -------------------------------------------------------
    def path(self, rel):
        return rel if os.path.isabs(rel) else os.path.join(self.b["_root"], rel)

    def has(self, kind, key):
        p = self.b["assets"].get(kind, {}).get(key)
        return bool(p) and os.path.exists(self.path(p))

    def cam(self, name, **over):
        d = cam(name, **over)
        if self.sd.get("punch") and "punch" not in over: d["punch"] = self.sd["punch"]
        if self.sd.get("shake") and "shake" not in over: d["shake"] = self.sd["shake"]
        return d

    def _add(self, kind, path, ss, dur, xfade, kw, key=None):
        dur = round(dur * float(self.b.get("stretch", 1.0)), 3)     # brief.stretch: 1.5 turns an 18 s cut into a 27 s ad cut
        xfade = xfade if self.shots else None
        start = self.t - (xfade[1] if xfade else 0.0)
        sh = dict(kind=kind, path=path, ss=ss, dur=dur, xfade=xfade, kw=kw, start=start, end=start + dur, key=key)
        self.shots.append(sh); self.t = sh["end"]
        return sh

    #: colour state -> still key, for products that have photography but no product video
    STATE_STILL = {"amber": "hero", "warm": "room", "green": "desk_green", "red": "bedside_red", "hand": "hands"}

    def state(self, key, dur, xfade=None, offset=0.0, **kw):
        """a colour state of the real product video (presets → products.states).
        Products with no video resolve to the equivalent still, so every mechanism runs on
        a photography-only product without being rewritten."""
        prod = self.b["_product"]
        if not self.b["assets"].get("video") or not prod.get("states"):
            for k in self.VIDEO_ONLY: kw.pop(k, None)
            return self.still(self.STATE_STILL.get(key, "hero"), dur, xfade, **kw)
        ss = prod["states"][key] + offset
        dur = min(dur, (prod["state_max"][key] - offset) / float(self.b.get("stretch", 1.0)))
        return self._add("video", self.path(self.b["assets"]["video"]), ss, dur, xfade, kw, key="_video")

    def rejected(self, kind, key):
        st = self.b["assets"].get("status" if kind == "stills" else "clip_status", {}).get(key, "")
        return str(st).lower().startswith("rejected")

    def still(self, key, dur, xfade=None, **kw):
        for k in self.VIDEO_ONLY: kw.pop(k, None)
        a = self.b["assets"]
        kw.setdefault("fit", a.get("fit", {}).get(key, "cover"))          # contain keeps a wide fixture whole
        for ck, cv in a.get("crops", {}).get(key, {}).items():
            kw.setdefault(ck, cv)
        if self.rejected("stills", key):
            # fidelity gate: fall back to the real product footage (the hand-turn state)
            return self.state("hand", dur, xfade, slow=1.2, cam=kw.get("cam") or self.cam("hold"))
        return self._add("still", self.path(self.b["assets"]["stills"][key]), 0, dur, xfade, kw, key=key)

    def clip(self, key, dur, xfade=None, fallback=None, **kw):
        """Higgsfield/Kling image-to-video clip if present, else the still it was made from"""
        if self.has("clips", key) and not self.rejected("clips", key):
            kw.pop("crop_cx", None); kw.pop("crop_cy", None)
            cap = 4.6 / float(self.b.get("stretch", 1.0))
            return self._add("video", self.path(self.b["assets"]["clips"][key]), 0, min(dur, cap), xfade, kw, key=key)
        return self.still(fallback or key, dur, xfade, **kw)

    def pre(self, path, dur, xfade=None, **kw):
        """a pre-rendered composition (triptych, before/after) used as a segment"""
        return self._add("video", path, 0, dur, xfade, kw)

    def card(self, lines, sub, dur=2.4, xfade=("fade", 0.5)):
        p = os.path.join(self.out, f"{self.name}-end.png")
        self.st.endcard(p, lines, sub)
        return self._add("still", p, 0, dur, xfade, {})

    # --- text ---------------------------------------------------------
    def cue(self, a, b, layer, **o):
        self.cues.append((a, b, layer, o))

    def slot(self, sh, t_local=0.5, block_h=260, prefer=("lower", "low", "upper", "centre", "top")):
        """named slot from presets (assets.slots / assets.video_slot) when one is declared for this asset,
        else the first slot that does not cover the detected product band"""
        a = self.b["assets"]
        name = a.get("video_slot") if sh.get("key") == "_video" else a.get("slots", {}).get(sh.get("key") or "")
        if name and SLOTS[name] + block_h <= SAFE["bottom"]:
            return SLOTS[name]
        try:
            t = sh["ss"] + (t_local if sh["kind"] == "video" else 0.0)
            return rk.auto_slot(sh["path"], t, block_h, prefer)
        except Exception:
            return SLOTS["low"]

    def auto_box(self, sh, y, h=200, t_local=0.5):
        """dark translucent box behind the text when the frame is bright at that slot (daylight scenes);
        styles that already box their text (genz, ugc) are left alone"""
        if self.sd.get("box"):
            return None
        try:
            fr = rk._frame_at(sh["path"], sh["ss"] + (t_local if sh["kind"] == "video" else 0.0))
            if fr is None:
                return None
            band = fr[max(0, y // 8):max(1, (y + h) // 8)]
            if band.mean() > 108:
                return (10, 10, 10, 165)
        except Exception:
            pass
        return None

    def say(self, sh, lines, pad=0.2, y=None, block_h=None, fade=None, rise=None, prefer=None, **kw):
        """headline over one shot, auto-placed off the product, inside the shot's window"""
        lines = [lines] if isinstance(lines, str) else lines
        size = kw.get("size") or self.sd["headline_size"]
        bh = block_h or int(len(lines) * size * 1.25 + (90 if kw.get("kicker") else 40))
        if y is None:
            y = self.slot(sh, block_h=bh, prefer=prefer) if prefer else self.slot(sh, block_h=bh)
        if "box" not in kw:
            bx = self.auto_box(sh, y, bh)
            if bx:
                kw["box"] = bx; kw["box_pad"] = (24, 12)
        o = {}
        if fade is not None: o["fade_in"] = o["fade_out"] = fade
        if rise is not None: o["rise"] = rise
        self.cue(sh["start"] + pad, sh["end"] - pad, self.st.headline(lines, y_top=y, **kw), **o)
        return y

    # --- audio --------------------------------------------------------
    def sound(self, path, start=0.0, gain=0.0, fi=0.0, fo=0.0, music=False, duck=None):
        self.sounds.append(dict(path=self.path(path), start=start, gain=gain, fi=fi, fo=fo, music=music, duck=duck))

    def music(self, gain=-3, fi=0.3, fo=1.8, duck=None):
        m = self.b.get("music") or self.sd.get("music")
        if m and os.path.exists(self.path(m)):
            self.sound(m, self.b.get("music_offset", 0.0), self.b.get("music_gain", gain), fi, fo, music=True, duck=duck)

    def sfx(self, key, t, gain=-10):
        p = self.b["assets"].get("sfx", {}).get(key)
        if p and os.path.exists(self.path(p)) and self.b.get("sfx", True):
            self.sound(p, max(0.0, t), gain)

    # --- finish -------------------------------------------------------
    def reel(self):
        r = rk.Reel(self.name, self.out, round(self.t, 3), self.b.get("grade", self.sd.get("grade", "")))
        for sh in self.shots:
            if sh["kind"] == "video":
                r.video(sh["path"], sh["ss"], sh["dur"], xfade=sh["xfade"], **sh["kw"])
            else:
                r.still(sh["path"], sh["dur"], xfade=sh["xfade"], **sh["kw"])
        for a, b_, layer, o in self.cues:
            r.cue(a, min(b_, self.t - 0.05), layer, **o)
        for s in self.sounds:
            r.sound(s["path"], s["start"], s["gain"], s["fi"], s["fo"], music=s["music"], duck=s["duck"])
        r.shots = self.shots
        r.colours = self.colours()
        return r

    def colours(self):
        """colour states visible in this cut (for the 'at least two colours' rule)"""
        if not self.b["_product"].get("rules", {}).get("two_colours", True):
            return ["n/a"]
        seen = set()
        cc = self.b["assets"].get("clip_colours", {})
        for sh in self.shots:
            k = sh.get("key") or ""
            if k == "_video":
                st = self.b["_product"]["states"]
                name = max((n for n, t in st.items() if t <= sh["ss"] + 1e-6), key=lambda n: st[n], default="")
                seen.update({"hand": {"amber", "red", "green"}, "warm": {"amber"}}.get(name, {name}))
            elif sh["kind"] == "video" and k in cc:
                seen.update(cc[k])
            elif "red" in k: seen.add("red")
            elif "green" in k: seen.add("green")
            elif k and k not in ("hero_off", "room_before", "flatlay", "unbox") and sh["path"].lower().endswith((".jpg", ".png", ".mp4")) and "end.png" not in sh["path"]:
                seen.add("amber")
        return sorted(seen)


def _col(word_line, key, b=None):
    """Tint the first word of 'Red. Movie night.' with the lamp colour.

    Only for a product whose light actually changes colour. On a single-temperature
    fixture this would tint an arbitrary word — 'Not brighter. Warmer.' came out with
    'Not' in red — so it returns None and the line renders in the style's own colour."""
    if b is not None and not b["_product"].get("rules", {}).get("two_colours", True):
        return None
    return {word_line.split(".")[0].split()[0]: COL[key]}


# ==========================================================================
# the twelve mechanisms
# ==========================================================================
@mechanism("transformation", "top", "dark room → flash → lamp on → colour cycle")
def m_transformation(b):
    B = Build(b); c = b["copy"]; st = B.st
    off = B.still("hero_off", 2.2, cam=B.cam("push", z1=1.06), post="eq=brightness=-0.04") if B.has("stills", "hero_off") \
        else B.still("hero", 2.2, cam=B.cam("push", z1=1.06), post="eq=brightness=-0.35:saturation=0.3")
    on = B.clip("hero", 3.2, xfade=TRANS["flash"], cam=B.cam("push"))
    am = B.state("amber", 2.4, cam=B.cam("drift"))
    rd = B.still("bedside_red", 2.2, xfade=TRANS["dissolve"], cam=B.cam("push_hard"))
    gr = B.still("desk_green", 2.2, xfade=TRANS["dissolve"], cam=B.cam("tilt_up"))
    hd = B.clip("hands", 3.0, cam=B.cam("hold"))
    mc = B.still("macro", 2.0, cam=B.cam("pull"))
    B.card([c["name"]], f'{c["price"]}  ·  {c["url"]}')
    B.cue(0.25, off["end"] - 0.1, st.headline(_wrap(c.get("hook", "Still lit by one tubelight?"), 20), y_top=B.slot(off, block_h=200)))
    B.say(on, c.get("turn", "Watch the room change."), pad=0.3, kicker=c.get("kicker", "one turn · three colours"))
    for sh, key in ((am, "amber"), (rd, "red"), (gr, "green")):
        line = c["colors"][key]
        B.say(sh, _wrap(line, 22), colors=_col(line, key, b))
        B.sfx("turn", sh["start"], -10)
    B.say(hd, _wrap(c.get("mechanism", "No app. No remote. Just turn it."), 20))
    B.say(mc, _wrap(c.get("proof_line", "Solid sheesham. Hand-painted glass."), 22), size=50)
    B.sfx("whoosh", on["start"] - 0.25, -12)
    B.music()
    return B.reel()


@mechanism("colour_loop", "top", "seamless amber → green → red → amber loop; no CTA until the last second")
def m_colour_loop(b):
    B = Build(b); c = b["copy"]; st = B.st
    cut = b.get("cut", 2.6); xf = TRANS["dissolve"]
    a1 = B.state("amber", cut, cam=B.cam("push"))
    B.state("green", cut, xfade=xf, cam=B.cam("drift"))
    dg = B.still("desk_green", cut, xfade=xf, cam=B.cam("tilt_up"))
    B.state("red", cut, xfade=xf, cam=B.cam("push_hard"))
    br = B.still("bedside_red", cut, xfade=xf, cam=B.cam("drift_back"))
    hd = B.state("hand", cut + 0.6, xfade=xf, slow=1.3, cam=B.cam("hold"))
    B.clip("backlit", cut, xfade=xf, cam=B.cam("push"))
    a2 = B.state("amber", cut, xfade=xf, cam=B.cam("pull"))       # ends near the opening frame → loops
    for sh, s in zip((a1, dg, br), c.get("captions", ["9:40 pm", "10:15 pm", "11:58 pm"])):
        B.say(sh, s, size=60)
    B.say(hd, _wrap(c.get("line", "the lamp that knows what time it is."), 22), size=60)
    B.cue(a2["start"] + 0.4, a2["end"] - 0.2, M(st.headline([c["name"]], y_top=1355, size=58), st.support([c["url"]], y_top=1428, size=34)))
    B.sfx("turn", hd["start"] + 0.3)
    B.music(gain=-2, fo=1.2)
    return B.reel()


@mechanism("before_after", "mid", "cold overhead-lit room wipes to the lamp-lit room")
def m_before_after(b):
    B = Build(b); c = b["copy"]; st = B.st
    stills, clips = b["assets"]["stills"], b["assets"].get("clips", {})
    before = B.path(stills["room_before"]) if B.has("stills", "room_before") else B.path(stills["room"])
    before_kind = "still"
    if B.has("clips", "room"):
        after, after_kind = B.path(clips["room"]), "video"
    else:
        after, after_kind = B.path(stills["room"]), "still"
    pre = os.path.join(B.out, f"{B.name}-ba.mp4")
    rk.render_before_after(before, after, pre, dur=4.4, wipe_start=1.4, wipe_dur=1.3, kind_b=before_kind, kind_a=after_kind,
                           vertical=b.get("vertical_wipe", False))
    ba = B.pre(pre, 4.4, post=("" if B.has("stills", "room_before") else "eq=saturation=0.35:contrast=0.9:brightness=0.08"))
    hero = B.clip("hero", 2.8, cam=B.cam("push"))
    hd = B.clip("hands", 2.8, xfade=TRANS["dissolve"], cam=B.cam("hold"))
    rd = B.still("bedside_red", 2.0, cam=B.cam("push_hard"))
    gr = B.still("desk_green", 2.0, cam=B.cam("tilt_up"))
    B.card([c.get("cta_line", "Same room. One lamp.")], f'{c["name"]} · {c["price"]} · {c["url"]}')
    bx = B.auto_box(ba, SLOTS["top"], 400, t_local=0.3)
    B.cue(0.25, 1.55, st.headline(_wrap(c.get("hook", "Same room. One lamp."), 20), y_top=SLOTS["upper"], box=bx, box_pad=(24, 12)))
    B.cue(0.25, 1.35, st.kicker(c.get("before", "before · tubelight"), y_top=SLOTS["top"], box=bx, box_pad=(18, 8)))
    B.cue(2.75, ba["end"] - 0.15, st.kicker(c.get("after", "after · rubik's cube lamp"), y_top=SLOTS["top"]))
    B.say(hero, c.get("line1", "Not brighter. Warmer."))
    B.say(hd, _wrap(c.get("mechanism", "Turn the block. The colour changes."), 20))
    B.say(rd, _wrap(c["colors"]["red"], 22), colors=_col(c["colors"]["red"], "red", b))
    B.say(gr, _wrap(c["colors"]["green"], 22), colors=_col(c["colors"]["green"], "green", b))
    B.sfx("whoosh", 1.3, -12); B.sfx("turn", hd["start"] + 0.4)
    B.music()
    return B.reel()


@mechanism("triptych", "top/mid", "three colour states side by side, all moving")
def m_triptych(b):
    B = Build(b); c = b["copy"]; st = B.st
    stills = b["assets"]["stills"]
    pre = os.path.join(B.out, f"{B.name}-tri.mp4")
    vx = b["_product"].get("video_cx", 0.5)          # lamp is left of centre in the product clip
    if b["assets"].get("video") and b["_product"].get("states"):
        V = B.path(b["assets"]["video"]); S_ = b["_product"]["states"]
        panel1 = [(V, S_["red"], "video", vx), (V, S_["amber"], "video", vx), (V, S_["green"], "video", vx)]
    else:   # photography-only product: three rooms instead of three colour states
        panel1 = [(B.path(stills[k]), 0, "still", 0.5) for k in ("room", "hero", "backlit")]
    rk.render_triptych(panel1, pre, 2.4)
    tri = B.pre(pre, 2.4)
    hd = B.clip("hands", 3.0, xfade=TRANS["whip"], cam=B.cam("hold"))
    pre2 = os.path.join(B.out, f"{B.name}-tri2.mp4")
    rk.render_triptych([(B.path(stills["bedside_red"]), 0, "still", 0.6), (B.path(stills["hero"]), 0, "still", 0.45),
                        (B.path(stills["desk_green"]), 0, "still", 0.5)], pre2, 2.4)
    tri2 = B.pre(pre2, 2.4, xfade=TRANS["whip"])
    hero = B.clip("hero", 2.6, xfade=TRANS["whip"], cam=B.cam("push"))
    B.card([c.get("hook", "3 moods. 1 turn.")], f'{c["name"]} · {c["price"]} · {c["url"]}')
    sw = (1080 - 12) // 3
    lab_size = 44 if max(len(l) for l in (c.get("panels") or ["Red"])) <= 6 else 34
    two_col = b["_product"].get("rules", {}).get("two_colours", True)
    labels = c.get("panels") or (["Red", "Amber", "Green"] if two_col else ["Dining", "Living", "Bedroom"])
    cols = [COL["red"], COL["amber"], COL["green"]] if two_col else [st.pal["accent"]] * 3
    for i, (name, col) in enumerate(zip(labels, cols)):
        x = min(i * (sw + 6) + 96, SAFE["right"] - (170 if lab_size > 38 else 210))   # label stays clear of the action rail
        for sh in (tri, tri2):
            B.cue(sh["start"] + 0.15, sh["end"] - 0.1, T([name], y_top=SLOTS["top"], size=lab_size, fontfile=st.d["headline_font"],
                                                         color=col, align="left", x_left=x, shadow_blur=14, shadow_alpha=240))
    B.cue(0.25, tri["end"] - 0.1, st.headline(_wrap(c.get("hook", "3 moods. 1 turn."), 18), y_top=SLOTS["upper"]))
    B.say(hd, _wrap(c.get("mechanism", "No app. Just turn it."), 24))
    B.cue(tri2["start"] + 0.2, tri2["end"] - 0.1, st.headline([c.get("line2", "Bedside. Console. Desk.")], y_top=SLOTS["upper"]))
    B.say(hero, _wrap(c.get("line3", "One lamp. Three rooms' worth of mood."), 22))
    for sh in (hd, tri2, hero):
        B.sfx("whoosh", sh["start"] - 0.2, -12)
    B.music()
    return B.reel()


@mechanism("kinetic", "top", "word-by-word pop over a static hero; one claim")
def m_kinetic(b):
    B = Build(b); c = b["copy"]; st = B.st
    hero = B.clip("backlit", 3.4, cam=B.cam("push", z1=1.08))
    words = c.get("hook", "nobody guesses how the colour changes.").split()
    n, per = len(words), b.get("per_word", 0.16)
    y = B.slot(hero, block_h=320, prefer=("upper", "lower", "low", "centre"))
    acc = []
    for i, w in enumerate(words):
        acc.append(w)
        s = 0.3 + i * per
        e = 0.3 + (i + 1) * per if i < n - 1 else hero["end"] - 0.15
        B.cue(s, e, st.headline(_wrap(" ".join(acc), 18), y_top=y), fade_in=0.05, fade_out=0.05, rise=6)
    hd = B.state("hand", 2.4, xfade=TRANS["flash"], speed=1.3, cam=B.cam("hold"))
    rd = B.state("red", 1.7, cam=B.cam("push_hard"))
    gr = B.state("green", 1.7, cam=B.cam("drift"))
    dg = B.still("dutch_green", 1.7, cam=B.cam("pull"))
    B.say(hd, _wrap(c.get("mechanism", "there's no switch. you turn it."), 18), fade=0.06, rise=6)
    B.say(rd, "red.", size=84, fade=0.06, rise=6); B.say(gr, "green.", size=84, fade=0.06, rise=6)
    B.say(dg, _wrap(c.get("line3", "real glass. real wood."), 18), fade=0.06, rise=6)
    pr = B.still("mirror", 2.2, xfade=TRANS["dip"], cam=B.cam("push"))
    py = B.slot(pr, block_h=240)
    B.cue(pr["start"] + 0.2, pr["end"] - 0.1, M(st.price(c["price"], y_top=py, size=96),
                                                 st.support([c.get("cta", "link in bio")], y_top=py + 150)))
    B.card([c["name"]], c["url"], dur=2.0)
    B.sfx("whoosh", hd["start"] - 0.2, -10); B.sfx("turn", hd["start"] + 0.2)
    B.sfx("turn", rd["start"], -10); B.sfx("turn", gr["start"], -10)
    B.music(gain=-2, fi=0.0, fo=0.8)
    return B.reel()


@mechanism("listicle", "mid", "numbered '3 reasons', counter + caption")
def m_listicle(b):
    B = Build(b); c = b["copy"]; st = B.st; each = b.get("cut", 3.0)
    items = c.get("items", [["It's real glass and solid sheesham.", "macro"], ["Three colours. No app.", "hands"],
                            ["Three-year warranty on the wood.", "hero"]])
    hook = B.state("warm", 2.2, cam=B.cam("push"))
    B.cue(0.25, hook["end"] - 0.1, st.headline(_wrap(c.get("hook", "3 reasons this isn't plastic."), 20), y_top=B.slot(hook, block_h=200)))
    for i, (txt, key) in enumerate(items):
        sh = B.clip(key, each, xfade=TRANS["whip"], fallback=key, cam=B.cam(("push", "hold", "tilt_up")[i % 3]))
        y = B.slot(sh, block_h=270, prefer=("lower", "upper", "low"))
        bx = B.auto_box(sh, y, 270)
        lay = M(T([str(i + 1)], y_top=y, size=110, fontfile=st.d.get("price_font", st.d["headline_font"]),
                  color=st.pal["accent"], align="left", x_left=100, shadow_blur=12, box=bx, box_pad=(20, 6)),
                st.headline(_wrap(txt, 24), y_top=y + 122, size=48, align="left", x_left=100, box=bx, box_pad=(20, 8)))
        B.cue(sh["start"] + 0.2, sh["end"] - 0.2, lay)
        B.sfx("whoosh", sh["start"] - 0.2, -12)
    B.card([c.get("cta_line", "Turn the block.")], f'{c["name"]} · {c["price"]} · {c["url"]}')
    B.music()
    return B.reel()


@mechanism("spec_sheet", "mid", "design-notes callouts with rules; numbers only")
def m_spec_sheet(b):
    B = Build(b); c = b["copy"]; st = B.st; each = b.get("cut", 2.4)
    specs = c.get("specs", [["8 × 8 in", "candy glass · hand-painted faces", "flatlay"], ["Solid sheesham", "one-of-a-kind grain", "macro"],
                            ["2700–3000K", "warm LED · 25,000 h", "mirror"], ["3 faces", "red · green · amber — turn to change", "dutch_green"]])
    hero = B.still("hero", 2.2, cam=B.cam("push"))
    B.cue(0.25, hero["end"] - 0.1, st.headline(_wrap(c.get("hook", "A lamp, not a gadget."), 20), y_top=B.slot(hero, block_h=180)))
    for i, (big, small, key) in enumerate(specs):
        sh = B.still(key, each, xfade=TRANS["whip"] if i else TRANS["dissolve"], cam=B.cam(("drift", "push", "pull", "tilt_up")[i % 4]))
        y = B.slot(sh, block_h=220, prefer=("lower", "upper", "low", "top"))
        bx = B.auto_box(sh, y, 160)
        lay = M(rule_layer(y - 24, 100, 520, tuple(st.pal.get("rule", st.pal["accent"])), 160, 2),
                st.headline([big], y_top=y, size=64, align="left", x_left=100, box=bx, box_pad=(20, 10)),
                # the small line carries half a spec card's value: ivory, not the dim accent, and a
                # heavier shadow — gold at 36px vanished on warm wood in the Aurora sizing reel
                st.support([small], y_top=y + 92, size=38, align="left", x_left=102, box=bx, box_pad=(20, 8),
                           color=st.pal["text"], shadow_blur=16))
        B.cue(sh["start"] + 0.2, sh["end"] - 0.2, lay, rise=10)
        B.sfx("whoosh", sh["start"] - 0.2, -14)
    hd = B.clip("hands", 2.6, xfade=TRANS["whip"], cam=B.cam("hold"))
    B.say(hd, _wrap(c.get("mechanism", "Turn. That's the whole interface."), 22), size=54)
    # a spec reel is kept, not clicked — recap on the last frame when the brief gives a cta_line
    B.card(_wrap(c.get("cta_line") or c["name"], 22), f'{c["name"]} · {c["price"]} · {c["url"]}')
    B.sfx("turn", hd["start"] + 0.3)
    B.music(gain=-3, fi=0.3)
    return B.reel()


@mechanism("vo_story", "mid", "narrator reel; captions are the 3–6 word version of each VO line")
def m_vo_story(b):
    B = Build(b); c = b["copy"]; st = B.st
    vo, o, lines = b.get("vo"), b.get("vo_offset", 0.6), b.get("vo_lines")
    if not vo or not lines:
        raise SystemExit("vo_story needs brief.vo (mp3 path) and brief.vo_lines [[start, end, caption, colour|null], ...]")
    hero = B.clip("hero", 2.8, cam=B.cam("push"))
    hd = B.clip("hands", 2.0, cam=B.cam("hold"))
    B.state("amber", 2.6, cam=B.cam("drift"))
    B.still("desk_green", 2.2, cam=B.cam("tilt_up"))
    B.still("bedside_red", 1.8, cam=B.cam("push_hard"))
    B.state("hand", 2.4, slow=1.2, cam=B.cam("hold"))
    B.still("macro", 1.8, xfade=TRANS["dissolve"], cam=B.cam("pull"))
    B.still("flatlay", 1.8, cam=B.cam("drift"))
    B.clip("room", 2.4, xfade=TRANS["dissolve"], cam=B.cam("push"))
    B.card([c["name"]], f'{c["price"]}  ·  {c["url"]}', dur=2.6)
    size = b.get("caption_size", 62)
    for i, (s, e, cap, key) in enumerate(lines):
        cap = [cap] if isinstance(cap, str) else cap
        colors = _col(cap[0], key, b) if key else None
        start = min(s + o, 0.25) if i == 0 else s + o      # the first caption is the visual hook: on screen by 0.3 s
        # place each caption off the product of the shot that is on screen when it appears
        mid = (start + e + o) / 2
        sh = next((x for x in B.shots if x["start"] <= mid < x["end"]), B.shots[-1])
        bh = int(len(cap) * size * 1.25 + 40)
        y = b.get("caption_y") or B.slot(sh, block_h=bh)
        bx = B.auto_box(sh, y, bh)
        B.cue(start, e + o, st.headline(cap, y_top=y, size=size, colors=colors, box=bx, box_pad=(24, 12)))
    B.sound(vo, o, 0)
    B.music(gain=-13, fi=0.5, fo=2.0)
    B.sfx("turn", hd["start"] + 0.3, -12)
    return B.reel()


@mechanism("ugc_pov", "top", "handheld, lowercase caption boxes, 'pov:' hook")
def m_ugc_pov(b):
    B = Build(b); c = b["copy"]; st = B.st; cut = b.get("cut", 1.714)
    g1 = B.state("green", cut, cam=B.cam("hold", z0=1.14, z1=1.16))
    hd = B.state("hand", cut, speed=1.3, cam=B.cam("hold"))
    rd = B.state("red", cut, offset=0.1, cam=B.cam("push_hard", px0=0.2, px1=-0.2))
    bd = B.still("bedside_red", cut, cam=B.cam("push"))
    un = B.still("unbox", cut, cam=B.cam("pull"))
    hd2 = B.state("hand", cut, offset=1.2, speed=1.3, cam=B.cam("hold"))
    dk = B.still("desk_green", cut, cam=B.cam("tilt_up"))
    mr = B.still("mirror", cut, cam=B.cam("push"))
    caps = c.get("captions", ["pov: guests keep asking about the lamp", "it's glass. on real wood.", "you just turn it", "red = movie night",
                              "came like this. no assembly.", "green = slow evening", "no app. nothing to charge.", "₹2,999 · link in bio"])
    for sh, cap in zip((g1, hd, rd, bd, un, hd2, dk, mr), caps):
        if "₹" in cap:
            B.cue(sh["start"] + 0.1, sh["end"] - 0.05, st.price(cap, y_top=B.slot(sh, block_h=120), size=56), fade_in=0.05, fade_out=0.05, rise=6)
        else:
            B.say(sh, _wrap(cap, 24), pad=0.08, fade=0.05, rise=6)
    B.card([c.get("cta_line", "turn the block.")], f'{c["name"]} · {c["url"]}', dur=1.8, xfade=None)
    for sh in (hd, hd2): B.sfx("turn", sh["start"], -8)
    for sh in (rd, un, dk): B.sfx("whoosh", sh["start"] - 0.2, -12)
    B.music(gain=-2, fi=0.0, fo=0.8)
    return B.reel()


@mechanism("price_reveal", "bottom", "value stack → big price → COD / warranty")
def m_price_reveal(b):
    B = Build(b); c = b["copy"]; st = B.st; each = b.get("cut", 1.8)
    hook = B.clip("hero", 2.4, cam=B.cam("push"))
    B.cue(0.25, hook["end"] - 0.1, st.headline(_wrap(c.get("hook", "Everyone asks about it. Nobody guesses the price."), 22), y_top=B.slot(hook, block_h=260)))
    stack = c.get("stack", [["Real glass.", "macro"], ["Solid sheesham.", "flatlay"], ["Three colours. One turn.", "hands"], ["3-year wood warranty.", "mirror"]])
    ticks = []
    for i, (txt, key) in enumerate(stack):
        sh = B.clip(key, each, xfade=TRANS["slide"] if i else None, fallback=key, cam=B.cam(("push", "drift", "hold", "pull")[i % 4]))
        ticks.append(txt)
        y = B.slot(sh, block_h=200, prefer=("lower", "upper", "low"))
        bx = B.auto_box(sh, y, 200)
        B.cue(sh["start"] + 0.15, sh["end"] - 0.1, st.headline(ticks[-3:], y_top=y, size=50, align="left", x_left=100, box=bx, box_pad=(20, 8)), rise=8)
        B.sfx("whoosh", sh["start"] - 0.15, -14)
    pr = B.still("bedside_red", 2.6, xfade=TRANS["dip"], cam=B.cam("push_hard"))
    py = B.slot(pr, block_h=250)
    B.cue(pr["start"] + 0.25, pr["end"] - 0.1, M(st.price(c["price"], y_top=py, size=104),
                                                 st.support([f'was {c["compare"]}'], y_top=py + 150, size=40)))
    B.sfx("turn", pr["start"], -8)
    cod = B.still("unbox", 2.2, cam=B.cam("pull"))
    B.say(cod, _wrap(c.get("terms", "Free shipping across India. COD available."), 22), size=52)
    B.card([c.get("cta_line", "Turn the block.")], f'{c["name"]} · {c["price"]} · {c["url"]}')
    B.music()
    return B.reel()


@mechanism("unboxing", "bottom / festive", "kraft box, tissue, reveal, gift line")
def m_unboxing(b):
    B = Build(b); c = b["copy"]; st = B.st
    un = B.still("unbox", 3.0, cam=B.cam("push"))
    fl = B.still("flatlay", 2.2, xfade=TRANS["dissolve"], cam=B.cam("drift"))
    hd = B.clip("hands", 3.0, xfade=TRANS["dissolve"], cam=B.cam("hold"))
    on = B.clip("hero", 2.6, xfade=TRANS["flash"], cam=B.cam("push"))
    fest = B.clip("diwali", 3.0, xfade=TRANS["dissolve"], cam=B.cam("tilt_up"))
    rd = B.still("bedside_red", 2.0, cam=B.cam("push_hard"))
    B.card([c.get("gift_line", "The gift they'll actually remember.")], c.get("delivery", f'{c["price"]} · delivered in 5–7 days · {c["url"]}'), dur=2.6)
    B.cue(0.25, un["end"] - 0.1, st.headline(_wrap(c.get("hook", "The gift they'll actually remember."), 20), y_top=B.slot(un, block_h=260)))
    B.say(fl, _wrap(c.get("line1", "Real glass. Solid sheesham. No assembly."), 22), size=52)
    B.say(hd, _wrap(c.get("mechanism", "Turn it. The colour changes."), 20))
    B.say(on, c.get("line3", "Warm by default."))
    B.say(fest, _wrap(c.get("line4", "Made in India. Ready for Diwali."), 22))
    B.say(rd, _wrap(c["colors"]["red"], 22), colors=_col(c["colors"]["red"], "red", b))
    B.sfx("whoosh", on["start"] - 0.2, -12); B.sfx("turn", hd["start"] + 0.4)
    B.music()
    return B.reel()


@mechanism("testimonial", "bottom", "a real review over night footage — needs a real quote and name")
def m_testimonial(b):
    B = Build(b); c = b["copy"]; st = B.st
    q, who = c.get("quote"), c.get("who")
    if not q or not who:
        raise SystemExit("testimonial: brief.copy.quote and brief.copy.who are required — never invent a review")
    bd = B.still("bedside_red", 3.4, cam=B.cam("push"))
    hero = B.clip("hero", 3.2, xfade=TRANS["dissolve"], cam=B.cam("push"))
    hd = B.clip("hands", 2.6, xfade=TRANS["dissolve"], cam=B.cam("hold"))
    room = B.clip("room", 2.8, xfade=TRANS["dissolve"], cam=B.cam("push"))
    B.card([c["name"]], f'{c["price"]} · {c["url"]}')
    lines = _wrap("“" + q + "”", 24)
    y = SLOTS["upper"]
    B.cue(0.3, hero["end"] - 0.2, M(st.headline(lines, y_top=y, size=56, fontfile="Cormorant_Garamond-500-i.ttf"),
                                    st.support(["— " + who], y_top=y + 68 * len(lines) + 30, size=36)))
    B.say(hd, _wrap(c.get("mechanism", "Turn the block. Three colours."), 20))
    if c.get("proof_line"):
        B.say(room, c["proof_line"])
    B.music(gain=-4)
    return B.reel()


# ==========================================================================
# brief → reel
# ==========================================================================
def resolve(brief, root, out):
    prod = PRESETS["products"][brief.get("product", "rubik")]
    style = dict(PRESETS["styles"][brief.get("style", "broad")]); style.update(brief.get("style_overrides", {}))
    b = dict(brief)
    b["_product"], b["_style"], b["_root"], b["_out"] = prod, Style(style), root, out
    b["copy"] = {**prod["copy"], **brief.get("copy", {})}
    a = json.loads(json.dumps(prod["assets"]))
    for k, v in brief.get("assets", {}).items():
        if isinstance(v, dict):
            a.setdefault(k, {}).update(v)
        else:
            a[k] = v
    b["assets"] = a
    return b


def build(brief, root=".", out="out"):
    if brief.get("mechanism") not in MECHANISMS:
        raise SystemExit(f"unknown mechanism {brief.get('mechanism')!r}; choose from {sorted(MECHANISMS)}")
    os.makedirs(out, exist_ok=True)
    return MECHANISMS[brief["mechanism"]](resolve(brief, root, out))


if __name__ == "__main__":
    for k, fn in MECHANISMS.items():
        print(f"{k:14s} {fn.mech['funnel']:14s} {fn.mech['note']}")
