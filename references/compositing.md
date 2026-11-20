# Deterministic page composition

## Contents

1. Purpose and limits
2. Run and outputs
3. Layout contract
4. Ledger and project lettering grammar
5. Panel review attestations
6. Geometry, crops, and protected regions
7. Fonts and exact text
8. Verification

## Purpose and limits

Use `scripts/compose_page.py` after each individual panel has passed visual review. It combines reviewed artwork, precise clipping masks, borders, balloons, tails, and exact source text. It does not generate art, judge likeness, infer speakers, rearrange a story, or fix anatomy.

The layout contract below is a small compositor input, separate from the story planning manifest. Translate approved planning records into it explicitly. Do not pretend that a field named `accepted` proves visual fidelity. The renderer checks an external attestation and the exact art hash; that prevents stale or mismatched images from silently passing, but cannot establish that a reviewer was truthful.

Keep generative edit masks separate from these deterministic clipping masks. OpenAI documents that its model may not follow an editing mask's exact shape. It recommends compositing an approved edit into an original when unchanged areas must remain pixel-identical. [Image generation](https://developers.openai.com/api/docs/guides/image-generation), [Image prompting](https://developers.openai.com/api/docs/guides/image-prompting), checked 20 November 2026.

Separate artwork and lettering is also a proven production method: the Pepper&Carrot project combines KRA artwork with SVG balloons and dialogue. Borrow the layer separation, not the source comic's setting or optional production techniques. [Pepper&Carrot production documentation](https://www.peppercarrot.com/en/documentation/010_Translate_the_comic.html), checked 20 November 2026.

## Run and outputs

Use Python 3.10 or later and Pillow. For pages with lettering, supply a single-file TTF or OTF font. A wordless page uses an empty dialogue ledger and balloon list, and needs no font. Complex-script text additionally requires Pillow built with libraqm. Never silently substitute an unlicensed or missing font.

```sh
python scripts/compose_page.py project/layout.json project/exports/page-01
```

Existing outputs are protected. Add `--overwrite` only when replacing the same intended export. Validation finishes before final files are written. Each output file is replaced atomically; a later filesystem failure can still leave an incomplete export set, so verify all five outputs.

| Output | Purpose |
|---|---|
| `composite.png` | Flattened RGBA page at declared pixel size |
| `lettering.png` | Full-page RGBA overlay with transparent pixels outside lettering |
| `page.svg` | Self-contained editable master with embedded artwork, fonts, vector clips, shapes, and text |
| `page.ora` | OpenRaster layers, merged preview, and thumbnail |
| `render_manifest.json` | Exact dialogue strings, input hashes, crop transforms, and layer inventory |

The SVG retains editable panel clip geometry. ORA panel layers contain the clipped raster result, not an editable vector mask. ORA keeps each panel separate, with additional page, border, tail, balloon, dialogue, and SFX layers. Verify the SVG in the target editor because font embedding and SVG text support differ between editors. PNG is the deterministic Pillow rendering. The compositor is a small production helper, not a replacement for a full desktop publishing engine.

## Layout contract

All coordinates are pixels. Page coordinates have origin at the upper-left, x right, y down. Source-image coordinates are explicitly called out below. Relative file paths resolve against `layout.json`; absolute paths are allowed for authorized local resources.

```json
{
  "version": 1,
  "page": {
    "id": "PAGE1", "width": 1200, "height": 1800,
    "background": "#ffffff", "min_font_size": 28
  },
  "ledger": "dialogue.json",
  "font_path": "fonts/approved-body.ttf",
  "styles": {
    "ordinary": {
      "shape": "ellipse",
      "allowed_kinds": ["speech", "offscreen"],
      "tail_policy": "required",
      "fill": "#ffffff", "stroke": "#111111", "stroke_width": 3,
      "font_size": 32, "text_color": "#111111",
      "padding": [18, 24, 18, 24], "line_spacing": 1.1,
      "text_align": "center", "direction": "ltr", "tail_width": 20
    },
    "internal": {
      "shape": "rect", "allowed_kinds": ["thought"],
      "tail_policy": "none", "font_size": 32, "padding": 18
    }
  },
  "panels": [{
    "id": "P1", "art": "approved/P1.png", "acceptance": "qa/P1.json",
    "frame": {"polygon": [[50,50],[1150,50],[1080,750],[50,750]]},
    "fit": "cover", "align": [0.5,0.5],
    "border": {"color":"#111111", "width":4},
    "subjects": [{"character_id":"C_01", "mouth":[800,440], "thought_anchor":[800,390]}],
    "critical_regions": [{"name":"face", "rect":[600,300,180,160]}]
  }],
  "balloons": [{
    "id":"B1", "dialogue_id":"D1", "panel_id":"P1", "style":"ordinary",
    "box":[90,90,520,210],
    "tail":{"kind":"on_panel", "character_id":"C_01", "target":[800,440]}
  }]
}
```

