#!/usr/bin/env python3
"""Check visitor navigation and basic HTML/link invariants on Stage 2A pages."""

from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
PAGES = (
    "index.html",
    "walks.html",
    "experience.html",
    "families.html",
    "access.html",
    "stories-learning.html",
)
EXPECTED_NAV = (
    ("/experience.html", "Experience"),
    ("/walks.html", "Dates & Tickets"),
    ("/access.html", "Plan Your Visit"),
    ("/families.html", "Families & Access"),
    ("/stories-learning.html", "Stories & Learning"),
    ("/people.html", "Meet the People"),
    ("/weavers/", "The Weavers"),
    ("/about/", "About"),
)
ERRORS = []


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.nav_links = []
        self.main_count = 0
        self.h1_count = 0
        self.title_count = 0
        self._in_title = False
        self._title_text = []
        self._in_nav = False
        self._nav_depth = 0
        self._anchor = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "main":
            self.main_count += 1
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self.title_count += 1
            self._in_title = True
        if tag == "nav" and values.get("aria-label") == "Main navigation":
            self._in_nav = True
            self._nav_depth = 1
        elif self._in_nav and tag == "nav":
            self._nav_depth += 1
        if tag == "a":
            self._anchor = {
                "href": values.get("href", ""),
                "target": values.get("target", ""),
                "aria-describedby": values.get("aria-describedby", ""),
                "text": [],
                "in_nav": self._in_nav,
            }

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._anchor is not None:
            link = self._anchor
            link["text"] = " ".join(link["text"]).strip()
            self.links.append(link)
            if link["in_nav"]:
                self.nav_links.append((link["href"], link["text"]))
            self._anchor = None
        if tag == "nav" and self._in_nav:
            self._nav_depth -= 1
            if self._nav_depth == 0:
                self._in_nav = False

    def handle_data(self, data):
        if self._in_title:
            self._title_text.append(data)
        if self._anchor is not None:
            self._anchor["text"].append(data)


def fail(page, message):
    ERRORS.append(f"{page}: {message}")


def check_page(relative_path):
    source_path = ROOT / relative_path
    parser = PageParser()
    try:
        parser.feed(source_path.read_text(encoding="utf-8"))
        parser.close()
    except (OSError, UnicodeError) as error:
        fail(relative_path, f"could not read page: {error}")
        return None

    if parser.main_count != 1:
        fail(relative_path, f"expected one main landmark, found {parser.main_count}")
    if parser.h1_count != 1:
        fail(relative_path, f"expected one H1, found {parser.h1_count}")
    if parser.title_count != 1 or not "".join(parser._title_text).strip():
        fail(relative_path, "expected one descriptive page title")

    nav_destinations = tuple(parser.nav_links)
    if nav_destinations != EXPECTED_NAV:
        fail(relative_path, f"primary navigation differs from required destinations: {nav_destinations!r}")
    if sum(href == "/access.html" for href, _ in nav_destinations) != 1:
        fail(relative_path, "primary navigation must contain exactly one Plan Your Visit destination")

    for link in parser.links:
        href = link["href"]
        if not href:
            fail(relative_path, "found a link without an href")
            continue
        parts = urlsplit(href)
        if parts.scheme or parts.netloc:
            if "trybooking.com/uk/HEFF" in href and link["target"] == "_blank":
                description = link["aria-describedby"]
                if not description and "new tab" not in link["text"].lower():
                    # The page-level adjacent note is checked below.
                    if "new tab" not in source_path.read_text(encoding="utf-8").lower():
                        fail(relative_path, "booking link opens a new tab without an accessible notice")
            continue

        target_path = unquote(parts.path)
        if target_path.startswith("/"):
            resolved = ROOT / target_path.lstrip("/")
        elif target_path:
            resolved = (source_path.parent / target_path).resolve()
        else:
            resolved = source_path
        if not resolved.exists():
            fail(relative_path, f"broken relative URL: {href}")
            continue
        if parts.fragment and resolved == source_path:
            fragment = unquote(parts.fragment)
            if fragment not in parser.ids:
                fail(relative_path, f"missing fragment destination: {href}")

    return nav_destinations


def check_event_status_data():
    data_path = ROOT / "availability.json"
    expected_sessions = {
        "2026-12-19-1030",
        "2026-12-19-1330",
        "2026-12-20-1030",
        "2026-12-20-1330",
        "2026-12-21-1030",
        "2026-12-21-1330",
    }
    allowed_statuses = {"available", "sold_out", "cancelled", "rescheduled", "completed"}
    allowed_notices = {"severe_weather", "meeting_point_change", "delayed_start", "cancelled_performance"}
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail("availability.json", f"could not read valid status data: {error}")
        return

    if not isinstance(data, dict):
        fail("availability.json", "status data must be an object")
        return

    sessions = data.get("sessions", {})
    if not isinstance(sessions, dict):
        fail("availability.json", "sessions must be an object")
        return
    if set(sessions) != expected_sessions:
        fail("availability.json", "session status data must cover the existing six performances")
    for session_id, session in sessions.items():
        if not isinstance(session, dict):
            fail("availability.json", f"session data for {session_id} must be an object")
            continue
        if session.get("status") is not None and session.get("status") not in allowed_statuses:
            fail("availability.json", f"unsupported status for {session_id}: {session.get('status')!r}")

    urgent_notice = data.get("urgentNotice")
    if urgent_notice is not None and (
        not isinstance(urgent_notice, dict) or urgent_notice.get("type") not in allowed_notices
    ):
        fail("availability.json", "urgent notice must use a supported notice type")

    walks_source = (ROOT / "walks.html").read_text(encoding="utf-8")
    if (
        'id="event-urgent-notice"' not in walks_source
        or 'id="event-urgent-notice" class="event-urgent-notice" hidden role="alert"' not in walks_source
        or "data-performance" not in walks_source
        or "data-message" not in walks_source
        or "data-updated" not in walks_source
        or 'href="mailto:contact@mancunianity.uk"' not in walks_source
    ):
        fail("walks.html", "hidden urgent notice must include status, time, action and contact fields")


def main():
    nav_sets = [check_page(page) for page in PAGES]
    comparable = [nav for nav in nav_sets if nav is not None]
    if comparable and any(nav != comparable[0] for nav in comparable[1:]):
        fail("navigation", "primary navigation destinations are not identical across changed pages")
    check_event_status_data()

    if ERRORS:
        print("\n".join(f"FAIL: {error}" for error in ERRORS))
        return 1

    print(f"OK: checked {len(PAGES)} visitor pages, navigation, local links and event-status data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
