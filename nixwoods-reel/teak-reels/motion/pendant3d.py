"""pendant3d - a small signed-distance ray marcher for the Double Arm Teak pendant.

Units are inches, from the PDP and teak-reels/ref/REFERENCE.md: a single 49 x 2 x 3 in bar of
solid teak with two parallel LED channels cut into the underside, hung on two black cables from a
teak canopy. Proportions not on the PDP (canopy length, fittings) are measured off the real
photographs in teak-reels/hf: the canopy is a long rectangular bar about 0.42x the main bar's
length; the bar's ends are softly rounded; the channels stop short of the ends.

The wood is not procedural: it is a strip cut from the canopy in sh05-canopy-cables.jpg.

Only what the product is, is modelled. No mounting bracket, screw or wiring is drawn - none is
documented anywhere, and inventing one would show customers hardware they will not receive.
"""
import math, os
import numpy as np
from numba import njit, prange
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- geometry (inches)
BAR_HL, BAR_HH, BAR_HD = 24.5, 1.5, 1.0        # 49 long, 3 high, 2 deep
CHAN_Z, CHAN_HW, CHAN_D, CHAN_HL = 0.46, 0.21, 0.13, 21.6
CAN_HL, CAN_HH, CAN_HD = 10.3, 0.5, 1.0        # ~0.42 x bar length (measured off sh00/sh01)
CABLE_R = 0.055
GRIP_R, GRIP_HH = 0.17, 0.36
CABLE_X = 9.5                                  # cables drop from near the canopy's ends
SUSP_R, TWOIN1_R = 0.05, 0.068                 # the suspension wire is fitted on site; the 2-in-1 carries current too
PLUG_R, PLUG_HH = 0.20, 0.55                   # wall plugs (white, per the guide's diagram)
SCREW_R, SCREW_HH, HEAD_R, HEAD_HH = 0.085, 0.70, 0.21, 0.05
SCREW_X = 6.5                                  # canopy fixing points: NOT documented - placed inboard of the
                                               # wire fittings; the guide only says "mark its screw holes"

def srgb_to_lin(c): c = c / 255.0; return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)
TEX = srgb_to_lin(np.asarray(Image.open(os.path.join(HERE, "teak-texture.png")).convert("RGB")).astype(np.float64))
CREAM = srgb_to_lin(np.array([243., 237., 227.]))

# ---------------------------------------------------------------- SDF primitives
@njit(cache=True, fastmath=True)
def clampf(x, a, b): return a if x < a else b if x > b else x

@njit(cache=True, fastmath=True)
def sd_box(px, py, pz, bx, by, bz, r):
    qx = abs(px) - bx + r; qy = abs(py) - by + r; qz = abs(pz) - bz + r
    ox = max(qx, 0.); oy = max(qy, 0.); oz = max(qz, 0.)
    return math.sqrt(ox*ox + oy*oy + oz*oz) + min(max(qx, max(qy, qz)), 0.) - r

@njit(cache=True, fastmath=True)
def sd_bar(px, py, pz):
    # capsule-ended in elevation (x-y), extruded in depth, edges eased
    r = 0.09
    cx = px - clampf(px, -(BAR_HL - BAR_HH), BAR_HL - BAR_HH)
    d2 = math.sqrt(cx*cx + py*py) - BAR_HH + r
    dz = abs(pz) - BAR_HD + r
    d = min(max(d2, dz), 0.) + math.sqrt(max(d2, 0.)**2 + max(dz, 0.)**2) - r
    # two channels cut into the underside
    for s in (-1., 1.):
        g = sd_box(px, py + BAR_HH, pz - s*CHAN_Z, CHAN_HL, CHAN_D, CHAN_HW, 0.02)
        d = max(d, -g)
    return d

@njit(cache=True, fastmath=True)
def sd_seg(px, py, pz, ax, ay, az, bx, by, bz, r):
    pax, pay, paz = px-ax, py-ay, pz-az; bax, bay, baz = bx-ax, by-ay, bz-az
    h = clampf((pax*bax + pay*bay + paz*baz) / max(bax*bax + bay*bay + baz*baz, 1e-9), 0., 1.)
    dx, dy, dz = pax - bax*h, pay - bay*h, paz - baz*h
    return math.sqrt(dx*dx + dy*dy + dz*dz) - r

