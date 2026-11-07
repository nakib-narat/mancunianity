# Stage 2A visitor UX review

## Affected-page inventory

| File path | Public URL | Primary audience | Primary visitor task | Primary call to action | Duplicated content | Accessibility concern | Stage 2A action |
|---|---|---|---|---|---|---|---|
| `index.html` | `/` | First-time visitors | Understand the experience, times, location and booking route | Choose a performance and book | Event dates, arrival times, tickets and booking links also appear on event pages | Practical facts and booking actions were repeated in a long hero; start times needed stronger hierarchy | Reorder the homepage around the proposition, performance starts, booking, concise essentials, visitor pathways, stories and reassurance |
| `walks.html` | `/walks.html` | Visitors choosing a date and time | Compare performances and begin booking | Choose a performance in TryBooking | Dates, ticket prices and arrival instructions repeat elsewhere | Six session links open a new tab; status counts are separate from booking-platform availability | Preserve the six official event records and current booking link; use the shared visitor navigation |
| `experience.html` | `/experience.html` | Visitors deciding what the experience involves | Understand the walk, audio and finale | Explore the performances | Arrival, late joining and duration repeat on the event page | Long-form story content precedes some practical details | Keep the artistic account and align its visitor navigation |
| `families.html` | `/families.html` | Parents, carers and family groups | Select tickets and assess practical family considerations | Choose a performance and book | Ticket prices, supervision, arrival and access details repeat on other pages | Dense hero copy made child ticket rules and supervision harder to scan | Lead with child ticket ages and Family Bundle composition; group supervision, route, headsets, seating, weather and late-arrival guidance |
| `access.html` | `/access.html` | Visitors with access requirements and anyone planning arrival | Review confirmed details and identify unknowns | Choose a performance and book, or contact the organiser | Dates, ticket prices and arrival are also on other event pages | Contact wording could suggest visitors should contact the organiser before booking | Use the existing guide as Plan Your Visit; add an at-a-glance summary and clarify that access contact is optional |
| `stories-learning.html` | `/stories-learning.html` | Visitors exploring the project’s stories and resources | Find story and learning content | Explore the stories and learning resources | Booking actions repeat elsewhere | Visitor-oriented booking and visit paths were not apparent in primary navigation | Align its navigation with the core visitor-flow pages |

## Repository and scope findings

- The site is static HTML. Primary navigation is manually repeated; the six
  core visitor-flow pages listed above now share the same six destinations.
- The repository contains additional navigation instances on secondary,
  archival, resource and utility pages. Those instances were not edited to
  stay within the brief's limit of seven existing public pages. Site-wide
  navigation parity beyond the six core visitor-flow pages remains a bounded
  follow-up rather than an implied completed change.
- `access.html` already contains the authoritative visitor and access guide, so
  no second Plan Your Visit URL was created.
- `walks.html` has six Event JSON-LD records. The Stage 1 checker passed before
  and after this work with the same counts; none of those records or the
  approved event facts were changed.
- The booking destination in the repository is
  `https://www.trybooking.com/uk/HEFF`. Direct checks of that page could not
  resolve the TryBooking hostname in this environment. The existing
  `docs/external-event-updates.md` records a possible venue wording difference
  on the external listing. Treat this as a **critical external follow-up**:
  the owner should verify the live venue, date/time products, prices, ticket
  categories, family composition, free-ticket requirements, duration,
  weather/cancellation wording and any booking fees directly in TryBooking.
  This PR does not change TryBooking or assert that the listing matches.
- The existing `walks.html` contains unverified physical/family statements
  about step-free access, maintained path surfaces, wheelchair seating and a
  chocolate gift/allergen information. These were not treated as approved
  facts; the owner should verify or remove them before relying on them.

## Visitor information gaps

