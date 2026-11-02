#!/usr/bin/env python3
"""Consistency checker for public event wording.

Usage: python3 scripts/check-event-facts.py [site_root]

site_root defaults to the repository root (source). Pass a build/output
directory to check generated production pages. Only public-facing pages
(*.html under site_root) are inspected; audit documents such as
APPROVED-EVENT-FACTS.md and docs/ may quote old values and are not checked.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
DATA_FILE = Path(__file__).resolve().parent.parent / "event-data.json"

PROHIBITED = [
    (r"\bages?\s*3\s*[–-]\s*17", "£5 category described as ages 3-17"),
    (r"over 3 and up to 17", "old £5 category wording (over 3 and up to 17)"),
    (r"under[- ]?(?:3|three)s?\b[^.]{0,60}\b(?:do(?:es)? not|don.t|no)\s+(?:require|need)\w*\s+a?\s*ticket", "under-threes need no ticket"),
    (r"\b(?:do(?:es)? not|don.t)\s+(?:require|need)\s+a\s+ticket", "claims no ticket is needed"),
    (r"no\s+ticket\s+(?:is\s+)?required", "claims no ticket is required"),
    (r"without\s+a\s+(?:ticket|reservation)", "claims attendance without a ticket"),
    (r"\bunder[- ]?(?:3|three)s?\b(?![^.]{0,60}\bfree ticket)", "'under 3' used instead of 'aged 3 and under'"),
    (r"arrive\s+20\s+minutes", "20-minute arrival wording"),
    (r"20\s+minutes\s+(?:before|early)", "20-minute arrival wording"),
    (r"\b(?:starts?|walks?|departs?|departures?|performances?)\s*(?:at|:|-|–)?\s*(?:10:00|13:00|10\.00|13\.00|10\s?am|1\s?pm)\b", "gathering time presented as walk departure"),
    (r"\b(?:10:00|13:00)\s+(?:departure|walk departs|start)\b", "gathering time presented as walk departure"),
    (r"booked start time", "ambiguous 'booked start time' arrival wording"),
]

SALES_PAGES = {
    "index.html": ["10:00", "10:30", "13:00", "13:30", "30 minutes", "aged 3 and under", "free ticket", "aged 4–17", "£5"],
    "walks.html": ["10:00", "10:30", "13:00", "13:30", "30 minutes", "aged 3 and under", "free ticket", "aged 4–17", "£5"],
    "access.html": ["10:00", "10:30", "13:00", "13:30", "30 minutes", "aged 3 and under", "free ticket", "aged 4–17", "£5"],
    "families.html": ["10:00", "10:30", "13:00", "13:30", "30 minutes", "aged 3 and under", "free ticket", "aged 4–17", "£5"],
    "experience.html": ["10:00", "10:30", "13:00", "13:30", "30 minutes"],
}

errors = []


def fail(page, msg):
    errors.append(f"{page}: {msg}")


def visible_text(html):
    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&#8211;", "–")):
        html = html.replace(a, b)
    return re.sub(r"\s+", " ", html)


def json_ld(html):
    return [json.loads(m) for m in re.findall(r'(?is)<script type="application/ld\+json">(.*?)</script>', html)]


def check_structured_data(page, html, data):
    morning = data["morning_departure_time"]
    afternoon = data["afternoon_departure_time"]
    for block in json_ld(html):
        for node in block.get("@graph", [block]):
            if node.get("@type") != "Event":
                continue
            start = node["startDate"]
            time = start[11:16]
            if time not in (morning, afternoon):
                fail(page, f"Event startDate {start} is not a walk departure time")
            if not start.endswith("+00:00"):
                fail(page, f"Event startDate {start} must use Europe/London December offset +00:00")
            gather = data["morning_gathering_time"] if time == morning else data["afternoon_gathering_time"]
            if node.get("doorTime", "")[11:16] != gather:
                fail(page, f"Event doorTime {node.get('doorTime')} should be gathering time {gather}")
            if "30 minutes before departure" not in node.get("description", ""):
                fail(page, "Event description lacks the 30-minutes-before-departure explanation")
            offers = {o["name"]: o["price"] for o in node.get("offers", [])}
            expected = {
                "Adult": "15",
                "Senior aged 65+": "12",
                "Child aged 4-17": "5",
                "Family bundle (two adults and two children or young people)": "38",
                "Child aged 3 and under (free; free ticket must be reserved)": "0",
                "Access companion": "0",
            }
            if offers != expected:
                fail(page, f"Event offers {offers} do not match approved tickets")


def main():
    data = json.loads(DATA_FILE.read_text())
    h = lambda t: int(t[:2]) * 60 + int(t[3:])
    if h(data["morning_departure_time"]) - h(data["morning_gathering_time"]) != data["required_arrival_minutes_before_departure"] or \
       h(data["afternoon_departure_time"]) - h(data["afternoon_gathering_time"]) != data["required_arrival_minutes_before_departure"]:
        fail("event-data.json", "gathering and departure times disagree with required arrival minutes")
    if data["free_child_maximum_age"] + 1 != data["paid_child_minimum_age"]:
        fail("event-data.json", "free and paid child age ranges are not contiguous")

    pages = sorted(ROOT.rglob("*.html"))
    if not pages:
        fail(str(ROOT), "no HTML pages found")
    for path in pages:
        rel = path.relative_to(ROOT).as_posix()
        html = path.read_text(encoding="utf-8")
        text = visible_text(html)
        scan = text + " " + " ".join(re.findall(r'(?is)<script type="application/ld\+json">(.*?)</script>', html))
        for pattern, label in PROHIBITED:
            m = re.search(pattern, scan, re.I)
            if m:
                fail(rel, f"prohibited wording ({label}): ...{scan[max(0, m.start()-30):m.end()+30]}...")
        if rel in SALES_PAGES:
            low = text.lower()
            for needle in SALES_PAGES[rel]:
                if needle.lower() not in low:
                    fail(rel, f"missing required text: {needle}")
        if rel == "walks.html":
            check_structured_data(rel, html, data)
    for rel in SALES_PAGES:
        if not (ROOT / rel).exists():
            fail(rel, "principal page missing")

    if errors:
        print("FAIL")
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(pages)} pages checked in {ROOT}")


main()
