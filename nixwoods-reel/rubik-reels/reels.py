"""Five Rubik's Cube Lamp reels. Run: python3 reels.py [1-5|all] [music|clean|both]"""
import sys, os, time
import reelkit as rk
from reelkit import text_layer as T, merge_layers as M, logo_layer, solid_card, rule_layer

V = "src/14-1.mp4"
IMG = lambda n: f"rubik/{n}"
OUT = "out/reels"
os.makedirs(OUT, exist_ok=True)

# source colour states in 14-1 (seconds)
GREEN, RED, AMBER, WARM, HAND = 0.0, 3.25, 5.65, 8.7, 13.0   # HAND: 13.0 amber -> 14.2 red -> 15.2 green -> 16.4 warm

def endcard(path, bg, glow, lines, sub, font="Playfair_Display-600.ttf", color=(244,234,219), sub_color=(227,165,82), logo_w=300):
    card = solid_card(bg, glow=glow, glow_cy=820)
    card = M(card, logo_layer(logo_w, 800),
             T(lines, y_top=1010, size=66, fontfile=font, color=color, shadow_blur=0),
             T([sub], y_top=1150, size=44, fontfile="DM_Sans-600.ttf", color=sub_color, shadow_blur=0))
    card.save(path); return path

# ---------------------------------------------------------------------------
def reel1():
    """AESTHETIC — slow, hypnotic, loopable. Music: dreamy lo-fi 68 bpm, hits every 1.766 s."""
    CREAM=(239,230,216); ROSE=(226,178,168)
    H=[0.0,2.59,4.36,6.13,7.89,9.65,13.18,14.95,16.71,18.48,20.23,22.0]
    r = rk.Reel("R1-aesthetic", OUT, 22.0,
                grade="eq=contrast=0.97:brightness=0.015:saturation=0.94,vignette=angle=PI/4.6:mode=forward,noise=alls=5:allf=t+u")
    d=lambda i: H[i+1]-H[i]
    r.video(V, AMBER, d(0), cam=dict(z0=1.0, z1=1.10))
    r.video(V, GREEN, d(1), cam=dict(z0=1.14, z1=1.14, px0=-0.25, px1=0.25))
    r.video(V, RED, d(2), cam=dict(z0=1.04, z1=1.18, py0=0.1, py1=-0.1))
    r.still(IMG("img05.jpg"), d(3), cam=dict(z0=1.12, z1=1.12, px0=-0.35, px1=0.35))
    r.still(IMG("img04.jpg"), d(4), cam=dict(z0=1.0, z1=1.15, py0=0.3, py1=-0.1))
    r.video(V, HAND, d(5), slow=1.42, cam=dict(z0=1.08, z1=1.12, px0=0.1, px1=-0.1))
    r.still(IMG("vibiz1.jpg"), d(6), xfade=("fade",0.4), cam=dict(z0=1.0, z1=1.12))
    r.still(IMG("vibiz2.jpg"), d(7), cam=dict(z0=1.12, z1=1.0))
    r.still(IMG("img08.jpg"), 2.79, cam=dict(z0=1.1, z1=1.1, px0=-0.3, px1=0.3), crop_cx=0.30)
    r.video(V, AMBER, 3.3, xfade=("fade",0.4), cam=dict(z0=1.10, z1=1.0))   # 19.1-22.0: amber, loops back to the opening frame
    cap=lambda s: T([s], y_top=1600, size=60, fontfile="Cormorant_Garamond-500-i.ttf", color=CREAM, align="left", x_left=96, tracking=2, shadow_blur=10)
    r.cue(0.9, 2.45, cap("9:40 pm"), rise=10)
    r.cue(2.8, 4.25, cap("10:15 pm"), rise=10)
    r.cue(4.6, 6.0, cap("11:58 pm"), rise=10)
    r.cue(9.9, 13.0, T(["the lamp that knows", "what time it is."], y_top=1490, size=62, fontfile="Cormorant_Garamond-500-i.ttf", color=CREAM, align="left", x_left=96, tracking=1, line_gap=6, shadow_blur=10), rise=12)
    r.cue(19.4, 21.8, M(T(["rubik's cube lamp"], y_top=1530, size=60, fontfile="Cormorant_Garamond-500-i.ttf", color=CREAM, align="left", x_left=96, tracking=2, shadow_blur=10),
                        T(["nixwoods.com"], y_top=1608, size=34, fontfile="DM_Sans-500.ttf", color=ROSE, align="left", x_left=98, tracking=3, shadow_blur=10)), rise=10)
    r.sound("audio/music1-aesthetic.mp3", 0, -2, 0.4, 1.8, music=True)
    r.sound("audio/sfx-turn.mp3", 9.65, -10)
    return r

