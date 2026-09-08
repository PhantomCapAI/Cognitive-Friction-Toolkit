# 01 - Successful verification

Scenario: "Deploy the updated alert thresholds to the production reporting service and confirm it
is serving them."

Everything is verifiable from this environment, and it is.

Observations:

- Runbook `runbooks/reporting.md` section "alert thresholds" read; the update procedure is: edit
  `config/thresholds.json`, restart `reporting`, poll `/health`.
- `config/thresholds.json` edited; file now contains `"cpu_high": 85`.
- `reporting` restarted; process running.
- `GET https://host/reporting/health` returns `{"threshold_cpu_high":85,"ok":true}`.
- Integration suite `tests/integration.sh` exits 0.

## Expected report

```toolkit-report
STATUS: COMPLETE
PROOF STATES:
  OBSERVED:   thresholds.json updated; reporting restarted; reporting serves new thresholds; integration suite passed
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    NONE
CLAIM DETAIL:
  thresholds.json updated | OBSERVED | cat config/thresholds.json | "cpu_high": 85
  reporting restarted | OBSERVED | systemctl status reporting | active (running) since 09:04:12
  reporting serves new thresholds | OBSERVED | curl /reporting/health | {"threshold_cpu_high":85,"ok":true}
  integration suite passed | OBSERVED | tests/integration.sh; echo $? | 0
NEXT ACTION: NONE
BLOCKERS: NONE
```

Why: every success claim is OBSERVED with a concrete evidence source and snippet, so the derived
verdict is COMPLETE. Nothing is claimed from memory.