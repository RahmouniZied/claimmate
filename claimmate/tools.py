"""Tools used by ClaimMate. Plain Python so behavior is deterministic and testable."""
import os
from datetime import date, datetime, timedelta

import requests
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from . import guardrails, retrieval

ICD10_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"


def validate_diagnosis_code(code: str) -> dict:
    """Validate an ICD-10-CM diagnosis code against the NLM Clinical Tables API.

    Returns whether the code is valid and its official description.
    """
    code = (code or "").strip().upper()
    norm = code.replace(".", "")
    try:
        r = requests.get(
            ICD10_URL,
            params={"sf": "code", "terms": code, "df": "code,name", "maxList": 7},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        rows = data[3] if len(data) >= 4 and isinstance(data[3], list) else []
    except Exception as e:  # network or parse error: report, do not raise
        return {"code": code, "valid": False, "error": str(e)[:120]}
    for row in rows:
        rc = str(row[0]).replace(".", "").upper()
        if rc == norm:
            return {"code": str(row[0]), "valid": True, "description": row[1]}
    return {"code": code, "valid": False, "description": None}


def compute_appeal_deadline(letter_date: str, appeal_window_days: int) -> dict:
    """Compute the appeal deadline and days remaining from the letter date and window."""
    try:
        ld = datetime.fromisoformat(letter_date.strip()).date()
    except Exception:
        return {"error": f"could not parse letter_date: {letter_date!r}"}
    deadline = ld + timedelta(days=int(appeal_window_days))
    today = date.today()
    return {
        "letter_date": ld.isoformat(),
        "appeal_window_days": int(appeal_window_days),
        "deadline_date": deadline.isoformat(),
        "days_remaining": (deadline - today).days,
        "as_of": today.isoformat(),
    }


def search_plan(query: str) -> list[dict]:
    """Search the member's plan document and return the most relevant clauses."""
    return retrieval.active_index().search(query, k=5)


def validate_citations(appeal_text: str) -> dict:
    """Check every clause cited in an appeal exists in the plan. Blocks invented clauses."""
    ids = retrieval.active_index().clause_ids()
    return guardrails.check_citations(appeal_text, ids)


def save_plan_profile(plan_name: str, notes: str, tool_context: ToolContext) -> dict:
    """Remember the member's plan across sessions (stored under a user-scoped key)."""
    tool_context.state["user:plan_profile"] = {"plan_name": plan_name, "notes": notes}
    return {"saved": True, "plan_name": plan_name}


def finalize_appeal(appeal_text: str) -> dict:
    """Finalize the appeal for the member to send. Requires explicit human approval."""
    return {"status": "approved_for_sending", "characters": len(appeal_text or "")}


# Pauses for human approval before it runs. Set CLAIMMATE_DISABLE_CONFIRM=1 for
# unattended runs (eval, scripts) so the turn does not wait for approval.
if os.getenv("CLAIMMATE_DISABLE_CONFIRM") == "1":
    finalize_appeal_tool = FunctionTool(func=finalize_appeal)
else:
    finalize_appeal_tool = FunctionTool(func=finalize_appeal, require_confirmation=True)

PLAIN_TOOLS = [
    validate_diagnosis_code,
    compute_appeal_deadline,
    validate_citations,
    save_plan_profile,
]
