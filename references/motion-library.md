# Motion library (the house look for graphics)

The references the graphics should look and move like. The storyboard (step 4b) names one or more entries for every graphic beat, and the HyperFrames scenes then match those entries.

## How to add a reference
Add one block per reference you like. Keep the **creator credit and the link**. Put the technique in your own words under "Borrow"; that's what the skill actually uses.

Put full prompt texts in `motion-prompts.md` next to this file, under the same id. That file is git-ignored, so it stays on your machine, and the skill reads it when the storyboard cites the id. Only paste a full prompt here, in this public file, if it's yours or the creator allows reuse.

```
### <short-id>  (e.g. ui-zoom-typing)
- Link: <url to the example>
- Creator: <@handle>
- Tags: product-ui | phone | chart | diagram | kinetic-type | shapes | particles | characters | photos | music | code
- Borrow: <2-4 lines: what to copy: framing, camera move, easing, timing, transitions, palette, how text/UI animates>
- Avoid: <anything in it that clashes with the house style (dark grounds, grids, frantic cuts...)>
- Prompt: <optional: only your own prompt, or one you have permission to reuse>
```

Sources to browse (by hand, as a viewer):
- **prompt-motion.com**: a gallery of motion graphics made with Claude, each with its prompt; tags include Product UI, Charts, Diagrams, Kinetic type, Shapes, Particles, Music and Code. The site's prompts belong to their creators, and its robots.txt blocks Claude's crawlers and AI use. So the skill must **not** scrape or fetch it. Browse it yourself, pick the pieces you like, and add them here using the format above.

## How the skill uses this file
1. While storyboarding, pick for each graphic beat the entry whose tags and "Borrow" notes fit the content (product UI → `product-ui`, a number → `chart`/`kinetic-type`). Cite it by id in the beat's `refs`.
2. When building the composition, apply the "Borrow" notes on top of the house rules in `brief.md` (ground, shadows, type, camera rules, content zones). The house rules win where they conflict; list any conflict in the report.
3. If the library is empty, follow the house rules alone and say so in the storyboard.

## Entries

### house-luxury-tech  (built in)
- Link: this repo, `references/examples/` (the Harvey short)
- Creator: house style
- Tags: product-ui, kinetic-type, photos
- Borrow: one bright near-white world of floating white cards with the three-layer shadow; a world camera that glides, steps (0.5 s power3.inOut, 0.25 s before the word), pushes (1.2–2 s) and whips at most once per run, with motion blur along screen velocity. Real product UI types, streams and clicks inside a fixed window while only an inner camera moves. Real source pages sit in a fixed frame on a blurred, washed clone of themselves.
- Avoid: anything dark, grids, label pills that restate the narration.

