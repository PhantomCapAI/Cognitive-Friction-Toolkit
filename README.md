# Cognitive-Friction-Toolkit

**phantom134-check**  
A skill file that forces AI to stop, verify, and prove before promising.

### The Problem
LLMs confidently tell you they can do things they can't. If you're a solo operator running live infrastructure with real money, that's a liability.

### What This Does
Triggers before any infrastructure task. Forces the AI to: STOP → READ the operating manual → VERIFY against real state → RESPOND HONESTLY.

Kills: confident hallucination, workflow bypass, silent failure, trial-and-error coding, stall theater.

### Install
Drop `SKILL.md` into your Claude skill directory or system prompt.

### Origin
Built after too many sessions where Claude said "I'll get that running" about services that were dormant, missing env vars, or blocked on manual steps.

**MIT** · Built by Phantom Capital · [@phantomcap_ai](https://x.com/phantomcap_ai)
