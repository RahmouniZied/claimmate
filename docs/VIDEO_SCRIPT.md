# Video script and recording runbook (target ~3 min, hard limit 5 min; public, no login)

All data is synthetic. Film the live app (`adk web`) with three short cut-ins: the architecture image, the agent card, and the eval result. Publish to YouTube as public or unlisted.

## Pre-flight (run once, before recording)

From the project root in PowerShell, with the venv created and `.env` holding your key:

```powershell
# The app you will film, clean single-agent menu (opens http://localhost:8000)
.venv\Scripts\adk web claimmate

# Optional second terminal, only if you want to film real A2A delegation:
.venv\Scripts\python -m uvicorn claimmate.a2a_server:app --host localhost --port 8001
```

Have these ready in tabs or a file viewer:
- `data/synthetic/letters/letter_01_mri.txt` (supported case) and `letter_03_cosmetic.txt` (abstention case)
- `docs/architecture.png`
- the agent card at `http://localhost:8001/.well-known/agent-card.json`
- the eval result: run `python evals/run_eval.py` once and keep the `4/4 = 100%` line on screen

## Beats

| Time | On screen | Voiceover |
|---|---|---|
| 0:00 to 0:15 | The denial letter `letter_01_mri.txt`. | "Your insurer just denied this claim. They are betting you will not appeal, because the deadline is buried and the policy is impossible to read." |
| 0:15 to 0:30 | Cut to `docs/architecture.png`. | "ClaimMate is not one prompt. An orchestrator reads the letter, and a specialist agent decides whether the plan actually supports you. They run on Gemini 3.1 Flash-Lite and talk over the agent-to-agent protocol." |
| 0:30 to 1:05 | In `adk web`, paste `letter_01_mri.txt`. Show it state the facts, validate the code, the deadline, then cite the clause. | "It states the facts, checks the diagnosis code against a public medical database, finds the deadline you would have missed, and drafts an appeal that cites the real plan clause, section 4.3." |
| 1:05 to 1:25 | Cut to `docs/before_after_card.png`, then in `adk web` paste `letter_03_cosmetic.txt` and show it abstain. | "A normal assistant invents a clause that does not exist. ClaimMate cites a real one, or, when the plan genuinely excludes the service, it tells you the truth and refuses to guess." |
| 1:25 to 1:45 | The citation gate passes, then the approval prompt appears. Do not approve yet. | "Every citation is checked against the plan. A gate blocks anything invented before you see it. And it stops here. It will not send a single word without your approval." |
| 1:45 to 2:05 | Browser tab on the agent card `http://localhost:8001/.well-known/agent-card.json`. | "The hard reasoning is its own agent, served over A2A, so it can be scaled or swapped without touching the rest of the system." |
| 2:05 to 2:25 | Open a new session in `adk web` and paste a second denial. It greets you and already knows the plan. | "Weeks later, a new denial. It already remembers your plan, so you start where you left off." |
| 2:25 to 2:45 | Cut to the `adk web` trace view, then to the `4/4 = 100%` eval line. | "Real tools, real grounding, measured. An eval suite passes every case, and it all runs on the free tier." |
| 2:45 to 3:00 | Back to the finished draft and the deadline. | "ClaimMate finds the clause they ignored, and never sends a word without you. All data here is synthetic." |

## Tips
- 1280x720 or higher, no personal tabs or names on screen (the project reads as personal).
- The approval prompt in `adk web` is the human-in-the-loop beat, do not disable confirmation while filming.
- If you skip the live A2A terminal, the agent card tab plus the architecture image still prove A2A is real.
- Keep it under 5 minutes. Shorter and clearer scores better than longer.
