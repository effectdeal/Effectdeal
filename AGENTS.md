# EFFECT DEAL development rules

- Keep page modules independent; do not import all pages into the initial shell.
- Access data through `/api` and the repository adapter. No database secrets in JavaScript.
- Enforce record scope and permissions on the server, including file downloads.
- Preserve historical submitted/approved report amounts. Compute currency using Decimal/haléře.
- Send `version` on edits and return 409 for conflicts.
- Do not add real payment actions or tracking without a separately specified integration.
- Add meaningful tests for permission, status or calculation changes; run `python -m pytest -q`.
- Update ROADMAP/README when a feature changes from demo/scaffold to production behavior.
- Never replace the existing database or user data with demo seeds in production.
