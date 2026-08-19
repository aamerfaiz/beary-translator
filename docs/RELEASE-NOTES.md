# Release notes — real dictionary data

**Date:** 2026-08-19

This release replaces the project's guessed vocabulary with the actual
**Beary–Kannada–English Lexicon** (*Nigantu*), Karnataka Beary Sahitya Academy,
2017, supplied as `docs/Dictionary.PDF`. `docs/` is now the source of truth.

## What changed, in short

| | Before | After |
|---|---|---|
| Entries | 105 | **17,234** |
| Source | Malayalam words run through guessed sound-shift rules | The Academy's printed Lexicon, verbatim |
| Attested entries | 5 of 105 | All 17,234 |
| Word lookup | Asked an AI, needed an API key | Answered from the dictionary, no key, no network |
| Grammar notes | Web sources + inference | The Academy's own phonology note and Editorial |

The previous lexicon was a best-effort approximation: it derived Beary forms by
applying rules like "initial v → b" to Malayalam vocabulary. It is now clear how
far off that could be. The old file claimed *water* = `bellam`; the Lexicon
gives `tan'ni`. It claimed *house* = `beedu`; the Lexicon gives `ava`, `porɛ`,
`bīḍụ`, `baitụ`. Roughly 95% of the old entries were unverified guesses, and
they have all been discarded.

## The extraction problem

The PDF's text is copyable but not readable as Unicode. It uses two legacy
8-bit fonts:

- **`apara`** — the Roman transliteration column. An ASCII-remapped font: the
  byte `A` draws "ā", `f` draws "ụ", `w` draws "ḍ", `q` draws "ṭ", `x` draws
  "ṣ". Copying the text out gives `ArfpA(bA)qf` where the page reads
  *ārụpā(bā)ṭụ*.
- **`Nudiweb01e`** — legacy ASCII-Kannada (Nudi), used for the two Kannada
  columns.

The 52-glyph `apara` mapping was recovered by extracting the embedded font and
rendering every glyph, then **verified against the Academy's own pronunciation
key** in `docs/PronunciationandStuff.PDF` (pp. xxxix–xlii), which independently
lists the full vowel and consonant inventory. Both agree exactly.

The Kannada fonts were deliberately **not** transcoded. The app shows only
Roman-script Beary and English, so the Kannada columns are used during
extraction purely as positional reference, and no Kannada reaches the app or
the data files.

## Page layout

All 752 pages share one layout, as described in the Preface:

| Column | Content | Used for |
|---|---|---|
| 1 | Beary headword in Kannada script, + part-of-speech tag, + cross-references | part of speech only |
| 2 | Beary transliterated into Roman script | **the Beary word** |
| 3 | Meaning in Kannada | not used |
| 4 | Meaning in English | **the English gloss** |

Part-of-speech tags are read by matching the raw Nudi bytes for `(ನಾ)` = noun
and `(ಕ್ರಿ)` = verb. The Academy tags only nouns and verbs, so 2,430 entries have
no tag — that means "not marked in the source", not "unknown".

Lines marked `*` under a headword are the `(ನೋ)` "see also" cross-references:
variant forms of the same word, which the Lexicon includes deliberately because
Beary varies considerably by region. These are kept as `see_also`.

## Four misprinted pages, and how they were repaired

On **pages 169, 174, 190 and 420** the Roman column is typeset one or more rows
out of step with the other three columns. Page 420 prints *nōlụ mīnụ* beside
"Justice" when "Justice" belongs to *nyāya*, one row below. Read naively, these
pages yield confidently wrong word–meaning pairs.

Detection uses two independent signals:

1. **Structural.** On a sound page nearly every Roman headword sits level with
   an English row. The four bad pages leave 34–52% of headwords stranded
   between rows; every other page in the book is at or below 5%.
2. **Semantic.** The Lexicon cross-references variants reciprocally — *ārane*
   says "see *ārāmatto*", *ārāmatto* says "see *ārane*", and both gloss as
   "Sixth". On a slipped page these agreements collapse.

