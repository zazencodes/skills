#!/usr/bin/env python3
"""Fetch a web page and print its readable text. The page reader for Gemini research workers.

Usage: read_page.py <url>

HTML is reduced to its visible text, one block per line. Other text types print as-is.
Exits non-zero on HTTP errors and non-text responses.
"""

import html.parser
import sys
import urllib.request

SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "head"}
BLOCK_TAGS = {
    "p", "div", "section", "article", "main", "li", "ul", "ol", "tr", "table", "br",
    "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote", "header", "footer", "nav", "dt", "dd",
}


class TextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    def text(self):
        lines = (" ".join(line.split()) for line in "".join(self.parts).splitlines())
        return "\n".join(line for line in lines if line)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: read_page.py <url>")
    request = urllib.request.Request(sys.argv[1], headers={"User-Agent": "Mozilla/5.0 (research reader)"})
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get_content_type()
        body = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
        final_url = response.geturl()
    if not (content_type.startswith("text/") or content_type in {"application/json", "application/xml"}):
        sys.exit(f"read_page: {final_url} is {content_type}, not a text page")
    print(f"URL: {final_url}\n")
    if content_type == "text/html":
        extractor = TextExtractor()
        extractor.feed(body)
        print(extractor.text())
    else:
        print(body)


if __name__ == "__main__":
    main()
