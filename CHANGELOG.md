---
title: "Claim Lifecycle Demo — Change Log"
filetype: "documentation"
type: "non-normative"
domain: "case-study"
version: "0.3.2"
doi: "TBD-0.3.2"
status: "Active"
created: "2026-02-12"
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
ai_assistance_details: "AI-assisted drafting and refinement of structured changelog entries under direct human review and release control."

dependencies: []

anchors:
  - "CLAIM-LIFECYCLE-DEMO-CHANGELOG-v0.3.2"
---

# Changelog

All notable changes to this demo are documented in this file.

This project follows semantic versioning for demo behavior and governance boundaries.

---

---

## [0.3.2] — 2026-02-20

### Fixed

- Corrected CRI-CORE enforcement pipeline return handling in `run_demo.py`.
- Updated lifecycle runner to properly unpack:
  `(stage_results, commit_allowed)`.
- Commit decisions now rely exclusively on `commit_allowed` from CRI-CORE.
- Eliminated legacy `all(r.passed)` logic to align with centralized kernel commit semantics.

### Notes

- This release does not modify lifecycle semantics.
- No changes to transition rules, evidence format, or claim structure.
- Ensures deterministic alignment with CRI-CORE v0.4.x enforcement contract.

---

## [0.3.0] — 2026-02-20

### Added

- Hardened `run_kernel_showcase.py` enforcement harness.
- Introduced scenario selection via CLI:
  - `authority`
  - `integrity`
  - `structure`
  - `all` (default)
- Added structural failure scenario (missing `contract.json`) to demonstrate run-structure enforcement.
- Added execution summary reporting (total / allowed / blocked).

### Demonstrates

- Authority boundary enforcement (self-approval violation).
- Integrity enforcement (SHA256 tamper detection).
- Structural contract gating (missing required artifact).
- Centralized commit gating via CRI-CORE `commit_allowed`.

### Notes

- Showcase runner remains lifecycle-agnostic.
- No lifecycle semantics evaluated in this harness.
- Kernel behavior unchanged; demo presentation hardened.

---

## [0.2.0] — 2026-02-14

### Added

- Integrated CRI-CORE enforcement pipeline into the demo runner.
- Materialized real CRI-CORE run artifact structure for each transition attempt:
  - `contract.json`
  - `report.md`
  - `randomness.json`
  - `approval.json`
  - `SHA256SUMS.txt`
  - `validation/invariant_results.json`
- Implemented structural version gating against the CRI-CORE run contract.
- Added enforcement-denial demonstration (self-approval violation scenario).

### Changed

- Transition proposals are now passed through an enforcement decision before claim state updates.
- Claim state transitions now occur only after explicit allow decisions.
- Updated README to reflect governed transition boundary and local enforcement dependency.
- Marked `transitions/transition-log.json1` as a runtime artifact and excluded it from version control.

### Archived

- Preserved original pre-enforcement demo runner in:
  `archive/run_demo.py`

### Notes

- `demo_runner/runs/` directories are execution artifacts and are not part of the versioned demo source.
- `transitions/transition-log.json` is an append-only execution artifact.
- This release does not modify claim semantics or transition rule definitions.
- Transition logs are generated during the demo execution.
- The log reflects runtime behavior and is not treated as a canonical source artifact.

---

## [0.1.1] — 2026-02-12

### Added

- Introduced an explicit governance enforcement boundary between evidence-driven transition proposals and claim state updates.
- Integrated an internal enforcement engine to evaluate transition proposals prior to applying state changes.
- Added structural support for enforcement decisions in the demo runner execution flow.

### Changed

- Updated the demo runner to submit transition proposals through a governance enforcement stage before applying transitions.
- Updated the root README to document the governed transition boundary and execution requirements.
- Updated the demo execution instructions to reflect the local enforcement engine dependency.

### Archived

- Preserved the original, pre-governance demo runner implementation under:
  `archive/run_demo.py`

### Notes

- `transitions/transition-log.json` is an execution artifact and is not treated as a versioned source file.
- This release introduces no changes to claim semantics or transition rule definitions.