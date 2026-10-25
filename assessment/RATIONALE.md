# Agreed rationale and open experimental questions

Discussion captured October 25, 2026. These are design arguments and hypotheses,
not results from a model experiment. The submission report condenses this record.

## Action precision and persona

The simulator-facing Wi-Fi and roaming interface previously exposed inversion
without an explicit target argument. Internal setup helpers are not equivalent
to tools available to the simulator. Adding an optional target allows deliberate
action selection while retaining existing no-argument and null toggle calls.

The LLM still interprets the agent's instruction and chooses an action. It can
misunderstand, select the wrong target, omit a step, ask questions or use a bare
toggle. Whether a mistake is deliberate role-play or accidental does not change
the fact that the revised interface permits mistakes. We cannot infer intent
from the trace alone.

Our position is that reliable execution of the chosen action does not itself
make a Hard customer unrealistically competent. We hypothesize a limited effect
on persona fidelity; we do not claim its magnitude has been measured. Retaining
possible mistakes does not guarantee unchanged error frequencies.

## Internal comparison versus explicit inspection

An explicit target call compares current and requested state inside Python to
avoid an unnecessary inversion. This is implementation of the requested action,
not autonomous diagnosis or selection of the correct target. The LLM can still
use read-only tools to inspect state first and then decide whether to act.
The result reports the resulting or already-matching setting, as appropriate.

## Scope within the pipeline

The two tool schemas/descriptions and their execution logic change. General
persona instructions, orchestrator, task definitions and evaluator do not.
Different chosen actions can nevertheless change later states, dialogue and
scores. We distinguish narrow code scope from potentially meaningful downstream
effects. The existing tests establish mechanics, not model adoption or fidelity.

## Experiment discussion still to finalize

Proposed cases are constructed tests, not additional observed public failures:

- Already-correct state: preserve it.
- Opposite state: perform the necessary change.
- Repeated instruction: do not undo progress.
- Explicit OFF-then-ON reset: execute both transitions, not just the endpoint.
- Ambiguous instruction: seek clarification rather than invent a target.
- Status question: inspect and report, without an unrequested repair.
- Blocked change: retain the existing environment restriction.

The priority empirical question is whether explicit targets reduce accidental
inversions while preserving genuine procedures, appropriate clarification and
the agent's responsibility to direct repairs. Autonomous repair is a control,
not a limitation this patch claims to fix. No new experiment runner or paid
model runs have been authorized by this discussion; the current report contains
a proposed design that we will review together before further implementation.