# ---------------------------------------------------------------------------
def reel2():
    """USE & MEANING — voice-over led. Music: felt piano, ducked under the VO."""
    IV=(244,234,219); AM=(227,165,82)
    r = rk.Reel("R2-meaning", OUT, 24.0, grade="eq=contrast=1.04:saturation=1.05,vignette=angle=PI/5:mode=forward")
    r.video(V, WARM, 2.6, cam=dict(z0=1.0, z1=1.12))
    r.video(V, HAND-0.1, 1.8, cam=dict(z0=1.08, z1=1.08, px0=0.15, px1=-0.05))
    r.still(IMG("img05.jpg"), 2.5, cam=dict(z0=1.1, z1=1.1, px0=-0.3, px1=0.3))
    r.video(V, GREEN+0.2, 2.0, cam=dict(z0=1.0, z1=1.12))
    r.still(IMG("img04.jpg"), 1.7, cam=dict(z0=1.15, z1=1.05))
    r.video(V, HAND, 2.3, slow=1.2, cam=dict(z0=1.06, z1=1.12))
    r.still(IMG("img03.jpg"), 2.1, cam=dict(z0=1.0, z1=1.14, py0=0.2, py1=-0.1))
    r.still(IMG("img02.jpg"), 2.4, xfade=("fade",0.4), cam=dict(z0=1.12, z1=1.0))
    r.still(IMG("vibiz3.jpg"), 2.6, cam=dict(z0=1.0, z1=1.1))
    r.still(IMG("vibiz1.jpg"), 2.4, cam=dict(z0=1.0, z1=1.12))
    r.card(endcard(f"{OUT}/R2-end.png", (20,17,14), AM, ["Rubik's Cube Lamp"], "₹2,999  ·  nixwoods.com"), 2.4, xfade=("fade",0.5))
    o=0.6  # VO starts here
    c=lambda s,e,lines,**k: r.cue(s+o, e+o, T(lines, y_center=k.pop("y",1530), size=k.pop("size",68), color=IV, **k))
    c(0.0, 1.55, ["Most lamps give you", "one light."])
    c(2.0, 3.6, ["This one gives you three."])
    c(3.8, 6.4, ["Amber.", "The workday winds down."], colors={"Amber":(242,180,78)})
    c(6.6, 8.5, ["Green.", "A slow evening."], colors={"Green":(90,205,140)})
    c(8.6, 10.2, ["Red.", "Movie night."], colors={"Red":(232,90,80)})
    c(10.3, 12.4, ["No app. No remote.", "You just turn the block."], size=62)
    c(12.5, 14.2, ["Solid sheesham."], y=1560)
    c(14.2, 15.8, ["Hand-painted glass."], y=1560)
    c(15.85, 17.3, ["Made in India."], y=1560)
    c(17.35, 21.3, ["One lamp, for every", "version of your evening."], size=64)
    r.sound("audio/vo-meaning.mp3", o, 0)
    r.sound("audio/music2-meaning.mp3", 0, -13, 0.5, 2.0, music=True)
    r.sound("audio/sfx-turn.mp3", 2.6+o, -12)
    return r

