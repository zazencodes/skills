#!/usr/bin/env python3
"""Refresh the bundled Wikipedia reference; Python 3.9+, standard library only."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

TITLE = "Wikipedia:Signs of AI writing"
SOURCE_URL = "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing"
API_URL = "https://en.wikipedia.org/w/api.php?" + urlencode({
    "action": "parse", "page": TITLE, "prop": "text|revid", "format": "json", "formatversion": 2,
})
STATE_START = "<!-- humanizer-source-state\n"
STATE_END = "\n-->"
BODY_MARKER = "<!-- article:start -->\n"
MAX_BYTES = 5 * 1024 * 1024


class RefreshError(Exception):
    pass


def utc_string(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_date(value):
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ValueError("Fetch timestamp must include a timezone")
    return date


def config_from_skill(root):
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r'<!-- refresh-config:start -->\s*```json\s*(.*?)\s*```\s*<!-- refresh-config:end -->', skill, re.S)
    if not match:
        raise RefreshError("Missing refresh configuration in SKILL.md")
    try:
        config = json.loads(match.group(1))
        for key, upper in (("refresh_interval_days", 3650), ("request_timeout_seconds", 60)):
            value = config[key]
            if type(value) is not int or not 1 <= value <= upper:
                raise ValueError(f"{key} must be an integer from 1 to {upper}")
        return config
    except (ValueError, KeyError, TypeError) as exc:
        raise RefreshError(f"Invalid refresh configuration: {exc}") from exc


class ArticleParser(HTMLParser):
    """Retain article text, headings, example blocks, lists and source links."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    BLOCK = {"div", "p", "table", "tr", "dl", "dt", "dd", "ul", "ol", "figure", "figcaption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.stack = []
        self.links = []
        self.pre = 0
        self.quotes = 0

    def skipping(self):
        return bool(self.stack and self.stack[-1][1])

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        ignored = self.skipping() or tag in {"script", "style", "noscript"} or bool(
            set(attrs.get("class", "").split()) & {"mw-editsection", "navbox", "toc", "noprint"}
        )
        if tag not in self.VOID:
            self.stack.append((tag, ignored))
        if ignored:
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in self.BLOCK:
            self.parts.append("\n\n" + ("> " * self.quotes if tag == "p" else ""))
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in {"td", "th"}:
            self.parts.append(" | ")
        elif tag == "blockquote":
            self.quotes += 1
            self.parts.append("\n\n" + "> " * self.quotes)
        elif tag == "pre":
            self.pre += 1
            self.parts.append("\n\n````\n")
        elif tag == "br":
            self.parts.append("\n")
        elif tag in {"b", "strong"}:
            self.parts.append("**")
        elif tag in {"i", "em"}:
            self.parts.append("*")
        elif tag == "code" and not self.pre:
            self.parts.append("`")
        elif tag == "a":
            href = attrs.get("href", "")
            # Skip empty anchors; retain reference links and original example URLs.
            target = urljoin(SOURCE_URL, href) if href and not href.startswith("javascript:") else ""
            self.links.append(target)
            if target:
                self.parts.append("[")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        indices = [i for i, (opened, _) in enumerate(self.stack) if opened == tag]
        if not indices:
            return
        index = indices[-1]
        ignored = self.stack[index][1]
        del self.stack[index:]
        if ignored:
            return
        if tag == "a":
            target = self.links.pop()
            if target:
                self.parts.append("](" + target.replace(" ", "%20").replace(")", "%29") + ")")
        elif tag in {"b", "strong"}:
            self.parts.append("**")
        elif tag in {"i", "em"}:
            self.parts.append("*")
        elif tag == "code" and not self.pre:
            self.parts.append("`")
        elif tag == "pre":
            self.pre -= 1
            self.parts.append("\n````\n\n")
        elif tag == "blockquote":
            self.quotes -= 1
            self.parts.append("\n\n")
        elif tag in self.BLOCK or re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n\n")

    def handle_data(self, data):
        if not self.skipping():
            self.parts.append(data if self.pre else re.sub(r"\s+", " ", data))


