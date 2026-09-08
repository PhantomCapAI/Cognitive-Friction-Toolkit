# Cognitive-Friction Toolkit

**No Promises Without Proof.**

A tiny, portable, dependency-free discipline for agent operations. It forces every success claim to
be paired with evidence and one explicit proof state, then derives the completion verdict
deterministically. The result is reports that can be audited, and failures that are visible instead
of silent.

## Proof states

| State | Meaning |
|---|---|
| OBSERVED | directly demonstrated by evidence produced or read this session |
| INFERRED | derived from OBSERVED evidence, not demonstrated |
| UNVERIFIED | claim exists; evidence absent |
| BLOCKED | verification impossible now; blocker explicit |

A task is COMPLETE only when every success claim is OBSERVED. Any UNVERIFIED, conflicting, or
BLOCKED success claim makes COMPLETE impossible. Details, the fixed response format, and the
deterministic verdict rules live in `SKILL.md`.

## What this is not

This is a set of rules and a checkable response format - not software infrastructure. There is no
backend, API, database, telemetry, or monitoring, and no runtime dependencies. The only executable
is a stdlib-only validator used to test the format itself.

## Using the skill

1. Copy `SKILL.md` into your agent skill directory, e.g. `.agents/skills/cognitive-friction-toolkit/SKILL.md`.
2. Run its procedure for any task whose outcome will be reported as a claim.

Procedure, in fixed order:

    SCOPE -> STOP -> READ -> VERIFY -> CLASSIFY -> REPORT -> SELF-CHECK

Response header, from `SKILL.md` Section 3:

    STATUS: COMPLETE | PARTIAL | FAILED | BLOCKED
    PROOF STATES: OBSERVED / INFERRED / UNVERIFIED / BLOCKED
    CLAIM DETAIL: <claim> | <state> | <evidence> | <snippet>
    NEXT ACTION / BLOCKERS

The status is derived from the counts of claims; it is never chosen freely. A report whose status
contradicts its own CLAIM DETAIL is malformed.

## Examples

`examples/` contains eight worked scenarios with the expected toolkit report for each:

1. `01-successful-verification.md` - every claim observed; COMPLETE.
2. `02-incomplete-evidence.md` - key claim never verified; PARTIAL, refuses COMPLETE.
3. `03-conflicting-evidence.md` - two observations disagree; BLOCKED pending reconciliation.
4. `04-blocked-verification.md` - missing access; BLOCKED with an explicit human action.
5. `05-failed-task.md` - attempt ran, outcome contradicted; FAILED.
6. `06-partial-task.md` - part of the work done; PARTIAL, no rounding up.
7. `07-looks-done-traps.md` - exit-code-zero "success" that is a contradiction; FAILED, not done.
8. `08-uncheckable-external-dependency.md` - local step verified, external system uncheckable; PARTIAL.

## Validation

```bash
python tests/validator.py
```

Zero dependencies (standard library only). Exit code `0` means every example and adversarial fixture
conforms to the format and verdict rules; `1` means at least one violation, listed with its location.
The validator fails closed: deleting an example, dropping a field, or flipping a status to make a
fixture pass is reported as a failure.

## Install

```bash
git clone https://github.com/PhantomCapAI/Cognitive-Friction-Toolkit.git
cd Cognitive-Friction-Toolkit
# Zero dependencies. Zero configuration.
```

## When to use it

- Any task where an agent might claim success without evidence.
- Multi-step workflows requiring auditability: deployments, API calls, file edits, money movements.
- Any environment where "trust but verify" is the operating assumption.

## When not to use it

- One-shot tasks where no claim of result is made.
- Tasks that explicitly disclaim verification (e.g. creative writing).
- Environments with no verification mechanism at all - in that case the toolkit itself becomes the
  minimum viable verification layer, and uncheckable claims must be reported as BLOCKED, not as done.

## Compatibility

Model-agnostic. Any tool-using agent can follow the procedure; there are no model-specific
instructions or proprietary features. All verification is command- and file-based, portable across
operating systems, and depends on no external service.

## Contributing

1. Fork the repository, create a feature branch.
2. Make changes following the procedure above (SCOPE through SELF-CHECK).
3. Run `python tests/validator.py` and include its output.
4. Submit a pull request whose own description follows the response format, so the PR's claims are
   verified like any other claims.
5. If you change a rule, change the examples, the adversarial fixtures, or both - a rule without a
   test is a promise without proof.

## License

MIT. See `LICENSE`. Provided without warranty, as-is, under the same terms every proof in this
toolkit is subject to: no claim stands without evidence.