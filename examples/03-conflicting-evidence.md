# 03 - Conflicting evidence

Scenario: "Confirm the production reporting service accepts API keys in the new format."

Two authoritative sources disagree.

Observations:

- Runbook `runbooks/reporting.md` v2026-03, section "auth", states: "API keys use the format
  `k-<24 hex>` and are accepted on the reporting endpoints."
- `GET https://host/reporting/status` with a freshly issued key in exactly that format returns
  `HTTP 401` with body `invalid key`.

Both observations were made directly. They cannot both be satisfied by "the key format works on
prod", and neither observation is strong enough to prove the claim false by itself (the key could
be unissued for an unrelated reason). The agent must not pick a side, average the two, or guess.

## Expected report

```toolkit-report
STATUS: BLOCKED
PROOF STATES:
  OBSERVED:   NONE
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    reporting accepts new-format API keys = conflicting observations (runbook v2026-03 says the format is accepted, live API returns HTTP 401 for a matching-format key)
CLAIM DETAIL:
  reporting accepts new-format API keys | BLOCKED | runbook runbooks/reporting.md v2026-03 p.12 AND curl /reporting/status (HTTP 401, body "invalid key") | two observations, mutually incompatible
NEXT ACTION: CTO reconciles the runbook against the live API (check key issuance and auth config), then agent re-verifies
BLOCKERS: reporting accepts new-format API keys -> CTO must determine which of the two sources describes the live system
```

Why: conflicting evidence is not a middle value and not a verdict; it is a blocker. t = 0, b = 1,
so the derived verdict is BLOCKED. The two observations are preserved verbatim so a human can
reconcile them without re-running anything.