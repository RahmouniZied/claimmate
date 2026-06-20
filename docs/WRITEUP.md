# ClaimMate: an agent that helps you fight a denied insurance claim

## The problem

Insurers deny claims knowing that most people never appeal. The appeal deadline is buried in dense paperwork, the policy is hard to read, and the people hurt most are often the sick, the elderly, and people who do not read insurance English fluently. Yet a large share of denials are overturned when someone actually files an appeal. The barrier is not the law. It is the paperwork and the fear.

## What ClaimMate does

You give it the denial letter and your plan. It then:

1. Reads the letter and states the key facts back to you.
2. Validates the diagnosis code against a public medical API.
3. Surfaces the appeal deadline and how many days remain.
4. Finds the exact plan clause that supports coverage, or abstains if none does.
5. Drafts a short appeal that cites only real clauses.
6. Blocks any invented citation with a deterministic gate.
7. Holds the appeal behind your approval. It never files anything.

## The proof, not a claim

The hardest part of an appeal is grounding it in the policy. A normal assistant will confidently cite a clause that does not exist, and that single fabrication can sink a real appeal.

Run `scripts/before_after.py` and you see the difference on the same denial: a naive model fabricates a plan clause and a supporting quote it was never given, and even invents clinical evidence, while ClaimMate cites only real clauses, or, on a service the plan genuinely excludes, says "I could not find supporting language and I will not guess." The abstention is not a failure. It is the point.

## How it works

ClaimMate is built with the Agent Development Kit. An orchestrator handles the flow and the drafting, and a separate Clause-Finder specialist does the hard reasoning: retrieve candidate clauses, decide whether any supports coverage, and abstain when none does. Both run on Gemini 3.1 Flash-Lite, so the whole project reproduces on the free tier at zero cost, and it still scores 100% on the eval suite because the deterministic retrieval does the searching and the model only judges and quotes. The Clause-Finder is a separate agent, so its model is independently configurable for stronger reasoning when billing is available, and it can run in process or be served and called over the A2A protocol. See `docs/ARCHITECTURE.md` for the diagram and the full mapping of components to course concepts.

## Why you can trust it

- A deterministic citation gate checks every cited clause against the plan and blocks anything invented.
- The Clause-Finder abstains rather than stretch unrelated language.
- Diagnosis codes are validated against the public NLM Clinical Tables API.
- The appeal waits behind a human approval step.
- An evaluation suite scores deadline extraction, code validation, correct clause grounding, the absence of invented citations, and abstention on the unsupported case. It passes all four cases, a 100 percent pass-rate, reproducible with `python evals/run_eval.py`.

## Why I built it

I wanted to see whether an agent could be genuinely trustworthy in a setting where a confident wrong answer does real harm. The rule I held to is simple: cite a real clause or abstain, and never act on someone's behalf without their consent. The deterministic citation gate and the human approval step are that rule written in code.

## Honest limitations

ClaimMate prepares a draft for you to review and submit. It does not file appeals. Clause retrieval is scoped to the plan you provide. All data in this project is synthetic and contains no real personal or health information. It is a foundation, and it is not a substitute for legal or medical advice.

## Reproduce

The repository runs end to end. The deterministic core runs with no API key. Add a Google AI Studio key to run the full agent, the eval, and the before and after comparison. A Kaggle notebook walks through every step.
