# Spatial planning and continuity

## Contents

1. Coordinate contract
2. Scene blocking before camera selection
3. Camera projection and orientation
4. Causal state and choreography
5. Nonliteral images and narrative time
6. Lighting and atmosphere
7. Helper commands and limits

## Coordinate contract

Keep four different systems explicit:

| System | Meaning | Example |
|---|---|---|
| World | Stable scene locations | Two subjects on opposite sides of the interaction axis |
| Camera/screen | Positions projected into one panel | The nearer subject projects to screen-left from this angle |
| Anatomy | The character's own left and right | An identifying mark stays on the same anatomical side |
| Reading | Intended traversal of panels and text | Traversal follows the reading direction chosen for this project |

Never mirror a canonical image simply to reverse page flow. A mirrored scar,
watch, sword hand, hair part, or costume closure changes identity. Redraw the
view from the correct camera and inspect anatomical asymmetries separately.

The bundled planning helper uses X east, Y north, Z height, with default world
up `[0,0,1]`. Choose an approximate unit and keep it consistent. For a crowded
interior, record room dimensions, floor levels, furniture footprints, door
hinges and swing, windows, and fixed landmarks in the project notes. A top-down
point map alone cannot prove a camera has an unobstructed sightline.

## Scene blocking before camera selection

Read the scene's complete action and dialogue first. Establish:

1. Every physical participant, including quiet listeners and offscreen people.
2. Fixed landmarks, walkable surfaces, entrances, cover and occluders.
3. Important objects, their owner or location, orientation, and condition.
4. Current poses, facing, spacing, height differences, and eyeline targets.
5. Environmental lights and any temporary source caused by the action.
6. An initial interaction axis and the major paths of movement.

Draw a top-down diagram and, when heights matter, a small side elevation.
Show the camera and target for each planned shot. These are construction aids
for 2D drawing, not a requirement to build or render a 3D scene. Keep diagrams
simple enough that the image model cannot confuse their labels or map symbols
with final artwork.

For a conversation, decide who is trying to change whose mind and where the
listener's attention goes. For a fight, establish the starting distance, reach,
support feet, obstacles, target and escape route. Blocking should support the
story, rather than making characters stand in an arbitrary symmetrical row.

### Check a reverse view

Fix two subjects in world space and choose a landmark that the current story
places beyond one of them. Project the first camera view, then move the camera
for the reverse. Check which subject and landmark are visible from the new
angle. Keep world positions fixed unless the script describes movement.

Write those visible relationships into the generation packet. Numeric
coordinates are a planning record, not a precise conditioning language that
an image model is guaranteed to follow. Compare the generated view to both
the map and the intended perspective. A beautiful eye-level shot fails a
required high-angle establishing view.

## Camera projection and orientation

