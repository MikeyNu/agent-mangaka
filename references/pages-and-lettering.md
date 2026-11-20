# Pages, vertical scroll and lettering

## Contents

1. Plan the publication format
2. Build the reading sequence
3. Reserve text before generating art
4. Assemble panels through precise masks
5. Define the project's balloon grammar
6. Bind every utterance to its source
7. Set readable and exact lettering
8. Export and inspect
9. Failure scenarios

## Plan the publication format

Declare page or vertical-scroll format, reading direction, language, output dimensions, intended display size, and print specifications if applicable. These are separate choices. Manga appearance does not automatically require right-to-left reading; English text in a right-to-left page sequence still uses its proper text direction.

| Format | Planning unit | Main reveal risk | Required preview |
|---|---|---|---|
| Print page or digital page | Panel, page and facing spread | A reveal may already be visible on the spread | Single page, facing spread and intended print/display size |
| Vertical scroll | Panel and moving viewport | A response or reveal appears too early while scrolling | Continuous phone-width scroll at representative viewport heights |
| Adaptation between formats | New reading composition | Cropping or stacking destroys pacing and text order | Recompose and inspect both formats separately |

For print, obtain the printer's trim, bleed, safe area, binding and color requirements. Keep important text and facial information away from trim and binding loss. Do not invent universal export numbers. For a platform, verify its current upload limits at export time; an older tutorial's canvas size is not an evergreen platform contract.

WEBTOON's own creator article emphasizes mobile reading and gives spacing examples for an 800px-wide canvas: roughly 200px between ordinary panels and 600-1000px for scene transitions, plus low bubble density. Those are explicitly guidelines. Scale them to the actual design, then test the phone preview; do not enforce them as universal timing rules. [WEBTOON CANVAS, getting started](https://tips.clip-studio.com/en-us/articles/4891), accessed 2026-11-20.

## Build the reading sequence

Assign a stable reading order to panels and utterances before artwork generation. Check the order visually after composition. A numbered ledger proves the intended order, not that readers can discover it.

Choose the default panel path from the declared reading direction. For LTR pages, an upper-left entry moving across and down is a common starting pattern; reverse the horizontal sequence when the project explicitly uses RTL pages. Insets, tall panels, overlapping frames and blocked gutters can create ambiguity. Neil Cohn's research showed that readers of empty comic layouts do not always follow a simple Z path. Its empty-panel method tests layout navigation, not every interaction between completed art and text. [Navigating Comics, 2013](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00186/full), accessed 2026-11-20.

In thumbnails, check the first entry, each transition, and the final exit into the next page or scroll beat. Vary size and shape according to the narrative purpose. A reaction insert, a wide environment and a narrow eye crop should earn their space. Steve Ellis's layout instruction connects these decisions to scene progression and directs artists to plan balloon placement early. [Comic and manga layouts](https://www.clipstudio.net/how-to-draw/archives/160963), accessed 2026-11-20.

For vertical work, treat whitespace as a controllable interval and a reveal boundary. A long gap can separate time or place, but a gap alone does not prove a precise duration. Test whether the reader sees setup and payoff together, whether isolated dialogue remains attributable, and whether a large illustration is revealed in the intended order. Do not derive final scroll pacing from a tiled contact sheet.

## Reserve text before generating art

Keep exact dialogue in a source ledger with utterance ID, speaker or narrator ID, semantic kind, scene/beat/panel assignment and order. Preserve punctuation, emphasis and explicit line breaks. Resolve character names and aliases before binding the line to a reference sheet.

Thumbnail the expected balloon area using measured sample text. Reserve clear areas and tail routes in the panel brief. Mark critical visual regions such as speaking faces, gesture hands, impact contacts and plot clues. Generate each panel as an individual art asset; the page must not depend on the image model inventing correct lettering or panel boundaries.

If a long exchange does not fit, first improve the composition or allocate another panel. Do not silently reduce text to an unreadable size, delete a line, change its speaker, or paraphrase the script. A proposed text revision is a separate story edit.

## Assemble panels through precise masks

Plan layout before generating the panel art, then finalize the assembly after individual panels pass review. Early layout planning and later final composition are compatible: the provisional frame determines aspect ratio and protected zones; the accepted art is then placed into its precise allocation.

Use this layer order as a project-adjustable production model:

