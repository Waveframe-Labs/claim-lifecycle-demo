---
title: "Claim Lifecycle Demo — End-to-End Governed Claim Example"
filetype: "documentation"
type: "guidance"
domain: "case-study"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Draft"
created: "2026-02-05"
updated: "2026-02-05"

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
ai_assistance_details: "AI-assisted drafting of the demo structure and documentation under direct human design, review, and final approval."

dependencies: []

anchors:
  - "CLAIM-LIFECYCLE-DEMO-README-v0.1.0"
---

# Claim Lifecycle Demo

This repository is a minimal, end-to-end demonstration of a governed scientific **claim lifecycle**.

It shows how a single claim moves through the following states:
```
proposed → supported → contradicted → superseded
```

Each state transition is driven by new evidence, validated for completeness, and recorded as an immutable event rather than a manual edit.

This repository exists to demonstrate *behavior*, not infrastructure.

---  

## Running the demo

From the repository root:

```bash
python demo_runner/run_demo.py
```  

The executed lifecycle transitions are appended to:

```
transitions/transition-log.json  
```  

This file provides the immutable history of the claim state changes. 

---  

## What is being tracked?

The primary object in this demo is a **claim**.

A claim represents the smallest testable scientific statement that a result depends on.

Example (used in this demo):

> A specific model version achieves at least a specified performance threshold under a declared dataset and configuration.

All artifacts (runs, metrics, configuration, environment, and assumptions) attach to the claim as lineage.

---

## What is a valid update?

A claim may only change state when a new **evidence submission**:

- references the claim by ID
- includes linked artifacts
- declares an intended transition
- passes metadata completeness checks
- satisfies transition rules

Only validated evidence can trigger a state change.

---

## Who can submit updates?

Anyone may submit evidence for a claim.

However, only evidence that passes validation and rule checks can update the claim’s state.

---

## What is demonstrated in this repository?

This demo shows:

- a single claim defined in `claims/`
- multiple evidence submissions in `evidence/`
- experiment-style artifacts in `artifacts/`
- an append-only transition history in `transitions/`
- explicit transition rules in `rules/`
- a small demo runner that enforces validation and state transitions

Nothing is overwritten.

Previous claim states remain visible and auditable.

---

## Relationship to the Waveframe Labs stack

This repository demonstrates a thin, concrete slice of the Waveframe Labs ecosystem:

- the claim lifecycle semantics
- evidence-driven state transitions
- validation and enforcement boundaries

The goal is to make the lifecycle itself observable and understandable without requiring any prior familiarity with the broader governance stack.

---

## Repository structure
```
claim-lifecycle-demo/
├─ claims/
│   └─ claim-001.yaml
│
├─ evidence/
│   ├─ ev-001-proposed.yaml
│   ├─ ev-002-supported.yaml
│   ├─ ev-003-contradicted.yaml
│   └─ ev-004-superseded.yaml
│
├─ artifacts/
│   ├─ run-001/
│   ├─ run-002/
│   └─ run-003/
│
├─ transitions/
│   └─ transition-log.json
│
├─ rules/
│   └─ transition-rules.yaml
│
├─ demo_runner/
│   └─ run_demo.py
│
└─ README.md
```

---

## How to run the demo

The demo is executed by running a small local runner which:

1. loads the claim
2. loads each evidence submission
3. validates metadata completeness
4. checks transition rules
5. appends an immutable transition event

The runner is intentionally simple so that the lifecycle and enforcement boundaries are easy to inspect.

(Instructions will be added once the runner and files are populated.)

---
