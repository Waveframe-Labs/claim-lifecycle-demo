"""
---
title: "Kernel enforcement showcase runner"
filetype: "operational"
type: "non-normative"
domain: "case-study"
version: "0.3.0"
doi: "TBD-0.3.0"
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
ai_assistance_details: "AI-assisted hardening of the kernel showcase runner to support scenario selection, structural failure demonstration, and execution summary reporting."

dependencies:
  - "../../CRI-CORE/src/cricore/enforcement/execution.py"

anchors:
  - "KERNEL-ENFORCEMENT-SHOWCASE-v0.3.0"
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

CRI_CORE_CONTRACT_VERSION = "0.1.0"


# -----------------------------------------------------------------------------
# Utilities
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
    to_delete = [
        name for name in list(sys.modules.keys())
        if name == "cricore" or name.startswith("cricore.")
    ]
    for name in to_delete:
        del sys.modules[name]


def _ensure_cricore_importable() -> None:
    try:
        import cricore  # noqa
        return
    except Exception:
        pass

    env_src = os.environ.get("CRICORE_SRC")
    if not env_src:
        raise RuntimeError(
            "CRI-CORE not importable.\n"
            "Install editable or set CRICORE_SRC to CRI-CORE /src path."
        )

    candidate = Path(env_src).expanduser().resolve()
    pkg_root = candidate / "cricore"

    if not candidate.exists() or not pkg_root.exists():
        raise RuntimeError("CRICORE_SRC invalid.")

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

    _purge_cricore_modules()


def _print_results(results: List[Any]) -> None:
    for r in results:
        stage_id = getattr(r, "stage_id", "<unknown>")
        passed = bool(getattr(r, "passed", False))
        print(f"{stage_id}: {'OK' if passed else 'FAILED'}")

        if not passed:
            for msg in getattr(r, "messages", []):
                print(f"  - {msg}")


# -----------------------------------------------------------------------------
# Run Construction
# -----------------------------------------------------------------------------

def _make_run_dir(run_id: str) -> Path:
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "validation").mkdir(parents=True, exist_ok=True)
    return run_dir


def _materialize_run(
    *,
    run_dir: Path,
    run_id: str,
    orchestrator_id: str,
    reviewer_id: str,
    include_contract: bool,
    include_manifest: bool,
    tamper_after_manifest: bool,
) -> Dict[str, Any]:

    created_utc = _utc_now_iso()

    if include_contract:
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
        f"# Showcase Run\n\nrun_id: {run_id}\n",
    )

    _write_json(
        run_dir / "randomness.json",
        {"run_id": run_id, "deterministic": True},
    )

    _write_json(
        run_dir / "approval.json",
        {
            "run_id": run_id,
            "approver": {"id": reviewer_id, "type": "human"},
            "approved_at_utc": _utc_now_iso(),
        },
    )

    _write_json(
        run_dir / "validation" / "invariant_results.json",
        {"run_id": run_id},
    )

    sha_path = run_dir / "SHA256SUMS.txt"

    if include_manifest:
        digest = _sha256_file(report_path)
        _write_text(sha_path, f"{digest}  report.md\n")

        if tamper_after_manifest:
            _write_text(
                report_path,
                report_path.read_text() + "\nTAMPERED\n",
            )
    else:
        _write_text(sha_path, "# no entries\n")

    return {
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
            "repository_ref": "demo://showcase",
            "commit_ref": "local",
        },
    }


def _kernel_eval(run_dir: Path, context: Dict[str, Any]) -> Tuple[List[Any], bool]:
    _ensure_cricore_importable()
    from cricore.enforcement.execution import run_enforcement_pipeline

    results, commit_allowed = run_enforcement_pipeline(
        str(run_dir),
        expected_contract_version=CRI_CORE_CONTRACT_VERSION,
        run_context=context,
    )
    return results, bool(commit_allowed)


# -----------------------------------------------------------------------------
# Scenario Execution
# -----------------------------------------------------------------------------

def _run_scenario(label: str, **kwargs) -> bool:
    run_id = _new_run_id()
    run_dir = _make_run_dir(run_id)

    context = _materialize_run(run_dir=run_dir, run_id=run_id, **kwargs)

    results, allowed = _kernel_eval(run_dir, context)

    print(f"\n== {label} ==")
    _print_results(results)
    print(f"COMMIT: {'allowed' if allowed else 'blocked'} (run_id={run_id})")

    return allowed


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    scenario = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    total = 0
    allowed_count = 0

    def exec_s(label: str, **kw):
        nonlocal total, allowed_count
        total += 1
        if _run_scenario(label, **kw):
            allowed_count += 1

    if scenario in ("authority", "all"):
        exec_s(
            "AUTHORITY FAIL",
            orchestrator_id="alice",
            reviewer_id="alice",
            include_contract=True,
            include_manifest=False,
            tamper_after_manifest=False,
        )

        exec_s(
            "AUTHORITY FIX",
            orchestrator_id="alice",
            reviewer_id="bob",
            include_contract=True,
            include_manifest=False,
            tamper_after_manifest=False,
        )

    if scenario in ("integrity", "all"):
        exec_s(
            "INTEGRITY FAIL",
            orchestrator_id="alice",
            reviewer_id="bob",
            include_contract=True,
            include_manifest=True,
            tamper_after_manifest=True,
        )

        exec_s(
            "INTEGRITY FIX",
            orchestrator_id="alice",
            reviewer_id="bob",
            include_contract=True,
            include_manifest=True,
            tamper_after_manifest=False,
        )

    if scenario in ("structure", "all"):
        exec_s(
            "STRUCTURE FAIL (missing contract)",
            orchestrator_id="alice",
            reviewer_id="bob",
            include_contract=False,
            include_manifest=False,
            tamper_after_manifest=False,
        )

    print("\nSUMMARY")
    print("-------")
    print(f"Total scenarios: {total}")
    print(f"Allowed: {allowed_count}")
    print(f"Blocked: {total - allowed_count}")


if __name__ == "__main__":
    main()