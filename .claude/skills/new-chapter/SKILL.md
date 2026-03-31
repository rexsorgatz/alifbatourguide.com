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

Note: The Google Doc must be shared with "anyone with the link can view" for this to work. If curl returns a login page or error, ask the user to check sharing permissions.

## Step 2: Clean the pandoc output

Run the cleanup script to extract the title, strip unwanted markup, and add the drop-cap class:

```bash
python3 clean.py /tmp/pandoc-output.html -o /tmp/cleaned.html
```

This handles: removing the first `<h2>` (extracted as the title), stripping heading `id` attributes, unwrapping `<u>` and `<span dir="rtl">` tags, removing `<img>` tags and empty paragraphs, removing footnote `<sup>` links, and adding `class="first"` to the first `<p>`. Arabic/Unicode text passes through untouched.

The script prints the extracted title and content stats to stderr. Read `/tmp/cleaned.html` to verify the output looks correct before proceeding.

## Step 3: Create the content file

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

## Step 4: Build the page

Run the build script to generate the final `index.html` from the content file and shared template:

```bash
python3 build.py {slug}
```

This reads `content.html`, wraps it in `_templates/chapter.html`, and writes `the-arabic-alphabet/{slug}/index.html`.

## Step 5: Report

After building, tell the user:
- The file path that was created
- A brief summary of what was extracted (approximate paragraph count, whether Arabic text was found, any links preserved)
- Remind them that images were skipped and will need to be added manually
- Remind them to update the homepage grid (`index.html`) when ready to publish by adding `class="live"` and the `href` to the letter's entry