No unverified physical features have been added to public copy. Confirmed
information includes the outdoor traffic-free route of less than a quarter of
a mile, outdoor concrete finale seating and supplied wireless headsets. Step-
free access, route measurements, venue facilities and equipment compatibility
are not treated as confirmed. The following information is still unavailable
and needs owner or specialist verification:

### Critical before event

- Confirm the event route's surface, widths, gradients, camber, riverside
  barrier details, road crossings, passing/turning space and service access.
- Verify or remove the existing `walks.html` claims about step-free access,
  maintained paths, wheelchair seating, a chocolate gift and allergen
  information.
- Confirm early-exit, rejoining and emergency-assistance arrangements.
- Confirm hearing-aid/neck-loop compatibility, headset fit and volume controls,
  and whether any equivalent audio alternative is available during the event.
- Recheck the live TryBooking location and all six ticket/session products
  against the approved facts before public promotion.

### Important before event

- Confirm accessible drop-off and parking information and public-transport
  directions.
- Find and verify the official Aviva Studios building-access guide before
  linking to it from the event access page.
- Confirm accessible toilet and Changing Places availability, assistance-dog
  arrangements, rest stops and seating details beyond the outdoor finale.
- Confirm the children’s headset arrangements, pushchair suitability and
  family facilities without making assumptions.
- Confirm sensory details, early-exit contact procedures and any on-the-day
  staffing directions.

### Future improvement

- Consider an in-experience transcript or equivalent audio alternative,
  detailed route description and formats for visitors who benefit from
  additional sensory or visual information.
- Consider gathering visitor feedback after the event, then developing a
  permission-based family follow-up activity, school resources, River Irwell
  stories and event photographs.
- Larger performance and asset improvements should be scoped separately;
  this change did not replace images, add a map or add a new dependency.

## Event status readiness

`walks.html` uses the existing `availability.json` as the one manually
maintained event-status source. Session `status` may be `available`,
`sold_out`, `cancelled`, `rescheduled` or `completed`; `null` means no
manually confirmed status is published. Update the file's `updatedAt` after
checking all session statuses. A session status is displayed only while the
timestamp is fresh. “Available” describes the event status, not a ticket
count; visitors must still confirm booking availability on TryBooking.

The same file's `urgentNotice` is `null` by default. When an actual update is
needed, set its `type` to `severe_weather`, `meeting_point_change`,
`delayed_start` or `cancelled_performance`, and provide its affected
performance, plain-text message, ISO timestamp, action label and internal
site or TryBooking action URL. The hidden-by-default alert includes the
affected performance, timestamp, visitor action and contact route. Clear the
notice when it no longer applies. No current status or urgent notice is
asserted by this change.

## Accessibility review classification

1. **Automatically checked:** Stage 1 event-facts checker; focused Stage 2A
   navigation destinations, duplicate/missing Plan Your Visit destinations,
   link destinations in the changed pages, and basic landmark/heading checks.
2. **Manually reviewed in browser:** The homepage was reviewed at 320, 390,
   768 and 1440 CSS pixels; the Families, Access and performance pages were
   reviewed at narrow viewports. No horizontal overflow was observed in those
   checks. The hidden-by-default event notice was inspected in its inactive
   state. This is not a full visual or zoom review.
3. **Requires disabled-user testing:** Screen-reader reading order, cognitive
   clarity, and practical use of touch and keyboard controls.
4. **Requires physical venue or route verification:** Route surfaces and
   dimensions, venue facilities, seating/rest details, equipment compatibility
   and emergency/early-exit arrangements.

No claim of WCAG 2.2 AA compliance is made.

## Responsive and visual validation

The homepage was checked at approximately 320, 390, 768 and 1440 CSS pixels;
Families, Access and the performance-selection page were checked at narrow
viewports. Browser zoom at 200% and 400%, and a complete visual review of every
changed page at every viewport, remain outstanding. The CSS retains existing
mobile breakpoints and adds one-column layouts for the new fact and pathway
groups on narrow screens. Further manual browser review and disabled-user
testing remain necessary.
