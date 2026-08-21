# Beary Grammar Notes 2.0 — Living / Corrections

`grammar_notes.md` is deliberately locked to the Academy's own printed front
matter — "Where the two disagreed, the Academy's text wins." That's correct
for what the Lexicon documents, but the Lexicon itself says it marks only
nouns and verbs, was compiled as "a first pass," and has no verb-conjugation
paradigm or postposition list at all. Sentence translation needs exactly
those things.

This file is the opposite kind of source: **native-speaker corrections**,
collected as they come up, not printed-book citations. Nothing here overrides
`grammar_notes.md` where the two actually cover the same ground — this file
fills in what the book leaves blank. Every entry should carry roughly how
sure we are and where it came from, since unlike the Academy text this can't
be checked against a page number.

## 1. Status

Started 2026-08-21, from corrections on a single test sentence. Small.
Grows as more sentences get checked. Nothing below has been cross-checked
against a second native speaker yet — treat as "one informant, high trust,
not yet corroborated."

## 2. Colloquial vocabulary the Lexicon doesn't surface as the natural word

The Lexicon's headword for a concept is sometimes the formal/older term, and
everyday speech uses a different (often borrowed) word. When both exist,
prefer the colloquial one for sentence translation — the Lexicon word isn't
wrong, it's registerally distant.

| Concept | Lexicon headword | Everyday word actually used | Note |
|---|---|---|---|
| bottle | *kuppi* ("Glass; glass bottle") | *baatli* | English "bottle" via Kannada; not a Lexicon headword at all |

## 3. Function words / postpositions

The Lexicon marks only nouns and verbs, so grammatical particles like these
don't show up in a part-of-speech search and are easy to miss entirely.

| Form | Function | Note |
|---|---|---|
| *ro* | genitive/linking postposition, roughly "of" | *thanni ro baatli* = "bottle of water" (water-of bottle) |

## 4. Sense gaps: word exists, but under a different English gloss

Retrieval in the app matches literal English words in the gloss. A dictionary
entry that covers the needed sense under different English phrasing gets
missed even though the word is right there. Recording the bridge here fixes
retrieval without editing the generated lexicon data.

| English sense wanted | Lexicon headword | Lexicon's own gloss | Bridge |
|---|---|---|---|
| already / beforehand | *mun'nolu* (folds to *munnolu*) | "1. In front of  2. After  3. Before" | "already" is a narrower case of sense 3 ("Before"); not obvious from the gloss text alone |

## 5. Morphology the Lexicon doesn't paradigm out

`grammar_notes.md` §4 documents one final-vowel alternation for verb endings
(`-ro`/`-ḍo`, `-re`/`-ḍe`, e.g. *piḍikurɛ = piḍikuḍɛ*). The same *-u → -e/-ɛ*
softening (citation/formal form ending in *-u* vs. the form actually spoken)
shows up outside verbs too:

- *munnolu* (dictionary citation form) → *munnole* (as spoken) — same
  softening pattern, applied to what the Lexicon leaves untagged (not marked
  noun or verb).

Tense/person suffixes observed but not yet generalized into a rule — each is
attested in exactly one example so far, treat as anecdotal until a second
example confirms the pattern:

| Suffix | Attested on | Apparent function |
|---|---|---|
| *-inne* | *pō* (go) → *poginne* | 1st person, past/"went" |
| *-chir* | *beccɛ*-family ("I have kept it") → *becchir* | 3rd person past, used for an elder (mother) — possibly a respect/honorific past form, not plain 3rd person |
| *aith* (separate word, not a suffix) | *pidi aith* = "realized" | auxiliary meaning roughly "became/happened," similar in function to Kannada *āyitu* |

## 6. Corrected example sentences

Full sentences a native speaker corrected, kept whole (not just decomposed
into the tables above) because word order and which words get dropped/fused
matter as much as the words themselves.

---

**English:** I had to go and get a bottle of water. Then I realized my
mother already kept a bottle for me.

**Beary (corrected):** naan thanni ro baatli edko poginne. Appa nak pidi
aith umma munnole thanni ro baatli becchir.

**Gloss of each word:**

| Beary | Gloss | Lexicon? |
|---|---|---|
| naan | I | colloquial for *ñānụ* |
| thanni | water | = *tan'ni*, exact |
| ro | of (linking) | not in Lexicon, see §3 |
| baatli | bottle | not in Lexicon, see §2 |
| edko | take/get | = *eḍkụ*, root only — ending not in Lexicon |
| poginne | went | = *pō* + *-inne*, see §5 |
| Appa | then | = *appa*, exact |
| nak | to me | = *n'akkụ*, contracted |
| pidi aith | realized | not in Lexicon, see §5 |
| umma | mother | = *umma*, exact |
| munnole | already | = *mun'nolu*, see §4 and §5 |
| becchir | had kept | = *beccɛ*-family + *-chir*, see §5 |

**Note on my first (wrong) attempt**, kept for contrast: guessed *ari*
(know) for "realized" — wrong sense; invented tense morphology for "had
to"/"already"/"kept" with no dictionary anchor at all. This is the exact
failure mode this file exists to close.

## 7. How to add to this file

1. Give a sentence pair (English + your correction of what the app or a
   model produced).
2. It gets decomposed into whichever of §2–§5 apply, plus logged whole in
   §6.
3. Nothing here gets folded into `grammar_notes.md` (that file stays a pure
   Academy citation) or into `lexicon_data.js` (regenerated from the PDF —
   hand edits there would be overwritten). This file is the durable home for
   corrections until there's enough to justify structural changes.
