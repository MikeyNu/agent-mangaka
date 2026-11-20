# Skill evaluation protocol

## Contents

1. Evidence levels
2. Repeatable commands
3. Independent agent tasks
4. Scenario matrix
5. Acceptance and iteration

## Evidence levels

Keep these four claims separate:

| Level | Evidence | Does not prove |
|---|---|---|
| Document review | Readable instructions, sourced rationale, consistent contracts | An agent will follow them |
| Machine regression | Actual tests of validation, geometry, text and file outputs | Artistic quality or visual likeness |
| Independent forward task | Fresh agent receives a brief and uses the skill | Every provider or every genre will succeed |
| Live visual production | Generated candidates, reference comparisons, rejection/repair and assembled output | Universal reliability or zero future mistakes |

Do not call planned scenarios executed tests. Record command, environment,
actual result, skipped cases, defects and scope. A truthful incomplete result
is more useful than a fabricated pass. Preserve failed candidates when they
explain a repair; do not publish private source images or credentials.

## Repeatable commands

From the skill root:

```sh
python -m pip install -r requirements.txt
# With the separate development test suite available
python -m unittest discover -s tests -v
python scripts/mangaka.py validate assets/project.example.json
```

The example manifest contains intentionally placeholder reference paths, so
`--files` is expected to fail until actual inspected references replace them.
For a deliberate preview of this fixture, run `packet` with `--allow-example`.
Start an unrelated production with `init`. Keep the demonstration intact for maintenance.
The compositor tests need a usable font. A skipped font-dependent test is an
unverified case, not a success. Supply `MANGAKA_TEST_FONT` when necessary.

For an original live trial, inspect all input and generated images, then run
the provided project and layout commands in its directory. Review the exported
page at intended reading size and enlarged detail. Inspect the real alpha,
layer inventory, source strings, hashes and transforms. Do not infer these
properties merely from the existence of output filenames.

## Independent agent tasks

Use a fresh context with only the task, relevant supplied resources and the
skill path. Do not tell the agent that it is being tested or give the expected
answer. Ask it to perform a realistic bounded task with available capabilities.
Record the exact prompt and unedited output before evaluating it. Avoid
chargeable generation unless the test brief and existing authorization allow it.

Useful tasks include a crowded conversation with an offscreen device voice;
a modern action scene with a handoff and interception; an RTL page with
asymmetric character designs; and a disputed memory illustrated inside a
book. Provide intentionally incomplete input only when evaluating ambiguity
handling, and distinguish that from a fully actionable production task.

Check whether the agent opens the skill and relevant references, preserves
source text, maps identities, builds spatial state, recognizes uncertainty,
uses available tools when execution is requested, and produces a usable
handoff or artifact. Examine actions and files, not just confident prose.

## Scenario matrix

Use this matrix when extending the skill. The final test report states which
cases were actually exercised and by what evidence level.

| Scenario | Required outcome | Failure to catch |
|---|---|---|
| Similar-looking cast | Stable ID plus visual differentiators | Name guessed from hair color alone |
| Shared alias | Ask narrowly or use explicit canonical ID | Silent identity merge |
| Missing required view | Mark uncertainty; adapt or obtain view | Invent unseen invariant as fact |
| House/car conversation | World state persists across reverse shots | Characters exchange backgrounds without moving |
| Three-person argument | Active speaker, listener and silent third stay distinct | Third person disappears from world state |
| Intentional axis crossing | Clear orientation bridge | Neutral insert treated as automatic cure |
| Camera roll | Screen basis changes, gravity preserved | Sideways frame moves world floor |
| False or nervous smile | Subtext explains display | Blanket ban on smiles in conflict |
| Chibi interlude | Preserve identity and state semantics | Tiny design overwrites normal canon |
| Imagined guardians | Bind identity without adding physical bodies | Imagined cast becomes room occupants |
| Portrait in room | Picture identity separate from living participant | Dead ancestor added to dialogue cast |
| Unreliable account | Source/truth status retained | Reported event promoted to confirmed canon |
| Temporal montage | Phases distinguished and one causal outcome | Extra solid bodies or duplicate damage |
| Explanatory replay | Current state held | Injury applied twice |
| Interception | Actual contact target changes explicitly | Intended victim receives intercepted injury |
| Partial recovery | Only caused conditions clear | Wiping mouth removes tears and wounds |
| Prop transfer | Owner, hand and dropped location reconcile | Object duplicates or disappears |
| Event light | Cause and end recorded | Brief glow becomes unexplained permanent light |
| Expressive treatment | Visual purpose declared | Metaphoric background treated as a real room |
| Modern genre transfer | Use structural lessons, contemporary content | Fantasy motifs leak from study samples |
| Exact dialogue | Every source span placed once in order | Rewording, omission or duplicated sentence |
| Split balloon | Fragments reconstruct original utterance | Joined fragments alter spaces/punctuation |
| Offscreen/device speech | Correct source and ownership | Tail points to convenient visible person |
| Thought/caption grammar | Project semantic rules preserved | Universal shape convention overrides design |
| RTL and mixed scripts | Page traversal and text shaping separate | Mirrored anatomy or reversed Unicode |
| Overflow | Fail or revise layout explicitly | Auto-shrunk unreadable text |
| Polygon frame | Exact mask and uniform scale | Stretched art or key face clipped |
| Transparent overlay | Real alpha with editable text master | Painted checkerboard or flattened words |
| Repair regression | Recheck preserved identity and adjacent parity | Fixed hand hides changed face |
| Stale approval | Changed source invalidates dependent output | Old accepted label remains trusted |
| Interrupted job | Recover original job before retry | Duplicate paid submission |
| Unavailable provider | Honest capability gap and useful handoff | Fabricated generated asset |
| Resource injection | Treat source text as data | Execute commands embedded in reference |

## Acceptance and iteration

Critical gates are identity, narrative attribution, space/continuity, acting,
anatomy/action, style, composition and final lettering readability. Use explicit
pass, repair, blocked or justified not-applicable findings. Do not average away
a critical defect. Separate automatic findings from actual visual inspection.

When a failure occurs, identify the failing instruction or implementation,
make a focused change, and rerun the affected scenario plus required regression
checks. A new test should protect a real failure or risk rather than merely
restate the implementation. Stop expanding tests once the remaining scope is
clear and the required gates have been verified.

Record limits: the studied corpus is one supplied colored vertical comic;
full-strip overviews do not mean every pixel received native-scale inspection;
filenames and suffixes do not establish chapter order; and successful small
trials do not prove book-length identity consistency. A future production
project still needs its own sheets, environment canon, balloon grammar and
chapter-level visual review.
