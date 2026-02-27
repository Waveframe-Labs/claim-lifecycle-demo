---
title: "Finance SOX Scenario Overview (Kernel Enforcement Use Case)"
filetype: "documentation"
type: "guidance"
domain: "case-study"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Active"
created: "2026-02-26"
updated: "2026-02-26"

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
ai_assistance_details: "AI-assisted drafting of a business-facing scenario walkthrough that maps a SOX-aligned internal control surface (threshold approvals, separation of duties, conflict-of-interest) onto CRI-CORE kernel enforcement behavior in the claim-lifecycle demo."

dependencies:
  - "./claims/finance-claim-001.yaml"
  - "./contracts/finance-contract-v1.yaml"
  - "./run_finance_demo.py"

anchors:
  - "FINANCE-SOX-v0.1.0"
---

# Finance SOX Scenario Overview (Kernel Enforcement Use Case)

## Purpose

This scenario explains—at a business level—how a deterministic enforcement kernel can **block** a high-risk financial state mutation unless it satisfies a declared internal control contract. The objective is not to claim legal compliance, but to demonstrate a **structural control mechanism** that supports SOX-aligned internal control requirements by enforcing approvals and accountability at the point of operational commitment.

## Scenario Summary

An AI agent recommends reallocating **$1.2M** between cost centers (Marketing → R&D). The organization has a SOX-aligned internal control contract that requires:

- **Threshold control:** Any financial mutation **> $500k** requires additional approvals.
- **Separation of duties:** The initiator may not be the approver; approvals must be from distinct identities.
- **Role-based approvals:** Required approvers include **Finance Controller** and **CFO**.
- **Conflict-of-interest control:** A flagged conflict blocks approval until resolved.
- **Audit defensibility:** The enforcement decision and required inputs are logged for replayability and review.

The kernel enforces these controls deterministically. If the contract requirements are not satisfied, the mutation is **denied** (commit not allowed).

## Roles and Ownership

- **AI Agent (Proposer):** Produces a recommendation and a proposed mutation; cannot approve.
- **Department Head (Initiator):** Submits the change request into the governed workflow.
- **Finance Controller (Control Approver):** Required approval role for high-value mutations.
- **CFO (Executive Approver):** Required approval role for high-value mutations.
- **Audit Consumer (Implicit):** Any party that needs to review what happened (leadership, auditors, regulators).

## What “State Mutation” Means Here

**State mutation** is the operational act that changes the system of record. In this scenario, it is the commitment of a budget reallocation instruction that would alter a financial ledger, planning system, or equivalent operational store.

The kernel does not interpret financial semantics. It only evaluates whether the proposed mutation is allowed **under the declared contract surface** at the time of the attempt.

## Contract Controls (Business Interpretation)

### 1) Threshold Control (> $500k)
Because $1.2M exceeds the threshold, the contract requires:
- Finance Controller approval
- CFO approval

### 2) Separation of Duties
The contract requires:
- Approvals must come from **distinct identities**
- The initiator cannot approve their own change

### 3) Conflict of Interest
The contract requires:
- If any required approver is flagged with an active conflict-of-interest, approval is blocked until resolved (or alternate approver is used).

## Walkthrough (Agent + Human Perspectives)

### Attempt 1 — Missing Required Approval (Denied)
**Agent perspective**
- Agent proposes: “Reallocate $1.2M Marketing → R&D”
- Claim is created with threshold classification: “> $500k”
- Contract surface loads required approvals

**Human perspective**
- Initiator submits request
- Finance Controller approves
- CFO approval missing

**Kernel decision**
- **DENY**
- Reason: threshold control requires CFO approval for mutations > $500k
- Operational commitment is blocked; no state mutation occurs

### Attempt 2 — Conflict-of-Interest Present (Denied)
**Human perspective**
- CFO provides approval
- CFO has an active conflict-of-interest flag set (e.g., declared conflict on this allocation category)

**Kernel decision**
- **DENY**
- Reason: conflict-of-interest policy not satisfied
- Operational commitment remains blocked

### Attempt 3 — Conflict Resolved + Distinct Approvals (Allowed)
**Human perspective**
- Conflict-of-interest flag is cleared (or alternate CFO approver is used)
- Finance Controller approval present
- CFO approval present
- Initiator remains distinct from approvers

**Kernel decision**
- **ALLOW**
- Mutation is permitted to commit
- Immutable run/audit record is produced capturing the decision and inputs

## Why This Matters to Business Leaders

This enforcement model provides:

- **Signal:** Clearly shows what is required before responsibility attaches.
- **Ownership:** Makes decision ownership explicit by role and identity.
- **Velocity with controls:** AI can propose quickly; mutation remains structurally constrained.
- **Audit defense:** Decisions are replayable and defensible under declared contract versions.

## What This Scenario Is Not

- Not a legal compliance engine
- Not a SOX implementation
- Not an automated truth verifier
- Not a replacement for organizational policy or governance

It is a demonstration of **structural enforcement** at the boundary where the system would otherwise mutate state.

## How This Maps to the Runnable Demo

The runnable demo in this folder uses:

- `claims/finance-claim-001.yaml` to represent the proposed mutation and attached approvals
- `contracts/finance-contract-v1.yaml` to represent the declared internal control surface
- `run_finance_demo.py` to invoke the kernel and show deny/allow outcomes based on the contract