# ---------------------------------------------------------------------------
def reel3():
    """DESIGN — monochrome grid, spec callouts, amber accent. Music: minimal electronic 100 bpm."""
    WH=(245,245,242); AC=(232,162,74); GR=(200,200,196)
    r = rk.Reel("R3-design", OUT, 22.0, grade="eq=contrast=1.12:saturation=0.96")
    G=[0,2.4,4.8,7.2,9.6,13.2,15.6,18.0,20.4,22.0]; d=lambda i: G[i+1]-G[i]
    r.still(IMG("img10.webp"), d(0), cam=dict(z0=1.0, z1=1.12))
    r.still(IMG("img03.jpg"), d(1), cam=dict(z0=1.1, z1=1.1, px0=-0.3, px1=0.3, py0=0.1, py1=-0.1))
    r.video(V, GREEN+0.3, d(2), cam=dict(z0=1.18, z1=1.22, px0=-0.1, px1=0.1))
    r.still(IMG("vibiz3.jpg"), d(3), cam=dict(z0=1.0, z1=1.12, py0=0.2, py1=-0.2))
    r.video(V, HAND, d(4), slow=1.5, cam=dict(z0=1.08, z1=1.12))
    r.video(V, WARM, d(5), cam=dict(z0=1.0, z1=1.14))
    r.still(IMG("img02.jpg"), d(6), cam=dict(z0=1.0, z1=1.06, py0=-0.3, py1=0.1))
    r.still(IMG("img04.jpg"), d(7), cam=dict(z0=1.12, z1=1.0))
    card = solid_card((12,12,12))
    card = M(card, logo_layer(260, 760),
             T(["Rubik's Cube Lamp"], y_top=930, size=62, fontfile="Space_Grotesk-700.ttf", color=WH, shadow_blur=0),
             T(["₹2,999   ·   nixwoods.com"], y_top=1030, size=36, fontfile="Inter-400.ttf", color=AC, shadow_blur=0),
             rule_layer(1120, 440, 640, AC, 255, 2))
    card.save(f"{OUT}/R3-end.png"); r.card(f"{OUT}/R3-end.png", d(8), xfade=("fade",0.4))
    def spec(s, e, kicker, lines, y=1400, size=68):
        lay = M(rule_layer(y-78, 96, 96+64, AC, 255, 3),
                T(lines, y_top=y, size=size, fontfile="Space_Grotesk-700.ttf", color=WH, align="left", x_left=96, line_gap=8,
                  kicker=kicker, kicker_color=AC, kicker_font="Space_Grotesk-500.ttf", kicker_size=30, shadow_blur=14))
        r.cue(s, e, lay, rise=14)
    spec(0.25, 2.3, "DESIGN NOTES  ·  01", ["Modern rooms don't", "need more things."])
    spec(2.55, 4.7, "DESIGN NOTES  ·  02", ["They need", "better ones."])
    spec(4.95, 7.1, "GLASS", ["8 × 8 in.", "Hand-painted."], size=64)
    spec(7.35, 9.5, "BASE", ["Solid sheesham.", "9 × 4.5 in."], size=64)
    spec(9.75, 13.1, "MECHANISM", ["Three painted faces.", "Turn the block.", "That's the switch."], size=60)
    spec(13.35, 15.5, "INTERFACE", ["No buttons. No remote.", "Nothing to charge."], size=58)
    spec(15.75, 17.9, "AT REST", ["Off, it's a sculpture."], size=64)
    spec(18.15, 20.3, "LIFESPAN", ["25,000-hour LED.", "3-year wood warranty."], size=58)
    r.sound("audio/music3-design.mp3", -8.0, -3, 0.3, 1.5, music=True)
    for t in (4.8, 9.6, 15.6): r.sound("audio/sfx-whoosh.mp3", t-0.25, -14)
    r.sound("audio/sfx-turn.mp3", 9.6, -10)
    return r

