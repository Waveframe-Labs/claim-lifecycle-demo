---
title: "Claim Lifecycle Demo — End-to-End Governed Claim Example"
filetype: "documentation"
type: "guidance"
domain: "case-study"
version: "0.3.2"
doi: "TBD-0.3.2"
status: "Active"
created: "2026-02-05"
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
ai_assistance_details: "AI-assisted revision to align README with enforcement showcase hardening and lifecycle runner commit semantics under CRI-CORE."

dependencies: []

anchors:
  - "CLAIM-LIFECYCLE-DEMO-README-v0.3.2"
---

# Claim Lifecycle Demo

This repository is a minimal, end-to-end demonstration of a governed
scientific claim lifecycle backed by a real enforcement engine.

It demonstrates two distinct but related boundaries:

1. A governed claim lifecycle (evidence → proposal → enforcement → state mutation).
2. A hardened kernel enforcement showcase (structural, authority, and integrity gating).

The lifecycle demo shows how a claim moves through:

    proposed → supported → contradicted → superseded

Each transition is:

- triggered by submitted evidence
- validated against explicit transition rules
- materialized as a CRI-CORE run artifact
- passed through a deterministic enforcement decision boundary
- and recorded as an immutable event

This repository demonstrates governance boundaries, not infrastructure scale.

---

## Two Demonstration Modes

### 1. Lifecycle Demonstration (`run_demo.py`)

Shows:

- Evidence-driven transition proposals
- Rule validation (transition graph constraints)
- CRI-CORE enforcement integration
- Authority boundary enforcement (self-approval denial)
- Append-only transition logging
- Commit gating via `commit_allowed`

This runner models a governed scientific workflow.

---

### 2. Kernel Enforcement Showcase (`run_kernel_showcase.py`)

Demonstrates enforcement behavior in isolation, without lifecycle semantics.

Scenarios:

- Authority failure → fix
- Integrity tamper detection → fix
- Structural contract failure (missing `contract.json`)

This harness proves:

- Structural admissibility enforcement
- Role separation enforcement
- SHA256 artifact integrity verification
- Stage cascade logic
- Centralized commit gating

It isolates the enforcement engine from lifecycle logic.

---

## What Is Being Tracked?

The primary object is a claim.

A claim represents the smallest testable scientific statement that
downstream conclusions depend on.

Example:

> A specific model version achieves at least a declared performance
> threshold under a defined dataset and evaluation configuration.

This demo focuses on governance mechanics rather than executing experiments.

---

## What Makes a Transition Valid?

A claim may change state only when a new evidence submission:

- references the claim by ID
- declares an intended state transition
- satisfies transition rules
- is materialized as a CRI-CORE run artifact
- passes enforcement validation

Claim state is never edited directly.

---

## Enforcement Capabilities Demonstrated

This repository demonstrates:

- Rule validation (transition graph constraints)
- Run structure contract enforcement
- Structural version gating
- Identity separation enforcement
- SHA256 integrity verification
- Integrity finalization cascade
- Explicit allow/deny decisions
- Centralized commit gating
- Append-only transition logging

---

## Repository Structure

    claims/           # Claim objects
    evidence/         # Evidence submissions
    rules/            # Transition rules
    transitions/      # Append-only transition log
    demo_runner/      # Lifecycle + enforcement harnesses

Execution artifacts:

    demo_runner/runs/

These are runtime outputs and are not treated as canonical source artifacts.

---

## Running the Demo

### Prerequisite

Both repositories must exist locally:

    C:\GitHub\CRI-CORE
    C:\GitHub\claim-lifecycle-demo

---

### Lifecycle Demo

From repository root:

```powershell
$env:PYTHONPATH="C:\GitHub\CRI-CORE\src"
python demo_runner\run_demo.py
```

---

### Kernel Showcase (All Scenarios)

```powershell
$env:PYTHONPATH="C:\GitHub\CRI-CORE\src"
python demo_runner\run_kernel_showcase.py
```

---

### Kernel Showcase (Selective Scenarios)

Authority only:

```powershell
python demo_runner\run_kernel_showcase.py authority
```

Integrity only:

```powershell
python demo_runner\run_kernel_showcase.py integrity
```

Structure only:

```powershell
python demo_runner\run_kernel_showcase.py structure
```

---

## Why This Matters

Most research workflows track files and artifacts.

This demo treats claims themselves as governed objects whose status changes
only through validated evidence and deterministic enforcement.

That enables:

- Deterministic lifecycle control
- Explicit role accountability
- Tamper-detectable execution artifacts
- Clear governance boundaries between proposal and mutation

---

## Scope

This repository demonstrates a governed lifecycle boundary and a hardened
kernel enforcement boundary.

CRI-CORE remains a separate enforcement engine.

This repository shows what governed claim mutation looks like in practice.
