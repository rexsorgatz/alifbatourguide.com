---
name: new-chapter
description: Create a new chapter page from a Google Doc URL
argument-hint: <google-doc-url> <slug> <chapter-title>
allowed-tools: WebFetch, Write, Bash, Read, Glob
---

# New Chapter from Google Doc

Create a new chapter page for The Arabic Alphabet: A Guided Tour.

## Arguments

The user provides: `$ARGUMENTS`

Parse three values from the arguments:
1. **Google Doc URL** — a `docs.google.com` URL
2. **Slug** — the folder name (e.g. `fa`, `qaf`, `kaf`)
3. **Chapter title** — the full chapter heading (e.g. "The F Word", "Qaf is for Cadi")

If any of these are missing, ask for them before proceeding.

## Step 1: Fetch the Google Doc

Extract the document ID from the URL. Google Doc URLs look like:
- `https://docs.google.com/document/d/{DOC_ID}/edit`
- `https://docs.google.com/document/d/{DOC_ID}/...`

Fetch the HTML export:
```
https://docs.google.com/document/d/{DOC_ID}/export?format=html
```

Use WebFetch to retrieve this.

## Step 2: Clean the HTML

Google Docs HTML export is full of junk. Strip it down to clean semantic HTML:

**Remove entirely:**
- All `<style>` blocks and `style="..."` attributes
- All `class` attributes
- All `id` attributes
- All `<span>` tags (unwrap them, keeping their text content)
- All `<img>` tags (skip images entirely)
- All `<div>` tags (unwrap them, keeping their content)
- All empty paragraphs (`<p><br></p>`, `<p></p>`)
- All Google's metadata, `<head>` content, `<html>`/`<body>` wrappers
- Any `<!-- comments -->`
- Any `<sup>` footnote reference links that point to Google Doc anchors

**Preserve and clean:**
- `<p>` tags — keep as-is, but remove any attributes
- `<strong>` and `<b>` — normalize to `<strong>`
- `<em>` and `<i>` — normalize to `<em>`
- `<blockquote>` — keep, remove attributes
- `<h1>` through `<h6>` — keep, remove attributes. Shift heading levels if needed so the chapter content starts at `<h3>` (since h1 and h2 are used by the site template)
- `<a href="...">` — keep links, but remove all attributes except `href`. Remove any Google redirect wrappers (URLs like `https://www.google.com/url?q=...&sa=...` should be unwrapped to just the target URL)
- `<ul>`, `<ol>`, `<li>` — keep, remove attributes
- `<table>`, `<tr>`, `<td>`, `<th>` — keep, remove attributes
- `<br>` — keep

**Arabic/Unicode text:**
- All Arabic, Persian, and Urdu script MUST be preserved exactly as-is
- All diacritical marks and special Unicode characters (Ḥ, Ṣ, Ṭ, Ẓ, â, î, û, etc.) MUST be preserved
- Never HTML-entity-encode Arabic characters — keep them as raw UTF-8

**Formatting cleanup:**
- Collapse multiple consecutive `<br>` into a single paragraph break
- Remove leading/trailing whitespace inside tags
- Ensure clean, readable indentation

## Step 3: Apply the first-paragraph drop cap

Add `class="first"` to the first `<p>` tag of the chapter body content. This triggers the site's drop-cap styling.

## Step 4: Create the chapter page

Create the directory and file at: `the-arabic-alphabet/{slug}/index.html`

Use this exact template, substituting `{SLUG}`, `{TITLE}`, and `{CONTENT}`:

```html
<!DOCTYPE html>
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

	<h1><a href="/">The Arabic Alphabet: A Guided Tour</a></h1>
	<h4>by Michael Beard</h4>
	<h5>illustrated by Houman Mortazavi</h5>

	<h2>{TITLE}</h2>

{CONTENT}


</article>
<br><br><br><br><br><br>
<footer>Copyright &copy;2025 Michael Beard</footer>

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-S1HS1928FK"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-S1HS1928FK');
</script>


</body>
</html>
```

## Step 5: Report

After creating the file, tell the user:
- The file path that was created
- A brief summary of what was extracted (approximate paragraph count, whether Arabic text was found, any links preserved)
- Remind them that images were skipped and will need to be added manually
- Remind them to update the homepage grid (`index.html`) when ready to publish by adding `class="live"` and the `href` to the letter's entry
