"""Extract auditable cases from the public submission; no model calls.

Usage: python assessment/extract_evidence.py PATH_TO_DOWNLOADED_JSON
Download URL and expected digest are in assessment/README.md.
"""

import hashlib
import json
import sys
from pathlib import Path

EXPECTED_SHA256 = "8c33f26a3032182d39a12511db9d45a2cbd9aa5c33d99a462cc23c836eb95176"
CASES = {
    "A": "17959bc5-43ff-4e42-8cd3-5899e244f3cf",
    "B": "d49a1fb1-72a1-44d5-92b3-9f18524c7bb3",
}


def main():
    source = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(source).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Source digest differs from the reviewed public artifact")
    data = json.loads(source)
    out = Path(__file__).resolve().parent
    for label, sid in CASES.items():
        sim = next(s for s in data["simulations"] if s["id"] == sid)
        task = next(t for t in data["tasks"] if t["id"] == sim["task_id"])
        lines = [
            f"# Evidence {label}",
            "",
            f"Simulation: `{sid}`",
            f"Task: `{task['id']}`",
            "",
            "Original zero-based turn_idx; tool calls/responses count as turns.",
            "Task and scoring are copied in full. Messages omit provider metadata,",
            "costs and duplicated raw responses; content and tool calls are unchanged.",
            "",
            "## Task",
            "```json",
            json.dumps(task, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Recorded scoring",
            "```json",
            json.dumps(sim["reward_info"], indent=2, ensure_ascii=False),
            "```",
        ]
        for message in sim["messages"]:
            lines += [
                "",
                f"## Turn {message['turn_idx']} - {message['role']}",
                "",
            ]
            if message.get("requestor"):
                lines.append(f"Requestor: {message['requestor']}")
            if message.get("content"):
                lines.append(message["content"])
            if message.get("tool_calls"):
                lines += [
                    "```json",
                    json.dumps(message["tool_calls"], indent=2, ensure_ascii=False),
                    "```",
                ]
        (out / f"evidence-{label}.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    print(f"Verified source; extracted {len(CASES)} full conversation cases.")


if __name__ == "__main__":
    main()
