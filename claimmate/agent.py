"""ClaimMate orchestrator. Exposes root_agent for `adk web`, `adk run`, and eval."""
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import AgentTool

from . import config, tools
from .clause_finder import clause_finder_agent


def _clause_finder_tool() -> AgentTool:
    """Local Clause-Finder by default; delegate over A2A if a URL is configured."""
    if config.CLAUSE_FINDER_A2A_URL:
        from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

        remote = RemoteA2aAgent(
            name="clause_finder",
            agent_card=config.CLAUSE_FINDER_A2A_URL,
            description="Remote Clause-Finder reached over A2A.",
        )
        return AgentTool(agent=remote)
    return AgentTool(agent=clause_finder_agent)


BASE_INSTRUCTION = """You are ClaimMate. You help a member appeal a denied health insurance claim. You DRAFT and PREPARE only. You never file or send anything, and you never invent facts.

Work through these steps in order:

1. Read the denial letter the member gives you (attached file or pasted text). Extract and state back briefly: payer, claim number, letter date (ISO format), denied service, diagnosis code, denied amount, denial reason, and the appeal window in days.

2. Call validate_diagnosis_code with the diagnosis code. Report its official description, or say plainly if it could not be validated.

3. Call compute_appeal_deadline with the letter date and the appeal window in days. Tell the member the deadline date and how many days remain.

4. Call clause_finder with a short description of the denial (denied service, denial reason, and the member's situation).
   - If its reply starts with ABSTAIN: do NOT draft an appeal. Tell the member honestly that you could not find plan language that supports coverage, explain why (for example the plan excludes it), and stop. Do not invent support.
   - Otherwise continue.

5. Draft a short, respectful internal appeal letter. Cite ONLY the clause ids that clause_finder returned, written as §X.Y, and rely only on what clause_finder quoted. Cite no other clause.

6. Call validate_citations with your draft text. If it reports any invalid citation, fix the draft and validate again. Only continue when ok is true.

7. Show the member the final draft and the deadline, then call finalize_appeal. That step asks the member to approve before the appeal is treated as ready to send. Never treat it as already sent.

If you learn the member's plan, call save_plan_profile once so you can recognize them next time.

Be brief, clear, and honest about limitations. The member reviews and submits the appeal themselves."""


def build_instruction(ctx: ReadonlyContext) -> str:
    profile = None
    try:
        profile = ctx.state.get("user:plan_profile")
    except Exception:
        profile = None
    if profile:
        return (
            f"NOTE: This is a returning member. Their plan is already on file: {profile}. "
            "Greet them, do not ask for the plan again, and reuse it.\n\n" + BASE_INSTRUCTION
        )
    return BASE_INSTRUCTION


root_agent = LlmAgent(
    name="claimmate",
    model=config.FLASH_MODEL,
    description="Helps a member appeal a denied health insurance claim, with grounded citations and human approval.",
    instruction=build_instruction,
    tools=[
        tools.validate_diagnosis_code,
        tools.compute_appeal_deadline,
        _clause_finder_tool(),
        tools.validate_citations,
        tools.save_plan_profile,
        tools.finalize_appeal_tool,
    ],
)