| Layer role | What belongs here |
|---|---|
| Page or scroll base | Background color and intended gutter treatment |
| Individual panel art | One accepted image per panel, retained at its native aspect ratio |
| Clip geometry and borders | Rectangular, polygonal or custom panel masks and dividers |
| Deliberate breakouts | Approved foreground elements or effects that cross a frame |
| Balloon bodies and tails | Reusable project designs with true transparency outside them |
| Exact text and effects | Dialogue, captions, sound lettering and final emphasis |

This is a recommended reconstruction strategy, not a claim that a flattened study image reveals the original artist's layers. CELSYS documents frame folders that hide drawing outside their frame and editable balloon tools with masks, separate outlines and adjustable fills. [Frames and Panels](https://help.clip-studio.com/en-us/manual_en/540_comic/Frames_and_Panels.htm), [Speech balloon tools](https://tips.clip-studio.com/en-us/articles/863), accessed 2026-11-20.

Scale uniformly and clip; do not stretch a face or body to fill an irregular frame. Protect the parts required to understand the beat. If a crop loses the speaking mouth, essential hand or impact, revise the frame or source composition. A local generative edit mask is not a substitute for deterministic final clipping.

Do not send the completed page back to an image model merely to draw gutters or add balloons. That can change already accepted faces, props and backgrounds. Preserve editable masks and layers in the master. For the supported helper's exact capabilities and limits, use [compositing.md](compositing.md).

If the supplied balloon design is a reusable raster, preserve its alpha and avoid distorting its border. If it needs an ornamental generative asset, create that asset separately, verify its true transparency, and place exact text with a text engine. Use editable vector paths where the project design can be reproduced accurately. A checkerboard painted into RGB pixels is not transparency.

## Define the project's balloon grammar

The user's supplied designs are authoritative. Inventory them by reference ID, semantic role, shape, fill/alpha, stroke, tail convention, font, emphasis rules and allowed variants. Distinguish geometry from meaning: a rectangle can hold narration, thought, interface text or speech depending on the project.

The following is a vocabulary to resolve against project references, not a universal assignment:

| Semantic purpose | Possible visual treatment | Binding requirement |
|---|---|---|
| Ordinary speech | Oval, rounded or custom body | Named visible speaker or explicit off-panel source |
| Shout or sudden outcry | Sharp burst, large type or another approved emphasis | Correct speaker and degree of emphasis |
| Weak, nervous or strained voice | Wavering outline, irregular tail or approved type variant | Keep the line readable and owned |
| Internal thought | Thought dots, fuzzy flash, caption or another project convention | Thinking character, distinct from audible speech |
| Narration or time/location cue | Rectangular or custom caption | Narrator or metadata role, usually no speaking tail |
| Phone, radio or disembodied voice | Project-specific electronic or remote style | Character and sound source are separately identified |
| Sound effect | Integrated lettering, free text or designed graphic | Event and location; a speaker may be absent |
| Identity or title card | Project-specific framing and typography | Named entity or paratext, never mistaken for dialogue |

