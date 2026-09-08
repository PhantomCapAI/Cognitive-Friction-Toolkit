# 07 - Looks-done traps

Scenario: "Ship the new token allowlist to the production gateway."

Outwardly everything looks successful - and it is all fake.

Observations:

- `cp allowlist.json /srv/gateway/` exits `0`.
- The destination file exists.
- Reading the destination file shows it is **empty** - the source was a truncated file and `cp`
  copied it faithfully.
- A health probe returns `HTTP 200`, but its body is the maintenance page, not the gateway status.

An agent that grades on exit codes, file existence, or "it didn't error" would report success. All
three of those observations are present and all three are consistent with a broken deploy. The
success claims are positively contradicted by file contents the agent itself read.

## Expected report

```toolkit-report
STATUS: FAILED
PROOF STATES:
  OBSERVED:   allowlist file on gateway is non-empty [FALSE]; gateway serves the allowlist [FALSE]
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    NONE
CLAIM DETAIL:
  allowlist file on gateway is non-empty [FALSE] | OBSERVED | read -r /srv/gateway/allowlist.json | empty; 0 bytes
  gateway serves the allowlist [FALSE] | OBSERVED | curl -s -o /dev/null -w '%{http_code} %{size_download}' /gateway/health | 200 412; body is maintenance page
NEXT ACTION: agent diffs the source allowlist against prod, fixes the truncated source, re-deploys, and re-verifies by content and body
BLOCKERS: NONE
```

Why: the apparent signals - exit 0, file present, HTTP 200 - are present but carry no weight.
f > 0, so the verdict is FAILED. The claims are demonstrated false from observed file contents and
response bodies. "Looks done" is the exact state the procedure exists to reject: absence of an
error message is not evidence that anything happened.