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

## Step 2: Clean the pandoc output and build the page

Run this Python script via Bash, substituting `{SLUG}` with the user's slug value:

```python
import re, os

with open('/tmp/pandoc-output.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract title from the first <h2> tag for use in meta tags
title_match = re.search(r'<h2[^>]*>(.*?)</h2>', content)
title = re.sub(r'<[^>]+>', '', title_match.group(1)) if title_match else 'Untitled'

# Clean: strip id attributes from headings
content = re.sub(r'<(h[2-6]) id="[^"]*">', r'<\1>', content)

# Clean: unwrap <u> tags (keep text)
content = re.sub(r'<u>(.*?)</u>', r'\1', content)

# Clean: remove <img> tags
content = re.sub(r'<img[^>]*/?>', '', content)

# Clean: remove empty paragraphs
content = re.sub(r'<p>\s*</p>', '', content)

# Add drop cap to first <p> tag
content = content.replace('<p>', '<p class="first">', 1)

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<title>The Arabic Alphabet: A Guided Tour - {TITLE}</title>
<meta name="title" content="The Arabic Alphabet: A Guided Tour" />
<meta name="description" content="An homage to the Arabic alphabet in 32 chapters, one letter at a time, from Alif to Yay." />
<meta name="keywords" content="" />
<meta name="generator" content="The mighty hands of Rex Sorgatz" />

<meta property="og:site_name" content="The Arabic Alphabet" />
<meta property="og:title" content="The Arabic Alphabet: A Guided Tour - {TITLE}" />
<meta property="og:description" content="An homage to the Arabic alphabet in 32 chapters, one letter at a time, from Alif to Yay.">
<meta property="og:image" content="https://alifbatourguide.com/the-arabic-alphabet/_img/cover-cropped.jpg" />

<link rel="icon" type="image/x-icon" href="https://alifbatourguide.com/favicon.ico">


<link rel="stylesheet" href="https://use.typekit.net/qlf7wqv.css" />
<link rel="stylesheet" href="https://alifbatourguide.com/css/_style.css" type="text/css" media="all" />
</head>

<body>
<article>

\t<h1><a href="/">The Arabic Alphabet: A Guided Tour</a></h1>
\t<h4>by Michael Beard</h4>
\t<h5>illustrated by Houman Mortazavi</h5>

{CONTENT}


</article>
<br><br><br><br><br><br>
<footer>Copyright &copy;2025 Michael Beard</footer>

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-S1HS1928FK"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-S1HS1928FK');
</script>


</body>
</html>'''

final = TEMPLATE.replace('{TITLE}', title).replace('{CONTENT}', content)

slug = '{SLUG}'
out_dir = f'the-arabic-alphabet/{slug}'
os.makedirs(out_dir, exist_ok=True)
with open(f'{out_dir}/index.html', 'w', encoding='utf-8') as f:
    f.write(final)

p_count = content.count('<p')
bq_count = content.count('<blockquote>')
link_count = content.count('<a href=')
h3_count = content.count('<h3>')
has_arabic = bool(re.search(r'[\u0600-\u06FF]', content))
print(f'Title: {title}')
print(f'Created: {out_dir}/index.html ({len(final)} bytes)')
print(f'Stats: {p_count} paragraphs, {h3_count} sections, {bq_count} blockquotes, {link_count} links, Arabic: {has_arabic}')
```

## Step 3: Report

After running the script, tell the user:
- The file path and title that were extracted
- The stats from the script output
- Remind them to update the homepage grid (`index.html`) when ready to publish by adding `class="live"` and the `href` to the letter's entry
