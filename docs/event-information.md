# Mancunianity Flows event information

This static site keeps public event copy in its page HTML and operational facts
in the root `event-data.json`. The public event pages directly updated for this
correction are `index.html`, `walks.html`, `experience.html`, `families.html`
and `access.html`.

## Event and schedule

- **Compact name:** Mancunianity Flows
- **Full title:** Mancunianity Flows: What Can a River Remember?
- **Description:** A River Irwell audio-theatre experience
- **Dates:** Saturday 19, Sunday 20 and Monday 21 December 2026; two
  performances per day, six in total.
- **Meeting and check-in point:** The Social, Aviva Studios.
- **Address:** The Social, Aviva Studios, Water Street, Manchester M3 4JQ,
  United Kingdom.

| Performance | Arrival and check-in opens | Recommended latest check-in | Starts | Usual approximate finish | May run until |
|---|---:|---:|---:|---:|---:|
| Morning | 10:00 am | 10:25 am | 10:30 am | 11:35 am | 11:40 am |
| Afternoon | 1:00 pm | 1:25 pm | 1:30 pm | 2:35 pm | 2:40 pm |

Arrival times are not performance starts. The recommended latest check-in
times are not closures. The walking group leaves when the performance starts.

Approved full arrival wording:

> Please arrive at The Social, Aviva Studios, from 10:00 am for the 10:30 am
> performance, or from 1:00 pm for the 1:30 pm performance.
>
> The 30-minute arrival period allows time for check-in and wireless headset
> collection. We recommend checking in no later than 10:25 am for the morning
> performance or 1:25 pm for the afternoon performance.
>
> The walking group leaves the meeting point when the performance starts at
> 10:30 am and 1:30 pm.

## Late joining and duration

> If you arrive after the performance has started, you may be able to catch up
> and join the group because the route is short. However, joining the group and
> receiving a wireless headset cannot be guaranteed.

Late visitors should follow directions from Mancunianity or Aviva Studios staff
where available. Do not promise late joining, a headset, staff presence, a
catch-up route, a joining location, a refund or a transfer for lateness.

> The complete experience usually lasts approximately 65 minutes. Please allow
> up to 70 minutes, including the final 15-minute musical finale.

The duration includes the walking audio-theatre experience and finale, but not
arrival, check-in or headset collection. Finish times are approximate and are
not guaranteed.

## Tickets and supervision

- Adult: £15
- Senior aged 65 and over: £12
- Child or young person aged 3–17: £5
- Under three: free, but a free ticket must be booked
- Access Companion: free, but a free ticket must be booked
- Family Bundle: £38 for two adults and two children or young people aged 3–17

Under three means ages zero, one and two. Under-threes and Access Companions
attend free, but a free ticket must still be booked for every person attending.
Capacity products and prices have not been changed in this repository.

> Anyone aged 17 or under must attend with a responsible adult aged 18 or over.
> Children and young people must remain with their accompanying adult
> throughout the experience. Accompanying adults are responsible for their
> supervision and safety.

## Weather, route and equipment

> The experience continues in most weather, so come prepared for the forecast
> with warm, waterproof clothing and suitable footwear.
>
> If severe weather makes a performance unsafe, affected ticket holders will
> be contacted by email and offered a transfer to another performance, subject
> to availability, or a refund.

The traffic-free pedestrian route is less than a quarter of a mile. Wireless
headsets are supplied and cleaned between uses. No app is required, and
visitors do not need personal audio equipment. Children receive a spotting
activity. The final 15 minutes are an interactive riverside musical finale;
seating is on outdoor concrete seat blocks. Visitors may wish to bring a small
waterproof cushion or folded sit mat.

These facts do not imply universal accessibility, absence of pedestrians,
bicycles or service access, or suitability for every mobility aid. Existing
more detailed access information remains in `access.html`.

## Organiser and contact

- Organiser: Nakib Narat
- Role: Organiser and creative director
- Public email: [contact@mancunianity.uk](mailto:contact@mancunianity.uk)

> Mancunianity Flows is organised by Nakib Narat.
>
> For general, booking or visitor enquiries, email
> contact@mancunianity.uk.

## Metadata, structured data and validation

`walks.html` contains the six existing session-level Event records and the
principal event metadata. The `startDate` values are the six performance
starts, in Europe/London (GMT, `+00:00`). The records use The Social, Aviva
Studios; Water Street; Manchester M3 4JQ. They retain the existing booking
URLs, offers, availability presentation, capacity, images and `endDate` values
of 11:35 and 14:35 GMT. Those structured end times represent the usual
approximate finish; public copy also says performances may run later and labels
all finish times approximate.

`python3 scripts/check-event-facts.py` scans repository HTML (29 HTML
documents, including the 404 page and a navigation test fixture) and validates
the six records. The website is static HTML and has no separate build output;
the served files are the checked source files.

## Implementation decisions and boundaries

- Existing static pages and data were updated in place; no framework,
  component layer, or runtime event-data loader was added.
- The existing Aviva Studios image is used for social metadata.
- The Event organizer remains an `Organization` named Mancunianity Flows.
  Public copy identifies Nakib Narat as organiser and creative director; the
  preferred organizer entity type is a separate genuine ambiguity and was not
  changed.
- TryBooking, issued tickets, partner listings and production deployment are
  outside this repository change. See `docs/external-event-updates.md`.
