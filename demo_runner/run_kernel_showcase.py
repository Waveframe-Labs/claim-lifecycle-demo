"""
---
title: "Kernel enforcement showcase runner"
filetype: "operational"
type: "non-normative"
domain: "case-study"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-02-18"
updated: "2026-02-18"

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
ai_assistance_details: "AI-assisted implementation of a CRI-CORE kernel enforcement showcase runner that demonstrates two blocked→fixed cycles (authority + integrity) with commit gated by publication-commit."

dependencies:
  - "./runs/*"
  - "../claims/claim-001.yaml"
  - "../rules/transition-rules.yaml"
  - "../transitions/transition-log.json"
  - "../transitions/rejections-log.json"
  - "../proposals/proposal-001.yaml"
  - "../evidence/ev-001-proposed.yaml"
  - "../evidence/ev-002-supported.yaml"
  - "../evidence/ev-003-contradicted.yaml"
  - "../evidence/ev-004-superseded.yaml"

anchors:
  - "KERNEL-ENFORCEMENT-SHOWCASE-v0.1.0"
---
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

import yaml


ROOT = Path(__file__).resolve().parent.parent

RUNS_ROOT = ROOT / "demo_runner" / "runs"

CLAIM_PATH = ROOT / "claims" / "claim-001.yaml"
RULES_PATH = ROOT / "rules" / "transition-rules.yaml"

TRANSITION_LOG_PATH = ROOT / "transitions" / "transition-log.json"
REJECTIONS_LOG_PATH = ROOT / "transitions" / "rejections-log.json"

PROPOSAL_001_PATH = ROOT / "proposals" / "proposal-001.yaml"
EVIDENCE_DIR = ROOT / "evidence"


# IMPORTANT:
# This is the CRI-CORE run contract version (structure gate), not the demo repo version.
CRI_CORE_CONTRACT_VERSION = "0.1.0"


# -----------------------------------------------------------------------------
# Time / serialization
# -----------------------------------------------------------------------------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_json_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _proposal_hash(proposal_obj: Mapping[str, Any]) -> str:
    return _sha256_hex(_stable_json_dumps(proposal_obj))


def _new_run_id(prefix: str = "SHOWCASE-RUN") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    micros = datetime.now(timezone.utc).strftime("%f")
    return f"{prefix}-{stamp}-{micros}"


# -----------------------------------------------------------------------------
# Front-matter loaders
# -----------------------------------------------------------------------------

def _load_yaml_with_front_matter(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No metadata block found in {path}")
    body = parts[2]
    obj = yaml.safe_load(body)
    if not isinstance(obj, dict):
        raise ValueError(f"YAML body is not a mapping in {path}")
    return obj


def _load_json_log_with_front_matter(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return json.loads(text)
    return json.loads(parts[2])


def _write_json_log_with_front_matter(path: Path, entries: List[Dict[str, Any]]) -> None:
    if not path.exists():
        header = (
            "---\n"
            "title: \"Log\"\n"
            "filetype: \"operational\"\n"
            "type: \"non-normative\"\n"
            "domain: \"case-study\"\n"
            "version: \"0.1.0\"\n"
            "status: \"Active\"\n"
            f"created: \"{datetime.now(timezone.utc).date().isoformat()}\"\n"
            f"updated: \"{datetime.now(timezone.utc).date().isoformat()}\"\n"
            "license: \"Apache-2.0\"\n"
            "---\n"
        )
        path.write_text(header + json.dumps(entries, indent=2), encoding="utf-8")
        return

    text = path.read_text(encoding="utf-8")
    head, _, rest = text.partition("---\n")
    _, _, after = rest.partition("---\n")
    meta_block = after.split("---", 1)[0]
    content = f"{head}---\n{meta_block}---\n{json.dumps(entries, indent=2)}"
    path.write_text(content, encoding="utf-8")


# -----------------------------------------------------------------------------
# CRI-CORE import isolation
# -----------------------------------------------------------------------------

def _purge_cricore_modules() -> None:
    to_delete = [n for n in list(sys.modules.keys()) if n == "cricore" or n.startswith("cricore.")]
    for n in to_delete:
        del sys.modules[n]


def _ensure_cricore_importable() -> None:
    """
    Set via PowerShell:
      $env:CRICORE_SRC="C:\\GitHub\\CRI-CORE\\src"
    """
    env_src = os.environ.get("CRICORE_SRC")
    if not env_src:
        raise RuntimeError("CRICORE_SRC is not set. Point it to your CRI-CORE /src directory.")

    candidate = Path(env_src).expanduser().resolve()
    pkg_root = candidate / "cricore"

    if not candidate.exists() or not candidate.is_dir():
        raise RuntimeError(f"CRICORE_SRC does not exist or is not a directory: {candidate}")
    if not pkg_root.exists() or not pkg_root.is_dir():
        raise RuntimeError(f"CRI-CORE package folder not found under: {pkg_root}")

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

    _purge_cricore_modules()


# -----------------------------------------------------------------------------
# Filesystem helpers
# -----------------------------------------------------------------------------

def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_sha256sums(run_dir: Path, rel_paths: List[str]) -> None:
    """
    Write a real SHA256SUMS.txt with at least one asserted entry.
    """
    lines: List[str] = []
    for rel in rel_paths:
        p = run_dir / rel
        digest = _compute_sha256(p)
        lines.append(f"{digest}  {rel}")
    _write_text(run_dir / "SHA256SUMS.txt", "\n".join(lines) + "\n")


# -----------------------------------------------------------------------------
# CRI-CORE run materialization
# -----------------------------------------------------------------------------

def _materialize_run(
    *,
    run_id: str,
    run_dir: Path,
    proposal_obj: Dict[str, Any],
    proposal_hash: str,
    orchestrator_id: str,
    reviewer_id: str,
) -> Dict[str, Any]:
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

    report_text = "\n".join(
        [
            "# Kernel Showcase Run Report",
            "",
            f"- run_id: `{run_id}`",
            f"- created_utc: `{created_utc}`",
            f"- contract_version: `{CRI_CORE_CONTRACT_VERSION}`",
            f"- proposal_hash: `{proposal_hash}`",
            "",
            "## Proposal",
            "```json",
            json.dumps(proposal_obj, indent=2),
            "```",
            "",
        ]
    )
    _write_text(run_dir / "report.md", report_text)

    _write_json(
        run_dir / "randomness.json",
        {"run_id": run_id, "deterministic": True, "seed": None},
    )

    _write_json(
        run_dir / "approval.json",
        {
            "run_id": run_id,
            "approver": {"id": reviewer_id, "type": "human"},
            "approved_at_utc": _utc_now_iso(),
            "context_ref": "kernel-showcase",
        },
    )

    _write_json(
        run_dir / "validation" / "invariant_results.json",
        {
            "run_id": run_id,
            "generated_at_utc": _utc_now_iso(),
            "notes": "placeholder invariant outputs (showcase)",
        },
    )

    # Write an asserted manifest (so we can force a mismatch by tampering later)
    _write_sha256sums(run_dir, ["report.md"])

    run_context: Dict[str, Any] = {
        "identities": {
            "orchestrator": {"id": orchestrator_id, "type": "human"},
            "reviewer": {"id": reviewer_id, "type": "human"},
            "self_approval_override": False,
        },
        "integrity": {
            "workflow_execution_ref": f"showcase://{run_id}",
            "run_payload_ref": f"showcase://{run_id}/payload",
            "attestation_ref": f"showcase://{run_id}/attestation",
        },
        "publication": {
            "repository_ref": "demo://claim-lifecycle-demo",
            "commit_ref": "showcase-local",
        },
        "proposal": proposal_obj,
    }

    return run_context


def _cricore_results(run_dir: Path, run_context: Dict[str, Any]) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
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
            }
        )

        if r.passed:
            messages.append(f"{r.stage_id}: OK")
        else:
            messages.append(f"{r.stage_id}: FAILED")
            for m in r.messages:
                messages.append(f"  - {m}")

    return allowed, messages, raw


def _publication_commit_passed(results_raw: List[Dict[str, Any]]) -> bool:
    for r in results_raw:
        if r.get("stage_id") == "publication-commit":
            return bool(r.get("passed"))
    return False


# -----------------------------------------------------------------------------
# Proposal selection (we use the same demo artifacts)
# -----------------------------------------------------------------------------

def _load_transition_from_proposal(
    *,
    evidence_id: str,
) -> Tuple[Dict[str, Any], str, str]:
    proposal_doc = _load_yaml_with_front_matter(PROPOSAL_001_PATH)
    transitions = proposal_doc.get("transitions", [])
    if not isinstance(transitions, list):
        raise ValueError("proposal-001.yaml transitions is not a list")

    for t in transitions:
        if not isinstance(t, dict):
            continue
        if t.get("evidence_id") == evidence_id:
            from_state = t.get("from")
            to_state = t.get("to")
            if not isinstance(from_state, str) or not isinstance(to_state, str):
                raise ValueError(f"proposal transition from/to must be strings for evidence_id={evidence_id}")
            return proposal_doc, from_state, to_state

    raise ValueError(f"proposal-001.yaml has no transition entry for evidence_id={evidence_id}")


def _load_evidence(evidence_id: str) -> Dict[str, Any]:
    p = EVIDENCE_DIR / f"{evidence_id}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"Evidence file not found: {p}")
    return _load_yaml_with_front_matter(p)


# -----------------------------------------------------------------------------
# Showcase flows
# -----------------------------------------------------------------------------

def _attempt(
    *,
    label: str,
    proposal_obj: Dict[str, Any],
    orchestrator: str,
    reviewer: str,
    tamper_report_after_hash: bool,
    expected_to_pass: bool,
    transition_log: List[Dict[str, Any]],
    rejection_log: List[Dict[str, Any]],
) -> None:
    run_id = _new_run_id()
    run_dir = RUNS_ROOT / run_id

    p_hash = _proposal_hash(proposal_obj)

    run_context = _materialize_run(
        run_id=run_id,
        run_dir=run_dir,
        proposal_obj=proposal_obj,
        proposal_hash=p_hash,
        orchestrator_id=orchestrator,
        reviewer_id=reviewer,
    )

    # Force integrity failure by changing a hashed file after SHA256SUMS is written
    if tamper_report_after_hash:
        report_path = run_dir / "report.md"
        report_path.write_text(report_path.read_text(encoding="utf-8") + "\nTAMPER\n", encoding="utf-8")

    allowed, messages, results_raw = _cricore_results(run_dir, run_context)

    print(f"\n== {label} ==")
    for line in messages:
        if line.endswith("FAILED") or line.startswith("  - ") or line.endswith("OK"):
            print(line)

    commit_ok = _publication_commit_passed(results_raw)

    if expected_to_pass:
        if not (allowed and commit_ok):
            raise RuntimeError(f"{label} expected PASS but kernel denied or commit not allowed (run_id={run_id})")
        transition_log.append(
            {
                "timestamp": _utc_now_iso(),
                "proposal_id": proposal_obj.get("proposal_id"),
                "proposal_hash": p_hash,
                "contract_version": proposal_obj.get("contract_version"),
                "claim_id": proposal_obj.get("claim_id"),
                "evidence_id": proposal_obj.get("evidence_id"),
                "from": proposal_obj.get("from"),
                "to": proposal_obj.get("to"),
                "cricore_run_id": run_id,
                "kernel_commit_allowed": True,
            }
        )
        print(f"COMMIT: allowed (run_id={run_id})")
    else:
        if allowed and commit_ok:
            raise RuntimeError(f"{label} expected FAIL but kernel allowed commit (run_id={run_id})")
        rejection_log.append(
            {
                "timestamp": _utc_now_iso(),
                "proposal_id": proposal_obj.get("proposal_id"),
                "proposal_hash": p_hash,
                "contract_version": proposal_obj.get("contract_version"),
                "claim_id": proposal_obj.get("claim_id"),
                "evidence_id": proposal_obj.get("evidence_id"),
                "from": proposal_obj.get("from"),
                "to": proposal_obj.get("to"),
                "cricore_run_id": run_id,
                "kernel_commit_allowed": False,
                "cricore_results": results_raw,
            }
        )
        print(f"COMMIT: blocked (run_id={run_id})")


def main() -> None:
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    claim = _load_yaml_with_front_matter(CLAIM_PATH)
    print("Kernel enforcement showcase")
    print("Current claim state:", claim.get("current_state"))

    transition_log = _load_json_log_with_front_matter(TRANSITION_LOG_PATH)
    rejection_log = _load_json_log_with_front_matter(REJECTIONS_LOG_PATH)

    # We'll use the SAME transition target each cycle for showcase simplicity:
    # evidence_id="ev-003-contradicted" is good because we already know self-approval triggers independence failure.
    evidence_id = "ev-003-contradicted"

    proposal_doc, from_state, to_state = _load_transition_from_proposal(evidence_id=evidence_id)
    evidence = _load_evidence(evidence_id)

    intended = evidence.get("intended_transition", {})
    if intended.get("from") != from_state or intended.get("to") != to_state:
        raise ValueError(
            f"proposal/evidence mismatch for {evidence_id}: "
            f"proposal {from_state}->{to_state} vs evidence {intended.get('from')}->{intended.get('to')}"
        )

    proposal_obj: Dict[str, Any] = {
        "proposal_id": proposal_doc.get("proposal_id", "proposal-001"),
        "type": "claim_transition",
        "claim_id": evidence["claim_id"],
        "evidence_id": evidence_id,
        "from": from_state,
        "to": to_state,
        "contract_version": proposal_doc.get("contract_version", CRI_CORE_CONTRACT_VERSION),
        "authority_requirements": proposal_doc.get("authority_requirements", []),
    }

    # ------------------------------------------------------------------
    # Cycle A: Authority failure -> fix
    # ------------------------------------------------------------------

    _attempt(
        label="A1 AUTHORITY FAIL (self-approval)",
        proposal_obj=proposal_obj,
        orchestrator="alice",
        reviewer="alice",
        tamper_report_after_hash=False,
        expected_to_pass=False,
        transition_log=transition_log,
        rejection_log=rejection_log,
    )

    _attempt(
        label="A2 AUTHORITY FIX (separate reviewer)",
        proposal_obj=proposal_obj,
        orchestrator="alice",
        reviewer="bob",
        tamper_report_after_hash=False,
        expected_to_pass=True,
        transition_log=transition_log,
        rejection_log=rejection_log,
    )

    # ------------------------------------------------------------------
    # Cycle B: Integrity failure (SHA mismatch) -> fix
    # ------------------------------------------------------------------

    _attempt(
        label="B1 INTEGRITY FAIL (tamper report after SHA)",
        proposal_obj=proposal_obj,
        orchestrator="alice",
        reviewer="bob",
        tamper_report_after_hash=True,
        expected_to_pass=False,
        transition_log=transition_log,
        rejection_log=rejection_log,
    )

    # Fix path: we just re-run without tamper (fresh run_dir with correct SHA)
    _attempt(
        label="B2 INTEGRITY FIX (no tamper, hashes match)",
        proposal_obj=proposal_obj,
        orchestrator="alice",
        reviewer="bob",
        tamper_report_after_hash=False,
        expected_to_pass=True,
        transition_log=transition_log,
        rejection_log=rejection_log,
    )

    _write_json_log_with_front_matter(TRANSITION_LOG_PATH, transition_log)
    _write_json_log_with_front_matter(REJECTIONS_LOG_PATH, rejection_log)

    print("\nDONE: kernel showcase complete.")
    print("Note: commit is treated as log-append only when publication-commit passes.")


if __name__ == "__main__":
    main()
