# NixWoods "gravity build": three lamps build themselves, then switch on

The idea comes from @pires.visuals' reel (instagram.com/reel/DdrdBZLo08N, 14.1 s, 345k views). In one take, debris
flies in and a tower builds itself floor by floor, then the camera pulls back to show the finished building. That reel
is AI video (Seedance).

This version was made **for free**, from real photos only, as the owner asked ("You have enough skills to make it for
free"). There are no generated frames and no Higgsfield credits were spent, so no AI label is needed.

9:16, 30 fps, 14.40 s, music3-design (on its measured beat grid of 0.6003 s; every light comes on a strong beat).
Output: `NW-CREATIVE-VID-20261012-nixwoods-gravity-build-v1.mp4`, plus `-cover.jpg` and `-sheet.jpg`.

## How it is made (`gravity_build.py`)
Each lamp goes through the same steps:
1. Cut the lamp out of its own 5 Aug DSLR photo.
2. Rebuild the room behind it row by row from the wall on either side, giving an empty plate.
3. Split the lamp into wooden blocks that fly up and settle into place, bottom to top. They carry motion blur, and
   sawdust is thrown up where each block lands.
4. Switch the light on, on the beat. The room comes up from dim to the untouched photo, so the last frame of each
   scene is the real photo.

| Time | Product (PRODUCT-ID tell) | Photo | Light | Card (Shopify, live 12 Oct) |
|---|---|---|---|---|
| 0–3.6 s | Aurora linear wall light (horizontal bar; the owner's file name says Aurora) | AC4I9649 | warms up evenly at 2.4 s | Aurora wall light, from ₹1,999 |
| 3.6–7.2 s | Minimalist floor lamp (a lit rod on a round base) | AC4I9777 | draws up the rod at 6.0 s | Minimalist floor lamp, from ₹6,999 |
| 7.2–10.8 s | Sculpted Glow (an LED rope looping through a rosewood frame) | AC4I9882 | draws along the rope at 9.6 s | Sculpted Glow lamp, ₹9,999 |
| 10.8–14.4 s | End card on a Dusk ground | — | — | logo, "Solid wood. / Made by *hand*.", nixwoods.com |

The hook "Built piece / by piece." is set in Fraunces 600 on a top scrim. It is up by 0.17 s and leaves before the
Aurora switches on.

## Against MOTION.md
- **Followed:**
  - real photos of the real lamps, upright;
  - light that warms up or draws itself, and never blinks;
  - the Dusk end card (logo, Fraunces headline with one amber italic word, URL in amber);
  - cards in cream, with the price in dark amber;
  - all text inside the safe zone and clear of the lit channel (the floor lamp's rod is 213 px from the card);
  - CRF 17, bt709, +faststart.
- **Changed, taken from the reference:**
  - The pieces turn as they fly in. They settle into place and never spin continuously, and the camera never shakes.
  - The reel runs 14.4 s, the reference's length, instead of 6–10 s, because it shows three products.
  - On a Reels screen, the Sculpted Glow's base sits in the bottom UI zone in the wide shot. Its top frame was kept
    clear of the card instead.

## Known limits
- **Extended walls:** the Aurora photo has almost no wall above the bar, and the Sculpted Glow photo has little above
  its frame. Each wall was extended upward with plain wall (each column's own colour), so the hook and cards have
  room.
- **Rebuilt wood:** the wood hidden behind the Sculpted Glow's rope is rebuilt along the grain. It shows only in the
  dim, unlit state, and the light covers it as it draws.
- **Dark rods:** the floor lamp's room is already dark, so its build is dimmed less than the others.
