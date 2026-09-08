---
name: cognitive-friction-toolkit
description: >
  No-Promises-Without-Proof discipline for any agent that reports task outcomes. Forces every success
  claim to carry evidence and exactly one proof state (OBSERVED / INFERRED / UNVERIFIED / BLOCKED),
  then derives the completion verdict deterministically. Prevents confident hallucination, silent
  partial failure, rounding up, and hallucinated completion. Model-agnostic. No dependencies.
---

# Cognitive-Friction Toolkit

**Rule: No Promises Without Proof.** A promise is any sentence that asserts a fact or a result.
A report is honest only when every success claim carries evidence and exactly one proof state.

## 1. Proof States

Exactly four. Assign exactly one per claim.

| State | Definition | What it licenses you to say | Minimum acceptable evidence |
|---|---|---|---|
| OBSERVED | Directly demonstrated by evidence you produced or read in this session | "It is the case that X." | Live output you ran or read: command output, file contents, config, log lines, API response you fetched |
| INFERRED | Reasonably derived from OBSERVED evidence; not directly demonstrated | "The evidence is consistent with X; I did not observe X itself." | An explicit chain from OBSERVED items |
| UNVERIFIED | Claim exists; sufficient evidence is absent | "I have no evidence either way." | None, and none claimed |
| BLOCKED | Verification cannot be performed now; the blocker is explicit | "Cannot verify X because <blocker>. Human action: <who> <what>." | A concrete blocker: missing access, tool, or state; or an external dependency not checkable here |

Strength when drawing conclusions: OBSERVED > INFERRED > UNVERIFIED. BLOCKED is not a strength;
it records that verification was attempted and is impossible right now.

Hard constraints:

- Memory is not evidence. Anything claimed from past sessions is UNVERIFIED until observed again.
- Conflicting observations cancel nothing; they keep the claim non-OBSERVED until reconciled.
  Record both observations, then classify the claim BLOCKED while unresolved.
- Never attempted verification -> UNVERIFIED, not BLOCKED. BLOCKED requires the attempt and the reason.
- An OBSERVED claim whose content is false is still OBSERVED; write the claim with the suffix `[FALSE]`.

## 2. Procedure (fixed order)

0. SCOPE - write the success claims: the statements that must be true to call the task done.
1. STOP - no code, no plan, no "sure I can do that", no report yet.
2. READ - consult the authoritative source for each claim (spec, docs, manual, live system).
   Read it; do not recall it.
3. VERIFY - for each claim, try to observe direct evidence. Record the source and the exact
   snippet seen. If verification is impossible, record the blocker.
4. CLASSIFY - label each claim with exactly one proof state.
5. REPORT - emit the fixed response format (Section 3).
6. SELF-CHECK - every OBSERVED claim must trace to evidence you personally produced or read this
   session; otherwise downgrade it. Re-run the verdict rules; a status that contradicts the counts
   is a format error.

## 3. Response format (fixed)

Every report uses exactly these fields. Unused fields say `NONE`. A claim your observation shows to
be false is written `claim [FALSE]`.

    STATUS: COMPLETE | PARTIAL | FAILED | BLOCKED
    PROOF STATES:
      OBSERVED:   <claim; claim | NONE>
      INFERRED:   <claim; claim | NONE>
      UNVERIFIED: <claim; claim | NONE>
      BLOCKED:    <claim = blocker; claim = blocker | NONE>
    CLAIM DETAIL:
      <claim> | <state> | <evidence source you observed> | <exact snippet>
    NEXT ACTION: <who> <does what> <by when> | NONE
    BLOCKERS: <none | claim -> <who> must <action>>

Verdict is derived, not chosen. Count from `CLAIM DETAIL`:

    f  = OBSERVED claims carrying [FALSE]
    t  = OBSERVED claims without [FALSE]
    b  = BLOCKED claims
    u  = UNVERIFIED + INFERRED claims

| Condition | STATUS |
|---|---|
| f > 0 | FAILED |
| f == 0 and u + b == 0 and t > 0 | COMPLETE |
| f == 0 and t > 0 | PARTIAL |
| f == 0 and b > 0 | BLOCKED |
| else (only INFERRED / UNVERIFIED) | PARTIAL |

Consequences: an empty OBSERVED list can never yield COMPLETE. Any UNVERIFIED, conflicting, or
BLOCKED success claim forbids COMPLETE. A status that contradicts the counts is a format error.

Consistency rules:

- CLAIM DETAIL carries exactly the success claims identified in SCOPE (Step 0), and nothing else.
  Supporting observations (commands that ran, setup steps, pre-flight checks) belong in the report
  narrative, not in CLAIM DETAIL; listing them as claims makes verdicts ambiguous and gameable.
- Every claim listed under PROOF STATES must appear exactly once in CLAIM DETAIL, with the same
  state, and with `evidence` non-empty for OBSERVED claims.
- Never use the marker `[FALSE]` in a claim text; it is reserved for observed contradictions.

## 4. Uncertainty

- "Should work", "I think it ran", "docs say so", "I remember" are UNVERIFIED or INFERRED -
  never OBSERVED.
- An external dependency that cannot be checked from this environment: mark exactly that claim
  BLOCKED and report the rest at their true states; do not collapse the whole task to BLOCKED.
- If the evidence permits two readings, say so; do not pick the optimistic one and stop checking.

## 5. Failure and escalation

- Attempted and the outcome contradicts a success claim -> FAILED; state what was observed. Do not
  retry blindly; propose the retry as NEXT ACTION and wait for approval.
- Succeeded partly -> PARTIAL; list done vs not-done; never round up.
- BLOCKED on human action -> STOP at the blocker. State it, state who must do what, and do not work
  around it. Do not silently adopt a narrower scope; propose it as NEXT ACTION for confirmation.
- Missing tools or tokens surface at SCOPE and again at VERIFY: classify the affected claims BLOCKED
  for access and say exactly what is missing.
- Never claim completion from the absence of errors. An absent error message is not evidence that a
  thing happened.

## 6. Anti-patterns

| Anti-pattern | Looks like | Honest form |
|---|---|---|
| Confident hallucination | "Deployed." without running anything | UNVERIFIED or BLOCKED until observed |
| Looks-done theater | "Done" because a file exists, exit code was 0, or the last command was silent | Name the exact observation standing as evidence; if none, not done |
| Silent partial | One sub-step never ran, reported as success | PARTIAL with the gap listed |
| Rounding up | A tail of INFERRED claims presented as part of DONE | PARTIAL; INFERRED stays INFERRED |
| Trust-me | "I'm sure", "this is fine" | Downshift to UNVERIFIED; observe or say so |
| Workflow skip | Claims full while CLAIM DETAIL is empty | Format violation; fails self-check |
| Wild averaging | Two conflicting outputs merged into a middle value | Report both; claim BLOCKED until reconciled |
| False denial | A real failure hidden as "could not verify" | Apply the verdict rules; FAILED vs BLOCKED is derived |

## 7. Validatability

The response format and verdict rules are machine-checkable. This repository ships a stdlib-only
validator (`tests/validator.py`) that computes the verdict from CLAIM DETAIL lines, checks every
example and a set of adversarial fixtures, and fails on any mismatch or missing field. A report that
passes the check is format-conformant; one that fails must be corrected before it is presented as
conformant.