"""
---
title: "Kernel enforcement showcase runner"
filetype: "operational"
type: "non-normative"
domain: "case-study"
version: "0.2.0"
doi: "TBD-0.2.0"
status: "Active"
created: "2026-02-18"
updated: "2026-02-19"

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
ai_assistance_details: "AI-assisted generation of a kernel-first enforcement showcase runner that demonstrates two fail→fix cycles (authority + integrity) using CRI-CORE's commit_allowed return value."

dependencies:
  - "../../CRI-CORE/src/cricore/enforcement/execution.py"

anchors:
  - "KERNEL-ENFORCEMENT-SHOWCASE-v0.2.0"
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

# CRI-CORE run artifact contract version (structure gate)
CRI_CORE_CONTRACT_VERSION = "0.1.0"


# -----------------------------------------------------------------------------
# Small utilities
# -----------------------------------------------------------------------------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_run_id(prefix: str = "SHOWCASE-RUN") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    micros = datetime.now(timezone.utc).strftime("%f")
    return f"{prefix}-{stamp}-{micros}"


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _purge_cricore_modules() -> None:
    # Avoid stale imports from an old editable install / different path
    to_delete = [
        name for name in list(sys.modules.keys())
        if name == "cricore" or name.startswith("cricore.")
    ]
    for name in to_delete:
        del sys.modules[name]


def _ensure_cricore_importable() -> None:
    """
    Preferred: CRI-CORE installed (pyproject / editable install).
    Fallback: load from CRICORE_SRC=/path/to/CRI-CORE/src
    """
    try:
        import cricore  # noqa: F401
        return
    except Exception:
        pass

    env_src = os.environ.get("CRICORE_SRC")
    if not env_src:
        raise RuntimeError(
            "CRI-CORE not importable.\n"
            "Either install CRI-CORE (editable) or set CRICORE_SRC to CRI-CORE's /src path.\n"
            "Example (PowerShell):\n"
            '  $env:CRICORE_SRC="C:\\GitHub\\CRI-CORE\\src"\n'
        )

    candidate = Path(env_src).expanduser().resolve()
    pkg_root = candidate / "cricore"
    if not candidate.exists() or not candidate.is_dir() or not pkg_root.exists():
        raise RuntimeError(
            "CRICORE_SRC is invalid.\n"
            f"Looked for src: {candidate}\n"
            f"Expected package folder: {pkg_root}\n"
        )

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

    _purge_cricore_modules()


def _print_results(results: List[Any]) -> None:
    """
    Print StageResult objects without depending on any specific stage IDs
    or internal ordering.
    """
    for r in results:
        stage_id = getattr(r, "stage_id", "<unknown-stage>")
        passed = bool(getattr(r, "passed", False))
        print(f"{stage_id}: {'OK' if passed else 'FAILED'}")

        if not passed:
            for msg in list(getattr(r, "messages", [])):
                print(f"  - {msg}")


# -----------------------------------------------------------------------------
# Run materialization (minimal CRI-CORE run directory)
# -----------------------------------------------------------------------------

def _make_run_dir(run_id: str) -> Path:
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "validation").mkdir(parents=True, exist_ok=True)
    return run_dir


def _materialize_minimal_run(
    *,
    run_dir: Path,
    run_id: str,
    proposal: Mapping[str, Any],
    orchestrator_id: str,
    reviewer_id: str,
    self_approval_override: bool,
    include_manifest_for_report: bool,
    tamper_report_after_manifest: bool,
) -> Dict[str, Any]:
    """
    Creates a CRI-CORE-compatible run directory.

    Integrity behavior:
      - If include_manifest_for_report=True, SHA256SUMS.txt will include an entry for report.md.
      - If tamper_report_after_manifest=True, report.md will be changed after SHA is written,
        producing a deliberate mismatch.
    """
    created_utc = _utc_now_iso()

    # Required files
    _write_json(
        run_dir / "contract.json",
        {
            "contract_version": CRI_CORE_CONTRACT_VERSION,
            "run_id": run_id,
            "created_utc": created_utc,
        },
    )

    report_path = run_dir / "report.md"
    _write_text(
        report_path,
        "\n".join(
            [
                "# Kernel Enforcement Showcase Run",
                "",
                f"- run_id: `{run_id}`",
                f"- created_utc: `{created_utc}`",
                f"- contract_version: `{CRI_CORE_CONTRACT_VERSION}`",
                "",
                "## Proposal (opaque to kernel except as referenced context)",
                "```json",
                json.dumps(dict(proposal), indent=2),
                "```",
                "",
            ]
        ),
    )

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
            "context_ref": "kernel-showcase",
        },
    )

    _write_json(
        run_dir / "validation" / "invariant_results.json",
        {
            "run_id": run_id,
            "generated_at_utc": _utc_now_iso(),
            "notes": "Showcase placeholder invariant outputs; structural presence only.",
        },
    )

    # SHA256SUMS.txt (controls integrity behavior)
    sha_path = run_dir / "SHA256SUMS.txt"
    if include_manifest_for_report:
        digest = _sha256_file(report_path)
        # Format: "<sha256>  <relative_path>"
        _write_text(sha_path, f"{digest}  report.md\n")
        if tamper_report_after_manifest:
            _write_text(
                report_path,
                report_path.read_text(encoding="utf-8") + "\n\nTAMPER: mutated after manifest write.\n",
            )
    else:
        _write_text(
            sha_path,
            "# Showcase manifest intentionally has no entries.\n",
        )

    # run_context (inputs to policy-free kernel stages)
    run_context: Dict[str, Any] = {
        "identities": {
            "orchestrator": {"id": orchestrator_id, "type": "human"},
            "reviewer": {"id": reviewer_id, "type": "human"},
            "self_approval_override": bool(self_approval_override),
        },
        "integrity": {
            "workflow_execution_ref": f"showcase://{run_id}",
            "run_payload_ref": f"showcase://{run_id}/payload",
            "attestation_ref": f"showcase://{run_id}/attestation",
        },
        "publication": {
            "repository_ref": "demo://claim-lifecycle-demo",
            "commit_ref": "showcase-uncommitted",
        },
        "proposal": dict(proposal),
    }

    return run_context


# -----------------------------------------------------------------------------
# Kernel invocation
# -----------------------------------------------------------------------------

def _kernel_evaluate(run_dir: Path, run_context: Dict[str, Any]) -> Tuple[List[Any], bool]:
    _ensure_cricore_importable()
    from cricore.enforcement.execution import run_enforcement_pipeline  # type: ignore

    results, commit_allowed = run_enforcement_pipeline(
        str(run_dir),
        expected_contract_version=CRI_CORE_CONTRACT_VERSION,
        run_context=run_context,
    )
    return results, bool(commit_allowed)


# -----------------------------------------------------------------------------
# Scenarios
# -----------------------------------------------------------------------------

def _scenario(
    *,
    label: str,
    orchestrator_id: str,
    reviewer_id: str,
    self_approval_override: bool,
    include_manifest_for_report: bool,
    tamper_report_after_manifest: bool,
) -> None:
    run_id = _new_run_id()
    run_dir = _make_run_dir(run_id)

    # Proposal is intentionally minimal + opaque to kernel at this stage.
    proposal = {
        "proposal_id": label,
        "type": "kernel_showcase_transition_attempt",
        "from": "supported",
        "to": "contradicted",
        "notes": "This is a kernel harness. Lifecycle semantics are not evaluated here.",
    }

    run_context = _materialize_minimal_run(
        run_dir=run_dir,
        run_id=run_id,
        proposal=proposal,
        orchestrator_id=orchestrator_id,
        reviewer_id=reviewer_id,
        self_approval_override=self_approval_override,
        include_manifest_for_report=include_manifest_for_report,
        tamper_report_after_manifest=tamper_report_after_manifest,
    )

    results, commit_allowed = _kernel_evaluate(run_dir, run_context)

    print(f"\n== {label} ==")
    _print_results(results)
    print(f"COMMIT: {'allowed' if commit_allowed else 'blocked'} (run_id={run_id})")


def main() -> None:
    print("Kernel enforcement showcase")
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    # A) Authority failure → fix
    _scenario(
        label="A1 AUTHORITY FAIL (self-approval)",
        orchestrator_id="alice",
        reviewer_id="alice",
        self_approval_override=False,
        include_manifest_for_report=False,      # not needed for authority scenario
        tamper_report_after_manifest=False,
    )

    _scenario(
        label="A2 AUTHORITY FIX (separate reviewer)",
        orchestrator_id="alice",
        reviewer_id="bob",
        self_approval_override=False,
        include_manifest_for_report=False,
        tamper_report_after_manifest=False,
    )

    # B) Integrity failure → fix
    _scenario(
        label="B1 INTEGRITY FAIL (tamper report after SHA)",
        orchestrator_id="alice",
        reviewer_id="bob",
        self_approval_override=False,
        include_manifest_for_report=True,       # include report.md hash entry
        tamper_report_after_manifest=True,      # then mutate report.md → mismatch
    )

    _scenario(
        label="B2 INTEGRITY FIX (no tamper, hashes match)",
        orchestrator_id="alice",
        reviewer_id="bob",
        self_approval_override=False,
        include_manifest_for_report=True,       # include report.md hash entry
        tamper_report_after_manifest=False,     # do not tamper → matches
    )

    print("\nDONE: kernel showcase complete.")
    print("Note: commit is treated as log-append only when commit_allowed is True.")


if __name__ == "__main__":
    main()
