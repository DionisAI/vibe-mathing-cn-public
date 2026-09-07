# Public discovery assets guide

`assets/` contains public documentation and AI-discovery material only.

- Every capability statement must point to a public schema, fixture, test, or fixed metadata entry.
- Keep the canonical name, public URL, empty-ledger status, and no-open-problem boundary synchronized with `README.md`, `README.en.md`, and `llms.txt`.
- Do not add private paths, credentials, runtime/session details, unadmitted candidates, rankings, hidden text, or unsupported superiority claims.
- Run `python3 scripts/check_public_readme.py` and `python3 scripts/check_ai_citation_assets.py` after changes.
