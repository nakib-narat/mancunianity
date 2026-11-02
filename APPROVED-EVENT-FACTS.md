# Mancunianity Flows: approved event facts

This is the working source of truth for customer-facing event information. Copy
approved facts from here; do not reconstruct them from memory. Items marked
**Confirmation required** must not be presented as settled policy.

Last checked against the repository: 2 November 2026.

## Event

- **Name:** Mancunianity Flows
- **Description:** A guided, step-free River Irwell walk with supplied wireless
  headphones, followed by a 15-minute live musical finale. The experience
  includes about 50 minutes of walking and lasts about 65 minutes overall.
- **Dates:** Saturday 19, Sunday 20 and Monday 21 December 2026
- **Departures (walk departs):** 10:30 and 13:30 each day
- **Gathering and check-in begin:** 10:00 (morning) and 13:00 (afternoon)
- **Arrival:** Visitors must arrive at the gathering time, 30 minutes before
  the walk departs. Walks leave promptly. Do not describe 10:00 or 13:00 as
  walk start times, and do not describe arrival as 20 minutes before departure.
- **Gathering period:** Allows time for ticket checking, welcome, headset fitting
  and the route briefing.
- **Approximate finish:** 11:35 for the 10:30 departure; 14:35 for the 13:30
  departure. Allow around 90 minutes in total for arrival, the experience and
  departure.
- **Capacity:** Up to 35 people per experience
- **Age guidance:** Particularly suited to ages 8 and over; younger children
  are welcome with a responsible adult. Every child must be included in the
  booking.

## Meeting point

- **Published meeting point:** Riverside entrance of Aviva Studios, Water
  Street, Manchester M3 4JG
- Hosts welcome visitors inside The Social before the walk.
- **Confirmation required:** Venue-approved entrance name, whether visitors
  should initially wait inside or outside, exact staff position, accessible
  drop-off, public-transport directions and practical arrival photographs.

## Tickets

- **Adult:** £15
- **Senior, aged 65+:** £12
- **Child, aged 4–17 inclusive:** £5
- **Family bundle:** £38 for two adults and two children or young people.
  **Owner decision required:** whether the bundle may include children aged 3
  and under is not approved; the website does not state it.
- **Child aged 3 and under:** Free, but a free ticket must be reserved for
  every child (safety, security, capacity management and accurate attendance
  count). Use "aged 3 and under", never "under 3".
- **Access companion:** Free, but a free ticket must be reserved
- **Booking fees:** No additional booking fees
- **Booking URL:** https://www.trybooking.com/uk/HEFF

Confirm ticket availability and the selected performance in TryBooking before
describing a booking as complete.

## Weather, cancellation and customer changes

- **Ordinary rain:** The experience is expected to go ahead in ordinary rain.
- **Severe weather or unsafe river conditions:** The event may be changed,
  postponed or cancelled. Booked visitors will be contacted using the details
  supplied at booking.
- **Confirmation required before promotion:** Who makes the safety decision,
  when the decision is made, the customer choice and refund/transfer terms if
  the organiser changes or cancels an event, and the policy when a customer
  cannot attend. Do not promise a refund, transfer or credit until approved
  terms are supplied and published in the booking terms.

## Contact

- **Email:** contact@mancunianity.uk

## Machine-readable data and validation

`event-data.json` mirrors these facts (separate gathering and departure fields).
`python3 scripts/check-event-facts.py [site_root]` validates public pages and
structured data; run it against the source and any generated output.

## Publication gate

The schedule in this document follows the 10:30 morning departure decision
recorded in the merged ticket-alignment change (PR #7), which says it was
updated to match the Aviva listing. The website and its six event records
currently use 10:30 and 13:30. Before significant promotion, retain the
authoritative venue/listing confirmation and complete every **Confirmation
required** item above. The booking URL, current availability, image permissions,
and live checkout behavior also require direct verification; repository
contents alone do not establish them.
