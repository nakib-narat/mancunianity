# Event information implementation notes

The website is a static HTML site with no package manager, build step or
component layer. Event-specific content remains in the existing pages, while
`event-data.json` holds operational facts used by the consistency checker.

## Implementation decisions

- Updated the homepage, performance listing, experience, family and access
  pages in place; no new runtime code or content framework was introduced.
- Kept the six existing session-level Event records and their TryBooking URLs,
  offers, availability status, capacity and images. Corrected their titles,
  start times, arrival `doorTime`, location, postcode and organizer email.
- Removed the existing Event `endDate` values. Public finish times are
  estimates and may run later, so encoding them as exact structured-data end
  times would overstate their precision.
- Reused the existing Aviva Studios image for social metadata; no image asset
  was fabricated.
- Preserved the existing Organization type in Event structured data rather
  than changing it to a Person. The public website identifies Nakib Narat as
  organiser and creative director, while the existing Event data describes
  Mancunianity Flows as its Organization; the preferred structured-data
  organizer identity should be confirmed separately before any type change.

## External follow-up

The website pull request cannot change TryBooking, issued tickets or partner
listings. The event owner should review the live booking page and update any
remaining location, postcode, ticket, arrival, duration or weather wording
using `docs/external-channel-corrections.md`. This pull request does not deploy
the website or make those external changes.

## Validation

Run `python3 scripts/check-event-facts.py` from the repository root. The static
site has no configured npm build, lint or type-check command.
