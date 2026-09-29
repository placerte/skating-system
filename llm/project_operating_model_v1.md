---
id: BLK-CORE-PROJECT-OPERATING-MODEL-V1
name: Project Operating Model
type: workflow
scope: core
version: 1.0
status: active
revised: 2026-03-20
summary: Defines roles, authority, lifecycle, and governing rules for all projects.
tags: [core, governance]
---

# Project Operating Model (v1)

This document defines the **rules of the world** for all projects using this block system.

It is the highest-level artifact and governs how all other blocks interact.

---

## Purpose

Establish a strict, contract-first operating model where:
- written artifacts are authoritative
- roles are clearly defined
- ambiguity is not tolerated during execution

---

## Core Principle

If it is not written in an artifact, it does not exist for execution.

---

## Roles

### Sponsor / Owner
- Defines real-world objective
- Approves major decisions
- Owns outcomes

### Design Authority
- Translates intent into artifacts
- Defines scope and constraints
- Produces handoffs

### Execution Agent
- Executes strictly from artifacts
- Does not invent scope
- Reports blockers

### Reviewer
- Validates outputs against artifacts
- Confirms completion criteria

---

## Authority Order

When sources conflict:

1. Handoff
2. Operating rules (this file)
3. Decision log
4. Project documentation
5. Chat

If conflict cannot be resolved -> STOP and report.

---

## Execution Model

Execution is **artifact-driven**.

- Handoff defines the task
- Executor performs work
- Deliverables are produced
- Validation confirms completion

No step relies on implicit understanding.

---

## Lifecycle

Default project stages:

1. Intake
2. Exploration
3. Structuring
4. Decision-making
5. Handoff
6. Execution
7. Review
8. Continuation or closure

Stages may be skipped, but not reinterpreted.

---

## Artifact Philosophy

Artifacts must be:
- explicit
- minimal
- unambiguous
- durable

Avoid:
- implicit assumptions
- narrative explanations
- redundant content

---

## Completion Principle

Completion is defined only by:
- required deliverables exist
- validation criteria are satisfied

Effort is irrelevant.

---

## Hard Rules

- Artifacts over chat
- No scope invention
- Stop on ambiguity
- Deliverable-driven completion
- Separation of concerns

---

## Specialization

This model is the parent layer.

Specialized workflows (app-dev, infra, research):
- may add constraints
- must not contradict this model

---

## Final Rule

If execution requires guessing intent, the system has failed.

Stop and report.
