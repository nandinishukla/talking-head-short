# Motion library (the house look for graphics)

The references the graphics should look and move like. The storyboard (step 4b) names one or more entries for every graphic beat, and the HyperFrames scenes then match those entries.

## How to add a reference
Add one block per reference you like. Keep the **creator credit and the link**. Put the technique in your own words under "Borrow"; that's what the skill actually uses.

Only paste a creator's full prompt under "Prompt" if it's yours, or if the creator allows reuse. If this repo is public, everything here is public.

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
