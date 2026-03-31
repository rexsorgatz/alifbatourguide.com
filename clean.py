#!/usr/bin/env python3
"""
Clean pandoc HTML output for use as chapter content.

Usage:
  python clean.py /tmp/pandoc-output.html
  python clean.py /tmp/pandoc-output.html -o /tmp/cleaned.html

Reads pandoc HTML, applies cleanup rules, prints stats, and writes
cleaned output. If no -o flag, writes to stdout.
"""

import re
import sys


def clean(html):
    """Clean pandoc HTML output for chapter content."""

    # Extract title from first <h2>
    title_match = re.search(r'<h2[^>]*>(.*?)</h2>', html)
    title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else 'Untitled'

    # Remove the first <h2> (re-added in content.html frontmatter)
    html = re.sub(r'<h2[^>]*>.*?</h2>\n?', '', html, count=1)

    # Strip id attributes from headings
    html = re.sub(r'<(h[2-6]) id="[^"]*">', r'<\1>', html)

    # Unwrap <u> tags (keep text)
    html = re.sub(r'<u>(.*?)</u>', r'\1', html)

    # Unwrap <span dir="rtl"> tags (keep content)
    html = re.sub(r'<span dir="rtl">(.*?)</span>', r'\1', html, flags=re.DOTALL)

    # Remove <img> tags
    html = re.sub(r'<img[^>]*/?\s*>', '', html)

    # Remove empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)

    # Remove sup footnote links (internal doc anchors)
    html = re.sub(r'<sup><a href="#[^"]*">[^<]*</a></sup>', '', html)

    # Add drop cap to first <p>
    html = html.replace('<p>', '<p class="first">', 1)

    return title, html


def stats(html):
    """Print content stats."""
    p_count = html.count('<p')
    bq_count = html.count('<blockquote>')
    link_count = html.count('<a href=')
    h3_count = html.count('<h3>')
    has_arabic = bool(re.search(r'[\u0600-\u06FF]', html))
    has_hebrew = bool(re.search(r'[\u0590-\u05FF]', html))
    has_greek = bool(re.search(r'[\u0370-\u03FF]', html))

    scripts = [s for s, v in [('Arabic', has_arabic), ('Hebrew', has_hebrew), ('Greek', has_greek)] if v]

    print(f'Title: {title}', file=sys.stderr)
    print(f'Stats: {p_count} paragraphs, {h3_count} sections, {bq_count} blockquotes, {link_count} links', file=sys.stderr)
    if scripts:
        print(f'Scripts: {", ".join(scripts)}', file=sys.stderr)


if __name__ == '__main__':
    args = sys.argv[1:]

    if not args or args[0] in ('-h', '--help'):
        print(__doc__.strip())
        sys.exit(0)

    input_path = args[0]
    output_path = None
    if '-o' in args:
        output_path = args[args.index('-o') + 1]

    with open(input_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    title, cleaned = clean(raw)
    stats(cleaned)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f'Wrote: {output_path}', file=sys.stderr)
    else:
        print(cleaned)
