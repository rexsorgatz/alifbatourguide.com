---
name: new-chapter
description: Create a new chapter page from a Google Doc URL
argument-hint: <google-doc-url> <slug>
allowed-tools: Write, Bash, Read, Glob
---

# New Chapter from Google Doc

Create a new chapter page for The Arabic Alphabet: A Guided Tour.

**Important: This is a formatting task, not an editorial task.** Transfer all text exactly as it appears in the Google Doc. Do not correct spelling, fix grammar, adjust punctuation, or reword any prose. The author's text is intentional — just convert the formatting to clean HTML.

## Arguments

The user provides: `$ARGUMENTS`

Parse two values from the arguments:
1. **Google Doc URL** — a `docs.google.com` URL
2. **Slug** — the folder name (e.g. `fa`, `qaf`, `kaf`)

The chapter title is extracted automatically from the document. If either argument is missing, ask for it before proceeding.

## Step 1: Fetch and convert the Google Doc

Extract the document ID from the URL. Google Doc URLs look like:
- `https://docs.google.com/document/d/{DOC_ID}/edit`
- `https://docs.google.com/document/d/{DOC_ID}/...`

Export as `.docx` and convert to clean HTML using pandoc:

```bash
curl -sL "https://docs.google.com/document/d/{DOC_ID}/export?format=docx" -o /tmp/gdoc-export.docx
pandoc /tmp/gdoc-export.docx -f docx -t html --wrap=none -o /tmp/pandoc-output.html
```

Then read `/tmp/pandoc-output.html` with the Read tool.

Note: The Google Doc must be shared with "anyone with the link can view" for this to work. If curl returns a login page or error, ask the user to check sharing permissions.

## Step 2: Clean the pandoc output

Pandoc's output is already mostly clean. Apply these final cleanups:

**Remove:**
- The first `<h2>` (the chapter title — it will be extracted for the frontmatter `title` field, then re-added as the visible `<h2>` in the content)
- All `id` attributes on headings (e.g. `id="the-f-word"`)
- All `<u>` tags inside links (unwrap them, keeping their text)
- All `<span dir="rtl">` tags (unwrap them, keeping their Arabic text content)
- All `<img>` tags (skip images entirely)
- All `<sup>` footnote reference links that point to internal doc anchors (keep `<sup>` used for ordinals like "8th")
- Any empty paragraphs

**Preserve as-is:**
- `<p>` tags
- `<strong>` and `<em>`
- `<blockquote>` (pandoc detects these from the docx structure)
- `<h3>` section headings. The chapter title is already extracted for the `<h2>`, so the doc's `<h3>` tags stay as `<h3>`. If the doc uses `<h2>` for section breaks, shift them to `<h3>`
- `<a href="...">` links (pandoc already strips Google redirect wrappers)
- `<ul>`, `<ol>`, `<li>`
- `<table>`, `<tr>`, `<td>`, `<th>`
- `<br>`

**Arabic/Unicode text:**
- All Arabic, Persian, and Urdu script MUST be preserved exactly as-is
- All diacritical marks and special Unicode characters (Ḥ, Ṣ, Ṭ, Ẓ, â, î, û, etc.) MUST be preserved
- Never HTML-entity-encode Arabic characters — keep them as raw UTF-8

## Step 3: Apply the first-paragraph drop cap

Add `class="first"` to the first `<p>` tag of the chapter body content. This triggers the site's drop-cap styling.

## Step 4: Create the content file

Create the directory and file at: `the-arabic-alphabet/{slug}/content.html`

The content file uses YAML frontmatter for metadata, followed by the chapter body HTML. The `<h2>` chapter title should be included as the first element of the body content.

Generate a `description` — 1-2 sentences that capture the chapter's themes and key topics. This appears in search results and social media previews. Aim for 140-180 characters. Match the tone of the book: erudite, wandering, full of surprising connections.

```html
---
title: {TITLE}
description: {1-2 sentence description of the chapter's themes}
illustrator: illustrated by Houman Mortazavi
---

	<h2>{TITLE}</h2>

{CLEANED_CONTENT}
```

Note: This is a **content fragment**, not a full HTML page. The shared template (`_templates/chapter.html`) provides the `<head>`, header, footer, and analytics. The `build.py` script assembles them.

## Step 5: Build the page

Run the build script to generate the final `index.html` from the content file and shared template:

```bash
python3 build.py {slug}
```

This reads `content.html`, wraps it in `_templates/chapter.html`, and writes `the-arabic-alphabet/{slug}/index.html`.

## Step 6: Report

After building, tell the user:
- The file path that was created
- A brief summary of what was extracted (approximate paragraph count, whether Arabic text was found, any links preserved)
- Remind them that images were skipped and will need to be added manually
- Remind them to update the homepage grid (`index.html`) when ready to publish by adding `class="live"` and the `href` to the letter's entry
