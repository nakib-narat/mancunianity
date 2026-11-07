#!/usr/bin/env python3
"""Check current event copy, metadata and rendered Event structured data.

Usage: python3 scripts/check-event-facts.py [site_root]

The site is static HTML, so the checked source files are also its rendered
output. All HTML documents are scanned for obsolete wording; 404.html and
nav-fix-test.html are included in that scan but are not event landing pages.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
DATA_FILE = Path(__file__).resolve().parent.parent / "event-data.json"
EXPECTED_TITLE = "Mancunianity Flows: What Can a River Remember?"
EXPECTED_DESCRIPTION = (
    "A River Irwell audio-theatre experience with supplied wireless headphones "
    "and a 15-minute live musical finale, taking place in Manchester from "
    "19–21 December 2026."
)
EXPECTED_STARTS = [
    "2026-12-19T10:30:00+00:00",
    "2026-12-19T13:30:00+00:00",
    "2026-12-20T10:30:00+00:00",
    "2026-12-20T13:30:00+00:00",
    "2026-12-21T10:30:00+00:00",
    "2026-12-21T13:30:00+00:00",
]
EXPECTED_ENDS = [
    "2026-12-19T11:35:00+00:00",
    "2026-12-19T14:35:00+00:00",
    "2026-12-20T11:35:00+00:00",
    "2026-12-20T14:35:00+00:00",
    "2026-12-21T11:35:00+00:00",
    "2026-12-21T14:35:00+00:00",
]
EXPECTED_FULL_ARRIVAL = (
    "Please arrive at The Social, Aviva Studios, from 10:00 am for the 10:30 am performance, "
    "or from 1:00 pm for the 1:30 pm performance. The 30-minute arrival period allows time "
    "for check-in and wireless headset collection. We recommend checking in no later than "
    "10:25 am for the morning performance or 1:25 pm for the afternoon performance. "
    "The walking group leaves the meeting point when the performance starts at 10:30 am and 1:30 pm."
)
EXPECTED_OFFERS = {
    "Adult": "15",
    "Senior aged 65 and over": "12",
    "Child or young person aged 3-17": "5",
    "Family Bundle: two adults and two children or young people aged 3-17": "38",
    "Under three: free, but a free ticket must be booked": "0",
    "Access Companion: free, but a free ticket must be booked": "0",
}
EVENT_PAGES = ("index.html", "walks.html", "access.html", "families.html")
REQUIRED_PAGES = (*EVENT_PAGES, "experience.html")
ERRORS = []


class PageParser(HTMLParser):
    """Extract visible text, metadata and JSON-LD without relying on HTML layout."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.visible = []
        self.metas = []
        self.canonicals = []
        self.json_ld = []
        self._ignored = 0
        self._json_script = False
        self._json_parts = []
        self._in_title = False
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style"}:
            self._ignored += 1
            if tag == "script" and values.get("type", "").lower() == "application/ld+json":
                self._json_script = True
                self._json_parts = []
        elif tag == "meta":
            self.metas.append(values)
        elif tag == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", ""))
        elif tag in {"p", "li", "br", "div", "section", "h1", "h2", "h3"}:
            self.visible.append(" ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style"}:
            if tag == "script" and self._json_script:
                self.json_ld.append("".join(self._json_parts))
                self._json_script = False
            self._ignored = max(0, self._ignored - 1)
        elif tag in {"p", "li", "br", "div", "section", "h1", "h2", "h3"}:
            self.visible.append(" ")

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        if self._json_script:
            self._json_parts.append(data)
        if not self._ignored:
            self.visible.append(data)

    @property
    def text(self):
        text = re.sub(r"\s+", " ", html.unescape(" ".join(self.visible))).strip()
        return re.sub(r"\s+([,.;:!?])", r"\1", text)

    @property
    def title(self):
        return re.sub(r"\s+", " ", html.unescape(" ".join(self.title_parts))).strip()


