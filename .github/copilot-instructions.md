# Copilot instructions

- `APPROVED-EVENT-FACTS.md` and `event-data.json` are the source of truth for event facts. Do not invent or reconstruct values.
- Performances start at 10:30 am and 1:30 pm. Arrival and check-in open at 10:00 am and 1:00 pm. The Social, Aviva Studios is the meeting and check-in point.
- Ticket categories: Adult £15; Senior aged 65 and over £12; Child or young person aged 3–17 £5; Under three free but ticket required; Access Companion free but ticket required; Family Bundle £38 for two adults and two children or young people aged 3–17.
- The site is static HTML with no build step. Before opening a PR run `python3 scripts/check-event-facts.py`.
- Do not deploy or merge automatically.
