"""
---
title: "Kernel enforcement showcase runner"
filetype: "operational"
type: "non-normative"
domain: "case-study"
version: "0.1.1"
doi: "TBD-0.1.1"
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
ai_assistance_details: "AI-assisted kernel showcase runner that routes transition attempts through CRI-CORE and demonstrates two blocked→fixed sequences (authority + integrity) without coupling to lifecycle state."

dependencies:
  - "./runs/"
  - "../README.md"

anchors:
  - "KERNEL-SHOWCASE-RUNNER-v0.1.1"
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


ROOT = Path(__file__).resolve().parent.parent
RUNS_ROOT = ROOT / "demo_runner" / "runs"

# This is the CRI-CORE run artifact contract version (structure gate), not this repo version.
CRI_CORE_RUN_CONTRACT_VERSION = "0.1.0"


# ----------------------------
# Small utilities
# ----------------------------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_json_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _compute_sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _new_run_id(prefix: str = "SHOWCASE-RUN") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    micros = datetime.now(timezone.utc).strftime("%f")
    return f"{prefix}-{stamp}-{micros}"


# ----------------------------
# CRI-CORE import isolation
# ----------------------------

def _purge_cricore_modules() -> None:
    """
    Prevent Python from reusing a previously imported cricore module from a
    different path (site-packages, old editable install, etc.).
    """
    to_delete = [n for n in list(sys.modules.keys()) if n == "cricore" or n.startswith("cricore.")]
    for n in to_delete:
        del sys.modules[n]


def _ensure_cricore_importable() -> None:
    """
    Ensure CRI-CORE is importable from a local src path.

    Use:
      $env:CRICORE_SRC="C:\\GitHub\\CRI-CORE\\src"
    """
    env_src = os.environ.get("CRICORE_SRC")
    if not env_src:
        raise RuntimeError(
            "CRICORE_SRC is not set.\n"
            "Set it to the CRI-CORE /src folder, e.g.:\n"
            '  $env:CRICORE_SRC="C:\\GitHub\\CRI-CORE\\src"'
        )

    candidate = Path(env_src).expanduser().resolve()
    pkg_root = candidate / "cricore"

    if not candidate.exists() or not candidate.is_dir():
        raise RuntimeError(f"CRICORE_SRC does not exist or is not a directory: {candidate}")
    if not pkg_root.exists() or not pkg_root.is_dir():
        raise RuntimeError(f"CRI-CORE package folder not found: {pkg_root}")

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

    _purge_cricore_modules()


# ----------------------------
# Run materialization
# ----------------------------

def _materialize_run_dir(
    *,
    run_dir: Path,
    run_id: str,
    proposal_obj: Dict[str, Any],
    proposal_hash: str,
    reviewer_id: str,
    sha_mode: str,
    tamper_report_after_sha: bool,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Create a structurally valid CRI-CORE run directory.

    sha_mode:
      - "empty": SHA256SUMS.txt exists but asserts no hashes (comment-only)
      - "report_only": SHA256SUMS.txt asserts report.md hash

    tamper_report_after_sha:
      - If True, report.md is modified AFTER SHA256SUMS.txt is written (integrity fail expected).
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "validation").mkdir(parents=True, exist_ok=True)

    created_utc = _utc_now_iso()

    # contract.json — satisfy run-structure + version gate
    _write_json(
        run_dir / "contract.json",
        {
            "contract_version": CRI_CORE_RUN_CONTRACT_VERSION,
            "run_id": run_id,
            "created_utc": created_utc,
        },
    )

    # report.md — make it a hashed target for integrity demo
    report_lines = [
        "# Kernel Showcase Run Report",
        "",
        f"- run_id: `{run_id}`",
        f"- created_utc: `{created_utc}`",
        f"- contract_version: `{CRI_CORE_RUN_CONTRACT_VERSION}`",
        f"- proposal_hash: `{proposal_hash}`",
        "",
        "## Proposal",
        "```json",
        json.dumps(proposal_obj, indent=2),
        "```",
        "",
    ]
    _write_text(run_dir / "report.md", "\n".join(report_lines))

    # randomness.json — structural presence
    _write_json(
        run_dir / "randomness.json",
        {
            "run_id": run_id,
            "deterministic": True,
            "seed": None,
        },
    )

    # approval.json — used by independence stage (reviewer identity binding)
    _write_json(
        run_dir / "approval.json",
        {
            "run_id": run_id,
            "approver": {"id": reviewer_id, "type": "human"},
            "approved_at_utc": _utc_now_iso(),
            "context_ref": "kernel-showcase",
        },
    )

    # invariant_results.json — structural presence
    _write_json(
        run_dir / "validation" / "invariant_results.json",
        {
            "run_id": run_id,
            "generated_at_utc": _utc_now_iso(),
            "notes": "Showcase placeholder invariant outputs; structural presence only.",
        },
    )

    # SHA256SUMS.txt — integrity surface
    sha_path = run_dir / "SHA256SUMS.txt"
    if sha_mode == "empty":
        _write_text(
            sha_path,
            "# Showcase manifest intentionally contains no asserted file hashes.\n"
            "# This keeps integrity surface present without claiming coverage.\n"
        )
    elif sha_mode == "report_only":
        digest = _compute_sha256_file(run_dir / "report.md")
        _write_text(
            sha_path,
            "# Showcase manifest asserts report.md hash.\n"
            f"{digest}  report.md\n",
        )
    else:
        raise ValueError(f"Unknown sha_mode: {sha_mode}")

    # Tamper AFTER SHA is written (forces mismatch when sha_mode=report_only)
    if tamper_report_after_sha:
        _write_text(run_dir / "report.md", (run_dir / "report.md").read_text(encoding="utf-8") + "\nTAMPER\n")

    # Minimal run_context required by the enforcement pipeline
    run_context: Dict[str, Any] = {
        "identities": {
            # orchestrator/reviewer IDs are what independence checks; approval.json mirrors reviewer_id
            "orchestrator": {"id": proposal_obj["authority_bindings"]["orchestrator_id"], "type": "human"},
            "reviewer": {"id": reviewer_id, "type": "human"},
            "self_approval_override": bool(proposal_obj["authority_bindings"].get("self_approval_override", False)),
        },
        "integrity": {
            "workflow_execution_ref": f"showcase://{run_id}",
            "run_payload_ref": f"showcase://{run_id}/payload",
            "attestation_ref": f"showcase://{run_id}/attestation",
        },
        "publication": {
            "repository_ref": "demo://claim-lifecycle-demo",
            "commit_ref": "uncommitted-local-showcase",
        },
        "proposal": proposal_obj,
    }

    return run_dir, run_context


def _cricore_eval(run_dir: Path, run_context: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Run CRI-CORE enforcement pipeline and return:
      - allowed: overall pipeline pass/fail
      - lines: human-readable stage summary
    """
    _ensure_cricore_importable()
    from cricore.enforcement.execution import run_enforcement_pipeline  # type: ignore

    results = run_enforcement_pipeline(
        str(run_dir),
        expected_contract_version=CRI_CORE_RUN_CONTRACT_VERSION,
        run_context=run_context,
    )

    allowed = all(r.passed for r in results)

    lines: List[str] = []
    for r in results:
        if r.passed:
            lines.append(f"{r.stage_id}: OK")
        else:
            lines.append(f"{r.stage_id}: FAILED")
            for m in r.messages:
                lines.append(f"  - {m}")

    return allowed, lines


