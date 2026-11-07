# Event content audit

## Resolved in the website source

The current event pages use The Social, Aviva Studios and postcode M3 4JQ;
separate arrival and performance times; corrected ticket age categories;
approved duration, late-joining, supervision and weather wording; and the
confirmed organiser/contact information. The six Event records are checked by
`scripts/check-event-facts.py`.

The repository is static HTML. `index.html`, `walks.html`, `experience.html`,
`families.html` and `access.html` were directly edited. The other HTML
documents were scanned but not rewritten for this correction. `404.html` is
the not-found document and `nav-fix-test.html` is a test fixture, not a current
event landing page. There is no archived event page in the current repository
tree.

## Genuine follow-up and scope boundaries

- The live TryBooking listing and any external partner/social listings require
  manual owner review; this repository cannot confirm or perform those changes.
  See `docs/external-event-updates.md`.
- The existing structured-data organizer is an `Organization` named
  Mancunianity Flows, while the public copy names Nakib Narat as organiser and
  creative director. The preferred entity type is not inferred or changed.
- Detailed access facts that remain unconfirmed in `access.html` are explicitly
  described as unconfirmed, not presented as event features.
- Google Rich Results Test and Schema.org Validator were not run against this
  local, un-deployed branch. The rendered local JSON-LD is parsed and checked
  by the repository regression script; the complete rendered block is included
  in the pull-request review notes for manual validation.

No unresolved or superseded event policy is presented as current public copy.
