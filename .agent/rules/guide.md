---
trigger: always_on
---

# PROJECT RULES

## GENERAL
- Do not add comments to the code unless it is to explain "why" behind a complex logic.
- Do not remove or modify existing functionality unless explicitly asked.
- Do not install new dependencies without asking first.
- Always read the relevant file before editing it.
- Keep changes minimal. Do not refactor unrelated code.

## CODE QUALITY
- Follow existing code style and patterns in the project.
- All code must be production-ready. No TODOs, no placeholders, no half-done logic.
- Do not use magic numbers. Use named constants.
- Use type hints for all function parameters and return values.
- Keep functions small and focused — one function, one job.

## ERROR HANDLING
- Never use bare `except`. Always catch specific exceptions.
- Never silently swallow errors. Always log or re-raise.
- Handle edge cases. Do not assume happy path.

## SECURITY
- Never hardcode secrets, tokens, or API keys.
- Never log sensitive data.

## COMMUNICATION
- If something is unclear, ask before coding.
- If a request would break existing functionality, warn first.
- Explain what you changed and why after each edit.
