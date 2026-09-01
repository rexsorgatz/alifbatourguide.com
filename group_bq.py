#!/usr/bin/env python3
"""Group blockquote lines by script: <br> within a script, <p> between scripts.

Arabic/Persian/Urdu lines, Latin transliteration, and plain Latin translation each
become their own <p>, with the lines inside joined by <br>.

Only *verse* runs are merged. A run containing a long line is left alone -- those
are prose quotations whose paragraph breaks are real (the Arberry jackal story in
jim, Mernissi in ha, Horwitz in ayn).
"""
import html, io, re, sys

ARABIC = re.compile('[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
LETTER = re.compile(r'[^\W\d_]', re.UNICODE)
P = re.compile(r'([ \t]*)<p>(.*?)</p>', re.S)
PROSE_LEN = 160  # a "line" longer than this is a prose paragraph, not a verse line
SHORT_LEN = 25   # "-- Davis]" and friends: too short to classify, inherit neighbour

# If a Latin line contains none of these it is transliteration, not English. Needed
# because an <em> that straddles a </p> hides the italics that would mark it.
STOPWORDS = set('''a an the and or but of to in on at by for with from as is are was
were be been it its that this these those he she they we you i his her their our my
not no if then than so what which who whom when where how all any each'''.split())


def plain(inner):
    return re.sub(r'<[^>]+>', '', html.unescape(inner)).strip()


def text_len(inner):
    return len(plain(inner))


def script_of(inner):
    txt = plain(inner)
    if len(txt) < SHORT_LEN:
        return None  # inherit from the previous line
    # An attribution ("-- trans. Dick Davis", "-- Hadiqat al-Haqiqat 3.8") belongs
    # with the lines it credits; it carries no stopwords of its own to go on.
    if re.match(r'\s*(--|—|–)', txt):
        return None
    letters = LETTER.findall(txt)
    arabic = [c for c in letters if ARABIC.match(c)]
    # dominance, not mere presence: English translations quote Arabic words inline
    if letters and len(arabic) / float(len(letters)) > 0.5:
        return 'AR'
    total = text_len(inner)
    ital = sum(text_len(m) for m in re.findall(r'<em>(.*?)</em>', inner, re.S))
    if total and ital / float(total) > 0.6:
        return 'TR'
    # Unicode-aware: an [a-z]+ split would cut "andâzim" at the â and match "and"
    words = set(re.findall(r'[^\W\d_]+', txt.lower(), re.UNICODE))
    return 'LA' if words & STOPWORDS else 'TR'


def regroup(bq):
    matches = list(P.finditer(bq))
    if len(matches) < 2:
        return bq, 0
    indent = matches[0].group(1)
    inners = [m.group(2) for m in matches]

    groups = []
    for inner in inners:
        s = script_of(inner)
        if s is None:
            s = groups[-1][0] if groups else 'LA'
        if groups and groups[-1][0] == s:
            groups[-1][1].append(inner)
        else:
            groups.append((s, [inner]))

    out, merged = [], 0
    for _, run in groups:
        if len(run) > 1 and max(text_len(x) for x in run) <= PROSE_LEN:
            out.append('<br>'.join(run))
            merged += len(run) - 1
        else:
            out.extend(run)
    if not merged:
        return bq, 0
    close = re.search(r'\n([ \t]*)</blockquote>$', bq)
    body = '\n'.join('%s<p>%s</p>' % (indent, p) for p in out)
    return '<blockquote>\n%s\n%s</blockquote>' % (body, close.group(1) if close else ''), merged


def process(path):
    s = io.open(path, encoding='utf-8').read()
    merged = [0]

    def sub(m):
        new, n = regroup(m.group(0))
        merged[0] += n
        return new

    out = re.sub(r'<blockquote>.*?</blockquote>', sub, s, flags=re.S)
    if out != s:
        io.open(path, 'w', encoding='utf-8').write(out)
    return merged[0]


if __name__ == '__main__':
    for p in sys.argv[1:]:
        n = process(p)
        if n:
            print('%s: merged %d line(s)' % (p, n))