Nate Piekos presents lettering conventions as traditions with editorial variation, including captions, thought, shouting, weak speech and remote voices. His guidance supports deliberate grammar rather than a universal shape classifier. [Blambot, Comic Book Grammar and Tradition](https://blambot.com/pages/comic-book-grammar-tradition), accessed 2026-11-20.

The historical visual study includes both fuzzy internal-thought forms and dotted-tail thought ovals. It also includes wavering speech, partly translucent balloons, rectangular narration and ornate name cards. Preserve such distinctions when they are selected for a new project; do not import them into a different project's approved balloon system by default.

When a needed semantic role has no design reference, derive the smallest compatible variant and record the decision. Do not silently substitute a generic circle when a required custom form is unsupported by the compositor. Route that asset through an editor or another capable tool and keep the rest of the pipeline intact.

## Bind every utterance to its source

Place text from the ledger by utterance ID, never by retyping remembered wording. Each line must occur exactly once in its intended narrative occurrence. A deliberate replay or repeated line needs a separate occurrence ID. An internal line must not become spoken merely because a tail was convenient.

Use speaker anchors to express ownership and direction. For ordinary visible speech, aim the tail toward the intended head or mouth along a clear implied line; the tail need not touch the mouth. Piekos describes tails stopping partway between balloon and speaker. Do not confuse a target anchor with the rendered tail endpoint. [Blambot, balloon tails](https://blambot.com/pages/comic-book-grammar-tradition), accessed 2026-11-20.

Route tails so they do not cross other tails, essential faces or important text. Avoid a direction that could plausibly assign the line to a nearby listener. A closeup with one visible person can still carry offscreen speech from someone else; the ledger controls the voice.

For a phone or radio, record both the character who speaks and the device from which the sound emerges. For off-panel speech, use the declared boundary or source direction and approved remote style. Do not invent a visible character solely to provide a mouth anchor. For group speech, enumerate the intended speakers and use the project's shared-balloon convention; never guess which cast members join in.

Treat conversational staging and lettering as a joint problem. If the desired bubble order would force crossed tails or reverse the intended read, revise the camera, balloon placement or panel allocation before final acceptance. Do not swap the characters' world positions to accommodate text.

## Set readable and exact lettering

Use project-approved fonts and inspect actual glyphs. Keep font, weight, case, leading, padding and alignment consistent unless an explicit variant conveys a delivery change. Font size alone does not establish readability; the glyph design, output scaling and reader device all matter.

Wrap text with measured glyph dimensions. Preserve punctuation, ellipses, capitalization and approved emphasis. Avoid accidental word splits and a crowded final line. Do not normalize a character's intentional speech pattern or punctuation during layout. If the engine cannot shape the language or wrap it correctly, use a capable text engine instead of reversing strings or substituting glyphs.

Keep page reading order separate from text direction. LTR English can appear in an RTL page layout. Arabic or Hebrew requires proper shaping and bidirectional text handling. Japanese vertical text requires a supported vertical typography workflow. Verify punctuation, brackets, numbers and mixed scripts in their rendered context.

Maintain a comfortable inner margin around words and adjust the body to the text. Preserve the supplied border thickness and shape character. A thought flash with dense lines needs enough separation from letters; a translucent fill needs sufficient contrast against every underlying image region.

Do a text-only pass: read every line in final order and compare it to the exact source ledger. Then do a silent visual pass: hide lettering and verify that poses, expressions and event order still carry their intended information. These are complementary checks, not competing standards.

## Export and inspect

Keep an editable master plus flattened delivery files and a transparent lettering overlay. A chapter's cut-up upload files are delivery segments, not necessarily story panels. Inspect joins so a balloon, tail or reveal is not accidentally broken by a file boundary.

Review at three scales:

1. Full page, spread or continuous-scroll overview for rhythm and panel hierarchy.
2. Actual intended reading size for dialogue order, legibility and reveal timing.
3. Native-resolution crops for glyph errors, tails, mask edges, alpha fringes and protected visual details.

Check each individual panel against its accepted source hash, then the assembled result against the intended crop and layer order. Check that page assembly did not stretch artwork, clip plot information, hide the wrong person or change speaker association. Machine checks can catch duplicate IDs, missing text and geometric collisions; they do not prove narrative comprehension or character likeness.

Verify the final transparent file over both a light and a dark background. Confirm that unused pixels are transparent, intended translucent fills remain translucent, and no white rectangle or checkerboard has been baked around the design. Inspect a representative export in the actual target viewer or printer proof workflow.

## Failure scenarios

| Scenario | Expected handling |
|---|---|
| Three speakers and an interjection | Explicit utterance order, unambiguous tails, no silent speaker reassignment |
| A thought immediately followed by speech | Separate semantic roles and approved styles, with the same character ID if appropriate |
| A long monologue exceeds the balloon | Recompose or split at an approved narrative boundary; preserve exact text |
| A diagonal frame hides the contact hand | Reject that crop and repair composition before assembly |
| A phone voice overlaps a listener closeup | Bind speaker to the remote character and sound source to the device |
| A flashback repeats a line | Create a distinct occurrence and preserve the temporal context |
| RTL pages with English dialogue | Reverse panel sequence only as declared; retain proper English text direction |
| A vertical reveal lands on an export join | Re-cut the delivery strips or adjust spacing after viewport review |
| The requested balloon is unsupported | Use a capable editor or faithful asset; report the specific limitation |
| A perfectly legible balloon points to the wrong twin | Fail speaker parity even though typography and geometry are otherwise valid |
