---
title: "Claim Lifecycle Demo — End-to-End Governed Claim Example"
filetype: "documentation"
type: "guidance"
domain: "case-study"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Draft"
created: "2026-02-05"
updated: "2026-02-06"

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
  - "CLAIM-LIFECYCLE-DEMO-README-v0.1.0"
---

# Claim Lifecycle Demo

This repository is a minimal, end-to-end demonstration of a governed scientific **claim lifecycle**.

It shows how a single claim moves through the following states:

```  
proposed→ supported → contradicted → superseded 
```  

Each state transition is driven by new evidence, validated against explicit rules, and recorded as an immutable event rather than a manual edit.

This repository exists to demonstrate **claim lifecycle behavior**, not infrastructure or platform tooling.

---

## What is being tracked?

The primary object in this demo is a **claim**.

A claim represents the smallest testable scientific statement that a result depends on.

Example (used in this demo):

> A specific model version achieves at least a specified performance threshold under a declared dataset and evaluation configuration.

This demo focuses on the governance and transition mechanics rather than on executing or validating real experiments.

---

## What is a valid update?

A claim may only change state when a new **evidence submission**:

- references the claim by ID
- declares an intended state transition
- may reference linked artifacts
- satisfies transition rules
- and passes metadata completeness requirements

Only validated evidence can trigger a state change.

---

## Who can submit updates?

Anyone may submit evidence for a claim.

However, claim state is not edited directly.  
State transitions occur only when an evidence submission is accepted by the rule boundary and recorded in the transition log.

---

## What is demonstrated in this repository?

This demo shows:

- a single governed claim object (`claims/`)
- multiple evidence submissions (`evidence/`)
- evidence records that model artifact linkage (evidence/)
- an append-only transition history (`transitions/`)
- explicit transition rules (`rules/`)
- and a minimal runner that enforces the lifecycle (`demo_runner/`)

No claim file is overwritten.

Previous states and prior evidence remain visible and auditable.

---

## Why this matters

Most research workflows track files, models, and results.

This demo treats **claims themselves** as first-class, governed objects whose status can change only through validated evidence and explicit transition rules.

This makes scientific conclusions auditable, reversible, and replaceable without rewriting history.

---

## Repository structure

```  
claim-lifecycle-demo/
├─ claims/
│ └─ claim-001.yaml
│ └─ claim-002.yaml
│
├─ evidence/
│ ├─ ev-001-proposed.yaml
│ ├─ ev-002-supported.yaml
│ ├─ ev-003-contradicted.yaml
│ └─ ev-004-superseded.yaml
│
├─ transitions/
│ └─ transition-log.json
│
├─ rules/
│ └─ transition-rules.yaml
│
├─ demo_runner/
│ └─ run_demo.py
│
├─ CITATION.cff
├─ LICENSE  
├─ .gitignore
└─ README.md  
```  


---

## Running the demo

From the repository root:

```bash
python demo_runner/run_demo.py
```  

This executes the full claim lifecycle and appends transition events to:

``` 
transitions/transition-log.json  
```  

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
- and the claim reaches a final superseded state without any direct mutation of the claim file.  

---  

## Relationship to the Waveframe Labs ecosystem

This repository demonstrates a thin, concrete slice of the Waveframe Labs governance model:  

- claim lifecycle semantics
- evidence-driven state transitions
- and an explicit validation and enforcement boundary
  
The goal is to make the lifecycle itself observable and understandable without requiring familiarity with the broader governance or tooling stack.

---  
