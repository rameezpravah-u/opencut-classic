# linear-reels — the wooden answer to the Aluma assembly reel

Reference: instagram.com/reel/DbVnOOksf-c (`alumaetg`, an Iranian aluminium lighting-profile
maker, 28 s, 63k views, 28 Jul 2026). Read with the Vibiz connector, which has authenticated
Instagram access — `vibiz_read_social_post` returns the caption, the thumbnail and a direct
`videoUrl`. **Use it for any future reference reel;** plain WebFetch hits a login wall, and the
`?stkn=` share token works only sometimes.

Their reel is a 3D assembly animation: black aluminium extrusion on a desk → LED strip lowers into
the channel → diffuser slides in → end cap → ceiling bracket and suspension → finished pendant lit
over a desk → logo. The Persian caption is a direct-from-manufacturer pitch — every stage in-house,
no middlemen, better price.

Rameez: "change the material to wood and make it for nixwoods." That claim is literally true for
NixWoods, and NixWoods has what Aluma had to fake in CGI: real footage of a craftsman finishing the
wood (`shelf-reels/src/IMG_7745.mp4`).

## Stages

| # | file | what |
|---|---|---|
| 1 | `hf/gen-stage1-channel.png` | solid rosewood bar, channel routed along its length, driver beside it |
| 2 | `hf/gen-stage2-led.png` | LED strip seated flush in the channel, copper pads visible at the near end |
| 3 | — | diffuser half slid in: near half glowing, far half open **(not generated — quota)** |
| 4 | — | end cap / brass fitting **(not generated)** |
| 5 | — | finished bar lit, suspended on cables in a dark room **(not generated)** |
| 6 | — | installed over a table in a warm room **(not generated)** |

Stages 1 and 2 are AI-generated (ElevenLabs `bytedance-seedream-5-pro`, 818 credits each). They are
**not** photographs of a NixWoods product — no such linear bar has been photographed on a bench.
Any paid placement needs Meta's AI disclosure.

## Why it stopped

- ElevenLabs **video** is refused on this account: `paid_plan_required`.
- ElevenLabs **images**: quota exhausted mid-run — 139 credits left of 10,000, 818 needed a stage.
- Higgsfield: 19.75 credits, about two image-to-video clips against the seven this needs.

A full CGI-style build costs roughly $6.50 in video (seedance-v2 priced at $0.92 a clip) or about
$0.50 in stills. Either needs a top-up. Until then the honest cut is: real workshop footage for the
making, these two stages for the assembly, and the existing lit renders for the payoff.
