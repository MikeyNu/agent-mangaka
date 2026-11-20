# Sources and evidence boundaries

## Contents

1. How to use this register
2. Model and prompting documentation
3. Production and layer workflows
4. Sequential art and drawing practice
5. Research and perception evidence
6. Local study evidence
7. Decisions made by this skill
8. Refresh and verification rules

## How to use this register

All external sources below were accessed and checked on **2026-11-20**. The date is the verification date, not necessarily the publication date. Exact URLs are included so an agent can revisit the current source before depending on a changing capability. This register supports [art direction](art-direction.md), [pages and lettering](pages-and-lettering.md), [compositing](compositing.md), and the workflow in [SKILL.md](../SKILL.md).

Keep these evidence categories separate:

| Category | What it can establish | What it cannot establish |
|---|---|---|
| Primary product documentation | A provider's documented parameters, limits, behaviors and examples at the checked date | Access through this agent's connector, account entitlement, or guaranteed output fidelity |
| First-person artist practice | What the artist reports doing or recommends, including successful and failed methods | One universal method, the workflow of another artist, or controlled evidence of AI reliability |
| Institutional instruction | A defined convention or practical teaching method | A mandatory law for all styles, audiences or narrative purposes |
| Empirical research | Findings under the study's actual task, sample and materials | Automatic generalization to every comic, language, layout or generated image |
| Direct local visual study | Features visible in the supplied pixels and recorded inspection regions | Hidden layers, author intent, source tools, exact lenses or whether 3D assistance was used |
| Skill design inference | A proposed procedure connecting these observations to agent behavior | A source claim or an experimentally proven success rate |

The user's current script and named designs determine fictional canon. External art advice does not override them. Product documentation determines technical possibilities only after the live tool exposes a compatible operation.

## Model and prompting documentation

