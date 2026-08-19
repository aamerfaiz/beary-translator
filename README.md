# Beary Translator

A single-page English ↔ Beary (Byari) translator, backed by the **17,234-entry
Beary–Kannada–English Lexicon** (*Nigantu*, Karnataka Beary Sahitya Academy,
2017). Beary is always shown in Roman/English script — no Kannada script
appears anywhere in the app.

## Quick start

1. Open `index.html` in your browser (double-click it, or drag it into a tab) —
   or visit the deployed GitHub Pages site.
2. Type a word and hit **Translate**. Use the swap button (⇅) to flip
   English → Beary and Beary → English.

**Word and phrase lookup needs no API key and no network.** It is answered
directly from the dictionary, so the result is exactly what the Academy
printed.

For **full sentences**, click the gear icon → paste a **DeepSeek API key** (or
any OpenAI-compatible endpoint) → Save. Sentences go to the model together with
the dictionary entries that match your input, so the model builds the sentence
out of real Beary words instead of recalling them.

Your API key is never written to disk by this app. It stays in the page's
memory for the session unless you tick **"Remember on this device"**, which
stores it in your browser's local storage. It is only ever sent to the endpoint
you configured.

## How the two modes differ

| | Word / phrase | Full sentence |
|---|---|---|
| Source | The Lexicon, verbatim | AI model, given matching Lexicon entries |
| API key | Not needed | Needed |
| Trust | As good as the printed dictionary | Draft — check anything important |

Typing works with or without diacritics: `tanni` and `tan'ni` both find
**Water**, `kavudi` finds `kavuḍi` (Cowrie).

## Files

| Path | Purpose |
|---|---|
| `index.html` | The app — open this. |
| `lexicon_data.js` | Generated. 17,234 entries as `[beary, ascii, english, pos, seeAlso]`. Loaded by a `<script>` tag so the app works from `file://`. |
| `data/dictionary.json` | Generated. Full extraction, including page numbers and provenance flags. |
| `grammar_notes.md` | Phonology and grammar, sourced from the Academy's own front matter. |
| `tools/extract_dictionary.py` | Extracts `data/dictionary.json` from `docs/Dictionary.PDF`. |
| `tools/build_lexicon.py` | Builds `lexicon_data.js` from `data/dictionary.json`. |
| `docs/` | The two source PDFs, plus `RELEASE-NOTES.md`. |

To rebuild the data from the PDFs:

```sh
pip install pymupdf
python3 tools/extract_dictionary.py   # -> data/dictionary.json
python3 tools/build_lexicon.py        # -> lexicon_data.js
```

## About the extraction

The dictionary PDF has no Unicode text. Both of its columns use legacy 8-bit
fonts: the Roman transliteration is set in `apara`, an ASCII-remapped font where
`A` draws "ā" and `w` draws "ḍ", and the Kannada is legacy Nudi. The extractor
recovers the `apara` mapping (verified against the Academy's own pronunciation
key) and reads the transliteration and English columns by position.

Four pages (169, 174, 190, 420) are misprinted in the source: their Roman column
is set one or more rows out of step with the Kannada and English columns. The
extractor detects this — a slipped page leaves headwords stranded between
rows — and repairs it by finding the row offset that makes the dictionary's own
cross-references agree again. See `docs/RELEASE-NOTES.md` for the detail.

Data quality is checked by the dictionary against itself: variant forms are
cross-referenced reciprocally and should share a meaning. **96.7%** of the
7,892 resolvable cross-references agree; the remainder are cases where the same
sense is worded differently in the two entries.

## Deploying

The app is fully static. GitHub Pages: Settings → Pages → Deploy from a
branch → Branch `main`, folder `/ (root)`.

## Credits

Vocabulary and grammar from the *Beary–Kannada–English Lexicon*, Karnataka
Beary Sahitya Academy, 2017 — editors B.M. Ichlangod, B.A. Shamshuddin Madikeri
and Abdul Rahman Kuthethoor, English glosses by Prof. B. Surendra Rao,
phonology note by Prof. B.A. Viveka Rai.

This is a personal project and is not affiliated with or endorsed by the
Academy.