@njit(cache=True, fastmath=True)
def sd_cyl(px, py, pz, cx, cy, cz, r, hh):
    dx = math.sqrt((px-cx)**2 + (pz-cz)**2) - r; dy = abs(py-cy) - hh
    return min(max(dx, dy), 0.) + math.sqrt(max(dx, 0.)**2 + max(dy, 0.)**2)

@njit(cache=True, fastmath=True)
def to_local(px, py, pz, ox, oy, oz, yaw, roll):
    x, y, z = px-ox, py-oy, pz-oz
    c, s = math.cos(-yaw), math.sin(-yaw); x, z = c*x + s*z, -s*x + c*z
    c, s = math.cos(-roll), math.sin(-roll); x, y = c*x - s*y, s*x + c*y
    return x, y, z

# P layout: 0-2 bar pos, 3 yaw, 4 roll | 5-7 canopy pos, 8 yaw, 9 roll | 10-15 cable A top,bot |
#           16-21 cable B top,bot | 22 led | 23 ceiling on, 24 ceiling y | 25-36 four fittings | 37 cables on
@njit(cache=True, fastmath=True)
def scene(px, py, pz, P):
    lx, ly, lz = to_local(px, py, pz, P[0], P[1], P[2], P[3], P[4])
    d = sd_bar(lx, ly, lz); m = 1.
    cx, cy, cz = to_local(px, py, pz, P[5], P[6], P[7], P[8], P[9])
    dc = sd_box(cx, cy, cz, CAN_HL, CAN_HH, CAN_HD, 0.07)
    if dc < d: d = dc; m = 2.
    if P[60] > .5:
        dk = sd_seg(px, py, pz, P[10], P[11], P[12], P[13], P[14], P[15], SUSP_R)
        if dk < d: d = dk; m = 3.
    if P[61] > .5:
        dk = sd_seg(px, py, pz, P[16], P[17], P[18], P[19], P[20], P[21], TWOIN1_R)
        if dk < d: d = dk; m = 3.
    if P[44] > .5:                                           # wall plugs
        for o in (38, 41):
            dp = sd_cyl(px, py, pz, P[o], P[o+1], P[o+2], PLUG_R, PLUG_HH)
            if dp < d: d = dp; m = 6.
    if P[52] > .5:                                           # screws: shaft up, head at the bottom
        for o in (45, 48):
            ds = sd_cyl(px, py, pz, P[o], P[o+1] + SCREW_HH, P[o+2], SCREW_R, SCREW_HH)
            dh = sd_cyl(px, py, pz, P[o], P[o+1], P[o+2], HEAD_R, HEAD_HH)
            # a cross slot in the head, so the spin reads
            ang = P[51]; ca, sa = math.cos(ang), math.sin(ang)
            rx = (px - P[o]) * ca + (pz - P[o+2]) * sa; rz = -(px - P[o]) * sa + (pz - P[o+2]) * ca
            slot = min(sd_box(rx, py - P[o+1] + HEAD_HH, rz, .16, .03, .022, 0.), sd_box(rx, py - P[o+1] + HEAD_HH, rz, .022, .03, .16, 0.))
            dh = max(dh, -slot)
            ds = min(ds, dh)
            if ds < d: d = ds; m = 7.
    if P[54] > .5:                                           # table top, for the hanging height
        dt = sd_box(px, py - P[53] + .75, pz, 32., .75, 16., .3)
        if dt < d: d = dt; m = 8.
    for o in (25, 28, 31, 34):
        dg = sd_cyl(px, py, pz, P[o], P[o+1], P[o+2], GRIP_R, GRIP_HH)
        if dg < d: d = dg; m = 3.
    if P[23] > .5:
        dp = P[24] - py
        if dp < d: d = dp; m = 5.
    return d, m

