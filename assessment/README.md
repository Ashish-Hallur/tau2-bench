# User simulator review

The [final two-page PDF](user-simulator-review.pdf) and [editable source](REPORT.md) diagnose two limitations and propose a
small experiment. This is an experimental fork, not a claim of improved official
benchmark performance. The implementation, tests and evidence accompany the report in this fork.

## Provenance

- Fork: https://github.com/Ashish-Hallur/tau2-bench
- Implementation base: `cc1df47baa1544a34bb8c8e5c4ca72ad223b96a2`
- Public run's recorded commit: `c60471675690a1f26cdb8419dbb7ed2142f149d1`
- [Public trajectory JSON](https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/gpt-5-2_sierra_2026-02-26/trajectories/gpt-5.2_high_telecom_gpt-5.2_4trials.json)
- SHA256: `8c33f26a3032182d39a12511db9d45a2cbd9aa5c33d99a462cc23c836eb95176`
- 114 tasks, 456 simulations, four trials; gpt-5.2 agent (high reasoning),
  gpt-5.2 simulator (low reasoning), seed 300. Public run dated February 26, 2026.
- [Paper](https://arxiv.org/abs/2506.07982) describes an earlier version.
  Historical evidence is not a rerun on the current implementation base.
- Review date: October 24, 2026. Selection: screened every 39th simulation
  (12 candidates), then examined the two cited cases in detail. This is a
  mechanism-focused selection, not a prevalence estimate or exhaustive audit.

## Reproduce the evidence

Download the linked JSON, then run:

```powershell
python -X utf8 assessment/extract_evidence.py PATH_TO_DOWNLOADED_JSON
```

[Case A](evidence-A.md) contains both wrong-state inversions and a control:
turns 50-53 check that Wi-Fi calling is already off and do not toggle it.
[Case B](evidence-B.md) contains the unrequested mobile-data repair and an
action-history discrepancy. Neither recorded reward establishes the causal
effect of the simulator behavior on task success.

## Implementation and verification

Implementation and evidence commit: `be114023b4de76f70400cc0505db133b170e1d5e`.
The PDF links to this immutable evidence snapshot.
Repository-wide Ruff lint and formatting checks passed before publication;
GNU Make was unavailable on Windows, so its checks were run directly.
The format check verified all 658 Python files without rewriting them.

`src/tau2/domains/telecom/user_tools.py`: optional `enabled` argument on
`toggle_roaming` and `toggle_wifi`. Explicit target states are idempotent;
omission/null preserves legacy inversion. Changed states use existing mutation
helpers. Tool descriptions expose the intended use to the simulator.

`tests/test_domains/test_telecom/test_requested_setting.py`: 18 offline cases
including state combinations, retries, legacy behavior, Wi-Fi disconnection,
airplane-mode restrictions, provider permission separation, schema export and
actual environment dispatch.

```powershell
$env:LITELLM_LOCAL_MODEL_COST_MAP = 'True'
python -X utf8 -m pytest tests/test_domains/test_telecom -q
ruff check src/tau2/domains/telecom/user_tools.py tests/test_domains/test_telecom/test_requested_setting.py assessment/extract_evidence.py
ruff format --check src/tau2/domains/telecom/user_tools.py tests/test_domains/test_telecom/test_requested_setting.py assessment/extract_evidence.py
```

Observed: 70 telecom tests passed, including 18 new cases. Two warnings concern
upstream audioop deprecation and an unrecognized pytest asyncio option.
On Windows, `-X utf8` is necessary because existing policy loading otherwise
uses the system encoding and fails before environment tests reach the patch.
No LLM experiment, paid calls, or full benchmark run was performed. No claim
is made about adoption of the new parameter, human fidelity, or reward uplift.
Task data, evaluator and agent tool definitions are unchanged. The shared user
tool schema also affects other modes exposing these tools; only telecom offline
tests were validated here. The patch does not prevent unrequested repairs.

AI assistance: Codex assisted with evidence extraction, analysis, implementation,
tests and drafting. Source turns were checked against the downloaded artifact;
The author reviewed the argument and final wording.
