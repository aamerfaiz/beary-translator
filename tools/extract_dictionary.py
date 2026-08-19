#!/usr/bin/env python3
"""
Extract the Beary-Kannada-English Lexicon (Nigantu, Karnataka Beary Sahitya
Academy, 2017) from docs/Dictionary.PDF into structured JSON.

The PDF has no Unicode text: it uses two legacy 8-bit fonts.

  * ``apara``      -- the Roman transliteration column. An ASCII-remapped font
                      where e.g. 'A' draws "ā", 'f' draws "ụ", 'w' draws "ḍ".
                      The mapping below was recovered by rendering every glyph
                      in the embedded font and was then verified against the
                      official pronunciation key in docs/PronunciationandStuff.PDF
                      (pages xxxix-xlii), which lists the full phoneme inventory.
  * ``Nudiweb01e`` -- legacy ASCII-Kannada (Nudi). Not transcoded here; we only
                      need it for the part-of-speech markers, which are matched
                      as raw byte strings (see POS_TAGS).

Page layout (identical on all 752 pages), per the Preface:
  col 1  x <170   Beary headword in Kannada script  (+ POS tag, + cross-ref line)
  col 2  x ~171   Beary transliterated into Roman script   <- what we want
  col 3  x ~290   meaning in Kannada
  col 4  x >=430  meaning in English                       <- what we want

Usage:  python3 tools/extract_dictionary.py [--pages N] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

try:
    import pymupdf
except ImportError:  # pragma: no cover
    sys.exit("pymupdf is required:  pip install pymupdf")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "docs", "Dictionary.PDF")

# ---------------------------------------------------------------------------
# 1. The 'apara' transliteration font: ASCII byte -> Unicode transliteration
# ---------------------------------------------------------------------------
APARA = {
    "A": "ā", "E": "ē", "I": "ī", "J": "jh", "K": "kh", "L": "ḷ", "M": "ṃ",
    "N": "ṇ", "O": "ō", "P": "ph", "S": "ś", "U": "ū", "V": "au", "Y": "ai",
    "Z": "ṅ", "[": "ɛ", "{": "ɛ̄", "f": "ụ", "q": "ṭ", "w": "ḍ", "x": "ṣ",
    "z": "ñ",
}
# every other printable ASCII byte in the font draws itself (a-e, g-p, r-v, y,
# digits, punctuation), so a plain passthrough is correct for them.

# Roman -> plain-ASCII fallback, so users can type "beary" without diacritics.
FOLD = {
    "ā": "a", "ē": "e", "ī": "i", "ō": "o", "ū": "u", "ụ": "u", "ɛ": "e",
    "ɛ̄": "e", "ḷ": "l", "ṃ": "m", "ṇ": "n", "ṭ": "t", "ḍ": "d", "ṣ": "sh",
    "ś": "sh", "ñ": "n", "ṅ": "n", "'": "",
}

# ---------------------------------------------------------------------------
# 2. Part-of-speech markers, as they appear in the raw Nudi bytes of column 1
# ---------------------------------------------------------------------------
POS_TAGS = {
    "£Á": "noun",       # (ನಾ)  naamapada
    "Qæ": "verb",       # (ಕ್ರಿ) kriyaapada
}
SEE_TAG = "£ÉÆÃ"        # (ನೋ)  "nodi" = see also; marks a cross-reference line

COL2_X = (168.0, 175.0)      # transliteration column, left edge
COL4_X = 430.0               # English column, left edge
Y_TOP, Y_BOTTOM = 14.0, 682.0  # strip running head / folio
ANCHOR_SLACK = 2.5           # a row's English sits ~0.8pt above its headword
ROW_GAP = 15.0               # >=this vertical gap starts a new row, below it is a wrap


def convert_apara(text: str) -> str:
    return "".join(APARA.get(ch, ch) for ch in text)


def fold_ascii(text: str) -> str:
    out = []
    for ch in text:
        if ch in FOLD:
            out.append(FOLD[ch])
        elif ch.isalpha() or ch.isspace():
            out.append(ch)
    s = unicodedata.normalize("NFKD", "".join(out))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def page_spans(page):
    """Deduplicated (y, x, font, text) spans.

    The transliteration column is stamped five times, each copy offset by a
    fraction of a point, to fake a bold weight. Exact-key dedup therefore does
    not collapse it -- we need a tolerance on both axes.
    """
    raw = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if not span["text"].strip():
                    continue
                raw.append((round(span["bbox"][1], 1), round(span["bbox"][0], 1),
                            span["font"], span["text"]))
    raw.sort()

    out = []
    by_text = {}
    for y, x, font, text in raw:
        dup = False
        for py, px in by_text.get((font, text), ()):
            if abs(py - y) < 1.5 and abs(px - x) < 1.5:
                dup = True
                break
        if dup:
            continue
        by_text.setdefault((font, text), []).append((y, x))
        out.append((y, x, font, text))
    return out


def clean_english(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([;,.])", r"\1", text)
    return text.strip(" ;,")


def split_senses(text: str):
    """'1. Evaporate 2. Cooling down' -> ['Evaporate', 'Cooling down']"""
    parts = re.split(r"(?:^|\s)\d+\.\s*", text)
    parts = [p.strip(" ;,.") for p in parts if p.strip(" ;,.")]
    if len(parts) > 1:
        return parts
    return [p.strip() for p in text.split(";") if p.strip()] or [text]


def parse_page(page, pageno, shift=0):
    """Extract one page.

    ``shift`` re-pairs a page whose Roman column slipped against the other
    three: the Beary headword at row i is matched with the Kannada/English of
    row ``i + shift``. The Kannada columns stay locked to English (they are in
    sync with it even on the broken pages), while the cross-reference lines
    stay locked to the Roman headword they are printed under.
    """
    spans = page_spans(page)
    body = [s for s in spans if Y_TOP < s[0] < Y_BOTTOM]

    anchors, extras, english, kannada1 = [], [], [], []
    for y, x, font, text in body:
        if font == "apara":
            if COL2_X[0] <= x <= COL2_X[1] and text[:1] not in (" ", "'", "*"):
                anchors.append((y, convert_apara(text)))
            else:
                extras.append((y, convert_apara(text)))
        elif font.startswith("Nudi"):
            if x < COL2_X[0]:
                kannada1.append((y, x, text))
        elif x >= COL4_X:
            english.append((y, text))

    if not anchors:
        return []

    # Group the English column into rows of its own. A gloss that wraps sits
    # ~13pt below its first line while the next row starts ~17.6pt below, so the
    # gap separates them cleanly. Deriving the grid from the English column
    # itself -- rather than from the Roman anchors -- keeps a wrapped gloss
    # intact even on a page where the Roman column has slipped.
    rows = []
    for y, text in sorted(english):
        if rows and y - rows[-1][1] < ROW_GAP:
            rows[-1][1] = y
            rows[-1][2].append(text)
        else:
            rows.append([y, y, [text]])

    def nearest_row(y):
        best, dist = None, 1e9
        for i, (top, bottom, _) in enumerate(rows):
            d = abs(top - y)
            if d < dist:
                best, dist = i, d
        return best if dist <= 6.0 else None

    entries = [{"beary": head.strip(), "_en": [], "_extra": [], "_kn": [],
                "page": pageno + 1} for _, head in anchors]

    # Structural alignment check: on a sound page essentially every Roman
    # headword sits level with an English row. A page whose Roman column has
    # slipped leaves headwords stranded between rows.
    stranded = sum(1 for y, _ in anchors if nearest_row(y) is None)
    parse_page.last_stranded = stranded / len(anchors)

    # The Kannada headword column stays locked to English on every page, broken
    # ones included, so part-of-speech is read off the English row grid.
    row_kn = [[] for _ in rows]
    for y, x, text in kannada1:
        i = nearest_row(y)
        if i is not None:
            row_kn[i].append(text)

    # Cross-reference lines are printed under the Roman headword, so they follow
    # the Roman column wherever it sits.
    anchor_tops = [a[0] for a in anchors]
    for y, text in extras:
        i = max((k for k, ay in enumerate(anchor_tops) if ay <= y + ANCHOR_SLACK),
                default=None)
        if i is not None:
            entries[i]["_extra"].append(text.strip())

    if shift:
        # Repair path: the two columns are uniformly offset, so pair by rank.
        paired = []
        for i, e in enumerate(entries):
            j = i + shift
            if 0 <= j < len(rows):
                e["_en"], e["_kn"] = rows[j][2], row_kn[j]
                paired.append(e)
        entries = paired
    else:
        for i, e in enumerate(entries):
            j = nearest_row(anchors[i][0])
            if j is not None:
                e["_en"], e["_kn"] = rows[j][2], row_kn[j]

    out = []
    for e in entries:
        english_text = clean_english(" ".join(e.pop("_en")))
        raw_kn = " ".join(e.pop("_kn"))
        extra = [x for x in e.pop("_extra") if x]

        pos = ""
        for marker, name in POS_TAGS.items():
            if "(" + marker in raw_kn:
                pos = name
                break

        see_also = []
        for line in extra:
            ref = line.lstrip("' *’").strip()
            if ref:
                see_also.append(ref)

        beary = e["beary"].strip()
        # A trailing "?" is part of the headword for interrogatives (āro ?).
        beary = re.sub(r"\s+", " ", beary)
        if not beary or not english_text:
            continue

        rec = {
            "beary": beary,
            "beary_ascii": fold_ascii(beary),
            "english": english_text,
            "senses": split_senses(english_text),
            "pos": pos,
            "page": e["page"],
        }
        if see_also:
            rec["see_also"] = see_also
        out.append(rec)
    return out


def flag_misaligned(entries, min_links=3, threshold=0.8):
    """Find pages where the printed Roman column is out of vertical sync with
    the Kannada/English columns.

    On a handful of pages the typesetter's column 2 flow slipped by one or more
    rows against columns 1/3/4, so the word printed beside an English gloss is
    not the word that gloss belongs to. We detect this without needing the
    Kannada: the dictionary cross-references variants reciprocally (X says
    "see Y", Y says "see X") and the two share a meaning. Where a page's
    cross-references almost all disagree, that page's pairing is untrustworthy.

    Returns the set of 1-based page numbers to distrust.
    """
    index = {}
    for e in entries:
        index.setdefault(e["beary"], []).append(e)

    def words(s):
        return set(re.findall(r"[a-z]+", s.lower()))

    checked, failed = {}, {}
    for e in entries:
        for ref in e.get("see_also", []):
            targets = index.get(ref)
            if not targets:
                continue
            page = e["page"]
            checked[page] = checked.get(page, 0) + 1
            if not any(words(e["english"]) & words(t["english"]) for t in targets):
                failed[page] = failed.get(page, 0) + 1

    return {
        p for p, n in checked.items()
        if n >= min_links and failed.get(p, 0) / n >= threshold
    }


def _gloss_words(s):
    return set(re.findall(r"[a-z]+", s.lower()))


def build_common_words(entries, cutoff=0.004):
    """Gloss words too common to be evidence of anything.

    Matching on bare token overlap makes "Put upside down" agree with "Lie face
    down", which is enough to pick the wrong row offset. Only distinctive words
    ("cowrie", "qawwali", "poppy") should count as a match.
    """
    freq = {}
    for e in entries:
        for w in _gloss_words(e["english"]):
            freq[w] = freq.get(w, 0) + 1
    limit = max(8, int(len(entries) * cutoff))
    return {w for w, n in freq.items() if n > limit}


def score_pairing(entries, index, common=frozenset()):
    """Score how well a page's Beary->English pairing hangs together.

    Two independent kinds of evidence, both checked against words from sound
    pages only:

    1. Cross-references. The dictionary links variants reciprocally, and a word
       and its variant share a meaning ("ārane" and "ārāmatto" are both "Sixth").
    2. Compounds. Most multi-word headwords gloss as the sum of their parts, so
       "kāḍụ kudurɛ" should gloss with a word from "kāḍụ" (forest/wild) or
       "kudurɛ" (horse). A slipped page breaks this everywhere at once.

    Returns (agreements, checks).
    """
    good = total = 0
    for e in entries:
        mine = _gloss_words(e["english"]) - common

        for ref in e.get("see_also", []):
            targets = index.get(ref)
            if not targets:
                continue
            total += 1
            if any(mine & (_gloss_words(t["english"]) - common) for t in targets):
                good += 1

        parts = e["beary"].split()
        if len(parts) > 1:
            for part in parts:
                targets = index.get(part)
                if not targets:
                    continue
                total += 1
                if any(mine & (_gloss_words(t["english"]) - common) for t in targets):
                    good += 1
    return good, total


def realign_page(doc, pageno, index, common=frozenset(), max_shift=12):
    """Search for the row offset that best repairs a slipped page.

    Returns (shift, entries, good, total) for the winning offset, or None when
    no offset produces a convincing chain of agreeing cross-references.
    """
    scored = []
    for shift in range(-max_shift, max_shift + 1):
        entries = parse_page(doc[pageno - 1], pageno - 1, shift=shift)
        if not entries:
            continue
        good, total = score_pairing(entries, index, common)
        if total < 3:
            continue
        # Rank on the number of confirmed agreements: a page where four
        # cross-references land is better evidence than one where three do out
        # of a smaller sample. Rate only breaks ties.
        scored.append((good, good / total, shift, total, entries))
    if not scored:
        return None
    scored.sort(key=lambda s: (s[0], s[1]), reverse=True)

    good, rate, shift, total, entries = scored[0]
    runner_up = scored[1][0] if len(scored) > 1 else 0
    # Accept only a decisive winner. A genuine offset lights up many agreements
    # at exactly one shift; noise scatters single hits across several.
    if good < 2 or good < 2 * runner_up:
        return None
    return shift, entries, good, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=0, help="limit pages (debug)")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "dictionary.json"))
    args = ap.parse_args()

    doc = pymupdf.open(PDF)
    total = len(doc) if not args.pages else min(args.pages, len(doc))

    entries = []
    stranded = {}
    for i in range(total):
        entries.extend(parse_page(doc[i], i))
        stranded[i + 1] = getattr(parse_page, "last_stranded", 0.0)
        if (i + 1) % 100 == 0:
            print(f"  ...page {i + 1}/{total}, {len(entries)} entries", file=sys.stderr)

    suspect = flag_misaligned(entries)
    suspect |= {p for p, frac in stranded.items() if frac > 0.15}
    if suspect:
        print(f"  slipped pages detected: {sorted(suspect)}", file=sys.stderr)

    # Repair the slipped pages against an index built only from sound pages.
    index = {}
    for e in entries:
        if e["page"] not in suspect:
            index.setdefault(e["beary"], []).append(e)

    common = build_common_words(entries)
    entries = [e for e in entries if e["page"] not in suspect]
    for page in sorted(suspect):
        fixed = realign_page(doc, page, index, common)
        if fixed is None:
            print(f"  page {page}: unrepairable, dropped", file=sys.stderr)
            continue
        shift, recovered, agree, links = fixed
        for e in recovered:
            e["realigned_by"] = shift
        entries.extend(recovered)
        print(f"  page {page}: realigned by {shift:+d} row(s), "
              f"{len(recovered)} entries, cross-refs {agree}/{links}", file=sys.stderr)
    entries.sort(key=lambda e: (e["page"],))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    print(f"Wrote {len(entries)} entries from {total} pages -> {args.out}")


if __name__ == "__main__":
    main()
