---
title: "Claim Lifecycle Demo — End-to-End Governed Claim Example"
filetype: "documentation"
type: "guidance"
domain: "case-study"
version: "0.2.0"
doi: "TBD-0.2.0"
status: "Draft"
created: "2026-02-05"
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
ai_assistance_details: "AI-assisted drafting and refinement of the demo documentation under direct human design, review, and final approval."

dependencies: []

anchors:
  - "CLAIM-LIFECYCLE-DEMO-README-v0.2.0"
---

# Claim Lifecycle Demo

This repository is a minimal, end-to-end demonstration of a **governed
scientific claim lifecycle** backed by a real enforcement engine.

It shows how a single claim moves through the following states:

    proposed → supported → contradicted → superseded

Each state transition is:

-   triggered by submitted evidence\
-   validated against explicit transition rules\
-   passed through a CRI-CORE enforcement decision boundary\
-   and recorded as an immutable event

This repository demonstrates lifecycle governance.\
It is not a platform or infrastructure showcase.

------------------------------------------------------------------------

## What is being tracked?

The primary object in this demo is a **claim**.

A claim represents the smallest testable scientific statement that
downstream results depend on.

Example (used in this demo):

> A specific model version achieves at least a specified performance
> threshold under a declared dataset and evaluation configuration.

This demo focuses on governance mechanics rather than executing real
experiments.

------------------------------------------------------------------------

## What makes a transition valid?

A claim may only change state when a new **evidence submission**:

-   references the claim by ID\
-   declares an intended state transition\
-   satisfies declared transition rules\
-   is materialized as a CRI-CORE run artifact\
-   and passes enforcement validation

Claim state is never edited directly.

------------------------------------------------------------------------

## How governance is enforced

The transition flow implemented in this demo:

    evidence submission
          ↓
    transition proposal
          ↓
    CRI-CORE run materialization
          ↓
    enforcement pipeline decision
          ↓
    state transition (if allowed)

Each transition attempt produces a structured run directory containing:

-   contract.json\
-   report.md\
-   approval.json\
-   randomness.json\
-   SHA256SUMS.txt\
-   validation artifacts

If enforcement fails, the transition is denied and state remains
unchanged.

------------------------------------------------------------------------

## Demonstrated enforcement behaviors

This demo currently demonstrates:

-   Rule validation (transition graph constraints)\
-   Run structure contract enforcement\
-   Identity separation enforcement (self-approval denial)\
-   Explicit allow/deny decisions\
-   Append-only transition logging

It does not yet enforce:

-   Cryptographic hash verification\
-   Artifact integrity binding\
-   Publication anchoring\
-   External attestation verification

Those are later-phase capabilities of the enforcement engine.

------------------------------------------------------------------------

## Repository structure

    claims/           # Claim objects
    evidence/         # Evidence submissions
    rules/            # Transition rules
    transitions/      # Append-only transition log
    demo_runner/      # Lifecycle + enforcement integration

Claim files are never overwritten.\
History remains visible and auditable.

------------------------------------------------------------------------

## Running the demo

### Prerequisite

Both repositories must exist locally:

    C:\GitHub\CRI-CORE
    C:\GitHub\claim-lifecycle-demo

### Windows (PowerShell)

From the root of this repository:

``` powershell
$env:PYTHONPATH="C:\GitHub\CRI-CORE\src"
python demo_runner\run_demo.py
```

------------------------------------------------------------------------

## Example execution output

    Initial claim state: proposed
    [OK] proposed -> supported via ev-002-supported
    [DENY] supported -> contradicted via ev-003-contradicted (attempt 1)
            independence: FAILED
    [OK] supported -> contradicted via ev-003-contradicted (run ...)
    [OK] contradicted -> superseded via ev-004-superseded

    Final claim state: superseded

This demonstrates:

-   Governance boundary is real\
-   Enforcement decisions are explicit\
-   Invalid transitions are denied\
-   State changes only occur after a successful enforcement pass

------------------------------------------------------------------------

## Why this matters

Most research workflows track files and artifacts.

This demo treats **claims themselves as governed objects** whose status
changes only through validated evidence and explicit enforcement.

That enables:

-   Deterministic lifecycle control\
-   Reversible conclusions without rewriting history\
-   Explicit accountability boundaries

------------------------------------------------------------------------

## Scope

This repository exists to demonstrate the lifecycle boundary clearly and
concretely.

The enforcement engine (CRI-CORE) is a separate component.\
The purpose here is to show what it looks like when a claim lifecycle is
actually governed.