For each panel, choose the dramatic purpose before the lens metaphor. Record
camera position, target, height, roll, shot size, visible landmarks, and the
important depth relationships. Add approximate field of view or lens language
only when useful to describe framing. Perspective depends on viewpoint; focal
length affects field of view. Moving the camera while changing focal length
can change perspective, but a lens number alone does not specify the scene.
[Fujifilm's explanation](https://www.fujifilm-x.com/en-gb/learning-centre/understanding-lens-compression/)
supports this distinction.

The helper computes a perspective ordering from position, target and up vector.
It checks whether recorded `screen_order` agrees with projected visible
participants. It does not compute a complete optical camera, exact framing,
occlusion, lens distortion, drawing perspective, or face orientation. Use a
thumbnail and visual inspection for those requirements.

The 180-degree convention is a useful orientation aid, not a ban on creative
camera movement. Crossing the interaction line can reverse apparent screen
positions. Plan a visible movement, a new establishing view, or another clear
orientation cue, and record `orientation_bridge` explaining it. A neutral
on-axis insert does not automatically explain a reversal in the next shot.
[Columbia's film glossary](https://filmglossary.ccnmtl.columbia.edu/term/180-degree-rule/)
describes the convention and its orientation purpose.

For groups, choose the active conversational pair or a stable scene axis.
When the conversational center changes, re-establish it. A scene supplies the
default axis; an optional `panel.axis` overrides it for that panel and is used
by validation and map output. A changed effective axis needs an explicit
`orientation_bridge`. Repeat the intended override on subsequent panels or
the scene default applies again. Use a linked new scene for an actual change
of place or timeline, carrying forward relevant state. Do not falsify positions
to satisfy the checker.

Use `camera.roll_degrees` for a tilted or sideways composition. The helper
rotates its screen basis; it does not alter world gravity. Optional scene
`gravity` records a world vector. If a story genuinely changes gravity, state
the cause and depict consequences. A sideways page tableau is not sufficient
evidence that a character is walking on a wall.

## Causal state and choreography

Each scene has a full `initial_state`. Each panel records a complete state
snapshot for all tracked actors, even those cropped out. Changes require an
explicit before, after and cause. Track position, facing, costume, held
objects and injuries. Add project-specific facts such as wetness, tears,
dirt, blood, fatigue and costume damage where they affect continuity.

Movement must be explainable between panels. A cut can omit intermediate
steps when the result remains understandable; it cannot secretly move a
listener across a road merely to improve a background. The cause can refer
to a visible beat or an explicitly planned offscreen interval.

Plan an action chain using a table such as:

| Beat | Actor and action | Target/contact | Persistent consequence |
|---|---|---|---|
| Prepare | A shifts weight to rear leg | Gaze at B's right shoulder | No impact yet |
| Commit | A extends right arm | Intended target B | Weight and reach change |
| Intercept | C catches A's wrist | Actual contact C's left hand | B remains unharmed |
| Recover | A withdraws, C releases | Grip visibly ends | Wrist soreness may remain |

Choose readable instants from this chain. Do not require four panels for
every movement. An anticipation pose, a clear contact image and a reaction
may be enough. Conversely, a confusing interception needs an additional
spatial cue even if the script uses one short sentence.

Separate an object's canonical identity from its changing owner and condition.
The helper checks recorded actor-state differences, but it does not provide a
complete prop-ownership physics engine. Maintain a supplementary prop ledger
and inspect handoffs, dropped objects, weapon direction and contact geometry.
Include that ledger's revision/hash in project metadata to invalidate affected
approvals when it changes.

Cleaning the mouth does not remove an unrelated wound. Dropping a weapon does
not delete it from the environment. An impact flash does not heal a character.
Reconcile consequences before starting the next panel.

## Nonliteral images and narrative time

Use explicit representation scope instead of blanket rules against repeated
bodies or exaggerated anatomy.

| Mode | Physical-state behavior | Required distinction |
|---|---|---|
| `normal` | May advance with declared changes | One physical body per actor |
| `chibi` | May advance if literally occurring | Preserve identity; explain stylization |
| `temporal_montage` | May advance through causal action | Distinguish successive phases from extra people |
| `replay` | Holds the current scene state | Do not apply the same injury or transfer again |
| `imagined` | Holds the current scene state | Imagined figure is not a new room occupant |
| `portrait` | Holds the current scene state | Depiction in a picture is not a physical actor |
| `symbolic` | Holds the current scene state | Metaphor is not literal geography |

`participants` names physical visible characters. `represented_characters`
binds additional identities shown in pictures, memories or symbolic images.
`instances` identifies declared physical, temporal, imagined or portrait
instances. All visible identities still require their original references.
Use a linked scene/timeline for a fully enacted flashback with its own state;
do not mutate the present scene while drawing the past.

An arm echo can show motion if it is visibly differentiated and planned.
An unexplained solid third arm fails anatomy. A temporary miniature face can
express embarrassment while preserving recognizability. Its proportions must
not overwrite the normal design sheet.

Source authority is independent of visual vividness. Use
`narrative_provenance` with a source kind, source ID and truth status when an
account is reported, contested, unreliable, imagined or unknown. A convincing
historical illustration inside a book can remain a disputed account. Do not
promote it into confirmed canon simply because the image looks realistic.

## Lighting and atmosphere

Record environmental light direction and quality. Use visible cues such as
lit cheek, cast shadow, rim light and illuminated floor to maintain continuity.
If the camera reverses, screen-left illumination can change while the world
light remains fixed. Do not preserve a screen-side highlight at the expense
of physical scene lighting.

Separate `environmental`, `event`, and `expressive` light domains. Event light
needs a cause such as a flashlight switching on. Expressive treatment needs a
purpose, such as isolating a vow or panic beat; it need not create a persistent
lamp in the room. Annotate the return to ordinary treatment. The checker
validates declared categories and required explanations, not rendered shadows.

## Helper commands and limits

```sh
python scripts/mangaka.py validate project.json --files
python scripts/mangaka.py map project.json P1 --out work/P1-map.svg
python scripts/mangaka.py map project.json P1 --out work/P1-map.png
python scripts/mangaka.py packet project.json P1 --out work/P1-packet.json
```

Keep the map, plan and final pixels in the same review. A passing JSON check
proves consistency of recorded data only. It cannot certify the actual
background, anatomy, height, pose, likeness, staging or drawing quality.