# ----------------------------
# Showcase scenarios
# ----------------------------

def _base_proposal(*, from_state: str, to_state: str) -> Dict[str, Any]:
    """
    Kernel showcase uses a domain proposal object.
    NOTE: This is NOT the CRI-CORE run artifact contract; it's demo-layer intent.
    """
    return {
        "proposal_id": "kernel-showcase-proposal-001",
        "type": "claim_transition",
        "claim_id": "claim-001",
        "from": from_state,
        "to": to_state,
        "demo_policy_version": "0.1.0",
        "authority_bindings": {
            "orchestrator_id": "alice",
            "self_approval_override": False,
        },
    }


def _print_block_reason(label: str, lines: List[str]) -> None:
    """
    Add a stable, narrative-friendly summary without relying on stage IDs for logic.
    """
    # We only classify for printing based on messages we already see.
    # This is narrative-only and can evolve later into failure_class mapping.
    joined = "\n".join(lines)
    if "self-approval detected" in joined:
        reason = "AUTHORITY_BLOCK (self-approval / independence)"
    elif "hash mismatch:" in joined or "manifest" in joined:
        reason = "INTEGRITY_BLOCK (manifest mismatch)"
    else:
        reason = "BLOCKED (see stage output)"
    print(f"{label} RESULT: {reason}")