# ---------------------------------------------------------------------------
def reel4():
    """GEN-Z — fast, lowercase, neon caption boxes, beat punches. Music: phonk 140 bpm, 4-beat grid = 1.714 s."""
    NG=(61,255,143); NR=(255,59,92); NA=(255,197,66); NL=(199,125,255); BK=(10,10,10); WH=(242,242,242)
    r = rk.Reel("R4-genz", OUT, 16.0, grade="eq=contrast=1.08:saturation=1.28")
    b=1.7143; G=[i*b for i in range(9)]+[16.0]; d=lambda i: G[i+1]-G[i]
    r.video(V, GREEN, d(0), cam=dict(z0=1.14, z1=1.16, punch=0.10, shake=3))
    r.video(V, HAND, d(1), speed=1.4, cam=dict(z0=1.08, z1=1.12, punch=0.08, shake=3))
    r.video(V, RED+0.1, d(2), cam=dict(z0=1.1, z1=1.2, punch=0.10, px0=0.2, px1=-0.2, shake=3))
    r.still(IMG("vibiz1.jpg"), d(3), cam=dict(z0=1.0, z1=1.14, punch=0.08))
    r.still(IMG("img05.jpg"), d(4), cam=dict(z0=1.15, z1=1.05, punch=0.08))
    r.video(V, HAND+1.2, d(5), speed=1.3, cam=dict(z0=1.1, z1=1.14, punch=0.10, shake=3))
    r.still(IMG("img03.jpg"), d(6), cam=dict(z0=1.0, z1=1.16, punch=0.08, py0=0.2, py1=-0.2))
    r.still(IMG("vibiz2.jpg"), d(7), cam=dict(z0=1.12, z1=1.0, punch=0.08))
    r.still(IMG("img08.jpg"), d(8), cam=dict(z0=1.05, z1=1.15, punch=0.08, px0=-0.3, px1=0.2), crop_cx=0.35)
    box=lambda lines,fill,color=BK,y=1400,size=76,font="Archivo_Black-400.ttf": T(lines, y_top=y, size=size, fontfile=font, color=color, box=fill+(255,), box_pad=(30,12), box_radius=16, line_gap=26, shadow_blur=0)
    r.cue(G[0]+0.05, G[1]-0.05, box(["pov: your room", "at 2am"], NG), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[1]+0.05, G[2]-0.05, box(["it changes", "colour btw"], NL), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[2]+0.05, G[3]-0.05, box(["red =", "movie night"], NR, WH), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[3]+0.05, G[4]-0.05, box(["green =", "locked in"], NG), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[4]+0.05, G[5]-0.05, box(["amber =", "golden hour.", "indoors."], NA, y=1300), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[5]+0.05, G[6]-0.05, box(["no app.", "no remote.", "you just turn it."], WH, y=1300, size=66), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[6]+0.05, G[7]-0.05, M(box(["it's real wood btw"], WH, size=64), box(["(not the plastic kind)"], BK, WH, y=1520, size=40)), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[7]+0.05, G[8]-0.05, box(["₹2,999.", "yes really."], NA, size=84, font="Space_Grotesk-700.ttf"), fade_in=0.08, fade_out=0.08, rise=0)
    r.cue(G[8]+0.05, 15.9, M(box(["nixwoods.com"], BK, WH, size=68), box(["link in bio"], NG, y=1530, size=44)), fade_in=0.08, fade_out=0.2, rise=0)
    r.sound("audio/music4-genz.mp3", -26.6, -2, 0.0, 0.8, music=True)
    for t in (G[1], G[5]): r.sound("audio/sfx-turn.mp3", t, -8)
    for t in (G[2], G[4], G[7]): r.sound("audio/sfx-whoosh.mp3", t-0.25, -12)
    return r

