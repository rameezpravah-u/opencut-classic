"""reelkit — small engine for building 9:16 reels with ffmpeg + Pillow.

Segments (video or still) get virtual camera moves (push-in, drift, pan) rendered with
zoompan on a 2x supersampled frame so the motion is sub-pixel smooth. Text cues are
rendered as transparent PNG layers and overlaid with fades and a soft rise-in.
"""
import os, subprocess, math, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 25
ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
if not os.path.isdir(ASSETS):
    ASSETS = os.path.join(os.path.dirname(ROOT), "assets")

def font(name, size):
    return ImageFont.truetype(os.path.join(ASSETS, name), size)

# --------------------------------------------------------------------------
# camera
# --------------------------------------------------------------------------
def ease_expr(n_frames):
    """smoothstep of on/N as an ffmpeg expression"""
    s = f"min(on/{n_frames},1)"
    return f"({s}*{s}*(3-2*{s}))"

def cam_filter(n_frames, z0=1.0, z1=1.12, px0=0.0, px1=0.0, py0=0.0, py1=0.0,
               punch=0.0, punch_frames=5, shake=0.0):
    """zoompan expression for a segment of n_frames output frames.
    z: zoom factor (1.0 = full frame). px/py: pan position in [-1,1] across the free range
    (-1 = left/top edge, 0 = centre, 1 = right/bottom). punch: extra zoom at the first frame
    that decays over punch_frames (beat hit). shake: handheld micro-motion amplitude in px."""
    e = ease_expr(n_frames)
    z = f"({z0}+({z1}-{z0})*{e})"
    if punch:
        z = f"({z}+{punch}*max(0,1-on/{punch_frames}))"
    px = f"({px0}+({px1}-{px0})*{e})"
    py = f"({py0}+({py1}-{py0})*{e})"
    sx = f"+{shake}*sin(on*0.9)*cos(on*0.37)" if shake else ""
    sy = f"+{shake}*cos(on*0.7)*sin(on*0.29)" if shake else ""
    x = f"(iw-iw/zoom)*(0.5+0.5*{px}){sx}"
    y = f"(ih-ih/zoom)*(0.5+0.5*{py}){sy}"
    return (f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}")

