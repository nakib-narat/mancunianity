# Copilot instructions

- `APPROVED-EVENT-FACTS.md` and `event-data.json` are the source of truth for event facts. Do not invent or reconstruct values.
- Gathering/check-in (10:00, 13:00) and walk departure (10:30, 13:30) are different; arrival is 30 minutes before departure. Never call 10:00 or 13:00 a walk start time.
- Free category: "aged 3 and under" (free ticket must still be reserved). Paid child category: "aged 4–17", £5.
- The site is static HTML with no build step. Before opening a PR run `python3 scripts/check-event-facts.py`.
- Do not merge or deploy automatically; open draft pull requests.
