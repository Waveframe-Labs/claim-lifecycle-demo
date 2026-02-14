"""
---
title: "Claim lifecycle demo runner"
filetype: "operational"
type: "non-normative"
domain: "case-study"
version: "0.2.0"
doi: "TBD-0.2.0"
status: "Active"
created: "2026-02-06"
updated: "2026-02-13"
author:
  name: "Shawn C. Wright"
  email: "swright@waveframelabs.org"
  orcid: "https://orcid.org/0009-0006-6043-9295"
maintainer:
  name: "Waveframe Labs"
  url: "https://waveframelabs.org"
license: "Apache-2.0"
copyright:
  holder: "Waveframe Labs"
  year: "2026"
ai_assisted: "partial"
ai_assistance_details: "AI-assisted integration of CRI-CORE enforcement gating into the claim lifecycle demo runner while preserving lifecycle semantics as the demo's responsibility."
dependencies:
  - "../claims/claim-001.yaml"
  - "../rules/transition-rules.yaml"
  - "../transitions/transition-log.json"
  - "../evidence/ev-001-proposed.yaml"
  - "../evidence/ev-002-supported.yaml"
  - "../evidence/ev-003-contradicted.yaml"
  - "../evidence/ev-004-superseded.yaml"
anchors:
  - "CLAIM-DEMO-RUNNER-v0.2.0"
---
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


ROOT = Path(__file__).resolve().parent.parent

CLAIM_PATH = ROOT / "claims" / "claim-001.yaml"
RULES_PATH = ROOT / "rules" / "transition-rules.yaml"
LOG_PATH = ROOT / "transitions" / "transition-log.json"

EVIDENCE_PATHS = [
    ROOT / "evidence" / "ev-001-proposed.yaml",
    ROOT / "evidence" / "ev-002-supported.yaml",
    ROOT / "evidence" / "ev-003-contradicted.yaml",
    ROOT / "evidence" / "ev-004-superseded.yaml",
]


# --- CRI-CORE integration helpers ------------------------------------------------

CRI_CORE_CONTRACT_VERSION = "0.1.0"

RUNS_ROOT = ROOT / "demo_runner" / "runs"


def _utc_now_iso() -> str:
    """Returns current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _ensure_cricore_importable() -> None:
    """
    Ensures CRI-CORE is importable from the local environment.

    Default assumption:
      <demo_root_parent> / CRI-CORE / src

    Override via environment variable:
      CRICORE_SRC=/path/to/CRI-CORE/src
    """
    env_src = os.environ.get("CRICORE_SRC")
    if env_src:
        candidate = Path(env_src).expanduser().resolve()
    else:
        candidate = (ROOT.parent / "CRI-CORE" / "src").resolve()

    if not candidate.exists() or not candidate.is_dir():
        raise RuntimeError(
            "CRI-CORE src path not found.\n"
            f"Looked for: {candidate}\n"
            "Set CRICORE_SRC to the CRI-CORE /src folder if needed."
        )

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _new_run_id(prefix: str = "DEMO-RUN") -> str:
    """Generates a unique run ID based on timestamp."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    micros = datetime.now(timezone.utc).strftime("%f")
    return f"{prefix}-{stamp}-{micros}"


def _materialize_minimal_cricore_run(
    *,
    run_id: str,
    proposal: Dict[str, Any],
    run_dir: Path,
    orchestrator_id: str,
    reviewer_id: str,
    self_approval_override: bool = False,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Creates a structurally valid CRI-CORE run directory.
    
    Adheres to CRI-CORE paths.py requirements (REQUIRED_FILES + REQUIRED_DIRECTORIES).
    
    Note:
    - SHA256SUMS.txt is a placeholder; cryptographic verification is not enforced 
      in this demo stage.
    - approval.json is generated, though semantic ordering (approval after validation)
      is not enforced here.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "validation").mkdir(parents=True, exist_ok=True)

    created_utc = _utc_now_iso()

    # contract.json (Required)
    _write_json(
        run_dir / "contract.json",
        {
            "contract_version": CRI_CORE_CONTRACT_VERSION,
            "run_id": run_id,
            "created_utc": created_utc,
        },
    )

    # report.md (Required)
    report_lines = [
        "# Demo Run Report",
        "",
        f"- run_id: `{run_id}`",
        f"- created_utc: `{created_utc}`",
        "",
        "## Proposal",
        "```json",
        json.dumps(proposal, indent=2),
        "```",
        "",
        "## Notes",
        "- This run directory is produced by the claim lifecycle demo as a client of CRI-CORE.",
        "- It exists to demonstrate a real run artifact contract surface and enforcement gate.",
        "",
    ]
    _write_text(run_dir / "report.md", "\n".join(report_lines))

    # randomness.json (Required)
    _write_json(
        run_dir / "randomness.json",
        {
            "run_id": run_id,
            "deterministic": True,
            "seed": None,
        },
    )

    # approval.json (Required)
    _write_json(
        run_dir / "approval.json",
        {
            "run_id": run_id,
            "approver": {"id": reviewer_id, "type": "human"},
            "approved_at_utc": _utc_now_iso(),
            "context_ref": "demo-runner",
        },
    )

    # SHA256SUMS.txt (Required)
    # Placeholder manifest.
    _write_text(
        run_dir / "SHA256SUMS.txt",
        "# Placeholder manifest (demo)\n# SHA verification is not enforced in CRI-CORE integrity stage yet.\n",
    )

    # validation outputs (Directory required)
    _write_json(
        run_dir / "validation" / "invariant_results.json",
        {
            "run_id": run_id,
            "generated_at_utc": _utc_now_iso(),
            "notes": "Demo-produced placeholder invariant outputs; structural presence only.",
        },
    )

    # run_context (Passed to CRI-CORE stages)
    run_context = {
        "identities": {
            "orchestrator": {"id": orchestrator_id, "type": "human"},
            "reviewer": {"id": reviewer_id, "type": "human"},
            "self_approval_override": bool(self_approval_override),
        },
        "integrity": {
            "workflow_execution_ref": f"demo://{run_id}",
            "run_payload_ref": f"demo://{run_id}/payload",
            "attestation_ref": f"demo://{run_id}/attestation",
        },
        "publication": {
            "repository_ref": "demo://claim-lifecycle-demo",
            "commit_ref": "uncommitted-local-run",
        },
        "proposal": proposal,
    }

    return run_dir, run_context


def _cricore_decide(run_dir: Path, run_context: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Executes the CRI-CORE enforcement pipeline.
    
    Returns:
      (allowed: bool, messages: List[str])
    """
    _ensure_cricore_importable()

    # Import only after sys.path is set.
    from cricore.enforcement.execution import run_enforcement_pipeline  # type: ignore

    results = run_enforcement_pipeline(
        str(run_dir),
        expected_contract_version=CRI_CORE_CONTRACT_VERSION,
        run_context=run_context,
    )

    allowed = all(r.passed for r in results)

    # Flatten stage messages for reporting.
    messages: List[str] = []
    for r in results:
        if not r.passed:
            messages.append(f"{r.stage_id}: FAILED")
            for m in r.messages:
                messages.append(f"  - {m}")
        else:
            messages.append(f"{r.stage_id}: OK")

    return allowed, messages


