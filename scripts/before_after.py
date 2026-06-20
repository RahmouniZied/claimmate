"""Proof asset: a naive ungrounded LLM vs ClaimMate on the same denial.

The naive call is free to invent a policy clause. ClaimMate cites a real clause
or abstains. Saves both to outputs/ for the writeup and video.

  python scripts/before_after.py --letter data/synthetic/letters/letter_03_cosmetic.txt

Needs GOOGLE_API_KEY.
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

os.environ.setdefault("CLAIMMATE_DISABLE_CONFIRM", "1")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
from google import genai  # noqa: E402
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from claimmate import config, guardrails, retrieval  # noqa: E402
from claimmate.agent import root_agent  # noqa: E402

load_dotenv()

NAIVE_PROMPT = (
    "You are a helpful assistant. Write a short health insurance appeal letter for the denial "
    "below. Cite the specific plan policy clause number that requires coverage.\n\nDENIAL:\n"
)


def naive(letter: str) -> str:
    client = genai.Client()
    r = client.models.generate_content(model=config.FLASH_MODEL, contents=NAIVE_PROMPT + letter)
    return r.text or ""


async def claimmate(letter: str) -> str:
    runner = Runner(app_name=config.APP_NAME, agent=root_agent, session_service=InMemorySessionService())
    await runner.session_service.create_session(app_name=config.APP_NAME, user_id="ba", session_id="ba")
    msg = types.Content(role="user", parts=[types.Part(
        text="Here is a denial from my Northwind Health PPO plan. Please help me appeal.\n\n" + letter)])
    out = []
    async for event in runner.run_async(user_id="ba", session_id="ba", new_message=msg):
        c = getattr(event, "content", None)
        if c and getattr(c, "parts", None):
            for p in c.parts:
                if getattr(p, "text", None):
                    out.append(p.text)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--letter", default="data/synthetic/letters/letter_03_cosmetic.txt")
    args = ap.parse_args()
    letter = (ROOT / args.letter).read_text(encoding="utf-8")
    plan_ids = retrieval.active_index().clause_ids()

    n = naive(letter)
    c = asyncio.run(claimmate(letter))

    n_check = guardrails.check_citations(n, plan_ids)
    c_check = guardrails.check_citations(c, plan_ids)

    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    report = (
        "=== NAIVE LLM (ungrounded) ===\n" + n
        + f"\n\nCited: {n_check['cited']}  Invalid/invented (not in plan): {n_check['invalid']}\n"
        + "\n\n=== CLAIMMATE (grounded) ===\n" + c
        + f"\n\nCited: {c_check['cited']}  Invalid/invented (not in plan): {c_check['invalid']}\n"
    )
    (out / "before_after.txt").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved {out / 'before_after.txt'}")
    print(f"Plan really contains: {sorted(plan_ids)}")


if __name__ == "__main__":
    main()
