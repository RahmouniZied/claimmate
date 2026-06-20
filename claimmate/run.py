"""Drive ClaimMate from the command line.

  python -m claimmate.run --letter data/synthetic/letters/letter_01_mri.txt
  python -m claimmate.run --memory-demo

Needs GOOGLE_API_KEY in the environment or a .env file.
"""
import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from . import config
from .agent import root_agent

load_dotenv()


def _render(event) -> None:
    content = getattr(event, "content", None)
    author = getattr(event, "author", "?")
    if not content or not getattr(content, "parts", None):
        return
    for part in content.parts:
        if getattr(part, "function_call", None):
            fc = part.function_call
            print(f"  [tool-call] {fc.name}({dict(fc.args or {})})")
        elif getattr(part, "function_response", None):
            fr = part.function_response
            resp = str(fr.response)
            print(f"  [tool-result] {fr.name} -> {resp[:200]}")
        elif getattr(part, "text", None):
            print(f"\n{author}: {part.text.strip()}\n")


async def run_claim(runner, user_id: str, session_id: str, message: str) -> None:
    msg = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=msg):
        _render(event)


def _runner() -> Runner:
    return Runner(
        app_name=config.APP_NAME,
        agent=root_agent,
        session_service=DatabaseSessionService(db_url=config.SESSION_DB_URL),
    )


async def _one(letter_path: str) -> None:
    runner = _runner()
    user_id = "demo-user"
    session_id = "s1"
    await runner.session_service.create_session(
        app_name=config.APP_NAME, user_id=user_id, session_id=session_id
    )
    letter = Path(letter_path).read_text(encoding="utf-8")
    await run_claim(
        runner, user_id, session_id,
        "Here is a denial letter from my Northwind Health PPO plan. "
        "Please help me appeal it.\n\n" + letter,
    )


async def _memory_demo() -> None:
    runner = _runner()
    user_id = "memory-demo-user"
    data = config.DATA_DIR / "letters"

    print("=== SESSION 1 (first denial, learns the plan) ===")
    await runner.session_service.create_session(
        app_name=config.APP_NAME, user_id=user_id, session_id="m1"
    )
    await run_claim(
        runner, user_id, "m1",
        "Here is a denial letter from my Northwind Health PPO plan. Please remember my plan "
        "and help me appeal.\n\n" + (data / "letter_01_mri.txt").read_text(encoding="utf-8"),
    )

    print("\n=== SESSION 2 (weeks later, new denial, should already know the plan) ===")
    await runner.session_service.create_session(
        app_name=config.APP_NAME, user_id=user_id, session_id="m2"
    )
    await run_claim(
        runner, user_id, "m2",
        "I got another denial. Please help.\n\n"
        + (data / "letter_02_er.txt").read_text(encoding="utf-8"),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--letter", help="path to a denial letter text file")
    ap.add_argument("--memory-demo", action="store_true", help="run the two-session memory demo")
    args = ap.parse_args()
    if args.memory_demo:
        asyncio.run(_memory_demo())
    elif args.letter:
        asyncio.run(_one(args.letter))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
