Cognitive Friction Toolkit
A skill that stops your AI agent from confidently lying to you.
Most agent tooling is built to make AI act faster. This is the brake. It forces an agent to stop, check what's actually true, and admit what it doesn't know — before it tells you "sure, I can do that."

The problem
LLMs default to confident action. Ask an agent to do something and it will almost always say yes — then hallucinate a service that isn't running, skip a required step, agree to a plan it can't execute, or quietly fail and tell you it succeeded.
That default is annoying in a chatbot. It's dangerous when there's real money, a live service, or a solo operator on the other end of the wrong answer.
The Cognitive Friction Toolkit adds a mandatory pre-flight pause to any task: stop, read, verify, then respond honestly.

Before / after
Without friction:

You: Deploy the payment service.
Agent: Done! The payment service is live and processing transactions. ✅
(The service was never deployed. The agent has no idea.)

With friction:

You: Deploy the payment service.
Agent: Checked the operating manual — the payment service is marked NOT DEPLOYED and STRIPE_KEY isn't set. I can't deploy it yet.
Blocked: the env var requires you to add it. What I can do right now: prep the deploy config so it's one step away once the key is in.

The difference isn't intelligence. It's discipline.

What it does
The toolkit enforces one rule — No Promises Without Proof — through a four-step procedure the agent must run before acting:
StepWhat happens0 — Know where you areConfirm the agent actually has the tools, tokens, and access for the task. If not, say so immediately.1 — StopNo code, no plan, no "sure."2 — ReadFind and read the relevant docs/state. From the source, not from memory.3 — VerifyCross-reference the request against what's actually possible right now. Look for blockers.4 — Respond honestlyIf clear, execute. If blocked, state what's blocked, what needs a human, and what can be done — and don't fake a workaround.
Anti-patterns it kills
Bad patternWhat happensThe fixConfident hallucinationSays a service is running when it's notForces a state checkWorkflow bypassSkips required stepsForces workflow verificationSilent failureAgrees to a plan it can't executeForces blocker identificationTrial and errorWrites code without reading docsForces doc-read firstStall theaterPretends to work on something asyncForces immediate honest statusEnvironment blindnessActs without checking accessForces an environment check

Install
Drop SKILL.md into your agent's skill directory (the toolkit is a single, model-agnostic markdown file — no dependencies).
bashgit clone https://github.com/PhantomCapAI/Cognitive-Friction-Toolkit.git
Point your agent at SKILL.md and trigger it before any infrastructure or high-stakes task. It works with any agent framework that can load a skill or system instruction.

When to use it
Use it on tasks where being confidently wrong has a cost:

Deploying or modifying live services
Anything touching money, keys, or wallets
Multi-step workflows with a required sequence
Any task that depends on the current state of a system

Skip it for low-stakes chat. The friction is the point — apply it where the point matters.

Why this exists
This came out of running real infrastructure where an agent's confident "done!" could mean a service that was never deployed and money that never moved. The lesson: the dangerous failure isn't the agent that can't do something — it's the agent that says it did.
Capability is everywhere. Honesty under pressure is rare. This is a small attempt to make it the default.

License
See LICENSE.
Contributing
Issues and PRs welcome — especially new anti-patterns you've watched an agent fall into.
