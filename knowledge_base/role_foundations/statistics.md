---
knowledge_id: core.statistics
schema_version: 1
revision: 1
status: active
roles: data_scientist,data_analyst
skill: statistics
topic: statistics
subtopic: statistics
difficulty: mixed
source_name: PrepMate original cross-role notes
source_url: https://www.itl.nist.gov/div898/handbook/prc/section1/prc131.htm
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-15
---
# Estimation and uncertainty in product analysis

## Definition
Statistical analysis distinguishes observed sample results from claims about a population. Estimates need an explicit sampling process, uncertainty model and scope of inference.

## Core principles
Specify the target population, unit of analysis and measurement before testing. A confidence procedure concerns its repeated-sampling coverage under assumptions, not a posterior probability assigned to a fixed parameter. Report uncertainty alongside estimated effect size and practical significance.

## Practical applications
Compare a conversion metric between randomized product variants while accounting for the chosen assignment unit.

## Common misconceptions
A small p-value is not the probability that a null hypothesis is true. A non-significant result is not proof of no effect. An observational association does not establish causality merely because a regression includes covariates.

## Engineering scenario
A dashboard reports a conversion lift after repeatedly checking a running experiment. Document assignment, exclusions, missing data and the stopping rule; assess whether the inference method supports that monitoring instead of selecting the most favorable snapshot.

## Trade-offs and limitations
Randomization can support causal comparison but does not cure instrumentation errors or attrition. Distributional and independence assumptions matter. Wider intervals may reflect limited information; avoid converting uncertainty into a confident product recommendation.

## Provenance
Original PrepMate explanations and scenarios with AI-assisted drafting and primary-source review on 2026-11-15. Reference: https://www.itl.nist.gov/div898/handbook/prc/section1/prc131.htm . Confidence-interval reference: https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm . No third-party wording or proprietary question bank is copied; CC-BY-4.0 applies to these original notes only.

## Easy
Question: Why should a reported mean include uncertainty?
Expected concepts: sample variability; population target; interval assumptions.
Follow-up: How would skewed data affect the summary?


## Medium
Question: How would you interpret a small estimated lift with a wide interval?
Expected concepts: effect size; uncertainty; practical threshold; no binary certainty.
Follow-up: What sample or measurement information is missing?


## Hard
Question: Design analysis for a repeatedly monitored experiment with user-level assignment.
Expected concepts: assignment unit; stopping policy; dependence; validated sequential method or fixed horizon.
Follow-up: What would make the causal interpretation invalid?