@njit(cache=True, fastmath=True)
def normal(px, py, pz, P):
    e = 0.0015
    a, _ = scene(px+e, py-e, pz-e, P); b, _ = scene(px-e, py-e, pz+e, P)
    c, _ = scene(px-e, py+e, pz-e, P); d, _ = scene(px+e, py+e, pz+e, P)
    nx = a - b - c + d; ny = -a - b + c + d; nz = -a + b - c + d
    l = math.sqrt(nx*nx + ny*ny + nz*nz) + 1e-12
    return nx/l, ny/l, nz/l

@njit(cache=True, fastmath=True)
def soft_shadow(px, py, pz, lx, ly, lz, P):
    res, t = 1., 0.02
    for _ in range(40):
        h, _ = scene(px + lx*t, py + ly*t, pz + lz*t, P)
        res = min(res, 9. * h / t)
        t += clampf(h, 0.02, 1.5)
        if res < 0.002 or t > 60.: break
    return clampf(res, 0., 1.)

@njit(cache=True, fastmath=True)
def ao(px, py, pz, nx, ny, nz, P):
    occ, sc = 0., 1.
    for i in range(5):
        h = 0.04 + 0.22 * i
        d, _ = scene(px + nx*h, py + ny*h, pz + nz*h, P)
        occ += (h - d) * sc; sc *= .7
    return clampf(1. - 1.6 * occ, 0., 1.)

@njit(cache=True, fastmath=True)
def tex(u, v, T):
    h, w = T.shape[0], T.shape[1]
    u = u - math.floor(u); v = v - math.floor(v)
    x = u * (w - 1); y = v * (h - 1)
    x0 = int(x); y0 = int(y); x1 = min(x0 + 1, w - 1); y1 = min(y0 + 1, h - 1)
    fx = x - x0; fy = y - y0
    r = np.empty(3)
    for c in range(3):
        r[c] = (T[y0, x0, c]*(1-fx) + T[y0, x1, c]*fx)*(1-fy) + (T[y1, x0, c]*(1-fx) + T[y1, x1, c]*fx)*fy
    return r

@njit(cache=True, fastmath=True)
def grain(x, y, z):
    """Fine figure that runs ALONG the length of the board, warping slowly - the way sawn teak reads.
    Layered on the photographed texture so close-ups have detail the 37-px source cannot carry."""
    w = 1.9 * math.sin(x * .13 + 1.7) + .7 * math.sin(x * .41 + .3) + .25 * math.sin(x * 1.3)
    c = (y + z) * 7.3 + w
    fine = math.sin(c * 6.0) * .5 + math.sin(c * 13.7 + 1.1) * .25
    ring = math.sin(c * 1.15) ** 8
    return 1. + .055 * fine - .10 * ring