def video_chain(n_frames, cam=None, slow=1.0, speed=1.0, reverse=False, pre="", post=""):
    """filter chain for a video input -> n_frames at 25fps with camera move"""
    parts = []
    if pre:
        parts.append(pre)
    if reverse:
        parts.append("reverse")
    if slow and slow != 1.0:
        # motion-interpolated slow motion
        parts.append(f"minterpolate=fps={int(round(FPS*slow))}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
        parts.append(f"setpts={slow}*PTS")
    if speed and speed != 1.0:
        parts.append(f"setpts=PTS/{speed}")
    parts.append(f"fps={FPS}")
    parts.append(f"scale={W*2}:{H*2}:flags=lanczos")
    parts.append(cam_filter(n_frames, **(cam or {})))
    parts.append(f"trim=end_frame={n_frames},setpts=PTS-STARTPTS")
    if post:
        parts.append(post)
    parts.append(f"fps={FPS},format=yuv420p,settb=1/{FPS}")
    return ",".join(parts)

def still_chain(n_frames, cam=None, crop_cx=0.5, crop_cy=0.5, post=""):
    """filter chain for a still image -> 9:16 window then camera move.
    crop_cx/cy: where the 9:16 window sits on the source (0..1)."""
    # scale so the short side of the 9:16 window is 2160 wide, then crop
    parts = [f"scale='if(gte(iw/ih,{W/H}),-2,{W*2})':'if(gte(iw/ih,{W/H}),{H*2},-2)':flags=lanczos",
             f"crop={W*2}:{H*2}:'(iw-{W*2})*{crop_cx}':'(ih-{H*2})*{crop_cy}'",
             "setsar=1",
             cam_filter(n_frames, **(cam or {})),
             f"trim=end_frame={n_frames},setpts=PTS-STARTPTS"]
    if post:
        parts.append(post)
    parts.append(f"fps={FPS},format=yuv420p,settb=1/{FPS}")
    return ",".join(parts)

# --------------------------------------------------------------------------
# text layers
# --------------------------------------------------------------------------
def _draw_shadowed(img, shadow, xy, text, f, fill, shadow_alpha=200):
    ImageDraw.Draw(shadow).text(xy, text, font=f, fill=(0, 0, 0, shadow_alpha))
    ImageDraw.Draw(img).text(xy, text, font=f, fill=fill)

def text_layer(lines, y_center=1180, size=84, fontfile="Playfair_Display-600.ttf",
               color=(244, 234, 219), colors=None, align="center", x_left=90,
               line_gap=14, kicker=None, kicker_color=(227, 165, 82), kicker_font="DM_Sans-600.ttf",
               kicker_size=30, sub=None, sub_color=None, sub_size=40, sub_font="DM_Sans-500.ttf",
               shadow_blur=14, shadow_alpha=210, box=None, box_pad=(26, 14), box_radius=18,
               tracking=0, italic_shift=0, y_top=None):
    """Render text onto a transparent 1080x1920 layer.
    colors: dict word->rgb for per-word colouring. box: rgb(a) fill drawn behind each line
    (Gen-Z caption style). tracking: extra px between characters. y_top overrides y_center."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font(fontfile, size)
    d = ImageDraw.Draw(img)

    def width(txt, fnt):
        if tracking:
            return sum(fnt.getlength(c) for c in txt) + tracking * (len(txt) - 1)
        return fnt.getlength(txt)

    def draw_text(xy, txt, fnt, fill, target, sh=True):
        x, y = xy
        if tracking:
            for c in txt:
                if sh:
                    ImageDraw.Draw(shadow).text((x, y), c, font=fnt, fill=(0, 0, 0, shadow_alpha))
                ImageDraw.Draw(target).text((x, y), c, font=fnt, fill=fill)
                x += fnt.getlength(c) + tracking
        else:
            if sh:
                ImageDraw.Draw(shadow).text((x, y), txt, font=fnt, fill=(0, 0, 0, shadow_alpha))
            ImageDraw.Draw(target).text((x, y), txt, font=fnt, fill=fill)

    heights = []
    for ln in lines:
        bb = f.getbbox(ln or "x")
        heights.append(bb[3] - bb[1])
    total = sum(heights) + line_gap * (len(lines) - 1)
    y = y_top if y_top is not None else y_center - total / 2
    if kicker:
        kf = font(kicker_font, kicker_size)
        spaced = kicker
        kw = sum(kf.getlength(c) for c in spaced) + 6 * (len(spaced) - 1)
        kx = (W - kw) / 2 if align == "center" else x_left
        ky = y - kicker_size - 34
        cx = kx
        for c in spaced:
            ImageDraw.Draw(shadow).text((cx, ky), c, font=kf, fill=(0, 0, 0, shadow_alpha))
            d.text((cx, ky), c, font=kf, fill=kicker_color + (255,))
            cx += kf.getlength(c) + 6
    for i, ln in enumerate(lines):
        bb = f.getbbox(ln or "x")
        lw = width(ln, f)
        x = (W - lw) / 2 - bb[0] if align == "center" else x_left
        yy = y - bb[1]
        if box:
            pad_x, pad_y = box_pad
            bx0, by0 = x + bb[0] - pad_x, y - pad_y
            bx1, by1 = x + bb[0] + lw + pad_x, y + heights[i] + pad_y
            d.rounded_rectangle((bx0, by0, bx1, by1), radius=box_radius, fill=box)
        if isinstance(colors, dict):
            cx = x
            for wi, wd in enumerate(ln.split(" ")):
                piece = wd + (" " if wi < len(ln.split(" ")) - 1 else "")
                col = colors.get(wd.strip(".,?!:;·"), color)
                draw_text((cx, yy), piece, f, col + (255,), img, sh=not box)
                cx += width(piece, f)
        else:
            draw_text((x, yy), ln, f, color + (255,), img, sh=not box)
        y += heights[i] + line_gap
    if sub:
        sf = font(sub_font, sub_size)
        sw = sf.getlength(sub)
        sx = (W - sw) / 2 if align == "center" else x_left
        sy = y + 16
        ImageDraw.Draw(shadow).text((sx, sy), sub, font=sf, fill=(0, 0, 0, shadow_alpha))
        d.text((sx, sy), sub, font=sf, fill=(sub_color or color) + (235,))
    if shadow_blur:
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        a = shadow.split()[3].point(lambda v: min(255, int(v * 1.3)))
        shadow.putalpha(a)
        return Image.alpha_composite(shadow, img)
    return img

def rule_layer(y, x0=90, x1=990, color=(255, 255, 255), alpha=120, thickness=2):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle((x0, y, x1, y + thickness), fill=color + (alpha,))
    return img

def merge_layers(*layers):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for l in layers:
        out = Image.alpha_composite(out, l)
    return out

def logo_layer(width=300, cy=800):
    logo = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    logo = logo.resize((width, int(logo.height * width / logo.width)), Image.LANCZOS)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(logo, ((W - width) // 2, cy - logo.height // 2))
    return img

def solid_card(rgb, glow=None, glow_cy=800, glow_r=520, glow_alpha=70):
    img = Image.new("RGBA", (W, H), rgb + (255,))
    if glow:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        cx = W // 2
        for r in range(glow_r, 0, -20):
            a = int(glow_alpha * (1 - r / glow_r) ** 1.6)
            gd.ellipse((cx - r, glow_cy - r * 0.9, cx + r, glow_cy + r * 0.9), fill=glow + (a,))
        g = g.filter(ImageFilter.GaussianBlur(60))
        img = Image.alpha_composite(img, g)
    return img

# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------
class Reel:
    def __init__(self, name, out_dir, duration, grade=""):
        self.name = name
        self.out = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.duration = duration
        self.grade = grade
        self.segs = []      # dicts: kind, path, ss, dur, chain kwargs, xfade (transition into this seg)
        self.cues = []      # (name, start, end, layer, opts)
        self.audio = []     # (path, start, gain_db, fade_in, fade_out, is_music)
        self.n_cue = 0

    def video(self, path, ss, dur, xfade=None, **kw):
        self.segs.append(dict(kind="video", path=path, ss=ss, dur=dur, xfade=xfade, kw=kw))

    def still(self, path, dur, xfade=None, **kw):
        self.segs.append(dict(kind="still", path=path, ss=0, dur=dur, xfade=xfade, kw=kw))

    def card(self, image, dur, xfade=None, **kw):
        self.segs.append(dict(kind="still", path=image, ss=0, dur=dur, xfade=xfade, kw=kw))

    def cue(self, start, end, layer, fade_in=0.22, fade_out=0.22, rise=18, name=None):
        name = name or f"c{self.n_cue:02d}"
        self.n_cue += 1
        p = os.path.join(self.out, f"{self.name}-{name}.png")
        layer.save(p)
        self.cues.append((p, start, end, fade_in, fade_out, rise))

    def sound(self, path, start=0.0, gain_db=0.0, fade_in=0.0, fade_out=0.0, music=False, duck=None):
        self.audio.append(dict(path=path, start=start, gain=gain_db, fi=fade_in, fo=fade_out,
                               music=music, duck=duck))

    def timeline(self):
        """returns list of (seg, start, end) accounting for xfades"""
        t = 0.0
        out = []
        for s in self.segs:
            xf = s["xfade"]
            if xf and out:
                t -= xf[1]
            out.append((s, t, t + s["dur"]))
            t += s["dur"]
        return out

    def render(self, suffix="", with_music=True, crf=18):
        cmd = ["ffmpeg", "-hide_banner", "-y"]
        fc = []
        idx = 0
        labels = []
        for i, s in enumerate(self.segs):
            n = int(round(s["dur"] * FPS))
            kw = dict(s["kw"])
            post = kw.pop("post", "")
            grade = kw.pop("grade", self.grade)
            post = ",".join(p for p in [grade, post] if p)
            if s["kind"] == "video":
                slow = kw.get("slow", 1.0) or 1.0
                speed = kw.get("speed", 1.0) or 1.0
                src_dur = s["dur"] / slow * speed + 0.4
                cmd += ["-ss", f"{s['ss']:.3f}", "-t", f"{src_dur:.3f}", "-i", s["path"]]
                fc.append(f"[{idx}:v]{video_chain(n, post=post, **kw)}[s{i}]")
            else:
                cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{s['dur'] + 0.2:.3f}", "-i", s["path"]]
                fc.append(f"[{idx}:v]{still_chain(n, post=post, **kw)}[s{i}]")
            labels.append(f"s{i}")
            idx += 1
        # chain with cuts / xfades
        cur = labels[0]
        cur_len = self.segs[0]["dur"]
        for i in range(1, len(self.segs)):
            s = self.segs[i]
            if s["xfade"]:
                kind, d = s["xfade"]
                off = cur_len - d
                fc.append(f"[{cur}][{labels[i]}]xfade=transition={kind}:duration={d}:offset={off:.3f},fps={FPS},settb=1/{FPS}[x{i}]")
                cur = f"x{i}"
                cur_len = off + s["dur"]
            else:
                fc.append(f"[{cur}][{labels[i]}]concat=n=2:v=1:a=0,fps={FPS},settb=1/{FPS}[x{i}]")
                cur = f"x{i}"
                cur_len += s["dur"]
        fc.append(f"[{cur}]settb=1/{FPS},fps={FPS}[base]")
        cur = "base"
        for k, (p, s, e, fi, fo, rise) in enumerate(self.cues):
            # each cue input only lasts its own window (keeps ffmpeg's input queues small)
            cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{e - s + 0.2:.3f}", "-i", p]
            fc.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d={fi}:alpha=1,"
                      f"fade=t=out:st={e - s - fo:.3f}:d={fo}:alpha=1,setpts=PTS+{s:.3f}/TB[o{k}]")
            yexpr = f"{rise}*(1-min((t-{s:.3f})/{max(fi, 0.05):.3f},1))" if rise else "0"
            fc.append(f"[{cur}][o{k}]overlay=0:'{yexpr}':enable='between(t,{s:.3f},{e:.3f})':format=auto[v{k}]")
            cur = f"v{k}"
            idx += 1
        fc.append(f"[{cur}]format=yuv420p[vout]")
        # audio
        alabels = []
        for j, a in enumerate(self.audio):
            if a["music"] and not with_music:
                continue
            cmd += ["-i", a["path"]]
            chain = [f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"]
            if a["start"] < 0:   # negative start = skip into the file
                chain.append(f"atrim=start={-a['start']:.3f},asetpts=PTS-STARTPTS")
                st = 0.0
            else:
                delay = int(a["start"] * 1000)
                chain.append(f"adelay={delay}|{delay}")
                st = a["start"]
            if a["fi"]:
                chain.append(f"afade=t=in:st={st:.3f}:d={a['fi']}")
            if a["fo"]:
                chain.append(f"afade=t=out:st={self.duration - a['fo']:.3f}:d={a['fo']}")
            chain.append(f"volume={a['gain']}dB")
            if a.get("duck"):
                # simple duck: volume envelope (start,end,db) list
                env = "+".join(f"between(t,{d0},{d1})*{db}" for d0, d1, db in a["duck"])
                chain.append(f"volume='pow(10,({env})/20)':eval=frame")
            fc.append(f"[{idx}:a]{','.join(chain)}[a{j}]")
            alabels.append(f"a{j}")
            idx += 1
        if alabels:
            fc.append("".join(f"[{l}]" for l in alabels) +
                      f"amix=inputs={len(alabels)}:duration=longest:normalize=0,"
                      f"atrim=0:{self.duration:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        graph_path = os.path.join(self.out, f"{self.name}{suffix}.graph")
        with open(graph_path, "w") as fh:
            fh.write(";\n".join(fc))
        cmd += ["-filter_complex_script", graph_path, "-map", "[vout]"]
        if alabels:
            cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
        else:
            cmd += ["-an"]
        outp = os.path.join(self.out, f"{self.name}{suffix}.mp4")
        cmd += ["-r", str(FPS), "-t", f"{self.duration:.3f}",
                "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
                "-profile:v", "high", "-movflags", "+faststart", outp]
        log = os.path.join(self.out, f"{self.name}{suffix}.log")
        with open(log, "w") as fh:
            r = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT)
        if r.returncode != 0:
            print(open(log).read()[-3000:])
            raise SystemExit(f"ffmpeg failed for {outp}")
        return outp

def contact_sheet(video, out_png, fps=2, cols=8, rows=4, scale=200):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", video,
                    "-vf", f"fps={fps},scale={scale}:-1,tile={cols}x{rows}", "-frames:v", "1", out_png], check=True)

# ==========================================================================
# v2 additions: safe zones, placement, kinetic text, mechanisms
# ==========================================================================
import numpy as np

# Instagram/TikTok UI-safe area on a 1080x1920 canvas (2026 guidance):
# top ~220px (status/camera), bottom ~400px (caption/handle/audio), right ~130px (action rail)
SAFE = dict(top=230, bottom=1500, left=70, right=950)   # y-range 230..1500 is always visible

# named vertical slots (y_top of the text block)
SLOTS = dict(top=300, upper=560, centre=880, lower=1200, low=1330, bottom=1420)

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")

def _frame_at(path, t):
    """one frame (RGB numpy, 135x240) at time t; stills are centre-cropped to 9:16 like still_chain"""
    if path.lower().endswith(IMG_EXT):
        im = Image.open(path).convert("RGB")
        w, h = im.size
        if w / h > W / H:
            nw = int(h * W / H); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w * H / W); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        return np.asarray(im.resize((W // 8, H // 8), Image.BILINEAR))
    out = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", path,
                          "-frames:v", "1", "-vf", f"scale={W//8}:{H//8}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(out, dtype=np.uint8)
    if a.size < (W//8)*(H//8)*3:
        return None
    return a.reshape((H//8, W//8, 3))

def product_region(path, t, margin=40):
    """(y0, y1) in canvas px of the glowing product: rows holding the top-4% brightest pixels
    (max channel, so a red or green lamp counts), contiguous run around the densest row."""
    fr = _frame_at(path, t)
    if fr is None:
        return (800, 1300)
    lum = fr.astype(np.float32).max(axis=2)
    mask = lum >= np.percentile(lum, 96)
    rows = mask.sum(axis=1).astype(np.float32)
    thr = 0.2 * rows.max()
    peak = int(rows.argmax())
    lo = hi = peak
    while lo > 0 and rows[lo - 1] > thr:
        lo -= 1
    while hi < len(rows) - 1 and rows[hi + 1] > thr:
        hi += 1
    return (max(0, lo * 8 - margin), min(H, (hi + 1) * 8 + margin))

def auto_slot(path, t, block_h=260, prefer=("lower", "low", "upper", "centre", "top")):
    """pick the first named slot whose text block does not overlap the bright product band
    and stays inside the safe area."""
    y0, y1 = product_region(path, t)
    for name in prefer:
        y = SLOTS[name]
        if y < SAFE["top"] or y + block_h > SAFE["bottom"]:
            continue
        if y + block_h < y0 - 20 or y > y1 + 20:
            return y
    # nothing clears the product: take the first slot that at least stays inside the safe area
    for name in prefer:
        y = SLOTS[name]
        if y >= SAFE["top"] and y + block_h <= SAFE["bottom"]:
            return y
    return SLOTS["upper"]

def kinetic_cues(reel, words, start, per_word=0.14, hold=1.6, **style):
    """word-by-word pop: each word gets its own cue appearing per_word seconds after the last;
    all stay until start+len*per_word+hold. style -> text_layer kwargs (size, fontfile, color, box...)"""
    n = len(words)
    end = start + n * per_word + hold
    # build cumulative lines so words accumulate on one line
    acc = []
    for i, w in enumerate(words):
        acc.append(w)
        s = start + i * per_word
        e = start + (i + 1) * per_word if i < n - 1 else end
        reel.cue(s, e, text_layer([" ".join(acc)], **style), fade_in=0.05, fade_out=0.05, rise=6)

def letterbox_layer(bar=150, color=(0, 0, 0)):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, bar), fill=color + (255,))
    d.rectangle((0, H - bar, W, H), fill=color + (255,))
    return img

def progress_bar_cues(reel, duration, y=1495, h=6, color=(227, 165, 82), steps=40):
    """thin progress bar that fills over the reel (retention trick)"""
    for i in range(1, steps + 1):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(img).rectangle((SAFE["left"], y, SAFE["left"] + (SAFE["right"] - SAFE["left"]) * i / steps, y + h), fill=color + (230,))
        s = duration * (i - 1) / steps
        e = duration * i / steps + 0.02
        reel.cue(s, e, img, fade_in=0.0, fade_out=0.0, rise=0)

def counter_cues(reel, items, start, each, **style):
    """numbered listicle labels: items = [(number, text)]"""
    for i, (num, txt) in enumerate(items):
        s = start + i * each
        lay = M(text_layer([str(num)], y_top=style.get("num_y", 1150), size=style.get("num_size", 150),
                           fontfile=style.get("num_font", "Playfair_Display-700.ttf"), color=style.get("num_color", (227, 165, 82)),
                           align="left", x_left=90, shadow_blur=12),
                text_layer([txt], y_top=style.get("y", 1330), size=style.get("size", 60), fontfile=style.get("font", "DM_Sans-600.ttf"),
                           color=style.get("color", (244, 234, 219)), align="left", x_left=90, shadow_blur=12))
        reel.cue(s + 0.05, s + each - 0.05, lay)

M = merge_layers

# --- multi-frame compositions (rendered as their own pre-clips) ---------
def render_triptych(clips, out_path, dur, labels=None, gap=6, bg=(10, 8, 6), label_style=None):
    """three vertical strips side by side, each a (path, ss, kind[, crop_cx]) tuple. Produces an mp4 usable as a segment."""
    n = len(clips)
    sw = (W - gap * (n - 1)) // n
    cmd = ["ffmpeg", "-hide_banner", "-y"]
    fc = []
    for i, clip in enumerate(clips):
        p, ss, kind = clip[:3]
        cx = clip[3] if len(clip) > 3 else 0.5        # where the strip sits on the source (0 = left edge, 1 = right)
        if kind == "video":
            cmd += ["-ss", f"{ss:.3f}", "-t", f"{dur + 0.3:.3f}", "-i", p]
        else:
            cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur + 0.3:.3f}", "-i", p]
        # crop a vertical strip from each source, scaled to full height
        fc.append(f"[{i}:v]scale=-2:{H}:flags=lanczos,crop={sw}:{H}:(iw-{sw})*{cx}:0,fps={FPS},setsar=1,format=yuv420p[c{i}]")
    fc.append(f"color=c=0x{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}:s={W}x{H}:r={FPS}:d={dur:.3f}[bg]")
    cur = "bg"
    for i in range(n):
        x = i * (sw + gap)
        fc.append(f"[{cur}][c{i}]overlay={x}:0:shortest=1[o{i}]")
        cur = f"o{i}"
    fc.append(f"[{cur}]trim=duration={dur:.3f},setpts=PTS-STARTPTS[v]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-pix_fmt", "yuv420p", "-r", str(FPS), out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path

def render_before_after(before, after, out_path, dur, wipe_start=0.6, wipe_dur=1.2, kind_b="video", kind_a="video", ss_b=0, ss_a=0, vertical=False):
    """A wipe reveal: 'after' slides over 'before' with a thin light-coloured edge.
    Uses xfade wipe so both sources keep playing."""
    cmd = ["ffmpeg", "-hide_banner", "-y"]
    for p, kind, ss in ((before, kind_b, ss_b), (after, kind_a, ss_a)):
        if kind == "video":
            cmd += ["-ss", f"{ss:.3f}", "-t", f"{dur + 0.5:.3f}", "-i", p]
        else:
            cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur + 0.5:.3f}", "-i", p]
    prep = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p,settb=1/{FPS}"
    trans = "wipeup" if vertical else "wipeleft"
    fc = (f"[0:v]{prep}[a];[1:v]{prep}[b];"
          f"[a][b]xfade=transition={trans}:duration={wipe_dur}:offset={wipe_start},trim=duration={dur:.3f},setpts=PTS-STARTPTS[v]")
    cmd += ["-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-pix_fmt", "yuv420p", "-r", str(FPS), out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path

# transition presets usable as Reel.video(..., xfade=(kind, dur))
TRANS = dict(cut=None, dissolve=("dissolve", 0.35), fade=("fade", 0.4), flash=("fadewhite", 0.18),
             dip=("fadeblack", 0.3), zoom=("zoomin", 0.3), whip=("smoothleft", 0.22), whip_up=("smoothup", 0.22),
             circle=("circleopen", 0.4), slide=("slideleft", 0.25))
