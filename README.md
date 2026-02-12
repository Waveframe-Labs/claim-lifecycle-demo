---
title: "Claim Lifecycle Demo — End-to-End Governed Claim Example"
filetype: "documentation"
type: "guidance"
domain: "case-study"
version: "0.1.1"
doi: "TBD-0.1.1"
status: "Draft"
created: "2026-02-05"
updated: "2026-02-12"

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
  - "CLAIM-LIFECYCLE-DEMO-README-v0.1.1"
---

# Claim Lifecycle Demo

This repository is a minimal, end-to-end demonstration of a **governed scientific claim lifecycle**.

It shows how a single claim moves through the following states:

```
proposed → supported → contradicted → superseded
```

Each state transition is driven by submitted evidence, evaluated against explicit rules, passed through a governance enforcement boundary, and recorded as an immutable event.

This repository demonstrates **claim lifecycle behavior**.  
It is not a platform or infrastructure showcase.

---

## What is being tracked?

The primary object in this demo is a **claim**.

A claim represents the smallest testable scientific statement that downstream results depend on.

Example (used in this demo):

> A specific model version achieves at least a specified performance threshold under a declared dataset and evaluation configuration.

This demo focuses on the governance and transition mechanics rather than on executing or validating real experiments.

---

## What is a valid update?

A claim may only change state when a new **evidence submission**:

- references the claim by ID
- declares an intended state transition
- may reference linked artifacts
- satisfies the declared transition rules
- and passes a governance enforcement boundary

Claim state is never edited directly.

---

## How transitions are governed

The transition flow implemented in this demo is:

```
evidence submission
      ↓
transition proposal
      ↓
governance enforcement decision
      ↓
state transition (if allowed)
```

The demo runner produces a transition proposal and submits it to an internal enforcement engine.  
Only an explicit allow decision permits the state transition to be applied.

This makes the transition boundary explicit and auditable.

---

## Who can submit updates?

Anyone may submit evidence for a claim.

However, claim state is not edited directly.  
State transitions occur only when an evidence submission passes:

- rule validation
- and governance enforcement

and is then recorded in the transition log.

---

## What is demonstrated in this repository?

This demo shows:

- a single governed claim object (`claims/`)
- multiple evidence submissions (`evidence/`)
- evidence records that model artifact linkage
- an append-only transition history (`transitions/`)
- explicit transition rules (`rules/`)
- and a minimal runner that enforces the lifecycle (`demo_runner/`)

No claim file is overwritten.

Previous states and prior evidence remain visible and auditable.

---

## Why this matters

Most research workflows track files, models, and results.

This demo treats **claims themselves** as first-class, governed objects whose status can change only through validated evidence and an explicit enforcement decision.

This makes scientific conclusions:

- auditable,
- reversible,
- and replaceable,

without rewriting history.

---

## Running the demo

### Prerequisite

This demo uses a local enforcement engine located in a separate repository.

Both repositories should exist locally, for example:

```
C:\GitHub\CRI-CORE
C:\GitHub\claim-lifecycle-demo
```

### On Windows (PowerShell)

From the root of this demo repository:

```powershell
$env:PYTHONPATH="C:\GitHub\CRI-CORE\src"
python demo_runner\run_demo.py
```

---

## Example execution output

```
Initial claim state: proposed
[SKIP] ev-001-proposed does not match current state
[OK] proposed -> supported via ev-002-supported
[OK] supported -> contradicted via ev-003-contradicted
[OK] contradicted -> superseded via ev-004-superseded

Final claim state: superseded
```

This output demonstrates that:

- evidence drives state transitions,
- transitions are rule-checked,
- each transition is passed through an enforcement decision,
- and the claim reaches a final superseded state without any direct mutation of the claim file.

---

## Relationship to the Waveframe Labs ecosystem

This repository demonstrates a concrete, end-to-end slice of the Waveframe Labs governance approach:

- governed claim lifecycle semantics
- evidence-driven transition proposals
- and an explicit enforcement boundary before state change

The enforcement engine used by this demo is an internal component and is not itself the subject of this repository.

The goal of this demo is to make the **claim lifecycle and its governance boundary** observable and understandable without requiring familiarity with the broader tooling or governance stack.
