# Visual QA, repair and acceptance

## Contents

1. Define acceptance before generation
2. Inspect candidates against original sources
3. Apply hard visual gates
4. Compare neighbors and the full sequence
5. Repair through a bounded adaptive loop
6. Record evidence and separate machine scope
7. Review the assembled page or scroll
8. Deliver and retain a resumable audit trail

## Define acceptance before generation

QA starts with the panel contract, not with whether the result looks attractive.
Read its `moment`, `story_intent`, `participants`, `represented_characters`,
`state`, `camera`, `acting`, `composition`, `dialogue_ids` and `reference_ids`.
Identify the few visible facts that carry the beat and the conditions that would
mislead the reader. Keep those conditions stable while reviewing candidates.

Choose checks that can actually fail in this panel. For an exchange, verify
the speaker, the listener's direction of attention and the projected positions
of any visible landmarks. For a silent change of state, verify the before and
after cues that let the reader recognize the change without dialogue.

Plan aspect ratio, lettering space and protected visual regions before the image
call. The early layout is provisional. Accept the individual unlettered panel
before building the final page container and masks, then review the placed crop
again. Artwork acceptance does not automatically approve every future placement.

Record representation and narrative scope before judging anomalies. An imagined
person, a framed portrait, a temporal afterimage and an unplanned duplicate body
are different cases. Inner contempt plus an outward reassuring smile may be the
correct acting. A literal glow, expressive background and change of location may
each justify a different lighting treatment.

## Inspect candidates against original sources

Save each returned candidate in staging with a unique version and hash, then open
it. A completion message, thumbnail or model's own description is not a visual
review. Confirm that the downloaded file is complete and belongs to the expected
job before interpreting its content.

Use this inspection set for every panel:

1. **Whole image at intended reading size.** Check immediate identity, gesture,
   focal information, emotion, depth, unwanted text and the selected story instant.
2. **Original reference comparison.** Place the relevant sheet views, environment
   anchors and approved style sample beside the candidate. Do not use only the
   previous generated panel, which may already contain drift.
3. **Native detail crops.** Inspect faces, asymmetrical identifiers, visible hands,
   grips, contact points, costume motifs, important props and suspicious edges.
   Record pixel rectangles and what each crop establishes.
4. **Neighbor comparison.** Compare the candidate with preceding accepted art and,
   when available, following art. Check transitions as well as separate quality.

Inspect every region through tiles when an image is too tall to read in one view.
An overview establishes coverage; selected crops establish detail coverage. State
which was actually performed. Never describe selected crop review as a native
inspection of every pixel. If the viewer cannot reveal necessary detail, mark
that gate unresolved and obtain a usable image or view.

Choose a reference angle that makes the questioned feature visible. Compare face
structure and identifying landmarks across perspective, not identical pixel
coordinates. A hidden earring should not be invented on the visible ear to make
matching easier. Record “occluded in this view,” then confirm identity through
other visible anchors. If the shot depends on the hidden detail, revise the view.

## Apply hard visual gates

Use `pass`, `repair` or `blocked` for review decisions. The accepted manifest must
contain explicit `pass` values for the seven required `qa.checks` keys below.
There is no average score that can compensate for a failed critical category.

| Gate | Inspect | Fail or block when |
|---|---|---|
| `identity` | Face, silhouette, proportions, anatomical asymmetry, active variant and costume | Wrong actor, blended sheets, transferred costume or unsupported identity change |
| `narrative` | Selected instant, event ownership, targets, source scope and dialogue binding | Wrong person acts/speaks, crucial event changes, premature reveal or unreliable account promoted to canon |
| `space` | World positions, camera projection, eyelines, heights, landmarks, props and light causes | Unexplained relocation, impossible contact, wrong background relationship or unsupported physical light change |
| `acting` | Inner state, outward display, intention, face, hands, body tension and response | Expression contradicts the intended performance or a reaction belongs to the wrong actor |
| `anatomy` | Topology, grasp, joints, support, overlap and action path | Unexplained extra body part, fused hands, lost grip or motion that cannot be read as intended |
| `style` | Line character, proportion range, values, palette, materials and declared expressive modes | Unplanned renderer/style shift, identity erosion or alien genre motifs |
| `composition` | Focal hierarchy, framing, depth, selected scale, crop safety and reserved lettering zones | Key action is hidden, crop removes meaning, or usable text space cannot be maintained |

Gate failure requires evidence. “The hand looks odd” is insufficient; specify the
subject, anatomical side, view and point where the silhouette or overlap breaks
continuity. State what must be preserved during repair.

