#!/usr/bin/env python3
"""Check public event wording and Event structured data.

Usage: python3 scripts/check-event-facts.py [site_root]

site_root defaults to the repository root. Pass a generated output directory
to check rendered pages. Only public HTML is scanned; internal documentation
may describe follow-up work.
"""
import html
import json
import re
import sys
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
EXPECTED_OFFERS = {
    "Adult": "15",
    "Senior aged 65 and over": "12",
    "Child or young person aged 3-17": "5",
    "Family Bundle: two adults and two children or young people aged 3-17": "38",
    "Under three: free, but a free ticket must be booked": "0",
    "Access Companion: free, but a free ticket must be booked": "0",
}

errors = []


def fail(page, message):
    errors.append(f"{page}: {message}")


def visible_text(source):
    source = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", source)
    source = re.sub(r"(?s)<[^>]+>", " ", source)
    return re.sub(r"\s+", " ", html.unescape(source))


def json_ld(source):
    blocks = re.findall(
        r'(?is)<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source,
    )
    return [json.loads(block) for block in blocks]


def event_nodes(block):
    nodes = block.get("@graph", [block]) if isinstance(block, dict) else []
    return [node for node in nodes if isinstance(node, dict) and node.get("@type") == "Event"]


def check_event_data(data):
    if data["morning_arrival_time"] != "10:00" or data["morning_performance_start_time"] != "10:30":
        fail("event-data.json", "morning arrival and performance start must be 10:00 and 10:30")
    if data["afternoon_arrival_time"] != "13:00" or data["afternoon_performance_start_time"] != "13:30":
        fail("event-data.json", "afternoon arrival and performance start must be 13:00 and 13:30")
    if data["morning_recommended_latest_checkin_time"] != "10:25" or data["afternoon_recommended_latest_checkin_time"] != "13:25":
        fail("event-data.json", "recommended latest check-in must be 10:25 and 13:25")
    if (data["free_child_minimum_age"], data["free_child_maximum_age"]) != (0, 2):
        fail("event-data.json", "free Under-three ticket age range must be zero to two")
    if (data["paid_child_minimum_age"], data["paid_child_maximum_age"]) != (3, 17):
        fail("event-data.json", "paid child ticket age range must be three to seventeen")
    if data["family_bundle_composition"] != "two adults and two children or young people aged 3-17":
        fail("event-data.json", "Family Bundle composition is incorrect")
    if data["meeting_point"] != "The Social, Aviva Studios" or data["postal_code"] != "M3 4JQ":
        fail("event-data.json", "meeting point or postcode is incorrect")


def check_structured_events(page, source):
    try:
        blocks = json_ld(source)
    except json.JSONDecodeError as error:
        fail(page, f"invalid JSON-LD: {error}")
        return
    events = [node for block in blocks for node in event_nodes(block)]
    if len(events) != 6:
        fail(page, f"expected six session-level Event records, found {len(events)}")
        return
    starts = [event.get("startDate") for event in events]
    if starts != EXPECTED_STARTS:
        fail(page, f"Event startDate values do not match the six confirmed performance starts: {starts}")
    for event in events:
        start = event.get("startDate", "")
        expected_door = start[:11] + ("10:00:00+00:00" if start[11:16] == "10:30" else "13:00:00+00:00")
        if event.get("doorTime") != expected_door:
            fail(page, f"doorTime {event.get('doorTime')} does not match arrival opening for {start}")
        if not event.get("name", "").startswith(EXPECTED_TITLE):
            fail(page, f"Event name does not use the full event title: {event.get('name')}")
        location = event.get("location", {})
        address = location.get("address", {})
        if location.get("name") != "The Social, Aviva Studios":
            fail(page, f"incorrect event location: {location.get('name')}")
        if address.get("postalCode") != "M3 4JQ" or address.get("streetAddress") != "The Social, Aviva Studios, Water Street":
            fail(page, f"incorrect event postal address: {address}")
        if "Riverside entrance" in location.get("name", ""):
            fail(page, "Riverside entrance must not be the event location")
        offers = {offer.get("name"): offer.get("price") for offer in event.get("offers", [])}
        if offers != EXPECTED_OFFERS:
            fail(page, f"Event offer categories or prices are incorrect: {offers}")
        if event.get("endDate"):
            fail(page, "do not encode estimated performance finishes as exact Event endDate values")
        if event.get("organizer", {}).get("email") != "contact@mancunianity.uk":
            fail(page, "Event organizer contact email is missing or incorrect")


