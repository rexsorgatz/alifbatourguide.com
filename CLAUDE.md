# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Arabic Alphabet: A Guided Tour** — a literary and visual website exploring the Arabic alphabet in 32 chapters. Written by Michael Beard, illustrated by Houman Mortazavi, developed by Rex Sorgatz. Live at https://alifbatourguide.com.

## Architecture

This is a **pure static HTML site** with no build system, no templating engine, and no server-side processing. Every page is hand-written HTML.

- `/index.html` — Homepage with letter grid linking to all 32 chapters
- `/css/_style.css` — All site styling (single file, ~57 lines)
- `/css/qlf7wqv.css` — Adobe Typekit font loader (matrix-ii serif)
- `/the-arabic-alphabet/*/index.html` — Individual chapter pages (one directory per letter)
- `/the-arabic-alphabet/_img/` — All chapter illustrations (PNG/JPG)
- `/the-arabic-alphabet/book/` — Print book layout slideshow (only page with JS)
- `/img/` — Homepage images

There is no build step, no package manager, no CSS preprocessor, and no JavaScript framework. To "deploy," commit and push.

## Chapter Page Convention

Each chapter follows a consistent HTML template:
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
