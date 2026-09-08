"""Validates the Cognitive-Friction Toolkit response format and verdict rules. Stdlib only."""

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"

REQUIRED_EXAMPLES = [
    "01-successful-verification.md",
    "02-incomplete-evidence.md",
    "03-conflicting-evidence.md",
    "04-blocked-verification.md",
    "05-failed-task.md",
    "06-partial-task.md",
    "07-looks-done-traps.md",
    "08-uncheckable-external-dependency.md",
]

ALLOWED_STATUS = {"COMPLETE", "PARTIAL", "FAILED", "BLOCKED"}
ALLOWED_STATES = {"OBSERVED", "INFERRED", "UNVERIFIED", "BLOCKED"}

REQUIRED_HEADERS = [
    "STATUS",
    "PROOF STATES",
    "OBSERVED",
    "INFERRED",
    "UNVERIFIED",
    "BLOCKED",
    "CLAIM DETAIL",
    "NEXT ACTION",
    "BLOCKERS",
]


def norm(claim):
    c = claim.strip()
    if c.endswith("[FALSE]"):
        c = c[: -len("[FALSE]")].rstrip()
    return c


def extract_blocks(text):
    blocks = []
    in_block = False
    buf = []
    for line in text.splitlines():
        s = line.strip()
        if not in_block:
            if s == "```toolkit-report":
                in_block = True
                buf = []
        else:
            if s.startswith("```"):
                in_block = False
                blocks.append("\n".join(buf))
            else:
                buf.append(line)
    return blocks


def parse_report(block):
    lines = block.splitlines()
    idx = {}
    for i, line in enumerate(lines):
        s = line.strip()
        for key in REQUIRED_HEADERS:
            if key not in idx and s.startswith(key + ":"):
                idx[key] = i

    def value_of(key):
        if key not in idx:
            return ""
        s = lines[idx[key]].strip()
        return s.split(":", 1)[1].strip() if ":" in s else ""

    status = value_of("STATUS").upper()
    next_action = value_of("NEXT ACTION")
    blockers = value_of("BLOCKERS")

    proof = {st: [] for st in ALLOWED_STATES}
    start = idx.get("PROOF STATES")
    end = idx.get("CLAIM DETAIL")
    sec = lines[start + 1 : end] if (start is not None and end is not None and end > start) else []
    for line in sec:
        s = line.strip()
        for st in ALLOWED_STATES:
            if s.startswith(st + ":"):
                val = s[len(st) + 1 :].strip()
                if val.upper() == "NONE":
                    continue
                for entry in (e.strip() for e in val.split(";") if e.strip()):
                    claim = entry
                    blocker = None
                    if st == "BLOCKED" and "=" in entry:
                        claim, blocker = entry.split("=", 1)
                        claim, blocker = claim.strip(), blocker.strip()
                    proof[st].append({"claim": claim, "blocker": blocker})

    details = []
    start, end = idx.get("CLAIM DETAIL"), idx.get("NEXT ACTION")
    sec = lines[start + 1 : end] if (start is not None and end is not None and end > start) else []
    for line in sec:
        s = line.strip()
        if not s or "|" not in s:
            continue
        parts = [p.strip() for p in s.split("|", 3)]
        if len(parts) == 4 and parts[1] in ALLOWED_STATES:
            details.append(
                {"claim": parts[0], "state": parts[1], "evidence": parts[2], "snippet": parts[3]}
            )

    return {
        "status": status,
        "proof": proof,
        "details": details,
        "next_action": next_action,
        "blockers": blockers,
        "headers": set(idx.keys()),
    }


def derive_status(f, t, b, u):
    if f > 0:
        return "FAILED"
    if f == 0 and u + b == 0 and t > 0:
        return "COMPLETE"
    if t > 0:
        return "PARTIAL"
    if b > 0:
        return "BLOCKED"
    return "PARTIAL"