This example illustrates fields, not a universally valid composition. Critical source rectangles must correspond to the actual art and projected crop. Set sizes from the intended reading format and inspect the result. A page minimum is a project decision, not a universal readability guarantee.

`frame` must contain exactly one of `rect: [x,y,width,height]` or `polygon: [[x,y],...]`. Do not repeat the polygon's first point at the end. Polygons must be nondegenerate, non-self-intersecting, and inside the page. Rectangles must have positive dimensions. Concave polygons are supported.

Supported styles are `ellipse`, `rect`, `rounded`, `thought`, and `burst`. Unsupported custom shapes fail explicitly. Use the project's editor for bespoke artwork rather than claiming a substituted ellipse is faithful. `rounded` supports `corner_radius`; `burst` and `thought` support `points` from 6 to 40. `thought` uses a single scalloped outline. Shapes describe geometry only; their meanings come from `allowed_kinds` and `tail_policy`.

Asymmetry is represented through independent box proportions, four-sided padding, `text_align`, optional tail `base: [x,y]`, and style-specific `tail_width`, `tail_reach`, `tail_gap`, and `thought_dot_scale`. Each style can override `font_path`. Define a distinct style variant when needed instead of changing an accepted style silently.

## Ledger and project lettering grammar

```json
{
  "dialogue": [
    {
      "dialogue_id": "D1", "page_id": "PAGE1", "panel_id": "P1",
      "speaker_id": "C_01", "kind": "speech", "reading_order": 1,
      "text": "<exact text from the current script>"
    }
  ]
}
```

Every ledger row requires a unique `dialogue_id`, `page_id`, `panel_id`, `kind`, and nonempty exact `text`. Supported kinds are `speech`, `thought`, `caption`, `offscreen`, and `sfx`. All rows for the composed page must be assigned exactly once. If any page row has `reading_order`, every row on that page must have a distinct positive reading order. Otherwise ledger array order is authoritative. The balloon array must follow that order. This is a consistency check, not a visual proof that the page reads naturally.

Never put text in a balloon layout record. It must refer to a ledger item. Do not fix typos, normalize punctuation, collapse spaces, or rewrite a line during composition. A source change requires an explicit ledger revision.

Styles declare `allowed_kinds` and `tail_policy: required|optional|none`. Do not universally map rectangles to narration or clouds to thoughts. A project may use a rectangular internal monologue without thought dots, or a rectangular spoken line. The selected project grammar controls that choice.

- `on_panel` tails must name the ledger speaker and aim toward that character's recorded `mouth`, within two pixels. This target is an attribution anchor, not a point the drawn tail must touch. The anchor must lie inside the relevant panel.
- `thought` tails use dots aimed toward the same speaker's recorded `thought_anchor`. The trail stops short of the head. A thought without a tail is valid when its style allows it.
- `offscreen` tails require an `offscreen` ledger item, the correct speaker ID, and a declared page-space target. A target may be a phone, doorway, or page edge. If the ledger provides `source_id`, the tail must match it. No visible mouth is fabricated.
- Captions can use an explicit `narrator_id`, including a character narrator. They do not receive speaking tails. `speaker_id` is optional for caption records and is preserved if supplied.
- SFX can have `speaker_id: null`. Use an explicitly authored spatial box and a style with a transparent fill and zero stroke for unboxed effects. SFX receive their own text layer. The helper does not rotate glyphs or provide arbitrary path lettering.

Tail direction and tail length are separate. `styles.<id>.tail_reach` defaults to `0.55`, measured from the tail base toward its target. A balloon may override it with `tail.reach`; the accepted range is greater than 0 through 1. Longer deliberate tails are permitted, but the drawn tip must leave the balloon body, retain its aim, and avoid recorded critical regions. `tail_gap` is an additional minimum pixel gap from the anchor, not the primary length control. The render manifest records the anchor, base, requested reach, and actual drawn tip. Blambot's lettering guidance describes tails aimed at the mouth through an imaginary continuation and gives a 50-60% distance guideline. Treat that as a useful starting point, not a mandatory ratio for every style. [Blambot comic lettering tips](https://blambot.com/pages/comic-book-grammar-tradition), checked 20 November 2026.

## Panel review attestations