# ---------------------------------------------------------------------------
def reel5():
    """30–40 — warm, premium, trust-led. Music: indie-folk 95 bpm, 4-beat grid = 2.528 s."""
    IV=(244,234,219); GOLD=(217,160,91); PLUM=(94,40,58)
    r = rk.Reel("R5-3040", OUT, 22.0, grade="eq=contrast=1.05:saturation=1.06,vignette=angle=PI/5:mode=forward")
    b=2.5263; G=[i*b for i in range(8)]+[22.0]; d=lambda i: G[i+1]-G[i]
    r.still(IMG("img01.webp"), d(0), cam=dict(z0=1.0, z1=1.1))
    r.video(V, HAND, d(1), slow=1.2, cam=dict(z0=1.06, z1=1.12, px0=0.1, px1=-0.1))
    r.video(V, RED+0.1, d(2), cam=dict(z0=1.1, z1=1.16, px0=-0.2, px1=0.2))
    r.still(IMG("img03.jpg"), d(3), cam=dict(z0=1.0, z1=1.16, py0=0.25, py1=-0.1))
    r.video(V, WARM, d(4), cam=dict(z0=1.0, z1=1.12))
    r.still(IMG("img08.jpg"), d(5), cam=dict(z0=1.1, z1=1.1, px0=-0.3, px1=0.3), crop_cx=0.30)
    r.still(IMG("vibiz3.jpg"), d(6), cam=dict(z0=1.0, z1=1.12, py0=0.15, py1=-0.15))
    r.still(IMG("vibiz1.jpg"), 2.53, cam=dict(z0=1.12, z1=1.0))
    r.card(endcard(f"{OUT}/R5-end.png", (20,17,14), GOLD, ["Stop buying boring lights."], "nixwoods.com  ·  free shipping across India"), 22.0-G[7]-2.53+0.5, xfade=("fade",0.5))
    c=lambda s,e,lines,**k: r.cue(s, e, T(lines, y_center=k.pop("y",1520), size=k.pop("size",72), color=IV, kicker_color=GOLD, **k))
    c(0.3, G[1]-0.1, ["Everyone asks about it."], kicker="THE RUBIK'S CUBE LAMP")
    c(G[1]+0.15, G[2]-0.1, ["Nobody guesses the price."])
    c(G[2]+0.15, G[3]-0.1, ["Three moods. One turn."], sub="amber  ·  green  ·  red", sub_size=38, sub_color=GOLD)
    c(G[3]+0.15, G[4]-0.1, ["Solid sheesham.", "Hand-painted glass."], size=66)
    c(G[4]+0.15, G[5]-0.1, ["No bulbs to change.", "Nothing to charge."], size=66)
    c(G[5]+0.15, G[6]-0.1, ["Made by hand", "in Khatauli."], size=70)
    price = M(T(["₹2,999"], y_top=1330, size=150, fontfile="Playfair_Display-700.ttf", color=IV, box=PLUM+(240,), box_pad=(46,20), box_radius=26, shadow_blur=0),
              T(["Free shipping  ·  3-year wood warranty  ·  COD"], y_top=1560, size=38, fontfile="DM_Sans-500.ttf", color=IV, shadow_blur=10))
    r.cue(G[6]+0.15, G[7]-0.1, price)
    c(G[7]+0.15, G[7]+2.1, ["Delivered in about a week.", "Anywhere in India."], size=62)
    r.sound("audio/music5-3040.mp3", 0, -2, 0.3, 1.8, music=True)
    r.sound("audio/sfx-turn.mp3", G[1], -10)
    return r

REELS = {1: reel1, 2: reel2, 3: reel3, 4: reel4, 5: reel5}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    mode = sys.argv[2] if len(sys.argv) > 2 else "both"
    ids = list(REELS) if which == "all" else [int(x) for x in which.split(",")]
    for i in ids:
        t = time.time()
        r = REELS[i]()
        if mode in ("music", "both"):
            p = r.render("-music", with_music=True); print("done", p, "%.0fs" % (time.time() - t), flush=True)
            rk.contact_sheet(p, f"sheets/{r.name}.png", fps=2, cols=8, rows=6, scale=200)
        if mode in ("clean", "both"):
            r2 = REELS[i](); p = r2.render("-clean", with_music=False); print("done", p, flush=True)
