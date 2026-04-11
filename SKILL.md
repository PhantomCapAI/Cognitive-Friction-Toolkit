---
name: phantom-ops-check
description: >
  Mandatory pre-flight check for ANY infrastructure task. Forces AI to stop, read the operating manual,
  verify system state, and respond honestly before taking action. Prevents confident hallucination,
  workflow bypass, silent failure, and stall theater.
---

# Phantom Ops Check — Stop Before You Speak

## Purpose

This skill exists because LLMs default to confident action. That default is dangerous when real money, live services, and a solo operator are on the line. This skill forces a hard pause: read the operating manual, verify the current state, and only THEN respond.

## Rule: No Promises Without Proof

Before you tell the user you can do something, confirm:

1. **The service exists and is in the state you think it is.** Check the operating manual. If it says DORMANT, it's dormant. If it says NOT DEPLOYED, it's not deployed.
2. **The env vars exist.** Don't assume keys are set.
3. **The workflow is what you think it is.** Check the correct sequence before acting.
4. **You've read the docs.** If the task touches any external service — read the official docs first. Not from memory. Actually read them.

## Procedure

### Step 0 — KNOW WHERE YOU ARE
Check your environment. Do you have the tools, tokens, and access to do what's being asked? If not, say so immediately. Don't try and fail.

### Step 1 — STOP
Do not write code. Do not suggest a plan. Do not say "sure, I can do that."

### Step 2 — READ
Find the section of the operating manual relevant to the task. Read current state, known failure modes, workflow rules, required env vars.

### Step 3 — VERIFY
Cross-reference the request against what's actually possible right now. Look for blockers, wrong workflows, missing pieces.

### Step 4 — RESPOND HONESTLY
If the task is clear and unblocked, execute. If there's a blocker:
- State what's blocked and why
- State what requires human action
- State what you CAN do right now
- Do NOT offer to "work around" blockers that require human action

## Anti-Patterns This Skill Kills

| Bad Pattern | What Happens | Fix |
|-------------|-------------|-----|
| Confident hallucination | Says a service is running when it's not | Forces state check |
| Workflow bypass | Skips required steps | Forces workflow verification |
| Silent failure | Agrees to a plan it can't execute | Forces blocker identification |
| Trial and error | Writes code without reading docs | Forces doc read first |
| Stall theater | Pretends to work on something async | Forces immediate honest status |
| Environment blindness | Tries actions without checking access | Forces environment check |
