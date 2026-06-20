"""Structured types shared by tools and agents."""
from pydantic import BaseModel, Field


class DenialExtract(BaseModel):
    """Fields pulled from a denial letter."""
    payer: str = ""
    claim_id: str = ""
    letter_date: str = ""              # ISO date, e.g. 2026-01-15
    denied_service: str = ""
    diagnosis_codes: list[str] = Field(default_factory=list)
    denied_amount: str = ""
    denial_reason_code: str = ""
    denial_reason_text: str = ""
    appeal_window_days: int | None = None
    appeal_instructions: str = ""


class ClauseCitation(BaseModel):
    clause_id: str
    heading: str = ""
    quote: str = ""


class ClauseFinding(BaseModel):
    """Result of the Clause-Finder. Abstains when no clause supports the appeal."""
    supported: bool
    abstained: bool = False
    citations: list[ClauseCitation] = Field(default_factory=list)
    rationale: str = ""