def main() -> None:
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    print("Kernel enforcement showcase")
    print("Note: This runner is a kernel harness. It does not mutate lifecycle state or logs.\n")

    # We keep the domain transition consistent across scenarios. The kernel does not
    # validate domain semantics here; it validates run contract + authority + integrity gates.
    from_state = "supported"
    to_state = "contradicted"

    # -------------------------
    # A1: AUTHORITY FAIL
    # -------------------------
    print("== A1 AUTHORITY FAIL (self-approval) ==")
    proposal_a1 = _base_proposal(from_state=from_state, to_state=to_state)
    proposal_a1["authority_bindings"]["orchestrator_id"] = "alice"
    proposal_hash_a1 = _sha256_hex(_stable_json_dumps(proposal_a1))

    run_id_a1 = _new_run_id()
    run_dir_a1 = RUNS_ROOT / run_id_a1

    _, ctx_a1 = _materialize_run_dir(
        run_dir=run_dir_a1,
        run_id=run_id_a1,
        proposal_obj=proposal_a1,
        proposal_hash=proposal_hash_a1,
        reviewer_id="alice",                  # self-approval
        sha_mode="empty",                     # no integrity assertion in authority scenario
        tamper_report_after_sha=False,
    )

    allowed_a1, lines_a1 = _cricore_eval(run_dir_a1, ctx_a1)
    print("\n".join(lines_a1))
    if not allowed_a1:
        _print_block_reason("A1", lines_a1)
    print(f"COMMIT: {'allowed' if allowed_a1 else 'blocked'} (run_id={run_id_a1})\n")

    # -------------------------
    # A2: AUTHORITY FIX
    # -------------------------
    print("== A2 AUTHORITY FIX (separate reviewer) ==")
    proposal_a2 = _base_proposal(from_state=from_state, to_state=to_state)
    proposal_a2["authority_bindings"]["orchestrator_id"] = "alice"
    proposal_hash_a2 = _sha256_hex(_stable_json_dumps(proposal_a2))

    run_id_a2 = _new_run_id()
    run_dir_a2 = RUNS_ROOT / run_id_a2

    _, ctx_a2 = _materialize_run_dir(
        run_dir=run_dir_a2,
        run_id=run_id_a2,
        proposal_obj=proposal_a2,
        proposal_hash=proposal_hash_a2,
        reviewer_id="bob",                    # separate reviewer
        sha_mode="empty",
        tamper_report_after_sha=False,
    )

    allowed_a2, lines_a2 = _cricore_eval(run_dir_a2, ctx_a2)
    print("\n".join(lines_a2))
    if not allowed_a2:
        _print_block_reason("A2", lines_a2)
    print(f"COMMIT: {'allowed' if allowed_a2 else 'blocked'} (run_id={run_id_a2})\n")

    # -------------------------
    # B1: INTEGRITY FAIL
    # -------------------------
    print("== B1 INTEGRITY FAIL (tamper report after SHA) ==")
    proposal_b1 = _base_proposal(from_state=from_state, to_state=to_state)
    proposal_b1["authority_bindings"]["orchestrator_id"] = "alice"
    proposal_hash_b1 = _sha256_hex(_stable_json_dumps(proposal_b1))

    run_id_b1 = _new_run_id()
    run_dir_b1 = RUNS_ROOT / run_id_b1

    _, ctx_b1 = _materialize_run_dir(
        run_dir=run_dir_b1,
        run_id=run_id_b1,
        proposal_obj=proposal_b1,
        proposal_hash=proposal_hash_b1,
        reviewer_id="bob",                    # authority OK, we want integrity fail
        sha_mode="report_only",               # assert report.md hash
        tamper_report_after_sha=True,         # then tamper it
    )

    allowed_b1, lines_b1 = _cricore_eval(run_dir_b1, ctx_b1)
    print("\n".join(lines_b1))
    if not allowed_b1:
        _print_block_reason("B1", lines_b1)
    print(f"COMMIT: {'allowed' if allowed_b1 else 'blocked'} (run_id={run_id_b1})\n")

    # -------------------------
    # B2: INTEGRITY FIX
    # -------------------------
    print("== B2 INTEGRITY FIX (no tamper, hashes match) ==")
    proposal_b2 = _base_proposal(from_state=from_state, to_state=to_state)
    proposal_b2["authority_bindings"]["orchestrator_id"] = "alice"
    proposal_hash_b2 = _sha256_hex(_stable_json_dumps(proposal_b2))

    run_id_b2 = _new_run_id()
    run_dir_b2 = RUNS_ROOT / run_id_b2

    _, ctx_b2 = _materialize_run_dir(
        run_dir=run_dir_b2,
        run_id=run_id_b2,
        proposal_obj=proposal_b2,
        proposal_hash=proposal_hash_b2,
        reviewer_id="bob",
        sha_mode="report_only",
        tamper_report_after_sha=False,
    )

    allowed_b2, lines_b2 = _cricore_eval(run_dir_b2, ctx_b2)
    print("\n".join(lines_b2))
    if not allowed_b2:
        _print_block_reason("B2", lines_b2)
    print(f"COMMIT: {'allowed' if allowed_b2 else 'blocked'} (run_id={run_id_b2})\n")

    print("DONE: kernel showcase complete.")
    print("Note: 'COMMIT' here is a narrative boundary: allowed iff the CRI-CORE pipeline passes.")


if __name__ == "__main__":
    main()