def check_report(parsed):
    v = []

    for key in REQUIRED_HEADERS:
        if key not in parsed["headers"]:
            v.append("missing required header: " + key)

    if parsed["status"] not in ALLOWED_STATUS:
        if parsed["status"]:
            v.append("invalid STATUS: " + parsed["status"])
        return v

    details = parsed["details"]
    proof = parsed["proof"]

    seen = {}
    for st, entries in proof.items():
        for e in entries:
            n = norm(e["claim"])
            if n in seen and seen[n] != st:
                v.append("claim appears in more than one state: " + n)
            seen.setdefault(n, st)

    counts = Counter(norm(d["claim"]) for d in details)
    for n, c in counts.items():
        if c > 1:
            v.append("duplicate claim in CLAIM DETAIL: " + n)

    for st, entries in proof.items():
        for e in entries:
            n = norm(e["claim"])
            matches = [d for d in details if norm(d["claim"]) == n]
            if not matches:
                v.append("claim in PROOF STATES missing from CLAIM DETAIL: " + n)
            for m in matches:
                if m["state"] != st:
                    v.append(
                        "claim '{}' state mismatch: PROOF STATES={}, CLAIM DETAIL={}".format(n, st, m["state"])
                    )

    for d in details:
        n = norm(d["claim"])
        found = any(norm(e["claim"]) == n for st, entries in proof.items() if st == d["state"] for e in entries)
        if not found:
            v.append("claim in CLAIM DETAIL missing from PROOF STATES: " + n)
        if d["state"] == "OBSERVED":
            evidence = d["evidence"].strip()
            if not evidence or evidence.upper() == "NONE":
                v.append("OBSERVED claim has no evidence: " + n)
        if d["state"] != "OBSERVED" and d["claim"].strip().endswith("[FALSE]"):
            v.append("[FALSE] only permitted on OBSERVED claims: " + n)

    f = t = b = u = 0
    for d in details:
        if d["state"] == "OBSERVED":
            if d["claim"].strip().endswith("[FALSE]"):
                f += 1
            else:
                t += 1
        elif d["state"] == "BLOCKED":
            b += 1
        else:
            u += 1

    derived = derive_status(f, t, b, u)
    if derived != parsed["status"]:
        v.append(
            "STATUS '{}' contradicts derived status '{}' (f={}, t={}, b={}, u={})".format(
                parsed["status"], derived, f, t, b, u
            )
        )

    return v


def check_expectations(prefix, parsed):
    v = []
    status = parsed["status"]
    details = parsed["details"]

    def has_state(st):
        return any(d["state"] == st for d in details)

    if prefix == "01":
        if status != "COMPLETE":
            v.append("ex01 expects COMPLETE")
        if any(d["state"] != "OBSERVED" for d in details):
            v.append("ex01 expects every claim OBSERVED")
    elif prefix == "02":
        if status != "PARTIAL":
            v.append("ex02 expects PARTIAL")
        if not has_state("UNVERIFIED"):
            v.append("ex02 expects an UNVERIFIED claim")
    elif prefix == "03":
        if status != "BLOCKED":
            v.append("ex03 expects BLOCKED")
        if has_state("OBSERVED"):
            v.append("ex03 expects no OBSERVED claims")
        blk = [d for d in details if d["state"] == "BLOCKED"]
        if not blk:
            v.append("ex03 expects a BLOCKED claim")
        else:
            blockers = [e["blocker"] for e in parsed["proof"]["BLOCKED"] if e.get("blocker")]
            if not any(blocker and "conflicting" in blocker.lower() for blocker in blockers):
                v.append("ex03 expects the BLOCKED claim to name the conflict")
    elif prefix == "04":
        if status != "BLOCKED":
            v.append("ex04 expects BLOCKED")
        if not parsed["blockers"].strip() or parsed["blockers"].strip().upper() == "NONE":
            v.append("ex04 expects a non-empty BLOCKERS line")
    elif prefix == "05":
        if status != "FAILED":
            v.append("ex05 expects FAILED")
        if not any(d["claim"].strip().endswith("[FALSE]") for d in details):
            v.append("ex05 expects a [FALSE] claim")
    elif prefix == "06":
        if status != "PARTIAL":
            v.append("ex06 expects PARTIAL")
        if not has_state("OBSERVED") or not has_state("UNVERIFIED"):
            v.append("ex06 expects OBSERVED and UNVERIFIED claims")
    elif prefix == "07":
        if status != "FAILED":
            v.append("ex07 expects FAILED")
        if not any(d["claim"].strip().endswith("[FALSE]") for d in details):
            v.append("ex07 expects [FALSE] claims")
        if has_state("UNVERIFIED"):
            v.append("ex07 expects no UNVERIFIED claims")
    elif prefix == "08":
        if status != "PARTIAL":
            v.append("ex08 expects PARTIAL")
        if not has_state("OBSERVED") or not has_state("BLOCKED"):
            v.append("ex08 expects OBSERVED and BLOCKED claims")
    return v