Apply permitted stylization narrowly. A near fist can exceed head size through
foreshortening; a temporal montage can repeat the fighter; a comic stomp may use
an extra leg sample. Require a declared purpose, readable differentiation and
consistent identity. An unexplained solid third arm in an ordinary pose fails.
Do not invent a stylization exception after generation to excuse a defect.

Track physical lighting separately from presentation. Compare environmental
sources, occlusion, cast-shadow direction and local event spill. Allow a planned
subjective red field or warm vow emphasis without adding a lamp to the floor plan.
A temporary attack flash may end while damage persists. Histogram similarity is
not a sufficient test of lighting continuity.

Speech ownership is a hard narrative gate even before typesetting. In a listener
close-up with an offscreen voice, the visible face is not necessarily the speaker.
A portrait cannot receive a literal speech tail unless the script gives it a
voice. Evaluate reference binding, acting and later tail ownership together.

## Compare neighbors and the full sequence

Review three views of continuity: current panel against canon, adjacent panels
against one another, and the complete scene against its beat/state plan. This
catches different errors. Two adjacent panels may match each other while both
misrepresent the original sheet; two individually accurate panels may still
contradict each other in gesture, action direction or timing.

For each transition ask what changed, what stayed fixed, why the cut occurred
and what the reader now knows. Check active and inactive cast, costume variants,
held and dropped props, wounds, dirt, environmental damage and movement causes.
A person absent from a crop may remain in the scene. A partial cleanup should not
reset every injury or erase the emotional consequence.

For action, trace preparation, force path, contact or near miss, reaction,
recovery and resulting state where those beats are needed. Verify who was the
intended target and who actually received contact. Check that speed marks,
cloth trails, debris and impact bursts support the same event. A shot may omit
contact deliberately, but the next result must make the intended causality clear.