def fail(page, message):
    ERRORS.append(f"{page}: {message}")


def parse_page(page, source):
    parser = PageParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception as error:  # HTMLParser errors should be reported, not hidden.
        fail(page, f"HTML parsing failed: {error}")
    return parser


def parse_json_blocks(page, parser):
    blocks = []
    for index, content in enumerate(parser.json_ld, start=1):
        try:
            blocks.append(json.loads(content))
        except json.JSONDecodeError as error:
            fail(page, f"JSON-LD block {index} is invalid: {error}")
    return blocks


def collect_events(node):
    found = []
    if isinstance(node, dict):
        types = node.get("@type", [])
        if types == "Event" or (isinstance(types, list) and "Event" in types):
            found.append(node)
        for value in node.values():
            found.extend(collect_events(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(collect_events(value))
    return found


def check_event_data(data):
    required = {
        "morning_arrival_time": "10:00",
        "morning_recommended_latest_checkin_time": "10:25",
        "morning_performance_start_time": "10:30",
        "morning_usual_finish_time": "11:35",
        "morning_possible_finish_time": "11:40",
        "afternoon_arrival_time": "13:00",
        "afternoon_recommended_latest_checkin_time": "13:25",
        "afternoon_performance_start_time": "13:30",
        "afternoon_usual_finish_time": "14:35",
        "afternoon_possible_finish_time": "14:40",
        "meeting_point": "The Social, Aviva Studios",
        "street_address": "Water Street",
        "postal_code": "M3 4JQ",
        "experience_usual_duration_minutes": 65,
        "experience_allow_up_to_minutes": 70,
        "musical_finale_minutes": 15,
        "adult_price_gbp": 15,
        "senior_price_gbp": 12,
        "paid_child_minimum_age": 3,
        "paid_child_maximum_age": 17,
        "paid_child_price_gbp": 5,
        "family_bundle_price_gbp": 38,
        "access_companion_price_gbp": 0,
    }
    for key, expected in required.items():
        if data.get(key) != expected:
            fail("event-data.json", f"{key} must be {expected!r}, got {data.get(key)!r}")
    if (data.get("free_child_minimum_age"), data.get("free_child_maximum_age")) != (0, 2):
        fail("event-data.json", "Under-three ticket age range must be zero to two")
    if data.get("free_child_ticket_required") is not True:
        fail("event-data.json", "Under-three tickets must be required")
    if data.get("access_companion_ticket_required") is not True:
        fail("event-data.json", "Access Companion tickets must be required")
    if data.get("family_bundle_composition") != "two adults and two children or young people aged 3-17":
        fail("event-data.json", "Family Bundle composition must be two adults and two 3-17 year olds")
    expected_dates = ["2026-12-19", "2026-12-20", "2026-12-21"]
    if data.get("event_dates") != expected_dates:
        fail("event-data.json", f"event dates must be {expected_dates}")
    if data.get("booking_url") != "https://www.trybooking.com/uk/HEFF":
        fail("event-data.json", "existing booking URL has changed")


def metadata(parser, key, value):
    return [meta for meta in parser.metas if meta.get(key) == value]


def check_metadata(page, parser, root):
    expected_title = EXPECTED_TITLE if page == "walks.html" else None
    if page == "walks.html" and parser.title != expected_title:
        fail(page, f"page title must be {expected_title!r}")
    if page == "index.html" and not parser.title.startswith(EXPECTED_TITLE):
        fail(page, "homepage title must use the full event title")

    description = metadata(parser, "name", "description")
    if len(description) != 1 or description[0].get("content") != EXPECTED_DESCRIPTION:
        fail(page, "expected one accurate event meta description")

    if len(parser.canonicals) != 1:
        fail(page, f"expected one canonical URL, found {len(parser.canonicals)}")
    expected_url = "https://mancunianity.uk/" if page == "index.html" else "https://mancunianity.uk/walks.html"
    if parser.canonicals != [expected_url]:
        fail(page, f"canonical URL must be {expected_url}")

    for key, value in (
        ("property", "og:title"),
        ("property", "og:description"),
        ("property", "og:url"),
        ("property", "og:image"),
        ("name", "twitter:title"),
        ("name", "twitter:description"),
        ("name", "twitter:image"),
    ):
        records = metadata(parser, key, value)
        if len(records) != 1:
            fail(page, f"expected one {value} metadata field, found {len(records)}")
    title = metadata(parser, "property", "og:title")
    desc = metadata(parser, "property", "og:description")
    url = metadata(parser, "property", "og:url")
    image = metadata(parser, "property", "og:image")
    if title and title[0].get("content") != EXPECTED_TITLE:
        fail(page, "Open Graph title is incorrect")
    if desc and desc[0].get("content") != EXPECTED_DESCRIPTION:
        fail(page, "Open Graph description is incorrect")
    if url and url[0].get("content") != expected_url:
        fail(page, "Open Graph URL does not match canonical URL")
    image_path = root / "images/aviva-studios.webp"
    if not image_path.is_file():
        fail(page, "existing social image asset is missing")
    if image and image[0].get("content") != "https://mancunianity.uk/images/aviva-studios.webp":
        fail(page, "Open Graph image does not reference the existing social image")
    twitter_card = metadata(parser, "name", "twitter:card")
    if len(twitter_card) != 1 or twitter_card[0].get("content") != "summary_large_image":
        fail(page, "Twitter card metadata is missing or incorrect")
    twitter_image = metadata(parser, "name", "twitter:image")
    if twitter_image and twitter_image[0].get("content") != "https://mancunianity.uk/images/aviva-studios.webp":
        fail(page, "Twitter image does not reference the existing social image")


def check_structured_events(page, blocks):
    events = [event for block in blocks for event in collect_events(block)]
    if len(events) != 6:
        fail(page, f"expected six session-level Event records, found {len(events)}")
        return
    starts = [event.get("startDate") for event in events]
    if starts != EXPECTED_STARTS:
        fail(page, f"Event startDate values do not match the six confirmed starts: {starts}")
    ends = [event.get("endDate") for event in events]
    if ends != EXPECTED_ENDS:
        fail(page, f"existing Event endDate values do not match usual approximate finishes: {ends}")

    event_ids = [event.get("@id") for event in events]
    if None in event_ids or len(set(event_ids)) != 6:
        fail(page, "Event @id values are missing or duplicated")

    expected_images = {
        "https://mancunianity.uk/images/access/river-irwell-route.webp",
        "https://mancunianity.uk/images/aviva-studios.webp",
    }
    for event in events:
        start = event.get("startDate", "")
        is_morning = start[11:16] == "10:30"
        arrival = "10:00:00+00:00" if is_morning else "13:00:00+00:00"
        expected_door = start[:11] + arrival
        expected_id = f"https://mancunianity.uk/walks.html#performance-{start[:10]}-{start[11:16].replace(':', '')}"
        if event.get("@type") != "Event":
            fail(page, f"structured record at {start} is not an Event")
        if event.get("name") != EXPECTED_TITLE:
            fail(page, f"Event title is incorrect for {start}")
        if event.get("@id") != expected_id or event.get("url") != expected_id:
            fail(page, f"Event ID/URL is incorrect for {start}")
        if event.get("doorTime") != expected_door:
            fail(page, f"doorTime {event.get('doorTime')} does not match arrival opening for {start}")
        location = event.get("location", {})
        address = location.get("address", {})
        if location.get("@type") != "Place" or location.get("name") != "The Social, Aviva Studios":
            fail(page, f"incorrect event venue for {start}: {location}")
        if address.get("@type") != "PostalAddress":
            fail(page, f"PostalAddress missing for {start}")
        if (
            address.get("streetAddress") != "Water Street"
            or address.get("addressLocality") != "Manchester"
            or address.get("postalCode") != "M3 4JQ"
            or address.get("addressCountry") != "GB"
        ):
            fail(page, f"incorrect event postal address for {start}: {address}")
        offers = {offer.get("name"): offer.get("price") for offer in event.get("offers", [])}
        if offers != EXPECTED_OFFERS:
            fail(page, f"Event ticket offers/prices are incorrect for {start}: {offers}")
        if any(offer.get("priceCurrency") != "GBP" for offer in event.get("offers", [])):
            fail(page, f"offer currency is not GBP for {start}")
        if any(offer.get("url") != "https://www.trybooking.com/uk/HEFF" for offer in event.get("offers", [])):
            fail(page, f"booking URL changed for an offer at {start}")
        images = set(event.get("image", []))
        if images != expected_images:
            fail(page, f"existing Event images changed for {start}: {images}")
        for image in images:
            local_path = image.removeprefix("https://mancunianity.uk/")
            if not (ROOT / local_path).is_file():
                fail(page, f"Event image asset is missing: {local_path}")
        organizer = event.get("organizer", {})
        if organizer.get("@type") != "Organization" or organizer.get("email") != "contact@mancunianity.uk":
            fail(page, f"organizer type or contact email is incorrect for {start}")
        if "performer" in event or "availability" in event:
            fail(page, f"unconfirmed performer or event availability added for {start}")


def check_page_copy(relative, text, source):
    if "M3 4JG" in source:
        fail(relative, "incorrect Aviva Studios postcode M3 4JG remains")
    if "Water STreet" in source:
        fail(relative, "incorrect Water STreet capitalization remains")
    if re.search(
        r"\b(?:meet(?:ing)? point|check[- ]?in(?: point)?)\b[^.]{0,100}\bRiverside entrance\b",
        text,
        re.I,
    ):
        fail(relative, "Riverside entrance is described as the event meeting point")
    prohibited = (
        (r"\b(?:arrive|arrival)\s+20 minutes\b|\b20 minutes before\b", "obsolete 20-minute arrival instruction"),
        (r"\b(?:Child|children) aged 4[–-]17\b|\baged 4[–-]17\b", "obsolete aged 4-17 ticket wording"),
        (r"\b(?:aged\s+3\s+and\s+under|three\s+and\s+under)\b", "obsolete 'aged three and under' wording"),
        (r"\bunder[- ]3s?\b|\bunder four\b", "obsolete under-three or under-four wording"),
        (
            r"\bunder[- ](?:three|3)s?\b[^.]{0,100}\bno ticket\b|\bno ticket\b[^.]{0,100}\bunder[- ](?:three|3)s?\b",
            "under-threes incorrectly described as not needing a ticket",
        ),
        (r"ordinary rain will not stop|severe weather or unsafe river conditions may", "obsolete weather/cancellation wording"),
        (r"\b(?:allow around |approximately )?90 minutes in total\b", "obsolete 90-minute total duration"),
        (
            r"\b(?:plus|in addition to|followed by an additional)\s+(?:the final )?15-minute (?:musical )?finale\b",
            "finale incorrectly presented as extra to the published duration",
        ),
        (
            r"\b(?:performance|walk|group)\s+(?:starts?|begins?|departs?)\s+(?:at\s+)?(?:10:00|13:00|1:00\s+pm)\b",
            "arrival opening time presented as a performance start",
        ),
        (
            r"\b(?:arrive|arrival(?: and check-in)?)\s+(?:at|from)\s+1:30\s+pm\b",
            "afternoon performance start presented as arrival",
        ),
        (
            r"\b(?:check[- ]?in|arrival)(?: time)?\s+(?:closes?|ends?)\s+(?:at\s+)?(?:10:25\s+am|1:25\s+pm)\b",
            "recommended latest check-in presented as a closure",
        ),
        (r"\b(?:late|lateness)[^.]{0,100}\b(?:refund|transfer)\b", "refund/transfer promise tied to lateness"),
        (r"\b(?:guaranteed|will be able to)\b[^.]{0,80}\b(?:late joining|catch up|headset)\b", "guarantee of late joining or headset"),
    )
    for pattern, label in prohibited:
        if re.search(pattern, text, re.I):
            fail(relative, label)

    if relative in EVENT_PAGES:
        for value in ("The Social, Aviva Studios", "M3 4JQ", "Water Street"):
            if value not in text:
                fail(relative, f"confirmed location text missing: {value}")
        ticket_labels = (
            r"\bAdult:?\s*£15\b",
            r"\bSenior aged 65 and over:?\s*£12\b",
            r"\bChild or young person aged 3[–-]17:?\s*£5\b",
            r"\bFamily Bundle:?\s*£38\b[^.]{0,100}\btwo adults and two children or young people aged 3[–-]17\b",
            r"\bUnder three:?\s*free, but a free ticket must be booked\b",
            r"\bAccess Companion:?\s*free, but a free ticket must be booked\b",
        )
        for pattern in ticket_labels:
            if not re.search(pattern, text, re.I):
                fail(relative, f"ticket category/price wording is missing or mismatched: {pattern}")
        for value in (
            "10:00 am",
            "10:25 am",
            "10:30 am",
            "1:00 pm",
            "1:25 pm",
            "1:30 pm",
            "Child or young person aged 3–17",
            "Family Bundle",
            "two adults and two children or young people aged 3–17",
            "£15",
            "£12",
            "£5",
            "£38",
        ):
            if value not in text:
                fail(relative, f"required event/ticket wording missing: {value}")
        if "Under-threes and Access Companions attend free, but a free ticket must still be booked for every person attending." not in text:
            fail(relative, "under-three and Access Companion ticket explanation is missing")
        if EXPECTED_FULL_ARRIVAL not in text:
            fail(relative, "approved full arrival, performance and recommended check-in wording is incomplete")
        if not re.search(
            r"up to 70 minutes, including (?:(?:the final|a) )?15-minute musical finale",
            text,
            re.I,
        ):
            fail(relative, "duration or included finale wording is missing")

    supervision_pages = ("index.html", "access.html", "families.html")
    supervision = (
        "Anyone aged 17 or under must attend with a responsible adult aged 18 or over. "
        "Children and young people must remain with their accompanying adult throughout the experience. "
        "Accompanying adults are responsible for their supervision and safety."
    )
    if relative in supervision_pages and supervision not in text:
        fail(relative, "approved supervision wording is missing")

    late_joining_pages = ("access.html", "experience.html")
    late_joining = (
        "If you arrive after the performance has started, you may be able to catch up and join the group "
        "because the route is short. However, joining the group and receiving a wireless headset cannot be guaranteed."
    )
    if relative in late_joining_pages and late_joining not in text:
        fail(relative, "approved late-joining wording is missing")

    weather_pages = ("access.html", "walks.html")
    weather = (
        "The experience continues in most weather, so come prepared for the forecast with warm, waterproof "
        "clothing and suitable footwear. If severe weather makes a performance unsafe, affected ticket holders "
        "will be contacted by email and offered a transfer to another performance, subject to availability, or a refund."
    )
    if relative in weather_pages and weather not in text:
        fail(relative, "approved weather and cancellation wording is missing")

    route_pages = ("access.html", "walks.html")
    route_facts = (
        "traffic-free pedestrian route",
        "less than a quarter of a mile",
        "Wireless headsets are supplied and cleaned between uses",
        "Children receive a spotting activity",
        "interactive riverside musical finale",
        "outdoor concrete seat blocks",
        "small waterproof cushion or folded sit mat",
    )
    if relative in route_pages:
        for fact in route_facts:
            if fact.lower() not in text.lower():
                fail(relative, f"confirmed route/equipment/finale information missing: {fact}")

    if relative == "access.html":
        if "Mancunianity Flows is organised by Nakib Narat." not in text:
            fail(relative, "organiser wording is missing")
        if "For general, booking or visitor enquiries, email contact@mancunianity.uk." not in text:
            fail(relative, "approved enquiry wording is missing")
        if not re.search(
            r'<a\b[^>]*href=["\']mailto:contact@mancunianity\.uk["\'][^>]*>\s*contact@mancunianity\.uk\s*</a>',
            source,
            re.I,
        ):
            fail(relative, "public contact email is not a working mailto link")


def main():
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail("event-data.json", f"cannot read valid event data: {error}")
        data = {}
    check_event_data(data)

    pages = sorted(ROOT.rglob("*.html"))
    if not pages:
        fail(str(ROOT), "no HTML documents found")
    for required in REQUIRED_PAGES:
        if not (ROOT / required).is_file():
            fail(required, "required current public event page is missing")

    parsed_pages = {}
    all_events = []
    for path in pages:
        relative = path.relative_to(ROOT).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as error:
            fail(relative, f"cannot read HTML document: {error}")
            continue
        parser = parse_page(relative, source)
        parsed_pages[relative] = (source, parser)
        check_page_copy(relative, parser.text, source)
        blocks = parse_json_blocks(relative, parser)
        events = [event for block in blocks for event in collect_events(block)]
        if relative != "walks.html" and events:
            fail(relative, "unexpected duplicate Event structured data outside walks.html")
        all_events.extend((relative, event) for event in events)

        if relative in {"index.html", "walks.html"}:
            check_metadata(relative, parser, ROOT)

    walks = parsed_pages.get("walks.html")
    if walks:
        source, parser = walks
        blocks = parse_json_blocks("walks.html", parser)
        check_structured_events("walks.html", blocks)
        for passage in (
            "Follow the River Irwell for around 50 minutes through stories, music, surprising history and an immersive headphone soundscape.",
            "The journey moves from Manchester across the River Irwell into Salford.",
            "Here the new Mancunianity Flows song is unveiled.",
        ):
            if passage not in parser.text:
                fail("walks.html", f"established artistic or route copy is missing: {passage[:80]}")

    experience = parsed_pages.get("experience.html")
    if experience:
        text = experience[1].text
        required_copy = (
            "Mancunianity Flows is an immersive audio-theatre journey through one extraordinary quarter-mile "
            "of the River Irwell, where nearly 200 years of transport, industry, architecture, ecology and "
            "Manchester-Salford connections sit almost on top of one another.",
            "Wear a supplied wireless headset and follow the Irwell through storytelling, local voices, songs, "
            "music and a specially created atmospheric soundscape. The landscape is not scenery. The real river, "
            "bridges, railway arches, waterways and buildings around you are the stage.",
            "No phone, app or personal headphones are needed. Wireless headphones are supplied and hygienically "
            "prepared before each experience.",
            "If you arrive after the performance has started, you may be able to catch up and join the group "
            "because the route is short. However, joining the group and receiving a wireless headset cannot be guaranteed.",
        )
        for passage in required_copy:
            if passage not in text:
                fail("experience.html", f"approved artistic or late-joining copy is missing: {passage[:80]}")

    # The static site must expose one set of six unique session records only.
    if len(all_events) != 6:
        fail("site", f"expected six Event records across all HTML, found {len(all_events)}")
    ids = [event.get("@id") for _, event in all_events]
    if len(set(ids)) != len(ids):
        fail("site", "duplicate Event @id found across rendered HTML")

    if ERRORS:
        print("FAIL")
        print("\n".join(ERRORS))
        sys.exit(1)
    skipped = len(pages) - len(parsed_pages)
    print(
        f"OK: HTML pages discovered: {len(pages)}; checked: {len(parsed_pages)}; "
        f"event-related pages checked: {sum(page in parsed_pages for page in REQUIRED_PAGES)}; "
        f"pages skipped: {skipped}; Event records checked: {len(all_events)}."
    )


main()