Repair searches row offsets from −12 to +12 and picks the one that maximises
agreement, scored on both cross-references and compound words (a compound like
*kāḍụ kudurɛ* should gloss with a word from *kāḍụ* "forest/wild" or *kudurɛ*
"horse"). Only a decisive winner is accepted. Common gloss words are excluded
from scoring, because matching on words like "down" makes "Put upside down"
agree with "Lie face down" and picks the wrong offset.

All four pages recovered, at offsets of −7, −9, −8 and −1 rows. Each was then
**checked by eye against the rendered page**, and the automatic offsets match:

- p169 → *kavvali* "A variety of song", *kasụkasụ* "Poppy seed", *kasaraṭụ* "Exercise"
- p174 → *kāḍụkudurɛ* "Wild horse", *kāḍụkākɛ* "Jungle crow", *kāṭāmurku* "Wild castor"
- p190 → *kilōgrām* "Kilogram", *kilīpu* "Clip", *kilikūḍụ* "Nest of a parrot"
- p420 → *nyāya* "Justice", *nyumōniya* "Pneumonia", *nratyasālɛ* "Dance school"

61 entries were recovered this way. Their records carry a `realigned_by` field
recording the offset applied, so the repair is auditable rather than silent.

## Quality checks

- **17,261** Roman headwords found across 752 pages; **17,234** kept. The 27
  dropped have no English gloss beside them in the source.
- **96.7%** of the 7,892 resolvable cross-references agree on meaning. The
  residual are genuine wording differences between two entries for one sense.
- The English column's row grid is derived from the English column itself
  rather than from the Roman anchors, so a gloss that wraps across two printed
  lines stays intact. This also fixed a handful of scrambled glosses on
  otherwise-sound pages — page 131's *kaṇḍɛ taniro* now reads "Literally,
  'Cooling of stomach', satisfying hunger" instead of an interleaved jumble.
- The app was driven end-to-end in a real browser to confirm both directions,
  diacritic-insensitive input, compound lookup and the no-match paths.

## App changes

- **Word lookup no longer uses AI.** An exact hit is served from the dictionary
  and labelled as such. This is the biggest practical change: the common case
  is now exact, instant, offline and free.
- **Sentence translation is retrieval-grounded.** Rather than injecting a
  100-word list into every request, the app looks up each word and each 2- and
  3-word window of your input, and sends only the matching entries (up to 70)
  plus the sourced grammar notes. Exact matches outrank near misses so a real
  word is never buried under compounds that merely share a prefix.
- **Diacritic-insensitive input.** Every entry carries a folded ASCII form, so
  `tanni` finds `tan'ni` and `kavudi` finds `kavuḍi`.
- Unknown single words report "Not in the Lexicon" or offer the nearest
  entries, instead of prompting for an API key.
- Results panel shows the dictionary entries behind an answer, with part of
  speech and variant forms.

## Known limitations

- **Page 174 keeps one bad row.** The offset is right for the rest of the page,
  but the first paired row is a boundary artefact of the columns not
  overlapping fully.
- **No Beary→English morphology.** Inflected forms fall back to prefix matching.
  A real stemmer would need the grammar the Academy says has not been written.
- **Sentence output is still AI-generated** and can be wrong even with good
  grounding, particularly for verb inflection.
- The Lexicon itself is a first edition; its editors expect corrections.

## Files added or replaced

```
tools/extract_dictionary.py   new    PDF -> data/dictionary.json
tools/build_lexicon.py        new    data/dictionary.json -> lexicon_data.js
data/dictionary.json          new    full extraction, 17,234 entries
lexicon_data.js               replaced   was 105 guessed entries
grammar_notes.md              rewritten  from the Academy's front matter
index.html                    rewritten  dictionary-first lookup
build_lexicon.py              removed    generated the guessed lexicon
lexicon.json                  removed    the guessed lexicon
```
