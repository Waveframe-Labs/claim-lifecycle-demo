<!--
title: "Claim lifecycle demo runner"
filetype: "operational"
type: "non-normative"
domain: "case-study"
version: "0.1.0"
doi: "TBD-0.1.0"
status: "Draft"
created: "2026-02-06"
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
ai_assistance_details: "AI-assisted scaffolding of the claim lifecycle demo runner logic under direct human design, review, and final approval."
dependencies:
  - "../claims/claim-001.yaml"
  - "../rules/transition-rules.yaml"
  - "../transitions/transition-log.json"
anchors:
  - "CLAIM-DEMO-RUNNER-v0.1.0"
-->

import json
import yaml
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

CLAIM_PATH = ROOT / "claims" / "claim-001.yaml"
RULES_PATH = ROOT / "rules" / "transition-rules.yaml"
LOG_PATH = ROOT / "transitions" / "transition-log.json"

EVIDENCE_PATHS = [
    ROOT / "evidence" / "ev-001-proposed.yaml",
    ROOT / "evidence" / "ev-002-supported.yaml",
    ROOT / "evidence" / "ev-003-contradicted.yaml",
    ROOT / "evidence" / "ev-004-superseded.yaml",
]


def load_yaml_with_front_matter(path):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No metadata block found in {path}")
    body = parts[2]
    return yaml.safe_load(body)


def load_transition_log():
    text = LOG_PATH.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    body = parts[2]
    return json.loads(body)


def write_transition_log(entries):
    header, _, rest = LOG_PATH.read_text(encoding="utf-8").partition("---\n")
    _, _, after = rest.partition("---\n")

    new_body = json.dumps(entries, indent=2)

    content = f"{header}---\n{after.split('---',1)[0]}---\n{new_body}"
    LOG_PATH.write_text(content, encoding="utf-8")


def transition_allowed(rules, from_state, to_state):
    for rule in rules["allowed_transitions"]:
        if rule["from"] == from_state and rule["to"] == to_state:
            return True
    return False


def main():
    claim = load_yaml_with_front_matter(CLAIM_PATH)
    rules = load_yaml_with_front_matter(RULES_PATH)
    log = load_transition_log()

    current_state = claim["current_state"]

    print(f"Initial claim state: {current_state}")

    for ev_path in EVIDENCE_PATHS:
        evidence = load_yaml_with_front_matter(ev_path)

        intended = evidence["intended_transition"]
        from_state = intended["from"]
        to_state = intended["to"]

        if from_state != current_state:
            print(f"[SKIP] {evidence['evidence_id']} does not match current state")
            continue

        if not transition_allowed(rules, from_state, to_state):
            print(f"[REJECT] Transition {from_state} -> {to_state} not allowed")
            continue

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "claim_id": evidence["claim_id"],
            "evidence_id": evidence["evidence_id"],
            "from": from_state,
            "to": to_state,
        }

        log.append(entry)
        current_state = to_state

        print(f"[OK] {from_state} -> {to_state} via {evidence['evidence_id']}")

    write_transition_log(log)

    print("\nFinal claim state:", current_state)


if __name__ == "__main__":
    main()
