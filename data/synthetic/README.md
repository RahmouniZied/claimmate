# Synthetic corpus

All files here are fictional and contain no real personal or health information.
They exist so the agent can be demonstrated and evaluated safely.

- `plans/northwind_ppo.md` is an invented health plan with numbered clauses (§).
- `letters/` holds four invented denial letters:
  - `letter_01_mri.txt` supported by §4.2 and §4.3 (imaging medical necessity).
  - `letter_02_er.txt` supported by §5.1 (emergency, prudent layperson).
  - `letter_03_cosmetic.txt` has no supporting clause. The plan excludes it under §9.3, so the agent must abstain.
  - `letter_04_drug.txt` supported by §6.4 (formulary exception).