| ID and exact source | Evidence | Supports | Limits and application |
|---|---|---|---|
| M01. [OpenAI: Image generation](https://developers.openai.com/api/docs/guides/image-generation) | Primary product documentation | Image generation and editing interfaces; documented limitations in precise text, recurring character consistency and composition; masks guide edits but may not be followed precisely. | Model names, supported parameters and input limits change. A generation mask is not the deterministic clipping mask used to assemble a page. Documented availability does not prove connector access. |
| M02. [OpenAI: Image prompting](https://developers.openai.com/api/docs/guides/image-prompting) | Primary product documentation and provider examples | Structured visible requirements, references assigned by number and purpose, separating requested changes from preservation constraints, focused iteration, and compositing an approved edit into original pixels when exact preservation is necessary. | Prompt structure improves specification, not certainty. The guide treats camera terms as appearance cues, not a guarantee of physical simulation. Compare actual outputs and recheck settings for the selected model. |
| M03. [Google DeepMind: Gemini Image prompt guide](https://deepmind.google/models/gemini-image/prompt-guide/) | Primary provider guidance | Naming style, subject, setting, action and composition; controlled iterative edits and changes of view. | General examples are not a benchmark for long-form comic identity or multi-character role binding. Use concrete reference assignments and inspect each result. |
| M04. [Google: Image generation with Gemini](https://ai.google.dev/gemini-api/docs/image-generation) | Primary product documentation | Model-specific reference-image allowances, image-generation interfaces and limitations. At verification this URL redirects to [Google AI Studio's image-generation documentation](https://aistudio.google.com/docs/image-generation). | A total image-input allowance is not an equal number of supported character identities. The checked guide distinguishes object, character and style allowances by model. Re-read the actual model section and live connector schema rather than freezing a number in this skill. |
| M05. [Google Developers Blog: Prompting Gemini 2.5 Flash Image](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/) | Primary provider examples for a named model | Descriptive scenes, single-panel prompts, explicit reference composition, iterative correction and positive descriptions of desired omissions. It acknowledges that absolute character consistency and nuanced typography may need refinement. | This is guidance for the named model, not a current API schema or a guarantee. Its integrated-lettering examples are not this skill's production choice. The skill uses separate exact typography and does not treat photographic terms as precise camera control. |
| M06. [Google Cloud: Omit content using a negative prompt](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/omit-content-using-a-negative-prompt) | Primary product documentation | Negative-prompt support is model-specific. The checked page identifies it as a legacy feature absent from Imagen models starting with `imagen-3.0-generate-002` and newer. | The page also contains endpoint deprecation information and older examples. Do not send a `negativePrompt` field to an incompatible model or transfer Imagen syntax to Gemini or another provider. Verify the live schema first. |

These sources justify model adapters rather than one universal prompt recipe. They do not establish that a website subscription, an Unlimited badge, an API balance or a connected tool shares the same billing entitlement. Account-specific access and costs require actual connector or account evidence. A quote, prompt packet or model listing is not a completed image job.

## Production and layer workflows

| ID and exact source | Evidence | Supports | Limits and application |
|---|---|---|---|
| W01. [David Revoy: Episode 21 Production Report](https://www.davidrevoy.com/article325/the-chaotic-making-of-episode-21) | First-person production report, published 2017-01-28 | Concept development, scenario, repeated storyboard revisions, style trials, and separation of vector balloons/dialogue/SFX from layered raster artwork. It documents failures and rework as part of actual production. | One artist's episode, not a universal production experiment. The report also describes optional Blender assistance. Borrow planning and layer separation without imposing 3D rendering, the fantasy setting, or this artist's visual identity. |
| W02. [Pepper&Carrot: Translate the webcomic](https://www.peppercarrot.com/en/documentation/010_Translate_the_comic.html) | Primary project workflow documentation | Published pages combine KRA artwork with SVG speech balloons; text, sound effects, balloon bodies and tails can be edited independently for translation. | Demonstrates a functioning separation of concerns. It does not require this skill to use exactly Krita and Inkscape, and it does not establish the hidden layers of the user's supplied study strips. |
| W03. [CELSYS: Frames and Panels](https://help.clip-studio.com/en-us/manual_en/540_comic/Frames_and_Panels.htm) | Primary application documentation | Frame folders restrict visible art to a frame, support division and editing, and distinguish frame borders from drawing content. | Application and edition behavior may change. The reusable principle is explicit clipping and editable frame geometry, not a claim that every editor or the bundled compositor supports every CELSYS feature. |
| W04. [CELSYS: Speech balloon tools](https://tips.clip-studio.com/en-us/articles/863) | Primary application instruction | Editable balloon geometry, fills and opacity, outline variants, straight/curved tails, flash forms and masking around characters or frames. | Describes available construction techniques. It does not define one universal meaning for each shape or prove that the source artist used these tools. A project-specific custom design may need another capable editor. |

## Sequential art and drawing practice

| ID and exact source | Evidence | Supports | Limits and application |
|---|---|---|---|
| A01. [Steve Ellis: Comic and manga layouts, paneling and flow](https://www.clipstudio.net/how-to-draw/archives/160963) | First-person professional artist instruction | Planning scene endpoints, breaking progression into panels, thumbnailing, varying panel emphasis and considering reading direction and balloon placement early. | Practical guidance, not a rule that every story needs a fixed panel count or a fixed grid. Apply it to the declared print or scroll format. |
| A02. [Nate Piekos, Blambot: Comic Book Grammar and Tradition](https://blambot.com/pages/comic-book-grammar-tradition) | First-person professional letterer instruction | Balloon and caption vocabulary, emphasis, remote voices, weak delivery, thought conventions and tail direction. A tail may aim toward a mouth along an implied continued line while stopping short of it. | Piekos explicitly describes editorial variation and exceptions. His tail-length example is a starting convention, not a compulsory ratio. The supplied project grammar controls the final design. |
| A03. [WEBTOON CANVAS: Getting Started](https://tips.clip-studio.com/en-us/articles/4891) | Official platform creator guidance | Mobile readability, vertical pacing, panel variation and spacing examples for an 800px-wide canvas. | The article labels its suggestions as guidelines. Its sample gaps and bubble density are not mandatory for other widths, devices or stories. Verify current upload requirements separately at delivery time. |
| A04. [Columbia Film Language Glossary: 180-Degree Rule](https://filmglossary.ccnmtl.columbia.edu/term/180-degree-rule/) | Institutional instruction with annotated film examples | Maintaining an action axis helps preserve screen relationships and reciprocal looking directions; the page also discusses deliberate violations. | A film convention adapted here to static sequential images. This source does not require every panel to stay forever on one side, and crossing an axis is not the same as moving actors in world space. |
| A05. [CELSYS: Basics of perspective drawing](https://tips.clip-studio.com/en-us/articles/807) | Primary drawing-tool instruction | One-, two- and three-point perspective, eye level, vanishing points and drawing a spatial construction on a 2D plane. | Teaches a construction framework, not an automatic proof that a stylized image obeys exact geometry. Perspective planning does not require rendered 3D assets. |
| A06. [Fujifilm: Understanding Lens Compression](https://www.fujifilm-x.com/en-gb/learning-centre/understanding-lens-compression/) | Primary manufacturer education with examples | Apparent compression follows viewpoint and relative subject distance; focal length determines framing from that position. | Photography explains the geometry, while a drawing may deliberately exaggerate it. Do not infer an exact lens from an illustration or claim a focal-length label alone controls an image model. |
| A07. [Stan Prokopenko: How to Draw Gesture](https://www.proko.com/course-lesson/how-to-draw-gesture) | First-person artist instruction | Gesture connects forms and communicates action and feeling; body language should be established before incidental contour detail. | A drawing lesson, not a validated emotion classifier. Performance must follow character intent, context and the script. |
| A08. [Magda Proski: How to Draw Expressive Faces](https://www.clipstudio.net/how-to-draw/archives/157239) | First-person professional artist instruction | Dimensional head construction and coordinated changes in facial features during expression. | Construction aids likeness, but the project sheet defines the character. A single facial sign does not prove a hidden emotion, and a smile may be socially performed. |
| A09. [Eridey: Guide to Drawing Shadows](https://www.clipstudio.net/how-to-draw/archives/163236) | First-person artist instruction | Distinguishing light-facing forms, core/form shadow, cast shadow and reflected light to explain volume and material. | This is a foundation for drawn lighting. Expressive face shading may intentionally depart from literal illumination and must be declared separately. |
| A10. [Chris Hurtt: Anticipation](https://www.animationmentor.com/blog/anticipation-the-12-basic-principles-of-animation/) | Professional animation instruction, published 2017-06-07 | Preparatory behavior can make a coming action understandable and can be broad or subtle. | Transfer to selected still moments is this skill's design inference. A surprise attack may intentionally omit visible preparation. |
| A11. [Animation Mentor: Twelve Principles of Animation](https://www.animationmentor.com/blog/tutorial-12-principles-of-animation/) | Professional animation instruction | Staging, anticipation, arcs, secondary action, exaggeration and related animation principles provide a vocabulary for action design. | Comics do not display the same timing as moving animation. Do not mechanically produce a separate panel for every principle or phase. |
| A12. [TehMochie: Find Your Chibi Style](https://tips.clip-studio.com/en-us/articles/4808) | First-person artist tutorial | Chibi permits different proportions, simplification choices, expressions and postures while retaining selected identity cues. | A community artist's demonstrated practice, not a CELSYS standard or a universal head-to-body ratio. Use only when the new project permits the mode. |

## Research and perception evidence

| ID and exact source | Evidence | Supports | Limits and application |
|---|---|---|---|
| R01. [Neil Cohn: Navigating Comics, 2013](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00186/full) | Original empirical research | Layout can lead readers away from a simple left-to-right/down Z path; panel grouping and navigation constraints matter. | Participants numbered empty panel layouts. Do not present this as a direct test of every completed comic, text-art interaction, reading direction or phone viewport. It supports checking the actual reading path. |
| R02. [James Gurney: Eye Tracking and Composition, Part 3](https://gurneyjourney.blogspot.com/2009/09/eye-tracking-and-composition-part-3.html) | Artist's first-person report of a small eye-tracking demonstration, published 2009-09-20 | The reported sixteen-viewer heatmaps emphasize depicted subjects and faces, and challenge the assumption that a golden-section line automatically attracts attention. | This is not a universal proof against compositional grids or a large controlled comics study. Use it to reject automatic golden-ratio scoring, then inspect the intended hierarchy in the actual work. |

## Local study evidence

The user supplied a private corpus of flattened vertical-comic WebP strips. The checked inventory contains **52 files and 51 distinct file hashes**. `008 (1).webp` and `008 (2).webp` are byte-identical. Filename suffixes are inventory labels and do not by themselves establish chapter or story order.

The study used contiguous tiled overviews and selected native-resolution crops. See the consolidated study observations and coverage ledger for exactly what was viewed, its source hash, dimensions and original-pixel crop rectangles. Full overview coverage is different from native inspection of every pixel. Private originals and inspection crops are not redistributed in this repository.

Examples of directly observed features and the separate design inference:

| Local evidence anchor | Visible evidence | Design inference applied by the skill |
|---|---|---|
| `002 (4).webp`, crop `[0,550,760,1950]` | Four people, tiled floor, red runner, window light and cast shadows appear in an elevated room view. | Plan the room and participants before selecting close views. The published pixels do not prove an original floor-plan file existed. |
| `005 (3).webp`, crops `[0,3100,760,5200]` and `[0,7900,760,9900]` | A spear-directed impact is followed by a wider relationship between attacker, displaced opponent and a separately spinning weapon. | Track attack, reaction, displacement and prop loss as distinct state changes. Exact biomechanics cannot be certified from these images alone. |
| `006 (4).webp`, crop `[0,5400,760,7950]` | Internal narration accompanies symbolic uniformed figures and a heraldic flag outside the room's literal background treatment. | Keep imagined or hypothetical figures out of actual scene occupancy unless the script makes them present. |
| `007 (3).webp`, crop `[0,6150,760,7600]` | A miniature duel diagram and orange directional arrow accompany an explanation by the current speaker. | Mark a replay/explanatory mode so the state tracker does not apply the past attack twice. |
| `008 (5).webp`, crop `[0,350,760,1450]` | Comic panic uses spiral eyes and faint repeated arm positions. | Permit explicitly planned motion echoes while rejecting accidental extra solid limbs. |
| `009 (3).webp`, crop `[0,9550,760,11050]` plus the preceding cloth insert | The child's mouth is cleaner while tears and distress remain. | Cleaning can be a partial state update rather than a full reset of injury or emotion. |
| `010 (3).webp`, crop `[0,0,760,1450]` | An overhead includes five participants, discarded equipment and a garden edge. | Include bystanders and persistent props in spatial planning; distinguish out-of-frame from absent. |

These interpretations are proposed explanations of function. They are not attributed statements by the artist. The corpus does not establish a numerical golden-ratio construction, exact camera focal lengths, original layer structure, absence of 3D reference, or a universally applicable medieval-fantasy aesthetic. It is primarily evidence for the supplied colored vertical-comic presentation; other formats require their own preview and evaluation.

## Decisions made by this skill

The following are project engineering decisions informed by the evidence above, not claims copied from a source:

- Stable character and environment IDs, a canon manifest and an exact dialogue ledger reduce ambiguous bindings.
- A theoretical spatial map separates world position from the projected screen relationship.
- Each panel is generated and reviewed independently before deterministic page assembly.
- Original reference assets remain primary anchors so copying previous generated panels does not compound drift.
- Art, clipping, borders, balloon geometry and exact text remain separate to make errors repairable and attribution inspectable.
- Literal, remembered, imagined, replayed and comic-exaggeration modes have explicit scope and state effects.
- Critical identity, speaker, geography and narrative errors block acceptance instead of being averaged into a quality score.
- Version hashes and review records can verify artifact provenance and stale approval, but cannot prove that a visual judgment was correct.
- A capability probe or synthetic fixture validates its stated mechanism only. It does not demonstrate consistent generated chapter quality.

The user's request establishes the separate-panel and layered-production requirement. The cited workflows show practical precedents. Neither fact proves that a prompt can eliminate every possible model error. Actual visual evaluation and subsequent repairs remain necessary.

## Refresh and verification rules

1. Before a provider call, inspect the live tool schema and the selected model's current official documentation. Record the model, operation, reference limits, controls and actual entitlement evidence.
2. Before export, verify current platform or printer requirements. Keep stable art principles separate from changing upload limits.
3. For each consequential claim, identify whether its basis is source text, local pixels, a test result or design inference. Do not promote a plausible interpretation into a documented fact.
4. When a page is inaccessible, do not infer its contents from its title. Use an already inspected source for the same claim or mark the claim unverified.
5. Preserve a test report's scope. Prompt evaluation, numeric validation, compositor rendering, visual review and actual model generation are different kinds of evidence.
6. Update this register and the affected reference when a capability or procedure changes. Retain the user's current project contract as the authority for story and design decisions.