### product-showreel-throughline
- Link: prompt-motion.com (entry link and creator still to add)
- Creator: see the prompt-motion.com entry
- Tags: product-ui, kinetic-type
- Borrow: pick one **through-line object** from the product (its cursor, a key button, the logo mark, one data point). It starts in the UI, changes shape or role at each scene change, and finally becomes the logo, so every transition is a match cut on that object. Measure its position at runtime rather than hard-coding it. Rebuild the UI as separate vector layers so parts move on their own, and let a cursor drive real clicks and drags while the camera zooms in screen-studio style until each moment fills the frame. Use springs with at most a small overshoot. Nothing pops in: elements grow, unfold or are revealed by a mask. The camera always drifts (about +4% per scene), and each scene starts at the zoom the last one ended on. Something changes on every beat (120 BPM). One accent colour, used only on the through-line object and the key word. Outgoing and incoming text get separate timing, so letters never overlap. A shape that fills the frame is scaled past all four corners.
- Avoid: particle bursts, glows, lens flares, camera shake, RGB split, crossfades, generic gradients, bouncy easing, holds over half a second, template looks. Where it clashes with the house rules (16:9 canvas, "camera never still" vs. the house's frame 0 at rest, its own brand palette vs. the near-white world), the house rules in `brief.md` win.
- Variant: a 30 s version of the same template that takes its visual style from a reference video the user supplies (download it, study its look and pacing, then apply it within these rules). With 30 s there is room for three or four product moments at a calmer pace.
- Variant: a 40 s "product film" version with the same rules. At that length, give each product moment its own small arc (UI state → action → result) and keep the beat-driven changes, but let the camera breathe longer inside each moment.
- Full prompt: private, in `motion-prompts.md` (base, 30 s and 40 s variants; not in this repo).

### gallery-3d-film-camera
- Link: prompt-motion.com (entry link and creator still to add)
- Creator: see the prompt-motion.com entry
- Tags: shapes, photos, kinetic-type
- Borrow: a real 3D space (three.js) instead of flat cards. Many cards sit on gently curved walls that form corridors and, seen from above, resolve into a wordmark. Build the whole piece toward one **signature shot**. The camera is a film camera: one named move per shot (dolly, crane, orbit, push-in, rack focus), eased in and out, and it never passes through geometry. Use a key, fill and rim light with soft shadows, an environment map for reflections, fog for depth, physically based materials with varied roughness and ACES tone mapping, so nothing looks like a default material. Elements react to each other, driven by springs or simple physics: a wave of accent light runs along a wall and each card tilts as it passes, and a card unhinges, swings with weight and settles. Depth of field only on the shots that need it. Seed every random number and compute each frame from time, so the render matches the preview.
- Avoid: default materials and lighting, floating text labels, glows everywhere, a slowly spinning object as the whole idea, tech-demo looks. For the shorts it suits a hook or a payoff visual (a full-frame run), rendered at 9:16 inside the house's near-white world; the house rules in `brief.md` win on format, type and levels.
- Full prompt: private, in `motion-prompts.md` (not in this repo).

### showreel-everything-transforms
- Link: prompt-motion.com (entry link and creator still to add)
- Creator: see the prompt-motion.com entry
- Tags: kinetic-type, shapes, charts, product-ui
- Borrow: name the concept in one line first (for example "ink becomes type becomes architecture"). Then make every shot out of the previous one: shapes, type and colour transform into the next scene, with no cuts or fades. Show range in equal shares: kinetic type, shape morphing, a 2D-to-3D moment, a data/UI moment and an end title. Keep one typeface, at most three colours plus black and white, and one consistent camera language. Something changes on every beat (120 BPM), the strongest moment lands in the last full bar, and the final frame matches the first so the piece loops.
- Avoid: particle bursts, glows, lens flares, camera shake, RGB split, crossfades, generic gradients, bouncy easing, holds over half a second, template looks. In a short, use its transform-don't-cut idea between graphic beats *inside* a run. Picture cuts between layouts stay hard cuts, and the house rules in `brief.md` win.
- Full prompt: private, in `motion-prompts.md` (not in this repo).

### launch-film-one-take-glass
- Link: prompt-motion.com (entry link and creator still to add)
- Creator: see the prompt-motion.com entry
- Tags: product-ui, phone, kinetic-type, photos, music
- Borrow: a keynote-style launch film in **one continuous 2D take**. Nothing fades, blurs or cuts; objects change shape instead:
  - text rises out of a mask line, icons pop from zero on a spring, and bars draw across;
  - pages push, and a black shape floods the whole frame, then contracts into the next scene;
  - one black shape keeps morphing through states (ordered ✓ → printing % → on its way → delivered ✓);
  - an iris of six blades closes over one scene and snaps open on the next;
  - a grid unfolds from behind a tile like a paper map, then reflows into a bento.
  - The surfaces are warm off-white with black UI and iOS-style liquid glass. The glass is built by cloning the scene behind it through a displacement map, with slight chromatic edges and a rim light.
  - A cursor drives every change with real clicks, drags and long-presses, and the camera zooms screen-studio style so the cursor scales with it.
  - The music structure sets the beats: the zoom lands on the drop and the quiet part sits in the breakdown.
- Technique notes worth reusing:
  - springs as closed-form step responses, summed per target so they stay a pure function of time;
  - a flood must overscale past the corners and take about 0.3 s;
  - text swapping inside a morphing shape needs its own mask;
  - footage goes in all-intra (`-g 1`), loaded as a blob URL;
  - scan the render for single-frame pops (frame-difference spikes about 3× their neighbours).
- Avoid: crossfades, blur-ins, "developing" brightness, 3D flips, particles, glows, holds over 1 s, template looks. Its sound rule (downloaded SFX) conflicts with the house rule (everything synthesized in code), so the house wins. In a short, use its flood/iris/morphing-shape transitions *inside* a graphic run (for example an order/status sequence as one morphing shape); layout changes stay hard cuts; format is 9:16 and the house rules in `brief.md` win.
- Full prompt: private, in `motion-prompts.md` (not in this repo).

### product-sting-frame-exact
- Link: prompt-motion.com (entry link and creator still to add)
- Creator: see the prompt-motion.com entry
- Tags: product-ui, phone, kinetic-type, music
- Borrow: a 12 s keynote-feel product sting, specified **frame by frame**: keyframe tables of exact positions, sizes, opacities and blur per frame, with hard cuts placed 2 frames before the beat they lead. The camera never cuts on a still frame. Every shot enters already moving (exponential ease-out) and leaves on an accelerating move or a blur ramp, with blur following speed and direction (separate x/y blur for smears). Story beats worth stealing for product UI:
  - a header rises out of a coloured haze inside an app window;
  - a cursor glides in, turns to face where it's heading, grows on hover and presses;
  - an app icon with four coloured squares orbiting into a cross;
  - the icon collapses into a menu-bar item, which springs out a frosted glass prompt box where the prompt types itself;
  - a whip-tilt through a light flash into the answer page scrolling into place, with the key phrase in bold;
  - a card rises over the page;
  - stacked cards with giant frosted-glass titles (a blurred copy of the image clipped to the letters);
  - a lone logo disc, then the end card.
  - Frosted glass = a blurred, lightened copy of what's behind, clipped to the shape. A zoom smear = 20–30 scaled, faded copies.
- Technique notes worth reusing:
  - every value continuous in the frame number, so half-frames render cleanly for a 59.94 master: keyframe tables with interpolation, no flooring on motion;
  - measure text only after fonts load;
  - scale a whole lockup to fit when a name gets longer;
  - a white element on a white page needs a 1 px edge and a faint shadow;
  - heavy blur can erase a shape: lower it until the shape still reads.
- Avoid: crossfades, frozen frames, stock UI kits, glows on UI text, unseeded randomness, template looks. Its palette (white, blues, navy; no purple or orange) and square 1080 format are specific to that brand. In a short, borrow its cursor behaviour, frosted-glass prompt box and cut/blur discipline inside graphic runs. The house rules in `brief.md` win on format, palette, type and sound.
- Full prompt: private, in `motion-prompts.md` (not in this repo).
