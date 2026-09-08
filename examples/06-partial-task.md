# 06 - Partial task

Scenario: "Rename 50 configuration files from `*-old.yaml` to `*-new.yaml` per the mapping in
`mapping.csv`, then run the validation suite."

The mapping is applied in two batches. Batch A (files 1-30) is renamed and cross-checked. Batch B
(files 31-50) is not started: the agent runs out of time in the requested window.

Observations:

- Files 1-30 confirmed present with new names.
- `tar` listing snapshot confirms 30 renames on disk.
- No rename command was ever run for files 31-50; they still exist under old names.

The agent reports what actually happened. It does not say "all 50 renamed" and it does not claim the
validation suite passed when it was never run.

## Expected report

```toolkit-report
STATUS: PARTIAL
PROOF STATES:
  OBSERVED:   batch A (files 1-30) renamed
  INFERRED:   NONE
  UNVERIFIED: validation suite passed; batch B (files 31-50) renamed
  BLOCKED:    NONE
CLAIM DETAIL:
  batch A (files 1-30) renamed | OBSERVED | find config/ -name '*-new.yaml' | wc -l | 30
  batch B (files 31-50) renamed | UNVERIFIED | NONE | NONE
  validation suite passed | UNVERIFIED | NONE | NONE
NEXT ACTION: agent resumes with batch B when the time window reopens, then runs the validation suite and reports
BLOCKERS: NONE
```

Why: some success claims are OBSERVED, others remain UNVERIFIED, and none is contradicted, so the
derived verdict is PARTIAL. The done portion and the undone portion are listed separately; nothing
is rounded up to COMPLETE.