For beats that depend on motion, use the [action-panel reading test](drawing-motion.md#read-the-result-and-repair-it).
Write down the movement and outcome you can infer from the unlettered art
before comparing them with the planned beat. Record the visible evidence under
the existing narrative, space, anatomy, style or composition gate. Repeat at
the placed crop and intended page or phone size.

For a changed location, use the [environmental impact reading test](environmental-impact.md#pass-the-decisions-into-production). Check the footprint against a familiar measure, then compare the settling debris and lasting damage across views.

For dialogue, follow speaker/addressee changes and compare balloon order with the
script ledger. Check silence, interruption, overlapping speech, nested thought,
remote sources and repeated occurrences. Do a silent art pass to test visual
acting, then a text pass to check source fidelity. Neither substitutes for the
combined reading experience.

Use a complete contact overview for style drift and scene rhythm, then read pages
at their intended display/print size or scroll at the target viewport. Review
windows across file joins. A contact sheet cannot reproduce scroll reveal timing.
Cohn's empty-panel study found reading strategies beyond a simple Z path; it
supports testing the actual layout rather than assuming order from coordinates.
It does not prove how every completed page will be read. [Navigating Comics](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00186/full),
2013, accessed 2026-11-20.

## Repair through a bounded adaptive loop

Set a per-panel repair allowance and stopping conditions from the current budget,
time constraints and available controls. For example, allow two targeted repair
attempts before revisiting the packet or composition. This is a strategy-change
threshold, not permission to accept a failing result or a universal generation
limit. Existing authorization governs whether further calls are available.

| Failure pattern | Next useful action | Required preservation |
|---|---|---|
| One local defect | Supported edit/mask with exact discrepancy and crop | Identity, pose, light and unaffected pixels |
| Wrong identity or merged cast | Rebind original references; simplify simultaneous constraints | Correct canonical actor and role |
| Geography or action is confused | Revise blocking/pose thumbnail and visible instructions | Story event, target, world positions and consequence |
| Repeated costume/style drift | Recheck original anchor, reference roles and active variant | Approved identity and project treatment |
| Persistent lettering/crop collision | Revise provisional frame, camera or reserved zone | Exact words and indispensable gesture/face |
| Tool cannot express required control | Use an available supported workflow or explicit handoff | Requirement and honest completion status |

After each candidate, record the defect, hypothesized cause, changed instruction
or input, result and observed regressions. Do not repeat an identical request
indefinitely. A more elaborate prompt is not always an improvement; conflicting
references, wrong source scope or an impossible crop need structural correction.

Review the repaired region at native size and the whole image at reading size.
Recheck all hard gates, with special attention to collateral changes. A repaired
hand with a different face still fails. Refresh adjacent parity if the pose,
expression, crop, light or style changed. Reuse intact evidence for untouched
assets instead of restarting the entire chapter without a reason.

If a critical defect remains after the strategy budget, keep the panel in staging
and identify the precise blocker. Request only the missing input or decision, or
continue independent panels. Never lower identity, attribution or story fidelity
to fit the tool output. No prompt structure, generation count or reviewer can
promise zero mistakes; acceptance means the required checks passed on the recorded
version, within the disclosed inspection scope.

## Record evidence and separate machine scope

If a panel has no depicted character, identity, acting and anatomy may each
use `{"status":"not_applicable","reason":"..."}` with a reason specific to the
shot. Narrative, space, style and composition still require review and a pass.

For accepted art, record `status: "accepted"`, `art`, `qa.art_sha256`,
`qa.dependency_sha256`, `qa.reviewer`, `qa.evidence`, and `qa.checks`. Evidence should
identify the reference hashes, compared neighbors, inspected views/crops and
concrete observations. Reviewer identity can be an agent/session identifier; do
not imply independent human approval if none occurred.

For each reviewed candidate, record the actual panel and version, reference ID,
crop coordinates when useful, the feature compared, and what was observed.
Compare against the relevant adjacent panel and record any unresolved difference.
Keep failed versions and repairs in the project history.

Run recorded consistency and file checks after relevant changes:

```sh
python scripts/mangaka.py validate story/project.json --files
```

| The helper can check recorded data | It cannot establish from the pixels |
|---|---|
| Stable IDs, links, declared reference roles and hashes | A face actually matches its sheet |
| Active dialogue coverage and declared speaker membership | A balloon visibly points to the right person |
| Explicit state transitions and some projected screen order | Plausible anatomy, occlusion, contact or readable action |
| Declared representation/provenance values | Whether an account is true or a stylization succeeds |
| Required pass labels, evidence presence and dependency freshness | Whether a reviewer inspected honestly or judged correctly |
| Accepted art bytes match the recorded hash | The image is narratively or aesthetically successful |

A validator pass reports consistency only. A hash confirms the reviewed version
has not changed; it does not certify quality. Source-span reconstruction, loose
prop semantics, nested speech, complex occlusion and final typography need the
appropriate downstream checks or manual review. Automated vision can flag likely
problems, but no similarity threshold should override an observed wrong identity.

## Review the assembled page or scroll

Place accepted art with uniform scaling and exact masks, then inspect the actual
composite. Frames, clip paths, borders and approved breakouts must remain separate
from untouched masters. CELSYS documents that frame folders mask drawing outside
the frame, illustrating why correct art can still lose meaning through its
container. [Frames and Panels](https://help.clip-studio.com/en-us/manual_en/540_comic/Frames_and_Panels.htm),
accessed 2026-11-20. See [compositing](compositing.md) for this helper's contract.

Check masked faces, essential hands, impact contacts, plot clues, edge tangencies,
intentional border crossings and layer order. Confirm that page assembly used the
accepted hashes and that no accidental resampling or stretching altered likeness.
If the source composition cannot survive its allocated shape, revise the layout
or panel; do not cover the failure with a balloon.

Apply a separate page/lettering review record. Its gates include exact text and
source-span reconstruction, speaker ownership, semantic balloon style, tail path,
reading order, glyph shaping, padding, overlap, transparency, export size and joins.
Panel `qa.checks` alone does not certify these assembly properties.

Inspect each balloon against the project grammar and rendered context. A rounded
shape may convey threat through fill and type; a burst-like edge may be thought.
A short tail may be valid if its implied continuation identifies the correct
speaker. Blambot's guidance explicitly describes that implied mouth direction and
a tail ending partway to the head. [Comic Book Grammar and Tradition](https://blambot.com/pages/comic-book-grammar-tradition),
accessed 2026-11-20. Competing plausible owners still require repair.

Compare rendered words with the exact source ledger, including punctuation and
emphasis. OCR can assist but must not silently rewrite the source or certify
complex fonts. Read mixed scripts and bidirectional text in the final export.
Verify transparent overlays over both light and dark backgrounds; check real
alpha, fringes, intended translucent fills and unwanted opaque rectangles.

## Deliver and retain a resumable audit trail

Deliver accepted panel masters, editable assembly, reading exports, transparent
lettering, the active canon/script manifests, prompts and review records. State
how many panels and pages passed, what was visually inspected, what was checked
only by machine, and any remaining blocked items. A tested synthetic fixture or
one successful sample is not evidence that an entire generated chapter passed.

Reopen acceptance whenever art bytes, canon, script, direction or dependencies
change. Keep old versions and review evidence, mark downstream items stale, and
recheck the affected sequence and composites. See [intake and canon](intake-and-canon.md)
for revision propagation and provider-job recovery. Finish with the reviewed
result and its actual limits, not a promise that future generations cannot fail.