# --- Demo domain helpers ---------------------------------------------------------

def load_yaml_with_front_matter(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No metadata block found in {path}")
    body = parts[2]
    return yaml.safe_load(body)


def load_transition_log() -> List[Dict[str, Any]]:
    text = LOG_PATH.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    body = parts[2]
    return json.loads(body)


def write_transition_log(entries: List[Dict[str, Any]]) -> None:
    header, _, rest = LOG_PATH.read_text(encoding="utf-8").partition("---\n")
    _, _, after = rest.partition("---\n")

    new_body = json.dumps(entries, indent=2)

    content = f"{header}---\n{after.split('---', 1)[0]}---\n{new_body}"
    LOG_PATH.write_text(content, encoding="utf-8")


def transition_allowed(rules: Dict[str, Any], from_state: str, to_state: str) -> bool:
    for rule in rules["allowed_transitions"]:
        if rule["from"] == from_state and rule["to"] == to_state:
            return True
    return False


# --- Main -----------------------------------------------------------------------

def main() -> None:
    claim = load_yaml_with_front_matter(CLAIM_PATH)
    rules = load_yaml_with_front_matter(RULES_PATH)
    log = load_transition_log()

    current_state = claim["current_state"]

    print(f"Initial claim state: {current_state}")

    RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    # Flag to ensure we only force a denial once (during 'supported' -> 'contradicted').
    injected_deny_used = False

    for ev_path in EVIDENCE_PATHS:
        evidence = load_yaml_with_front_matter(ev_path)

        intended = evidence["intended_transition"]
        from_state = intended["from"]
        to_state = intended["to"]

        # Only attempt a governed transition if it matches the current state.
        if from_state != current_state:
            print(f"[SKIP] {evidence['evidence_id']} does not match current state")
            continue

        if not transition_allowed(rules, from_state, to_state):
            print(f"[REJECT] Transition {from_state} -> {to_state} not allowed by rules")
            continue

        # Build proposal object
        proposal = {
            "type": "claim_transition",
            "claim_id": evidence["claim_id"],
            "evidence_id": evidence["evidence_id"],
            "from": from_state,
            "to": to_state,
        }

        # Configuration for attempts:
        # Tuple format: (orchestrator_id, reviewer_id, self_approval_override)
        attempt_contexts: List[Tuple[str, str, bool]] = []

        # Logic to demonstrate gating:
        # Force a failure on the "supported" -> "contradicted" transition by using
        # the same identity for orchestrator and reviewer without override.
        if (
            evidence.get("evidence_id") == "ev-003-contradicted"
            and not injected_deny_used
        ):
            # Attempt 1: Fail (Self-approval violation)
            attempt_contexts.append(("alice", "alice", False))
            # Attempt 2: Pass (Valid reviewer)
            attempt_contexts.append(("alice", "bob", False))
            injected_deny_used = True
        else:
            # Default: Valid transition
            attempt_contexts.append(("alice", "bob", False))

        for attempt_idx, (orch, reviewer, override) in enumerate(attempt_contexts, start=1):
            run_id = _new_run_id()
            run_dir = RUNS_ROOT / run_id

            _, run_context = _materialize_minimal_cricore_run(
                run_id=run_id,
                proposal=proposal,
                run_dir=run_dir,
                orchestrator_id=orch,
                reviewer_id=reviewer,
                self_approval_override=override,
            )

            allowed, messages = _cricore_decide(run_dir, run_context)

            if not allowed:
                print(f"[DENY] {from_state} -> {to_state} via {evidence['evidence_id']} (attempt {attempt_idx})")
                for line in messages:
                    if line.endswith("FAILED") or line.startswith("  - "):
                        print(f"        {line}")
                continue

            # Transition allowed
            entry = {
                "timestamp": _utc_now_iso(),
                "claim_id": evidence["claim_id"],
                "evidence_id": evidence["evidence_id"],
                "from": from_state,
                "to": to_state,
                "cricore_run_id": run_id,
            }

            log.append(entry)
            current_state = to_state

            print(f"[OK] {from_state} -> {to_state} via {evidence['evidence_id']} (run {run_id})")
            break 

    write_transition_log(log)

    print("\nFinal claim state:", current_state)


if __name__ == "__main__":
    main()