@njit(parallel=True, cache=True, fastmath=True)
def render(W, H, cam, P, T, bg):
    """cam: [ox,oy,oz, fx,fy,fz, rx,ry,rz, ux,uy,uz, tan_half_fov]. Returns linear rgb and an emission pass."""
    out = np.empty((H, W, 3)); emi = np.zeros((H, W))
    ox, oy, oz = cam[0], cam[1], cam[2]
    asp = W / H
    kx, ky, kz = -.46, .80, .38; kl = math.sqrt(kx*kx + ky*ky + kz*kz); kx /= kl; ky /= kl; kz /= kl
    fx_, fy_, fz_ = .70, .25, .55; fl = math.sqrt(fx_*fx_ + fy_*fy_ + fz_*fz_); fx_ /= fl; fy_ /= fl; fz_ /= fl
    for j in prange(H):
        for i in range(W):
            sx = (2. * (i + .5) / W - 1.) * cam[12] * asp
            sy = (1. - 2. * (j + .5) / H) * cam[12]
            dx = cam[3] + cam[6]*sx + cam[9]*sy; dy = cam[4] + cam[7]*sx + cam[10]*sy; dz = cam[5] + cam[8]*sx + cam[11]*sy
            dl = math.sqrt(dx*dx + dy*dy + dz*dz); dx /= dl; dy /= dl; dz /= dl
            t = 0.; hit = False; m = 0.
            for _ in range(160):
                px, py, pz = ox + dx*t, oy + dy*t, oz + dz*t
                d, m = scene(px, py, pz, P)
                if d < 0.0006 * (1. + t): hit = True; break
                t += d
                if t > 400.: break
            if not hit:
                out[j, i, 0] = bg[0]; out[j, i, 1] = bg[1]; out[j, i, 2] = bg[2]
                continue
            nx, ny, nz = normal(px, py, pz, P)
            # albedo
            if m == 1. or m == 2.:
                if m == 1.:
                    lx, ly, lz = to_local(px, py, pz, P[0], P[1], P[2], P[3], P[4]); uoff = 0.
                else:
                    lx, ly, lz = to_local(px, py, pz, P[5], P[6], P[7], P[8], P[9]); uoff = .37
                anx = abs(nx); any_ = abs(ny)
                u = (lx + 24.5) / 49. * .66 + uoff
                v = (ly + 1.5) / 3. if anx < .7 and any_ < .7 else (lz + 1.) / 2.
                a = tex(u, v, T) * grain(lx, ly, lz)
                # inside a channel = the diffuser
                led = False
                if m == 1. and ly < -BAR_HH + CHAN_D + .03 and abs(lx) < CHAN_HL - .02:
                    for s in (-1., 1.):
                        if abs(lz - s*CHAN_Z) < CHAN_HW - .01: led = True
                if led:
                    on = P[22]
                    a[0] = .30; a[1] = .29; a[2] = .28
                    if on > 0.:
                        emi[j, i] = on
                        out[j, i, 0] = 1.00 * on * 3.2 + a[0] * (1-on)
                        out[j, i, 1] = .74 * on * 3.2 + a[1] * (1-on)
                        out[j, i, 2] = .46 * on * 3.2 + a[2] * (1-on)
                        continue
                spec_k, shin = .16, 36.
            elif m == 3.:
                a = np.empty(3); a[0] = a[1] = a[2] = .022; spec_k, shin = .45, 70.
            elif m == 6.:
                a = np.empty(3); a[0] = .78; a[1] = .77; a[2] = .74; spec_k, shin = .08, 20.
            elif m == 7.:
                a = np.empty(3); a[0] = .30; a[1] = .31; a[2] = .33; spec_k, shin = .9, 90.
            elif m == 8.:
                a = np.empty(3); a[0] = bg[0] * .74; a[1] = bg[1] * .72; a[2] = bg[2] * .69; spec_k, shin = .05, 12.
            else:
                a = np.empty(3); a[0] = bg[0]; a[1] = bg[1]; a[2] = bg[2]; spec_k, shin = 0., 1.
            sp_x, sp_y, sp_z = px + nx*.004, py + ny*.004, pz + nz*.004
            sh = soft_shadow(sp_x, sp_y, sp_z, kx, ky, kz, P)
            occ = ao(px, py, pz, nx, ny, nz, P)
            dk = max(nx*kx + ny*ky + nz*kz, 0.)
            df = max(nx*fx_ + ny*fy_ + nz*fz_, 0.)
            sky = .5 + .5 * ny
            bounce = .5 - .5 * ny                       # light coming back up off the room
            # half vector with the view
            hx, hy, hz = kx - dx, ky - dy, kz - dz; hl = math.sqrt(hx*hx + hy*hy + hz*hz) + 1e-9
            spec = spec_k * max((nx*hx + ny*hy + nz*hz) / hl, 0.) ** shin * sh
            # warm bounce from the lit channels onto the ceiling and the room above
            glow = 0.
            if P[22] > 0. and m == 5.:
                bdx = px - P[0]; bdz = pz - P[2]
                glow = P[22] * .9 * math.exp(-(bdx*bdx) / 900. - (bdz*bdz) / 60.) * math.exp(-(P[24] - P[1]) / 40.)
            for c in range(3):
                lit = a[c] * (2.3 * dk * sh + .32 * df + .55 * sky * occ + .62 * bounce * occ * (1.0, .93, .84)[c]) + spec
                if m == 5.:
                    near = math.exp(-((px - P[5])**2) / 700. - ((pz - P[7])**2) / 260.)
                    shade = (.80 + .20 * occ) * (.72 + .28 * sh)
                    lit = bg[c] * (1. - near + near * shade)
                    lit += glow * (1.0, .72, .42)[c]
                    if P[59] > 0.:                              # pencil marks where the screws will go
                        for o in (55, 57):
                            r2 = (px - P[o])**2 + (pz - P[o+1])**2
                            if r2 < .045: lit = lit * (1. - P[59] * .85)
                out[j, i, c] = lit
    return out, emi

