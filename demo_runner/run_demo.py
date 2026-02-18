"""
---
title: "Claim lifecycle demo runner"
filetype: "operational"
type: "non-normative"
domain: "case-study"
version: "0.3.0"
doi: "TBD-0.3.0"
status: "Active"
created: "2026-02-06"
updated: "2026-02-17"

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
ai_assistance_details: "AI-assisted integration of proposal artifacts and deterministic proposal hashing into the claim lifecycle demo runner while preserving lifecycle semantics as the demo's responsibility."

dependencies:
  - "../proposals/proposal-001.yaml"
  - "../claims/claim-001.yaml"
  - "../rules/transition-rules.yaml"
  - "../transitions/transition-log.json"
  - "../evidence/ev-001-proposed.yaml"
  - "../evidence/ev-002-supported.yaml"
  - "../evidence/ev-003-contradicted.yaml"
  - "../evidence/ev-004-superseded.yaml"

anchors:
  - "CLAIM-DEMO-RUNNER-v0.3.0"
---
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple

import yaml


ROOT = Path(__file__).resolve().parent.parent

CLAIM_PATH = ROOT / "claims" / "claim-001.yaml"
RULES_PATH = ROOT / "rules" / "transition-rules.yaml"
LOG_PATH = ROOT / "transitions" / "transition-log.json"

REJECTIONS_LOG_PATH = ROOT / "transitions" / "rejections-log.json"

PROPOSALS_PATHS = [
    ROOT / "proposals" / "proposal-001.yaml",
]

EVIDENCE_DIR = ROOT / "evidence"

# --- CRI-CORE integration helpers ------------------------------------------------

# IMPORTANT:
# This is the CRI-CORE run contract version (structure gate), not the demo repo version.
CRI_CORE_CONTRACT_VERSION = "0.1.0"

RUNS_ROOT = ROOT / "demo_runner" / "runs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _purge_cricore_modules() -> None:
    """
    Prevents Python from reusing a previously imported cricore module from a
    different path (site-packages, an old editable install, etc.).
    """
    to_delete = [name for name in sys.modules.keys() if name == "cricore" or name.startswith("cricore.")]
    for name in to_delete:
        del sys.modules[name]


def _ensure_cricore_importable() -> None:
    """
    Ensures CRI-CORE is importable from the local environment.

    Default assumption:
        <this_repo_parent>/CRI-CORE/src

    Override via environment variable:
      CRICORE_SRC=/path/to/CRI-CORE/src
    """
    env_src = os.environ.get("CRICORE_SRC")
    if env_src:
        candidate = Path(env_src).expanduser().resolve()
    else:
        candidate = (ROOT.parent / "CRI-CORE" / "src").resolve()

    pkg_root = candidate / "cricore"
    if not candidate.exists() or not candidate.is_dir() or not pkg_root.exists() or not pkg_root.is_dir():
        raise RuntimeError(
            "CRI-CORE src path not found or missing package folder.\n"
            f"Looked for src: {candidate}\n"
            f"Expected package: {pkg_root}\n"
            "Set CRICORE_SRC to the CRI-CORE /src folder if needed."
        )

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

    _purge_cricore_modules()


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _new_run_id(prefix: str = "DEMO-RUN") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    micros = datetime.now(timezone.utc).strftime("%f")
    return f"{prefix}-{stamp}-{micros}"


def _stable_json_dumps(obj: Any) -> str:
    """
    Deterministic JSON encoding for hashing.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _proposal_hash(proposal_obj: Mapping[str, Any]) -> str:
    """
    Hash the proposal content deterministically.
    """
    return _sha256_hex(_stable_json_dumps(proposal_obj))