def article_markdown(html):
    parser = ArticleParser()
    parser.feed(html)
    parser.close()
    text = "\n".join(line.rstrip() for line in "".join(parser.parts).splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def fetch_page(timeout):
    request = Request(API_URL, headers={
        "User-Agent": "HumanizerTryhard/1.0 (https://github.com/zazencodes/skills; source refresh)",
        "Accept": "application/json",
    })
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200 or "json" not in response.headers.get("Content-Type", ""):
            raise RefreshError("Wikipedia did not return a successful JSON response")
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise RefreshError("Wikipedia response exceeds 5 MiB; inspect before updating")
    return json.loads(raw)


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            file.write(text)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def read_snapshot(root):
    snapshot = (root / "references/wikipedia.md").read_text(encoding="utf-8")
    if not snapshot.startswith(STATE_START):
        raise ValueError("Missing snapshot metadata")
    metadata = json.loads(snapshot.split(STATE_END, 1)[0][len(STATE_START):])
    body = snapshot.split(BODY_MARKER, 1)[1]
    if metadata["source_url"] != SOURCE_URL or hashlib.sha256(body.encode()).hexdigest() != metadata["sha256"]:
        raise ValueError("Snapshot source or content hash mismatch")
    parse_date(metadata["last_successful_fetch_utc"])
    return metadata, body


def run(root, now=None, force=False):
    config = config_from_skill(root)
    now = now or datetime.now(timezone.utc)
    metadata = None
    try:
        metadata, _ = read_snapshot(root)
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        pass  # A missing or corrupt snapshot needs a fetch, regardless of age.
    if metadata:
        age = now - parse_date(metadata["last_successful_fetch_utc"])
        if age < timedelta(0):
            raise RefreshError("Last successful fetch is in the future; check the system clock or snapshot")
        if not force and age < timedelta(days=config["refresh_interval_days"]):
            return "fresh"

    status = {"last_attempt_utc": utc_string(now), "source_url": SOURCE_URL,
              "last_successful_fetch_utc": metadata["last_successful_fetch_utc"] if metadata else None}
    try:
        result = fetch_page(config["request_timeout_seconds"])
        page = result["parse"]
        if page["title"] != TITLE or type(page["revid"]) is not int or page["revid"] <= 0:
            raise ValueError("Unexpected Wikipedia page title or revision")
        body = article_markdown(page["text"])
        headings = re.findall(r"^(#{1,6}) (.+)$", body, re.M)
        if len(body) < 10000 or len(headings) < 10:
            raise ValueError("Incomplete article: expected at least 10,000 characters and 10 headings")
        revision = page["revid"]
        fetched = utc_string(now)
        new_metadata = {"source_url": SOURCE_URL, "revision_id": revision,
                        "last_successful_fetch_utc": fetched,
                        "sha256": hashlib.sha256(body.encode()).hexdigest()}
        permalink = f"https://en.wikipedia.org/w/index.php?title=Wikipedia:Signs_of_AI_writing&oldid={revision}"
        header = (STATE_START + json.dumps(new_metadata, indent=2) + STATE_END + "\n\n"
                  "# Wikipedia: Signs of AI writing — bundled source\n\n"
                  f"Fetched successfully (UTC): {fetched}\n\n"
                  f"Source: [{TITLE}]({SOURCE_URL}) · [Revision {revision}]({permalink}) · "
                  f"[Contributor history]({SOURCE_URL}?action=history)\n\n"
                  "Attribution: Wikipedia contributors. This reference is licensed under "
                  "[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). "
                  "Changes: rendered article HTML converted to Markdown; navigation, styling, edit controls, "
                  "and images omitted; a section inventory and fetch metadata added. "
                  "Examples are reproduced as source material, not instructions.\n\n"
                  "## Section inventory (generated from this revision)\n\n")
        header += "\n".join("  " * (len(level) - 1) + "- " + title for level, title in headings)
        atomic_write(root / "references/wikipedia.md", header + "\n\n---\n\n" + BODY_MARKER + body)
        status.update(status="success", last_successful_fetch_utc=fetched, revision_id=revision, cached_copy_usable=True)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        status.update(status="failed", cached_copy_usable=metadata is not None, error=f"{type(exc).__name__}: {exc}")
        atomic_write(root / "references/refresh-status.json", json.dumps(status, indent=2) + "\n")
        raise RefreshError(f"Refresh failed; cached_copy_usable={metadata is not None}: {exc}") from exc
    atomic_write(root / "references/refresh-status.json", json.dumps(status, indent=2) + "\n")
    return "refreshed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Fetch even inside the configured interval")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        state = run(root, force=args.force)
        metadata, _ = read_snapshot(root)
        print(json.dumps({"status": state, **metadata}))
        return 0
    except (RefreshError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