# ---------------------------------------------------------------- camera
def look(eye, target, fov_deg):
    e = np.array(eye, float); f = np.array(target, float) - e; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    return np.array([*e, *f, *r, *u, math.tan(math.radians(fov_deg) / 2)])

def finish(lin, emi, bloom_px=30):
    """Filmic shoulder, bloom off the emission pass, back to sRGB uint8."""
    H, W = emi.shape
    if emi.max() > 0:
        e = (np.clip(lin, 0, None) * emi[..., None])
        s = Image.fromarray(np.clip(e / 3.5 * 255, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
        from PIL import ImageFilter
        b1 = np.asarray(s.filter(ImageFilter.GaussianBlur(bloom_px / 4)).resize((W, H), Image.BILINEAR)).astype(float) / 255 * 3.5
        b2 = np.asarray(s.filter(ImageFilter.GaussianBlur(bloom_px / 1.3)).resize((W, H), Image.BILINEAR)).astype(float) / 255 * 3.5
        lin = lin + b1 * .55 + b2 * .45
    x = np.clip(lin, 0, None)
    x = x * (1 + x / 9.) / (1 + x)                        # gentle shoulder, keeps cream at cream
    x = x / (1 * (1 + 1 / 9.) / 2)                         # renormalise so 1.0 maps to ~1.0
    x = np.clip(x, 0, 1)
    s = np.where(x <= .0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - .055)
    return (np.clip(s, 0, 1) * 255 + .5).astype(np.uint8)

def params(bar=(0, 0, 0), bar_yaw=0., bar_roll=0., can=(0, 30, 0), can_yaw=0., can_roll=0.,
           cables=True, led=0., ceiling=None, cableA=None, cableB=None, grips=None,
           wireA=None, wireB=None, plugs=None, screws=None, screw_spin=0., table=None,
           marks=None, marks_a=0.):
    P = np.zeros(64)
    P[0:3] = bar; P[3] = bar_yaw; P[4] = bar_roll
    P[5:8] = can; P[8] = can_yaw; P[9] = can_roll
    bx, by, bz = bar; cx, cy, cz = can
    top_bar = by + BAR_HH + GRIP_HH; bot_can = cy - CAN_HH - GRIP_HH
    ga = grips or [(bx - CABLE_X, top_bar, bz), (bx + CABLE_X, top_bar, bz),
                   (cx - CABLE_X, bot_can, cz), (cx + CABLE_X, bot_can, cz)]
    for k, g in enumerate(ga): P[25 + 3*k:28 + 3*k] = g
    A = cableA or ((ga[2][0], ga[2][1], ga[2][2]), (ga[0][0], ga[0][1], ga[0][2]))
    Bc = cableB or ((ga[3][0], ga[3][1], ga[3][2]), (ga[1][0], ga[1][1], ga[1][2]))
    P[10:13], P[13:16] = A; P[16:19], P[19:22] = Bc
    P[22] = led
    if ceiling is not None: P[23] = 1; P[24] = ceiling
    P[37] = 1. if cables else 0.
    P[60] = (1. if cables else 0.) if wireA is None else float(wireA)
    P[61] = (1. if cables else 0.) if wireB is None else float(wireB)
    if plugs: P[38:41], P[41:44] = plugs; P[44] = 1
    if screws: P[45:48], P[48:51] = screws; P[52] = 1; P[51] = screw_spin
    if table is not None: P[53] = table; P[54] = 1
    if marks: P[55:57], P[57:59] = marks; P[59] = marks_a
    return P

def frame_rgb(W, H, cam, P, ss=1.5, bloom_px=30):
    """Supersample by rendering larger and averaging down - the cables are thinner than a pixel at width."""
    w, h = int(W * ss), int(H * ss)
    lin, emi = render(w, h, cam, P, TEX, CREAM)
    img = Image.fromarray(finish(lin, emi, bloom_px * ss)).resize((W, H), Image.LANCZOS)
    return np.asarray(img)
