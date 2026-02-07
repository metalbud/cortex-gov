# AI-Assisted Project Automation System

## Purpose
This repository defines a document-driven workflow for human-led, AI-executed projects.
Humans define intent, constraints, and outcomes. AI agents execute tasks under strict rules.

The project document is the single source of truth.

## Core Principles
- Humans decide what and why
- AI decides how, within constraints
- No task is complete without verification
- Evidence is required for all status changes

## Roles
Human:
- Defines goals, constraints, priorities
- Resolves ambiguity
- Approves outcomes

AI Agent:
- Selects tasks
- Executes work
- Produces evidence
- Updates task status accurately

## Status Flow
TODO → IN_PROGRESS → VERIFY → DONE (or BLOCKED)

DONE is never allowed directly from IN_PROGRESS.