```json
{
  "panel_id": "P1",
  "status": "accepted",
  "art_sha256": "the actual SHA-256 of the approved image bytes",
  "reviewed_by": "the actual reviewer or review session",
  "checks": {
    "identity":"pass", "narrative":"pass", "continuity":"pass",
    "emotion":"pass", "anatomy":"pass", "style":"pass", "composition":"pass"
  },
  "notes": "Specific review evidence belongs here."
}
```

`status` must be `accepted`; the panel ID and image hash must match. All seven check keys are required. A `pass` string is accepted, or a check can be an object containing `status: pass|not_applicable` and a nonempty `reason`. Never mark uncertainty as passed. Visible subjects require identity, emotion, and anatomy to pass. Use `not_applicable` only for genuinely irrelevant checks, with a specific reason. Text supplied here is an attestation, not a substitute for the actual comparison images and review evidence maintained by the skill.

The geometry-test fixture contains original colored shapes and is labelled accordingly. Its synthetic review records exercise the validation mechanism. They provide no evidence about generated artistic quality, character consistency, or storytelling.

## Geometry, crops, and protected regions

`cover` scales uniformly to cover the frame bounding box and clips the excess. `contain` scales uniformly to fit inside it and leaves uncovered space showing lower layers. Neither mode stretches. `align` chooses the normalized horizontal and vertical offset, each from 0 to 1.

Optional `crop: [x,y,width,height]` selects an integer-pixel rectangle from the approved source. The source remains untouched. Out-of-range, zero-area, or fractional crops fail explicitly. The SVG embeds the selected crop with a uniform transform; the manifest records the original hash, crop, scale, and offset.

`critical_regions[].rect` is in original source pixels. Mark faces, speaking mouths, essential hands, plot props, and other genuinely necessary content. The renderer rejects crops, frame masks, later overlapping panel art, panel borders, or rendered tail/trail pixels that hide these regions. By default it also rejects balloon bodies that cover them. `protect_from_lettering: false` relaxes only the balloon-body check; it does not permit thought dots or tails to cross a protected face. Declare face regions when a tail or thought trail approaches a character, then inspect its direction and ending visually. The helper cannot infer an unrecorded face region from artwork.

The renderer limits one page to 40 million pixels to bound memory. Split very long scroll chapters into delivery strips or pages. Preserve the original planning and master art outside those delivery segments.

## Fonts and exact text

The font file is mandatory. The SVG embeds it, and the manifest records its hash. Ensure the project has the right to redistribute that font. TTF/OTF Unicode cmap formats 4, 12, and 13 are supported; collections and unsupported maps fail explicitly. Missing glyphs fail rather than producing empty boxes.

Text wraps at whitespace using measured glyph advances. Punctuation and whitespace are retained, and exact source strings are recorded in the SVG metadata and render manifest. Explicit newlines are honored. An oversized word, excessive whitespace run, insufficient balloon height, or glyphs outside the actual balloon shape fail. The helper never shrinks text automatically. Enlarge the balloon, change the composition, or explicitly revise the approved source rather than reducing readability.

Tabs and carriage returns fail explicitly. Normalize file line endings through an intentional source-edit step if needed. CJK text without spaces requires approved explicit line breaks or a layout engine with language-aware line breaking; this helper does not invent those rules.

Arabic, Hebrew, combining sequences, and other complex shaping require libraqm. With it, use the style's `direction: rtl|ltr`; without it, the helper fails honestly for complex text. It does not reverse strings. Native editor support and font shaping can still differ, so inspect the final SVG and PNG in their intended reader.

## Verification

The test command and fixture below require the separate development test suite.

```sh
python -m unittest discover -s tests -p test_compositor.py -v
```

Tests look for a supplied `MANGAKA_TEST_FONT`, DejaVu Sans on Linux, or Arial on Windows/macOS. If no explicit test font exists, the tests report skips. A skipped run is not a passed verification gate. Provide a suitable font and rerun.

The test fixture builder is `fixture(folder)` in `tests/test_compositor.py`. It creates small original colored geometry, source ledger, layout, and clearly labelled synthetic attestations. It tests irregular masks, exact strings and XML escaping, real alpha, layered ORA export, uniform scaling, stale hashes, missing review evidence, speaker and target mismatch, missing glyphs, overflow, complex shaping, project-specific thought/caption grammar, and offscreen sources.

Inspect `composite.png` and `lettering.png` at intended reading size and enlarged detail. Confirm that all five exports exist, ORA layer order matches the manifest, SVG fonts and images are embedded, and SVG/PNG display the same story and text. Automated geometry tests do not replace panel-to-reference or panel-to-panel visual QA.
