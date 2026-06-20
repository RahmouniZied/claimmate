# ClaimMate

An AI agent that helps a person appeal a denied health insurance claim.

Insurers deny claims knowing most people never appeal. The deadline is buried and the policy is hard to read. ClaimMate reads the denial letter, finds the appeal deadline, locates the **real** plan clause that supports coverage (or **abstains** when none does), drafts a citation-grounded appeal, and **never finalizes without the member's approval**.

All data in this repo is synthetic. ClaimMate drafts and prepares an appeal. It does not file anything.

## What it does

1. Reads the denial letter and states back the key facts.
2. Validates the diagnosis code against the public NLM Clinical Tables API.
3. Computes the appeal deadline and days remaining.
4. Asks a Clause-Finder specialist for the plan clause that supports coverage, or an abstention.
5. If supported, drafts a short appeal citing only real clauses. If not, says so honestly and stops.
6. Runs a deterministic citation gate that blocks any clause not present in the plan.
7. Shows the draft and asks the member to approve before it is treated as ready to send.

## Built with the Agent Development Kit

| Component | What it shows |
|---|---|
| ADK multi-agent | An orchestrator plus a Clause-Finder specialist |
| Tools and external API | ICD-10 validation (live NLM API), deadline math, plan search |
| A2A | The Clause-Finder can be served and called over the A2A protocol |
| Memory | The member's plan persists across sessions (user-scoped state) |
| Evals and guardrails | An eval pass-rate plus a citation gate that blocks invented clauses |
| Deploy and traces | `adk web` trace view; optional `adk deploy cloud_run` |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then add your Google AI Studio key
```

## Run

```bash
adk web                          # chat UI + live traces (run from the project root)
python -m claimmate.run --letter data/synthetic/letters/letter_01_mri.txt
python -m claimmate.run --memory-demo
python evals/run_eval.py         # prints the pass-rate
python scripts/before_after.py   # naive model vs ClaimMate
```

Serve the Clause-Finder over A2A:

```bash
uvicorn claimmate.a2a_server:app --host localhost --port 8001
set CLAIMMATE_CLAUSE_FINDER_URL=http://localhost:8001
```

## Verify

The deterministic core runs without an API key:

```bash
python -c "from claimmate import tools, retrieval, guardrails; \
print(tools.validate_diagnosis_code('M54.50')); \
print(guardrails.check_citations('Per §99.9', retrieval.active_index().clause_ids()))"
```

## Layout

```
claimmate/        agent, clause-finder, tools, retrieval, guardrails, A2A server, runner
data/synthetic/   fictional plan and denial letters
evals/            scoring harness
scripts/          naive vs ClaimMate proof
notebooks/        Kaggle notebook
docs/             writeup, rationale, video script, architecture
```

## Limitations

ClaimMate prepares a draft for the member to review and submit. Clause retrieval is scoped to the uploaded plan. It is a foundation, not a substitute for legal or medical advice.