def validate_example(path):
    blocks = extract_blocks(path.read_text(encoding="utf-8"))
    if not blocks:
        return ["no toolkit-report block found"]
    violations = []
    prefix = path.stem.split("-")[0]
    for block in blocks:
        parsed = parse_report(block)
        violations.extend(check_report(parsed))
        violations.extend(check_expectations(prefix, parsed))
    return violations


FIXTURES = [
    (
        "hallucinated-complete",
        """STATUS: COMPLETE
PROOF STATES:
  OBSERVED:   NONE
  INFERRED:   NONE
  UNVERIFIED: service restarted
  BLOCKED:    NONE
CLAIM DETAIL:
  service restarted | UNVERIFIED | NONE | NONE
NEXT ACTION: NONE
BLOCKERS: NONE""",
        "contradicts derived status",
    ),
    (
        "empty-evidence",
        """STATUS: COMPLETE
PROOF STATES:
  OBSERVED:   config updated
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    NONE
CLAIM DETAIL:
  config updated | OBSERVED | NONE | NONE
NEXT ACTION: NONE
BLOCKERS: NONE""",
        "has no evidence",
    ),
    (
        "claims-without-detail",
        """STATUS: COMPLETE
PROOF STATES:
  OBSERVED:   done
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    NONE
CLAIM DETAIL:
NEXT ACTION: NONE
BLOCKERS: NONE""",
        "missing from CLAIM DETAIL",
    ),
    (
        "failure-masked-as-blocked",
        """STATUS: BLOCKED
PROOF STATES:
  OBSERVED:   transfer succeeded [FALSE]
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    NONE
CLAIM DETAIL:
  transfer succeeded [FALSE] | OBSERVED | tx receipt | status 0x0
NEXT ACTION: NONE
BLOCKERS: NONE""",
        "contradicts derived status",
    ),
    (
        "bad-status-token",
        """STATUS: DONE ALREADY
PROOF STATES:
  OBSERVED:   x
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    NONE
CLAIM DETAIL:
  x | OBSERVED | cmd | out
NEXT ACTION: NONE
BLOCKERS: NONE""",
        "invalid STATUS",
    ),
    (
        "claim-in-two-sections",
        """STATUS: PARTIAL
PROOF STATES:
  INFERRED:   foo
  UNVERIFIED: foo
  OBSERVED:   NONE
  BLOCKED:    NONE
CLAIM DETAIL:
  foo | INFERRED | NONE | NONE
  foo | UNVERIFIED | NONE | NONE
NEXT ACTION: NONE
BLOCKERS: NONE""",
        "more than one state",
    ),
    (
        "looks-done-form-valid",
        """STATUS: COMPLETE
PROOF STATES:
  OBSERVED:   deployment output written
  INFERRED:   NONE
  UNVERIFIED: NONE
  BLOCKED:    NONE
CLAIM DETAIL:
  deployment output written | OBSERVED | tee deploy.log; wc -l deploy.log | 23 lines
NEXT ACTION: NONE
BLOCKERS: NONE""",
        None,
    ),
]


def run_fixture(report):
    return check_report(parse_report(report))


def main():
    problems = 0

    missing = [name for name in REQUIRED_EXAMPLES if not (EXAMPLES_DIR / name).exists()]
    if missing:
        problems += 1
        print("FAIL missing required examples:")
        for name in missing:
            print("    - " + name)

    for path in sorted(EXAMPLES_DIR.glob("*.md")):
        violations = validate_example(path)
        if violations:
            problems += 1
            print("FAIL " + path.name)
            for v in violations:
                print("    - " + v)
        else:
            print("PASS " + path.name)

    for name, report, marker in FIXTURES:
        violations = run_fixture(report)
        ok = (marker is None and not violations) or (
            marker is not None and any(marker in v for v in violations)
        )
        if ok:
            print("PASS fixture " + name)
        else:
            problems += 1
            print("FAIL fixture " + name + " (expected marker: " + str(marker) + ")")
            for v in violations:
                print("    - " + v)

    if problems:
        print("\n{} item(s) failed".format(problems))
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())