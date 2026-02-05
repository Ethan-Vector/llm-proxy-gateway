# Contributing

1. Create a feature branch.
2. Run:
   - `ruff check .`
   - `ruff format .`
   - `pytest`
3. Keep changes small and focused.
4. Update docs if behavior changes.

## Design rules
- Providers must be behind a small interface (`BaseProvider`).
- Keep OpenAI schema support intentionally minimal unless needed.
- Prefer deterministic behavior in tests (use MockProvider).
