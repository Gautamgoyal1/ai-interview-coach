---
knowledge_id: core.incident_response
schema_version: 1
revision: 1
status: active
roles: cybersecurity_analyst
skill: incident response
topic: incident_response
subtopic: incident_response
difficulty: mixed
source_name: PrepMate original cross-role notes
source_url: https://csrc.nist.gov/pubs/sp/800/61/r3/final
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-15
---
# Evidence-preserving incident triage

## Definition
Incident response coordinates detection, investigation, containment and recovery within an organization's broader cybersecurity risk management. Actions should be authorized, recorded and proportional to impact.

## Core principles
Establish incident scope from evidence and preserve relevant logs with timing and provenance. Coordinate containment with service owners and an approved response plan. Record hypotheses separately from confirmed observations, and define recovery checks before closing the incident.

## Practical applications
Investigate suspicious access to stored interview reports without copying private answers into an unrestricted incident chat.

## Common misconceptions
One alert is not proof that an account is compromised. Blocking an address does not establish complete containment. Deleting suspicious data can destroy evidence needed to understand scope.

## Engineering scenario
Several downloads use one account from unusual locations. Preserve access logs and request identifiers, check token/session activity and sharing policies, consult the incident owner and apply approved containment. Verify legitimate workflows during recovery.

## Trade-offs and limitations
Fast containment can disrupt users or destroy volatile evidence if performed carelessly. Collection must follow applicable policy and access rules. A tabletop exercise is useful preparation but does not prove that production detection or recovery works.

## Provenance
Original PrepMate explanations and scenarios with AI-assisted drafting and primary-source review on 2026-11-15. Reference: https://csrc.nist.gov/pubs/sp/800/61/r3/final . No third-party wording or proprietary question bank is copied; CC-BY-4.0 applies to these original notes only.

## Easy
Question: What should an analyst record when triaging an alert?
Expected concepts: time; source; scope; evidence; uncertainty; authorization.
Follow-up: Which user data should be minimized?


## Medium
Question: How would you investigate unusual report downloads?
Expected concepts: correlated events; identity context; evidence preservation; approved containment.
Follow-up: What alternative benign explanation should you test?


## Hard
Question: Plan containment and recovery when a shared service token may be exposed.
Expected concepts: scope; dependency mapping; revocation; evidence; recovery validation; owner coordination.
Follow-up: How do you verify containment without assuming the alert disappeared?