def check_metadata(page, source):
    if page != "walks.html":
        return
    required = [
        f'<title>{EXPECTED_TITLE}</title>',
        f'<meta name="description" content="{EXPECTED_DESCRIPTION}">',
        '<link rel="canonical" href="https://mancunianity.uk/walks.html">',
        f'<meta property="og:title" content="{EXPECTED_TITLE}">',
        f'<meta property="og:description" content="{EXPECTED_DESCRIPTION}">',
        '<meta property="og:url" content="https://mancunianity.uk/walks.html">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta property="og:image" content="https://mancunianity.uk/images/aviva-studios.webp">',
    ]
    for expected in required:
        if expected not in source:
            fail(page, f"required event metadata missing: {expected}")
    if not (ROOT / "images/aviva-studios.webp").is_file():
        fail(page, "event metadata references a missing social image")


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    check_event_data(data)
    pages = sorted(ROOT.rglob("*.html"))
    if not pages:
        fail(str(ROOT), "no HTML pages found")

    for path in pages:
        relative = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        text = visible_text(source)
        if "M3 4JG" in source:
            fail(relative, "incorrect Aviva Studios postcode M3 4JG remains")
        if "Water STreet" in source:
            fail(relative, "incorrect Water STreet capitalization remains")
        if re.search(r"\b(?:meet|meeting point)\b[^.]{0,80}\bRiverside entrance\b", text, re.I):
            fail(relative, "Riverside entrance is described as the event meeting point")
        if re.search(r"\b(?:arrive|arrival)\s+20 minutes\b|\b20 minutes before\b", text, re.I):
            fail(relative, "obsolete 20-minute arrival instruction remains")
        if re.search(r"\b(?:Child|children) aged 4[–-]17\b|\baged 4[–-]17\b", text, re.I):
            fail(relative, "obsolete paid child or Family Bundle age range remains")
        if re.search(r"\b(?:aged\s+3\s+and\s+under|three\s+and\s+under)\b", text, re.I):
            fail(relative, "obsolete under-three category wording remains")
        if re.search(r"\bunder[- ]3s?\b|\bunder four\b", text, re.I):
            fail(relative, "obsolete under-three or under-four wording remains")
        if re.search(r"ordinary rain will not stop|severe weather or unsafe river conditions may", text, re.I):
            fail(relative, "obsolete weather or cancellation wording remains")
        if re.search(
            r"\b(?:performance|walk|group)\s+(?:starts?|begins?|departs?)\s+(?:at\s+)?(?:10:00|13:00|1:00\s+pm)\b",
            text,
            re.I,
        ):
            fail(relative, "arrival and check-in opening time is presented as a performance start")
        if re.search(r"\barrive\s+(?:at\s+)?1:30\s+pm\b", text, re.I):
            fail(relative, "afternoon performance start is presented as an arrival time")

        if relative in {"index.html", "walks.html", "access.html", "families.html"}:
            if "The Social, Aviva Studios" not in text or "M3 4JQ" not in text:
                fail(relative, "confirmed meeting point and postcode must be visible")
            for phrase in (
                "10:30 am",
                "1:30 pm",
                "10:00 am",
                "1:00 pm",
                "10:25 am",
                "1:25 pm",
                "Under-threes and Access Companions attend free, but a free ticket must still be booked for every person attending.",
            ):
                if phrase not in text:
                    fail(relative, f"required event information missing: {phrase}")
        if relative in {"index.html", "walks.html", "access.html", "families.html"}:
            for phrase in (
                "Child or young person aged 3–17",
                "Family Bundle",
                "two adults and two children or young people aged 3–17",
                "£15",
                "£12",
                "£5",
                "£38",
            ):
                if phrase not in text:
                    fail(relative, f"required ticket information missing: {phrase}")
        if relative in {"access.html", "families.html"}:
            if "Anyone aged 17 or under must attend with a responsible adult aged 18 or over." not in text:
                fail(relative, "approved child and young person supervision wording is missing")
        if relative == "walks.html":
            check_structured_events(relative, source)
            check_metadata(relative, source)
            if "The walking group leaves the meeting point when the performance starts at 10:30 am and 1:30 pm." not in text:
                fail(relative, "full approved arrival wording is incomplete")

    experience = ROOT / "experience.html"
    if experience.exists():
        text = visible_text(experience.read_text(encoding="utf-8"))
        for phrase in (
            "The landscape is not scenery.",
            "Manchester-Salford connections",
            "If you arrive after the performance has started, you may be able to catch up and join the group because the route is short.",
        ):
            if phrase not in text:
                fail("experience.html", f"required event description missing: {phrase}")

    if errors:
        print("FAIL")
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(pages)} public pages and six Event records checked in {ROOT}")


main()
