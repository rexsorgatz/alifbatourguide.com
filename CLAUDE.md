# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Arabic Alphabet: A Guided Tour** — a literary and visual website exploring the Arabic alphabet in 32 chapters. Written by Michael Beard, illustrated by Houman Mortazavi, developed by Rex Sorgatz. Live at https://alifbatourguide.com.

## Architecture

This is a **static HTML site** with a minimal build system for chapter pages.

- `/index.html` — Homepage with letter grid linking to all 32 chapters
- `/css/_style.css` — All site styling (single file, ~57 lines)
- `/css/qlf7wqv.css` — Adobe Typekit font loader (matrix-ii serif)
- `/the-arabic-alphabet/*/index.html` — Individual chapter pages (one directory per letter)
- `/the-arabic-alphabet/*/content.html` — Chapter content fragments (body + frontmatter)
- `/the-arabic-alphabet/_img/` — All chapter illustrations (PNG/JPG)
- `/the-arabic-alphabet/book/` — Print book layout slideshow (only page with JS)
- `/img/` — Homepage images
- `/_templates/chapter.html` — Shared chapter page template
- `/build.py` — Builds `index.html` from `content.html` + template

No package manager, no CSS preprocessor, no JavaScript framework. To "deploy," commit and push.

**Note:** `/the-arabic-alphabet/_img/` is in `.gitignore` — chapter illustrations exist on disk but are not tracked in git. This can be toggled on/off as needed.

## Build System

Chapter pages use a simple Python build script (`build.py`) with a shared template (`_templates/chapter.html`). The template provides the `<head>`, site header, footer, and analytics. Each chapter's `content.html` contains just the body content with YAML frontmatter (`title`, `description`, and `illustrator` fields).

```bash
python build.py              # build all chapters that have content.html
python build.py alif ba      # build specific chapters
python build.py --migrate    # extract content.html from existing index.html files
python build.py --diff       # preview what would change without writing
```

**Editing workflow:** Edit `content.html` (the source of truth), then run `python build.py {slug}` to regenerate `index.html`. Never edit `index.html` directly — it will be overwritten on the next build.

The `content.html` format:
```html
---
title: Alif
description: The first letter of the Arabic alphabet is a single vertical stroke...
illustrator: illustrated by Houman Mortazavi
---

	<h2>Alif, The Minimal Stroke</h2>

	<p class="first">Content here...</p>
```

## Chapter Page Convention

Each chapter follows a consistent HTML structure:
- `<head>`: meta tags with chapter-specific title, OG tags, canonical Typekit CSS link, shared `_style.css`
- `<body>`: `<article>` wrapper containing h1 site title (linking to `/`), author/illustrator bylines, chapter heading image, h2 chapter title, prose content with inline images
- Footer: Google Analytics snippet (gtag.js, ID `G-S1HS1928FK`)
- Images use relative paths to `../_img/` and always include `loading="lazy"`
- Favicon linked via absolute URL: `https://alifbatourguide.com/favicon.ico`

Note: The homepage links Typekit CSS via `/css/qlf7wqv.css` (local copy), while chapter pages link directly to `https://use.typekit.net/qlf7wqv.css`. Both work but are inconsistent.

## Published vs. Upcoming Chapters

Published chapters (23 total): intro, alif, ba, peh, ta, tha, jim, cheh, ha, kha, dal, dha, ra, za, zhe, sin, shin, sad, dad, taa, zaa, ayn, ghazal.

Upcoming chapters (links in homepage grid without `class="live"` or `href`): F, Q, K, G, L, M, N, Ha-Hawaz, Wow, Yay.

## Design System

- **Brand color**: `#d05a5f` (rust/brick red) — used for borders, links, accents, drop caps
- **Background**: `#fffdfc` (warm cream)
- **Muted text**: `#acacac` (gray, used for disabled letter grid items)
- **Font**: matrix-ii, serif (Adobe Typekit) at 22px base size
- **Layout**: max-width 850px, 90% width with auto margins
- **Mobile breakpoint**: 480px (only affects letter grid width)
- **Drop cap**: `.first:first-letter` class creates a large red initial letter
- **Top border**: 20px solid `#d05a5f` across entire body

## Content Notes

- Chapters contain extensive Arabic, Persian, and Urdu Unicode characters with diacritical marks
- Transliteration uses specialized Unicode (e.g., Ḥ, Ṣ, Ṭ, Ẓ, â, î, û)
- The `.arabic` CSS class applies "Simplified Arabic" font family for inline Arabic text
- MailChimp email signup form appears on homepage and book page

## Adding New Chapters

Use the `/new-chapter` skill to create chapter pages from Google Docs. It takes a Google Doc URL and a folder slug. The chapter title is extracted automatically from the document. The doc must be link-shared ("anyone with the link can view"). The skill exports the doc as `.docx`, converts to clean HTML via `pandoc`, creates a `content.html` fragment, then runs `build.py` to assemble the final page from the shared template. This preserves headings, blockquotes, bold/italic, links, and Arabic/Unicode text. Requires `pandoc` (install via `brew install pandoc`).
