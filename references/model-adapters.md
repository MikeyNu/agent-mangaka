# Image generation adapters and reference packets

## Contents

1. Discover the actual capability
2. Reference roles and prompt structure
3. Native image tool
4. Other providers and connector differences
5. Repair and escalation
6. Job recovery and evidence

## Discover the actual capability

Before generation, inspect the live tool schema, model documentation and
available reference mechanisms. Record provider, model identifier if exposed,
operation, supported sizes, reference limits, edit support, alpha support,
input/output formats, and applicable cost or entitlement. Recheck changing
capabilities rather than treating a saved example as a current API contract.

Use the user's chosen provider where it supports the task. If a requested
feature is unavailable, explain the specific gap and use an authorized
alternative when appropriate. Do not silently switch from final artwork to
prompt-only delivery when image generation is available.

The skill does not install an image backend, supply credentials, promise free
jobs, or infer API entitlement from a website plan. A website Unlimited button
and a connector's credit-based generation can use different entitlement paths.
Inspect the live quote and existing authorization before a paid submission.
Do not probe access by repeatedly submitting chargeable jobs.

## Reference roles and prompt structure

Maintain one canonical reference package per identity and environment. For
each panel, select the views that support its camera and action. Always include
the original identity anchors when practical. A preceding generated panel is
useful for local continuity, but must not become the only identity authority.

| Role | Supplies | Must not silently supply |
|---|---|---|
| Character sheet | Face, silhouette, asymmetry, costume | Another character's identity |
| Environment design | Architecture, palette, landmark relationships | An unrelated scene's layout |
| Blocking diagram | Position, orientation, camera, sightline | Final linework, labels or map symbols |
| Pose thumbnail | Gesture, contact and silhouette | Costume or face changes |
| Style anchor | Ink, color, edge, shading treatment | Setting, plot or cast |
| Accepted adjacent panel | Local continuity and visible condition | Corrections to original canon |
| Balloon sample | Approved lettering grammar | Text to paint into panel art |

Do not overload a provider's reference limit. Prioritize named identity and
required environment, then simplify the shot or prepare a clearly labelled
reference board using authorized assets. A crowded board can reduce usable
facial detail. Inspect the actual images the provider will receive, not only
their filenames. Use native views/crops for analysis; artistic alteration of a
reference must use the appropriate image-editing capability and remain a
derived asset.

### Panel packet template

```text
DELIVERABLE
One unlettered panel, target aspect ratio and useful resolution.

REFERENCE ROLES
Image 1: canonical character C_A, use its front and three-quarter face.
Image 2: canonical character C_B, use the rear costume.
Image 3: environment E_ROOM, preserve the door/window relationship.
Image 4: top-down blocking only, do not reproduce labels or diagram style.

NARRATIVE MOMENT
Who is doing what to whom, selected action phase, listener and story purpose.

IDENTITY AND STATE LOCKS
Visible identifying traits, anatomical asymmetries, current clothes,
injuries, held objects and relevant conditions.

SPACE AND CAMERA
World relationships, camera position/height and intended framing translated
into visible depth, screen order, eyelines and background landmarks.

ACTING AND ACTION
Inner emotion, displayed expression, social intention, gesture,
support/balance, contact and gaze target.

DRAWING AND LIGHT
Project ink, palette, shadows, edge treatment, perspective and motivated
exaggeration. Distinguish event or expressive treatment from normal light.

COMPOSITION AND LETTERING RESERVE
Critical readable face/hand/prop, crop safety and intentionally quiet space.

EXCLUSIONS
No lettering, balloons, borders, unrelated people, identity mixing or
specific known artifact. Add only the exclusions relevant to this shot.

ACCEPTANCE TARGETS
The few visible facts that must be checked before this candidate advances.
```

The compiler returns exact dialogue separately in `lettering_only`. Translate
delivery into acting instructions rather than asking the model to reproduce
the line. Keep exact text in the source ledger for deterministic typesetting.
An individual provider request may contain the acting context, but it must
not ask for lettering inside the art.

Positive physical instructions are usually clearer than long contradictory
negative lists. For instance, specify one extended left arm with its elbow,
wrist, hand and object relationship. Add a focused exclusion for an observed
extra-arm failure. More words are not a guarantee of better control. Resolve
contradictions and reduce the shot's simultaneous demands when needed.

## Native image tool

The available native tool in the development session exposed `prompt`,
`transparent_background`, and two mutually exclusive reference routes:
`referenced_image_paths` or `num_last_images_to_include`.

