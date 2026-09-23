---
name: ecom-product-video
description: >-
  Turn product photography, phone footage and competitor reference reels into short vertical
  product videos (9:16 reels, ad cuts, PDP loops). Use this whenever someone wants a product
  video, reel, TikTok, Short or ad creative for something they sell; sends a competitor's or
  creator's video and asks to "do this for us", "make it like this", or change its material,
  colour or product; asks to cut phone footage of a product into something postable; or asks
  why a product video looks cheap, dark, soft or off-brand. Use it even when they just say
  "make a video of this" and attach product photos — the failure modes here are specific and
  expensive, and most of them are invisible until after you ship.
---

# E-commerce product video

Short product video is mostly a craft of **not** getting things wrong. The creative idea is
usually easy; what sinks reels is a list of unglamorous, repeatable faults — a hook that
withholds nothing, a product rendered in the wrong shape, a shot that reads as a smudge on a
phone at low brightness, a silent truncation that eats the end card. This skill is that list,
in the order the faults actually bite.

## 1. Look at the reference before you interpret it

If someone sends a video and says "like this", **watch it frame by frame first**. Summarising
from the caption or the thumbnail produces a reel in the same *spirit*, which is almost never
what they asked for — they usually mean the specific thing: these shots, this order, this pace.

Instagram, TikTok and X posts are behind a login wall for plain HTTP fetches, and share tokens
(`?stkn=`) work only sometimes. Connectors that read social posts with the user's own
authentication do work — they return caption, author, thumbnail and a direct video URL. Look for
one before telling the user you can't see their reference. Asking for screenshots is the fallback,
not the first move.

Then **measure** rather than eyeball. Shot boundaries fall out of a frame-difference pass:

```python
# 10 fps greyscale, flag frames where the mean absolute difference spikes
d = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
cuts = [i / 10 for i, v in enumerate(d) if v > d.mean() + 2.2 * d.std()]
```

You will usually find the reel is three long takes and some connective tissue, not the rapid
cutting you assumed. Matching the real structure is what makes a rebuild feel like the original.

## 2. What you may take from a reference, and what you may not

Structure, pacing, shot list and the *idea* are fair to learn from. The footage is not. Recolouring
a competitor's animation and posting it as your client's ad hands them an asset built on someone
else's work — a legal problem for them, not a creative one for you.

Say this once, plainly, then immediately show what you *can* do: rebuild their shot list and
timings with the client's own assets. In practice that gets people what they wanted, because what
they admired was the structure. If they reaffirm the request after you've explained, that's their
decision to make about their own risk — but don't skip the explanation, and don't lecture twice.

## 3. Inventory the library before you generate anything

**The single most expensive mistake in this work is generating an asset that already exists.**
It costs money, it costs a round trip, and worst of all you will have told the user "we don't have
that" — which they may believe and act on.

Before any generation, list every product folder and *read the filenames against the shot list you
are about to shoot*, not against a general sense of what's there. A folder searched once for
"reel assets" has not been searched for "a ceiling canopy" or "an end cap" or "a box being opened".
Product photography sets routinely contain exactly the detail shot you were about to pay for.

## 4. Never invent what the product looks like

A generated frame showing the wrong shape, the wrong mechanism or hardware the customer will not
receive is worse than no frame. It misrepresents the thing being sold, and people notice.

- Generate **from a reference image of the real product**, never from a text description alone.
- Compare every generated frame against real photography before it goes in the cut, and record an
  approve/reject verdict somewhere durable so the next session doesn't re-litigate it.
- Don't depict a mechanism the product doesn't use. If a competitor's install sequence shows a
  chrome cable gripper and this product ships a wooden canopy, that sequence cannot be borrowed —
  the customer would receive something else.

## 5. The hook is most of the reel

Score it before you build anything around it. Three gates, and a hook failing any of them is worth
rewriting even when the line reads nicely:

- **Gap** — does it withhold something the viewer now wants resolved?
- **Truth** — is it verifiable, with no invented claim, spec or timing?
- **Pull** — is there a reason to keep watching rather than a statement to agree with?

Lines that *describe* score badly ("polished by hand", "everyone makes these in aluminium") because
they state a category rather than open one. Lines that name what the footage is withholding score
well ("wait for it to light up", "this one is not aluminium", "turn it on and look at the mugs").
The best hooks usually come from asking: *what does this footage not show yet?*

## 6. Framing a wide product in a vertical frame

Most products are wider than 9:16. Three options, and picking the wrong one is the most common
reason a reel looks amateur:

