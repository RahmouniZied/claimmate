"""Evaluate ClaimMate on the synthetic cases.

Scores deadline extraction, ICD-10 validation, correct clause grounding,
absence of invented citations, and abstention on the unsupported case.

  python evals/run_eval.py

Needs GOOGLE_API_KEY. Writes outputs/eval_report.json.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Unattended run: do not pause on the approval gate. Must be set before import.
os.environ.setdefault("CLAIMMATE_DISABLE_CONFIRM", "1")

# Space cases out to respect free-tier requests-per-minute limits.
PACING_SECONDS = float(os.environ.get("CLAIMMATE_EVAL_PACING_SECONDS", "4"))

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from claimmate import config, guardrails, retrieval  # noqa: E402
from claimmate.agent import root_agent  # noqa: E402

load_dotenv()

CASES = [
    {"file": "letter_01_mri.txt", "dx": "M54.50", "expected": {"4.2", "4.3"}, "supported": True},
    {"file": "letter_02_er.txt", "dx": "R07.9", "expected": {"5.1"}, "supported": True},
    {"file": "letter_03_cosmetic.txt", "dx": "Z41.1", "expected": set(), "supported": False},
    {"file": "letter_04_drug.txt", "dx": "L40.0", "expected": {"6.4"}, "supported": True},
]


async def _collect(runner, user_id, session_id, message):
    await runner.session_service.create_session(
        app_name=config.APP_NAME, user_id=user_id, session_id=session_id
    )
    tool_results, final_text = [], []
    msg = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=msg):
        content = getattr(event, "content", None)
        if not content or not getattr(content, "parts", None):
            continue
        for part in content.parts:
            if getattr(part, "function_response", None):
                tool_results.append((part.function_response.name, str(part.function_response.response)))
            elif getattr(part, "text", None):
                final_text.append(part.text)
    return tool_results, "\n".join(final_text)


def _score(case, tool_results, final_text):
    plan_ids = retrieval.active_index().clause_ids()
    blob = " ".join(r for _, r in tool_results)
    clause_out = " ".join(r for n, r in tool_results if n == "clause_finder")
    cited = guardrails.cited_ids(final_text)
    checks = {}
    checks["deadline_computed"] = "deadline_date" in blob
    checks["icd_validated"] = f"'code': '{case['dx']}'" in blob and "'valid': True" in blob
    checks["no_invented_citations"] = guardrails.check_citations(final_text, plan_ids)["ok"]
    if case["supported"]:
        checks["cited_correct_clause"] = bool(cited & case["expected"])
        checks["did_not_abstain"] = "ABSTAIN" not in clause_out.upper()
    else:
        checks["abstained"] = ("ABSTAIN" in clause_out.upper()) or not (cited - {"9.3"})
    return checks


async def main():
    runner = Runner(app_name=config.APP_NAME, agent=root_agent, session_service=InMemorySessionService())
    letters = config.DATA_DIR / "letters"
    report, passed = [], 0
    for i, case in enumerate(CASES):
        if i:
            await asyncio.sleep(PACING_SECONDS)
        letter = (letters / case["file"]).read_text(encoding="utf-8")
        try:
            tr, ft = await _collect(
                runner, "eval", f"e{i}",
                "Here is a denial letter from my Northwind Health PPO plan. Please help me appeal.\n\n" + letter,
            )
        except Exception as e:
            print(f"[{case['file']}] RUN ERROR: {e}")
            report.append({"file": case["file"], "error": str(e)})
            continue
        checks = _score(case, tr, ft)
        ok = all(checks.values())
        passed += ok
        print(f"[{case['file']}] {'PASS' if ok else 'FAIL'}  {checks}")
        report.append({"file": case["file"], "pass": ok, "checks": checks})

    total = len(CASES)
    rate = round(100 * passed / total, 1)
    print(f"\nPASS RATE: {passed}/{total} = {rate}%")
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    (out / "eval_report.json").write_text(
        json.dumps({"passed": passed, "total": total, "pass_rate_pct": rate, "cases": report}, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {out / 'eval_report.json'}")


if __name__ == "__main__":
    asyncio.run(main())