Use local image paths when every target reference is available locally. Inspect
unseen local images before editing. Use the smallest supported recent-image
count only when a required image has no local path. Do not provide both routes.
For new images without references, omit both. Re-read the live tool contract
if these capabilities change.

Set true transparency explicitly for an overlay or cutout. A checkerboard
painted into RGB pixels is not alpha. Verify channel mode and inspect on both
light and dark backgrounds. The page compositor creates deterministic RGBA
lettering without asking the image model to paint exact dialogue.

No model version was exposed by this native tool during the development trial.
Record that fact; do not invent a model identity from visual quality. The live
trial used canonical references plus a scene diagram, rejected one attractive
candidate for incorrect camera height, and generated a focused repair before
using it as an adjacent reference. See the evaluation report for actual scope.

Native tools may display and save images automatically. Follow their delivery
contract and avoid duplicate uploads or invented output URLs. Keep the original
artifact and its generation metadata for the project when authorized.

## Other providers and connector differences

Official provider guidance is useful, but the actual connector may expose a
smaller or differently named parameter set. Never copy raw API fields into an
unrelated tool without checking its schema.

| Adapter | Verified guidance or session observation | Operational consequence |
|---|---|---|
| OpenAI image API | Supports generation/edit workflows and reference images; documented limitations include consistency and precise composition | Use canonical references and iterative visual review; do not promise perfect identity |
| OpenAI generative edits | An edit mask can guide rather than exactly constrain the result | Use deterministic clipping or an approved edit composite when pixel-exact boundaries are required |
| Native session image tool | Local-path or recent-image references; alpha flag; no explicit negative-prompt field | State relevant exclusions in prose; do not invent mask/seed/negative fields |
| Higgsfield connected tool | Session metadata for `gpt_image_2_6` and `gpt_image_2_6_flare` exposed image references mapped through `params.medias`; no dedicated mask or negative field was declared | Re-discover model and operation, map reference roles explicitly, use supported parameters only |
| Gemini image workflows | Official guidance emphasizes clear subject, context, style and iterative editing | Preserve reference roles and focused refinements; check current model reference limits |
| Google Imagen | Dedicated negative prompting is model-dependent; official docs describe its removal in newer versions beginning with `imagen-3.0-generate-002` | Never assume a universal `negative_prompt` field |

The Higgsfield names above are dated observations from 20 November 2026, not
hard-coded recommendations or a future availability promise. Some connector
output modes can support vector files while disallowing references; choosing
such a mode would defeat identity-bound panel production. Inspect the full
operation's constraints, not just its advertised file extension.

Primary sources, checked 20 November 2026:

- [OpenAI image generation](https://developers.openai.com/api/docs/guides/image-generation)
- [OpenAI image prompting](https://developers.openai.com/api/docs/guides/image-prompting)
- [Gemini image generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini image prompt guide](https://deepmind.google/models/gemini-image/prompt-guide/)
- [Google's image prompting examples](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/)
- [Imagen negative-prompt availability](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/omit-content-using-a-negative-prompt)

## Repair and escalation

Classify the discrepancy before editing: identity, geometry, acting, anatomy,
style, content omission, artifact, or lettering-space failure. Repair the
smallest coherent area that can fix it. Keep the original accepted master,
candidate versions, prompt changes and reference order.

A repair instruction should name the current defect, target result and
preservation locks. Reinspect the repaired region, face, silhouette, important
asymmetries and adjacent-panel parity. An improved hand with an altered face
does not pass. A repair can create a new defect outside its intended region.

After two unsuccessful repairs of the same material defect, reassess the cause
before another call. This is an escalation checkpoint, not a universal retry
limit or permission to accept a failure. Improve the reference view, reduce
occlusion, supply a clearer pose sketch, separate action phases, adjust framing
with story intent preserved, or use an authorized capable editor/provider.
Keep within the user's budget and task scope. If the required result remains
unachievable, deliver the exact blocker and reviewable candidate evidence.

Do not weaken the acceptance requirements after seeing an attractive wrong
image. A deliberate creative change must be justified in the plan and reflected
in downstream continuity, layout and review, not hidden as a successful repair.

## Job recovery and evidence

Before submission, save the request identifier if available, prompt, ordered
references and hashes, model/schema snapshot, cost quote and authorization
scope. Record returned job IDs and status. Poll an existing job using its
documented status method. A timeout or truncated response is not evidence that
the job failed; recover it before submitting a duplicate.

After download, verify that the file exists, decodes, has expected dimensions
and transparency, and belongs to the expected job. Technical validity is only
the first check. Open the image and perform the visual review before acceptance.
Store actual output hashes and pass/repair reasons. Resume from that checkpoint
rather than regenerating completed approved panels.
