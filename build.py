#!/usr/bin/env python3
"""
Build chapter pages from content fragments + shared template.

Usage:
  python build.py              # build all chapters that have content.html
  python build.py alif ba      # build specific chapters
  python build.py --migrate    # extract content.html from existing index.html files
  python build.py --diff       # show what would change without writing
"""

import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ROOT, '_templates', 'chapter.html')
CHAPTERS_DIR = os.path.join(ROOT, 'the-arabic-alphabet')
SITE_URL = 'https://alifbatourguide.com'

SKIP_DIRS = {'_img', 'book'}


def list_chapter_dirs():
    """List all chapter directory names, excluding non-chapter dirs."""
    return sorted([
        d for d in os.listdir(CHAPTERS_DIR)
        if os.path.isdir(os.path.join(CHAPTERS_DIR, d))
        and d not in SKIP_DIRS
    ])


def parse_frontmatter(text):
    """Extract YAML-style frontmatter and body from a content file."""
    if text.startswith('---'):
        end = text.index('---', 3)
        frontmatter = text[3:end].strip()
        body = text[end + 3:].lstrip('\n')
        meta = {}
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip().strip('"').strip("'")
        return meta, body
    return {}, text


def extract_h2_title(html):
    """Fallback: extract title text from first <h2> tag."""
    match = re.search(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
    if match:
        return re.sub(r'<[^>]+>', '', match.group(1)).strip()
    return None


def build_chapter(slug, template, diff_only=False):
    """Build a single chapter's index.html from its content.html."""
    content_path = os.path.join(CHAPTERS_DIR, slug, 'content.html')
    if not os.path.exists(content_path):
        return None

    with open(content_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    meta, body = parse_frontmatter(raw)
    title = meta.get('title') or extract_h2_title(body) or 'Untitled'
    illustrator = meta.get('illustrator', 'illustrated by Houman Mortazavi')
    description = meta.get('description',
                           'An homage to the Arabic alphabet in 32 chapters, '
                           'one letter at a time, from Alif to Yay.')

    output = (template
              .replace('{TITLE}', title)
              .replace('{ILLUSTRATOR}', illustrator)
              .replace('{DESCRIPTION}', description)
              .replace('{SLUG}', slug)
              .replace('{CONTENT}', body))

    out_path = os.path.join(CHAPTERS_DIR, slug, 'index.html')

    if diff_only:
        if os.path.exists(out_path):
            with open(out_path, 'r', encoding='utf-8') as f:
                existing = f.read()
            if existing == output:
                return f'  Unchanged: {slug}'
            else:
                return f'  Would update: {slug}/index.html'
        else:
            return f'  Would create: {slug}/index.html'

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    return title


def find_all_content_chapters():
    """Find all chapter directories that have a content.html file."""
    pattern = os.path.join(CHAPTERS_DIR, '*', 'content.html')
    paths = sorted(glob.glob(pattern))
    return [os.path.basename(os.path.dirname(p)) for p in paths]


def migrate_chapter(slug):
    """Extract content.html from an existing index.html."""
    index_path = os.path.join(CHAPTERS_DIR, slug, 'index.html')
    content_path = os.path.join(CHAPTERS_DIR, slug, 'content.html')

    if os.path.exists(content_path):
        return f'  Skipped: {slug} (content.html already exists)'

    if not os.path.exists(index_path):
        return f'  Skipped: {slug} (no index.html)'

    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract <title> text for frontmatter
    title_match = re.search(
        r'<title>The Arabic Alphabet: A Guided Tour - (.*?)</title>', html
    )
    title = title_match.group(1).strip() if title_match else None

    # Find content between bylines and </article>
    byline_match = re.search(
        r'<h5>illustrated.*?by Houman Mortazavi</h5>\s*\n', html
    )
    article_end = html.rfind('</article>')

    if not byline_match or article_end == -1:
        return f'  Skipped: {slug} (could not find content boundaries)'

    body = html[byline_match.end():article_end].rstrip()

    # Build content.html with frontmatter
    parts = []
    if title:
        parts.append(f'---\ntitle: {title}\n---\n')
    parts.append(body)
    parts.append('\n')

    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(''.join(parts))

    return f'  Migrated: {slug} -> content.html ({title})'


def generate_sitemap():
    """Generate sitemap.xml from all published pages."""
    urls = [SITE_URL + '/']

    for slug in list_chapter_dirs():
        if os.path.exists(os.path.join(CHAPTERS_DIR, slug, 'index.html')):
            urls.append(f'{SITE_URL}/the-arabic-alphabet/{slug}/')

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        xml.append(f'  <url><loc>{url}</loc></url>')
    xml.append('</urlset>')
    xml.append('')

    sitemap_path = os.path.join(ROOT, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml))

    print(f'  Sitemap: {len(urls)} URLs -> sitemap.xml')


def main():
    args = sys.argv[1:]

    # --migrate mode
    if '--migrate' in args:
        args.remove('--migrate')
        slugs = args or list_chapter_dirs()
        print(f'Migrating {len(slugs)} chapter(s)...')
        for slug in slugs:
            print(migrate_chapter(slug))
        return

    # --diff mode
    diff_only = '--diff' in args
    if diff_only:
        args.remove('--diff')

    # Build mode
    if not os.path.exists(TEMPLATE_PATH):
        print(f'Error: template not found at {TEMPLATE_PATH}')
        sys.exit(1)

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    if args:
        slugs = args
    else:
        slugs = find_all_content_chapters()

    if not slugs:
        print('No content.html files found. Run with --migrate first.')
        return

    if diff_only:
        print(f'Checking {len(slugs)} chapter(s)...')
        for slug in slugs:
            result = build_chapter(slug, template, diff_only=True)
            if result:
                print(result)
        return

    building_all = not sys.argv[1:] or diff_only

    print(f'Building {len(slugs)} chapter(s)...')
    for slug in slugs:
        title = build_chapter(slug, template)
        if title:
            print(f'  Built: {slug}/index.html ({title})')
        else:
            print(f'  Skipped: {slug} (no content.html)')

    if building_all:
        generate_sitemap()
    print('Done.')


if __name__ == '__main__':
    main()