| approach | when it works | when it fails |
|---|---|---|
| `cover` (crop to fill) | close detail; pan along the subject with different crop centres | cuts the ends off a long product — a four-foot pendant loses the four feet |
| `contain` (whole image over a blurred copy of itself) | bright photography of a long subject | **dark** source — the blurred backing is near-black and the subject becomes a thin lit band |
| extend the background vertically | a standalone poster with a plain wall to continue | inside a reel, where it leaves the subject small and the frame mostly empty |

The default instinct — "show the whole product" — produces small subjects in big empty frames. For
reels, prefer tight crops at several different centres so consecutive shots differ in scale, and
save one wide as a deliberate pull-back where it lands as a payoff.

**Check upscale factor before committing a shot.** A 493px source filling a 1080-wide frame is
2.2× and visibly soft. Compute it; don't judge it on a thumbnail.

## 7. Grade to the footage you actually have

A grade tuned on one shoot will destroy another. Measure first:

```python
lum = np.asarray(Image.open(f).convert("L"))
print(f, lum.mean(), np.percentile(lum, 5), np.percentile(lum, 95))
```

Footage whose darkest 5% sits at 122 tolerates a heavy crush; footage sitting at 28 turns to mud
under the same curve. When a dark grade must be applied to bright studio photography, lift the toe
with a curve rather than pulling brightness down globally.

And verify colour by number, not by eye. Highlight-extraction tricks that zero luma while leaving
chroma untouched produce **magenta** glows that look plausible in a thumbnail. After any bloom or
recolour, print the mean per channel and confirm it matches intent — warm light wants R > G > B.

## 8. Phone footage arrives broken

Modern phone video is HEVC 10-bit **HLG** with a rotation flag. Dropped into a timeline untouched
it renders washed-out grey, and people assume the camera was bad. Tonemap to SDR first:

```
zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,
tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p
```

Normalise to the output resolution in the same pass and keep the originals out of the repo.

## 9. Derive before you buy

Generation budgets run out mid-project. Before spending, ask whether the beat you need is a
*transformation of a frame you already have*:

- **A diffuser going on** — blur the bright LED dots into one continuous line. That is what a
  diffuser does optically, so the result is honest as well as free.
- **A light switching on** — screen-composite a warm, blurred copy of the brightest pixels.
- **A part going into place** — wipe between two stills of the same setup at two stages. This is
  the single highest-value trick in the list: it produces assembly motion from photographs.
- **Night** — a grade on the lit version.
- **A different material** — weight every pixel *continuously* by how much it already resembles the
  material, then scale toward a target sampled from real photography of the target material. Binary
  colour masks leak into backgrounds and catch only lit grain, so the subject comes out speckled;
  a continuous weight moves dark and lit grain together and leaves neutral pixels alone. Verify by
  measuring drift on neutral pixels — it should be ~0.

## 10. Guards that catch the failures you cannot see

These faults are silent. Each one has shipped in real work.

- **Reading past the end of a source clip.** ffmpeg doesn't error; it runs out of frames and drops
  everything after that shot, end card included, while the container still reports full duration.
  Compute what each shot needs — accounting for slow/speed, which change how much source a given
  output duration consumes — and refuse rather than truncate.
- **A missing end card.** Extract the final frame after every render and confirm it's there.
- **Text plates on dark grades.** An automatic contrast box reads as a smudge; switch it off and
  rely on a shadow.
- **File size.** Check against a stated ceiling. Re-encode from the master, not from an already
  re-encoded copy, and check dark gradients for banding afterwards — that's where it shows first.
- **Render intermediates in version control.** Text layers and transition segments are regenerated
  every run; ignore them or the repository grows by their full size on every re-render.

## 11. Claims, disclosure and honesty in the cut

- No invented specs, prices, dispatch times or testimonials. If a figure isn't in a datasheet or on
  the PDP, it doesn't go on screen.
- If **any** frame is AI-generated, say so where it matters: paid placements on Meta need the AI
  disclosure ticked, and a rendered room shouldn't be captioned as a photograph. A one-line note in
  the caption ("last frame is a render") costs nothing and protects the brand.
- An edit that implies something the footage didn't capture — a grade-driven "switch on" when
  nothing filmed a switch — is a legitimate device, but don't let the caption claim it as a demo.

## 12. Before you call it done

Watch the video. A contact sheet shows framing and text placement; it cannot show pacing, a
truncated tail, or audio. Then confirm: hook scored and on screen early enough · every shot fills
the frame · grade measured against this footage · end card present · under the size ceiling ·
claims checked · disclosure noted if anything is generated · the file named, stored and recorded
wherever the project's downstream consumers actually look.