def _materialize_minimal_cricore_run(
    *,
    run_id: str,
    proposal: Dict[str, Any],
    proposal_hash: str,
    run_dir: Path,
    orchestrator_id: str,
    reviewer_id: str,
    self_approval_override: bool = False,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Creates a structurally valid CRI-CORE run directory.

    Notes:
      - SHA256SUMS.txt is present; if CRI-CORE treats presence as strict, this must
        be a valid manifest for files it lists. In this demo, the manifest is left
        empty/comment-only so it does not assert coverage.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "validation").mkdir(parents=True, exist_ok=True)

    created_utc = _utc_now_iso()

    _write_json(
        run_dir / "contract.json",
        {
            "contract_version": CRI_CORE_CONTRACT_VERSION,
            "run_id": run_id,
            "created_utc": created_utc,
        },
    )

    report_lines = [
        "# Demo Run Report",
        "",
        f"- run_id: `{run_id}`",
        f"- created_utc: `{created_utc}`",
        f"- contract_version: `{CRI_CORE_CONTRACT_VERSION}`",
        f"- proposal_hash: `{proposal_hash}`",
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

    _write_json(
        run_dir / "randomness.json",
        {
            "run_id": run_id,
            "deterministic": True,
            "seed": None,
        },
    )

    _write_json(
        run_dir / "approval.json",
        {
            "run_id": run_id,
            "approver": {"id": reviewer_id, "type": "human"},
            "approved_at_utc": _utc_now_iso(),
            "context_ref": "demo-runner",
        },
    )

    # IMPORTANT:
    # Leave the manifest comment-only so it doesn't claim coverage of any files.
    _write_text(
        run_dir / "SHA256SUMS.txt",
        "# Demo manifest intentionally contains no asserted file hashes.\n"
        "# This keeps the demo focused on transition gating + authority boundaries.\n"
    )

    _write_json(
        run_dir / "validation" / "invariant_results.json",
        {
            "run_id": run_id,
            "generated_at_utc": _utc_now_iso(),
            "notes": "Demo-produced placeholder invariant outputs; structural presence only.",
        },
    )

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


def _cricore_decide(run_dir: Path, run_context: Dict[str, Any]) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
    """
    Executes the CRI-CORE enforcement pipeline.

    Returns:
      (allowed: bool, messages: List[str], results_raw: List[StageResult-like dicts])
    """
    _ensure_cricore_importable()

    from cricore.enforcement.execution import run_enforcement_pipeline  # type: ignore

    results = run_enforcement_pipeline(
        str(run_dir),
        expected_contract_version=CRI_CORE_CONTRACT_VERSION,
        run_context=run_context,
    )

    allowed = all(r.passed for r in results)

    messages: List[str] = []
    raw: List[Dict[str, Any]] = []

    for r in results:
        raw.append(
            {
                "stage_id": r.stage_id,
                "passed": bool(r.passed),
                "failure_classes": [str(fc) for fc in getattr(r, "failure_classes", [])],
                "messages": list(getattr(r, "messages", [])),
                "checked_at_utc": getattr(r, "checked_at_utc", None),
                "engine_version": getattr(r, "engine_version", None),
            }
        )

        if not r.passed:
            messages.append(f"{r.stage_id}: FAILED")
            for m in r.messages:
                messages.append(f"  - {m}")
        else:
            messages.append(f"{r.stage_id}: OK")

    return allowed, messages, raw


# --- Demo domain helpers ---------------------------------------------------------

def load_yaml_with_front_matter(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No metadata block found in {path}")
    body = parts[2]
    return yaml.safe_load(body)


def _load_log_json_with_front_matter(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    body = parts[2]
    return json.loads(body)


def _write_log_json_with_front_matter(path: Path, entries: List[Dict[str, Any]]) -> None:
    if not path.exists():
        # create minimal header if missing
        header = (
            "---\n"
            "title: \"Transition Log\"\n"
            "filetype: \"operational\"\n"
            "type: \"non-normative\"\n"
            "domain: \"case-study\"\n"
            "version: \"0.1.0\"\n"
            "status: \"Active\"\n"
            "created: \"2026-02-17\"\n"
            "updated: \"2026-02-17\"\n"
            "license: \"Apache-2.0\"\n"
            "---\n"
        )
        path.write_text(header + json.dumps(entries, indent=2), encoding="utf-8")
        return

    header, _, rest = path.read_text(encoding="utf-8").partition("---\n")
    _, _, after = rest.partition("---\n")

    new_body = json.dumps(entries, indent=2)
    content = f"{header}---\n{after.split('---', 1)[0]}---\n{new_body}"
    path.write_text(content, encoding="utf-8")


def transition_allowed(rules: Dict[str, Any], from_state: str, to_state: str) -> bool:
    for rule in rules["allowed_transitions"]:
        if rule["from"] == from_state and rule["to"] == to_state:
            return True
    return False


def _load_evidence_by_id(evidence_id: str) -> Dict[str, Any]:
    path = EVIDENCE_DIR / f"{evidence_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Evidence file not found for {evidence_id}: {path}")
    return load_yaml_with_front_matter(path)


# --- Main -----------------------------------------------------------------------

def main() -> None:
    claim = load_yaml_with_front_matter(CLAIM_PATH)
    rules = load_yaml_with_front_matter(RULES_PATH)

    transition_log = _load_log_json_with_front_matter(LOG_PATH)
    rejection_log = _load_log_json_with_front_matter(REJECTIONS_LOG_PATH)

    current_state = claim["current_state"]
    print(f"Initial claim state: {current_state}")
    print("Loaded claim object:", claim) 

    RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    # One explicit rejection case: keep your existing deny injection, but now we
    # record a rejection artifact entry too (without mutating claim state).
    injected_deny_used = False

    for proposal_path in PROPOSALS_PATHS:
        proposal_doc = load_yaml_with_front_matter(proposal_path)

        transitions = proposal_doc.get("transitions", [])
        if not isinstance(transitions, list) or not transitions:
            raise ValueError(f"Proposal has no transitions list: {proposal_path}")

        for t in transitions:
            evidence_id = t.get("evidence_id")
            from_state = t.get("from")
            to_state = t.get("to")

            if not isinstance(evidence_id, str) or not isinstance(from_state, str) or not isinstance(to_state, str):
                raise ValueError(f"Invalid transition entry in proposal: {t}")

            evidence = _load_evidence_by_id(evidence_id)

            # Enforce that proposal and evidence agree on the intended transition.
            intended = evidence["intended_transition"]
            if intended["from"] != from_state or intended["to"] != to_state:
                raise ValueError(
                    f"Proposal/evidence mismatch for {evidence_id}: "
                    f"proposal {from_state}->{to_state} vs evidence {intended['from']}->{intended['to']}"
                )

            if from_state != current_state:
                print(f"[SKIP] {evidence_id} does not match current state (current={current_state})")
                continue

            if not transition_allowed(rules, from_state, to_state):
                print(f"[REJECT] Transition {from_state} -> {to_state} not allowed by rules")
                continue

            # Proposal object (atomic binding surface)
            proposal_obj: Dict[str, Any] = {
                "proposal_id": proposal_doc.get("proposal_id", "unknown-proposal"),
                "type": "claim_transition",
                "claim_id": evidence["claim_id"],
                "evidence_id": evidence_id,
                "from": from_state,
                "to": to_state,
                "contract_version": proposal_doc.get("contract_version", CRI_CORE_CONTRACT_VERSION),
                "authority_requirements": proposal_doc.get("authority_requirements", []),
            }

            p_hash = _proposal_hash(proposal_obj)

            attempt_contexts: List[Tuple[str, str, bool]] = []

            # Preserve your demo denial injection
            if evidence_id == "ev-003-contradicted" and not injected_deny_used:
                attempt_contexts.append(("alice", "alice", False))  # deny (self-approval)
                attempt_contexts.append(("alice", "bob", False))    # allow
                injected_deny_used = True
            else:
                attempt_contexts.append(("alice", "bob", False))

            for attempt_idx, (orch, reviewer, override) in enumerate(attempt_contexts, start=1):
                run_id = _new_run_id()
                run_dir = RUNS_ROOT / run_id

                _, run_context = _materialize_minimal_cricore_run(
                    run_id=run_id,
                    proposal=proposal_obj,
                    proposal_hash=p_hash,
                    run_dir=run_dir,
                    orchestrator_id=orch,
                    reviewer_id=reviewer,
                    self_approval_override=override,
                )

                allowed, messages, results_raw = _cricore_decide(run_dir, run_context)

                if not allowed:
                    print(f"[DENY] {from_state} -> {to_state} via {evidence_id} (attempt {attempt_idx})")
                    for line in messages:
                        if line.endswith("FAILED") or line.startswith("  - "):
                            print(f"        {line}")

                    # Optional but recommended: rejection record (no mutation)
                    rejection_log.append(
                        {
                            "timestamp": _utc_now_iso(),
                            "proposal_id": proposal_obj["proposal_id"],
                            "proposal_hash": p_hash,
                            "claim_id": evidence["claim_id"],
                            "evidence_id": evidence_id,
                            "from": from_state,
                            "to": to_state,
                            "contract_version": proposal_obj["contract_version"],
                            "cricore_run_id": run_id,
                            "authority_bindings": {
                                "orchestrator": orch,
                                "reviewer": reviewer,
                                "self_approval_override": bool(override),
                            },
                            "cricore_results": results_raw,
                        }
                    )
                    continue

                # Allowed: append immutable transition record
                entry = {
                    "timestamp": _utc_now_iso(),
                    "proposal_id": proposal_obj["proposal_id"],
                    "proposal_hash": p_hash,
                    "contract_version": proposal_obj["contract_version"],
                    "claim_id": evidence["claim_id"],
                    "evidence_id": evidence_id,
                    "from": from_state,
                    "to": to_state,
                    "cricore_run_id": run_id,
                    "authority_bindings": {
                        "orchestrator": orch,
                        "reviewer": reviewer,
                        "self_approval_override": bool(override),
                    },
                }

                transition_log.append(entry)
                current_state = to_state

                print(f"[OK] {from_state} -> {to_state} via {evidence_id} (run {run_id})")
                break

    _write_log_json_with_front_matter(LOG_PATH, transition_log)
    _write_log_json_with_front_matter(REJECTIONS_LOG_PATH, rejection_log)
    print("\nFinal claim state:", current_state)


if __name__ == "__main__":
    main()
