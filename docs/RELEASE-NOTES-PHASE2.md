# Release notes — Phase 2: sentence formation & grammar

**Date:** 2026-08-20 · **Branch:** `grammer-sentences`

Phase 1 replaced guessed vocabulary with the Academy's Lexicon. Phase 2 is about
what happens *between* the words: getting the model to build a Beary sentence
rather than substituting Beary words into English word order.

## What the plan asked for, and what changed

The Phase 2 plan was written before Phase 1 landed, so several of its premises
could not be checked at the time. They can now, against 17,234 attested entries.
Four of them turned out to be wrong, and the plan's own cited ablation is the
reason that matters: feeding a model **wrong** grammar rules dropped accuracy
from 85% to 38% — worse than giving it nothing. A confidently wrong rule is the
most expensive thing to ship here.

| Plan said | Data says | Action |
|---|---|---|
| Beary = "Malayalam vocabulary + Tulu grammar" | The Academy calls Beary a language in its own right, a sister of Kannada. Malayalam resemblance is contact, not descent. | Rewrote the framing |
| "Beary merges the ḻ/ṇ/ṟ retroflex distinctions" — feed this as a negative constraint | ṭ appears in 2,295 entries, ḍ in 3,943, ṇ in 895. They are contrastive phonemes of Beary. | **Inverted** — the constraint now says *preserve* them |
| Sound-shift rule: geminates simplify to one consonant | 19.8% of headwords carry a doubled consonant (eṭṭụ, illa, okkɛ) | **Dropped**; constraint now says do not drop them |
| Sound-shift rule: word-final -a → -e | 3,360 entries end in -a, only 75 in -e. The Beary reflex is -ɛ (1,893). | **Dropped** |
| Sound-shift rule: word-initial v → b | 320 headwords still begin with v (vakīlụ, vañcanɛ, vamśa) | **Dropped** as a rule |
| Standardise romanisation to doubled vowels (aa, ee) | That scheme cannot express ụ vs u or ɛ vs e, which are separate phonemes, and loses retroflex marking | **Declined** — see below |

Those sound-shift rules were the same ones that produced the discarded Phase 1
lexicon. They were never Beary rules; they were the guesswork Phase 1 removed.

## The Tulu question

The plan's core idea — scaffold with Tulu, which is far better documented — is
right, but only for **structure**. Tested against the Lexicon, of the 66 Tulu
surface forms in `tulu_grammar_scaffold.json`, only 23% appear in Beary at all,
and most of those mean something else:

| Tulu | means | Beary lookalike | actually means |
|---|---|---|---|
| piravu | behind | pirāvu | pigeon |
| nama | we | nāma | mark worn on the forehead |
| enna | my | enna | counting |
| idi | throughout | iḍi | thunder |
| muta | up to, till | mūta | elder |

Tulu's whole case-marked pronoun paradigm (yAn, enk, ninan, nikk, imbe, akulu,
eer) is absent from Beary. Its verb classes key on verbs ending in *-pu* and
*-N*; Beary verb citation forms end in **-kụ** (417), **-ṭụ** (343) and **-ḍụ**
(134). So the conjugation rules would not apply either.

The split this produced: **sentence structure from Tulu, every surface form from
the Beary Lexicon, never the reverse.** The two layers are kept apart in
`data/grammar_pack.json` and labelled with their evidence, so nobody later
mistakes one for the other.

## Grammar mined from the dictionary

A word list is not a grammar, but 17,234 entries glossed in English contain a
lot of grammar implicitly — an entry glossed "To him" is a dative pronoun
whether or not anyone labelled it one. `tools/build_grammar_pack.py` extracts:

- **17 pronoun slots**, including a visible case system: dative `-kụ`/`-gu`
  (n'akkụ *to me*, ōnugu *to him*), genitive `-ḍo`/`-o` (n'aṇḍo *my*, niṇḍo
  *your*), accusative `-e`/`-le` (n'aṅale *us*)
- **9 question words**, which share a frame: most start **e-** (eññɛ, eṇḍụ,
  endi, eṅanɛ, ettarɛ), the who/whose group starts **ā-**
- **15 postpositions** (ulga *inside*, perovu *behind*, mēlụ *above*, aḍi
  *under*, kūḍɛ *with*, illāmɛ *without*)
- **15 numerals**, with ordinals in `-ane`/`-āmatto`
- **5 function-word slots** (uṇḍu *is/exists*, illa *no*, pin'nɛ *and*)
- **5 suffix rules** from the Academy's Editorial, each re-verified against the
  data rather than trusted (feminine `-ti`: 247 hits; causative `-bāṭụ`/`-pāṭụ`:
  245/295; verbal noun `-ḍo`/`-ro`: 1,217/1,057; ordinal: 10/11)

One filter does most of the work. The Academy tags **only nouns and verbs** and
leaves pronouns, adjectives and adverbs untagged, so an untagged entry is the
likelier function word. Without it, "mine" pulls in `kani` and `gani` — a mine
you dig — and "like" pulls in `meccụ`, the verb. Every mined form records the
gloss, part of speech and page it came from, so the whole pack is auditable.

## The prompt

`buildSystemPrompt()` now has labelled sections instead of one paragraph:

1. **Identity and spelling** — what Beary is, and the transliteration to
   reproduce exactly, spelling out that ụ≠u and ɛ≠e.
2. **What not to do** — the negative constraints, aimed at the actual failure
   mode: a model asked for a language this small tends to emit Malayalam,
   Kannada or Tulu instead. The Tulu false friends above are named explicitly.
3. **How Beary sentences work** — syntax rules, the "not established" gaps
   stated as gaps, the suffix rules, then the mined paradigms.
4. **Dictionary entries for this input** — the Phase 1 retrieval.
5. **How to answer**, ending in a five-point self-check the model runs on its
   own draft before replying.

The result is ~2,000 tokens.

## Romanisation: why the plan's step 1 was declined

The plan opened with "standardise romanisation — always double a vowel for
length (aa, ee)". That was written when the lexicon was ad-hoc guesswork. It no
longer is: the Lexicon has an official transliteration, published with a
pronunciation key, and it encodes real contrasts. Doubling vowels cannot express
`ụ` vs `u` or `ɛ` vs `e`, and drops retroflex marking entirely — it would delete
phonemic information to save roughly 150 tokens out of 2,000.

The token concern is handled where it belongs instead: every entry already
carries a diacritic-free ASCII form, used for **matching what a user types**,
while output keeps the Academy's spelling.

## App changes

- **Bracket variants are now searchable.** The Lexicon writes a variant by
  bracketing what changes: `añci(cɛ)` means *añci* or *añcɛ*. It is a
  replacement, not an insertion — so stripping the brackets to get "añcicɛ",
  which is what the old build did, produced a form that is not a word. 1,484
  entries were affected; 1,454 now index under both real spellings. Typing
  `anci` or `ance` both work.
- **English inflection is handled.** The Lexicon glosses verbs bare ("Give"), so
  "gave" used to miss. Now regular endings are stripped and ~60 irregulars are
  mapped, so *gave* → koḍu, *went* → pō, *books* → kitābu.
- **Nine short headwords repaired.** Words like `pō` (go) and `bā` (come) are
  letter-spaced in the PDF and were extracted as "p ō", "b ā" — unfindable. A
  lone consonant is not a possible Beary word, so short two-chunk headwords are
  now rejoined. `ī mun'nolu` is genuinely two words and is left alone.
- **A correction link** appears under AI-generated sentences, opening a
  pre-filled GitHub issue with the input, the output and a space for the right
  answer.

## What is still missing

**Verb conjugation.** This is the one real gap, and no amount of prompting fills
it. The Lexicon gives verbs in citation form only; the Academy says outright
that no Beary grammar exists. Two entries hint at it (*uṇḍɛ* "I have eaten",
*beccɛ* "I have kept it") and that is all. The prompt therefore instructs the
model **not** to fake a conjugation, which keeps it honest but leaves tense
weakly expressed.

**No measured accuracy claim.** The percentages in the Phase 2 plan come from
the cited Tulu paper, not from this repo. No API key was available in this
session, so no A/B was run here, and the arXiv link could not be opened from
this network to verify it. The techniques used are independently well
established, but this release makes no measured claim of its own.

**No native-speaker validation.** Still the highest-value missing piece. The
correction link is the passive channel; a handful of checked sentences would be
worth more than any further prompt engineering — above all a single verb across
person and tense ("I go / you go / he goes / I went / I will go"), which would
close the one gap the dictionary cannot.

## Files

```
tools/build_grammar_pack.py   new    dictionary -> data/grammar_pack.json + grammar_data.js
data/grammar_pack.json        new    mined grammar, every form carrying its evidence
grammar_data.js               new    16 KB, loaded by the page
tools/extract_dictionary.py   changed  bracket-variant expansion, letter-spacing repair
tools/build_lexicon.py        changed  emits every searchable spelling per entry
index.html                    changed  four-section prompt, self-check, de-inflection, report link
grammar_notes.md              changed  adds the recovered paradigms (§7-9)
```

Rebuild with:

```sh
python3 tools/extract_dictionary.py
python3 tools/build_lexicon.py
python3 tools/build_grammar_pack.py
```

---

# Update — grammar from a speaker, and the dialect toggle

**Date:** 2026-08-20

The section above closed by saying native-speaker validation was the highest-
value missing piece, and that a single verb across person and tense would close
the one gap the dictionary cannot. That happened. A speaker of the Mangalore
city variety supplied a verb paradigm and four worked sentences, which filled
the gap and corrected two things this repo had wrong.

## What the sentences confirmed

Every content word and pronoun checked out against the Lexicon:

| speaker | Lexicon | page |
|---|---|---|
| naa / naan | ñānụ "I; myself; me" | 339 |
| nee | n'ī "You" | 434 |
| awnu | avnu "He" | 40 |
| nak | n'akkụ "To me" | 421 |
| nik | n'ikkụ "To you" | 431 |
| nando | n'aṇḍo "Mine" | 421 |
| chengayi | ceṅṅa(ṅā)yi "Friend" | 299 |
| po | pō "Go" | 524 |
| undu | uṇḍu "Is there; exists" | 72 |
| yawde | evuḍɛ "Where ?" | 104 |
| pidille | **piḍillɛ "Don't know"** | 485 |
| abba | abba "Father" | 23 |
| maad | māḍụ "Roof" | 619 |

`piḍillɛ` is a headword in its own right, and `piḍi` p484 sense 3 is
"Knowledge" — so the negative is transparently *knowledge + illa (no)*.

`pō` is the entry Phase 2 repaired from the letter-spaced "p ō". It would have
been unfindable a day earlier.

## Two corrections to this repo

**`authl` / `avtulu`.** The notes claimed the Lexicon had exactly four words for
house. It has at least six: `ava`, `aga`, `avtu`, `porɛ`, `bīḍụ`, `baitụ`. The
first search only matched glosses that were exactly the word "House", missing
`aga` "Home" and the `avtu` stem. `avtulu` p40 = "At home" is the speaker's
`authl`, and `avtuḍo cela(lo)vu` p40 confirms the stem. The pronunciation fits
because the Academy's key gives plain `t` as "th of thief", so `avtu` is
[auθu] — the "outh" of South, as the speaker described it.

**The `-ḍo` diagnostic was wrong.** This repo had recorded that a bracketed
`-ḍo(ro)` marks a verbal noun and an unbracketed `-ḍo` marks a genitive. That
is not the distinction. `-ḍo`/`-ro` is one suffix serving both functions —
`abbaro` "father's" is the same ending as in the gerunds.

## The nasal rule

The speaker observed that "awndo is always do". That turns out to be a regular
phonological rule, and the dictionary confirms it with no exceptions at all:

| | count |
|---|---|
| words ending `-ro` preceded by a nasal | **0** of 159 |
| bracketed `ḍo(ro)` preceded by a nasal | **0** of 980 |
| bracketed `ḍo(ro)` preceded by a vowel | **980** of 980 |

After a nasal (n, ṇ, ñ, ṅ, m) the alternation is neutralised to `-ḍo`; `ro` is
impossible there. That is why the pronoun genitives never alternate — the nasal
blocks it — and not, as previously recorded, because they are a different
morpheme. The speaker's own phrase shows both halves at once: **`nando authro
maad`**, where `nando` has the nasal and takes `ḍo`, and `authro` has none and
takes the southern `ro`.

## The verb paradigm

None of this is in the Lexicon; it cannot be, since the Lexicon lists citation
forms only.

Verbs are **stem + tense marker + person ending**, and the person ending is
much smaller than expected: **1st and 2nd person are always identical**, and
only the 3rd person is marked, with `-a`.

| | past `-y-` | future `-nd-` | immediate `-nd-` + `-o` |
|---|---|---|---|
| naa (I) | poye | ponday | pondo |
| nee (you) | poye | ponday | pondo |
| awnu (he) | poy**a** | pond**a** | — |
| nanga (we) | — | poi | — |

`koḍu` "give" → `kodte` "I gave" follows the same shape with `-t-` for the
tense consonant. This corrected an earlier guess in this repo that `-e` was a
1st-person ending; it is not a person marker at all.

Also recovered: negation by suffix (`piḍi` + `illɛ`), dative subjects for
experiencer verbs (`nak piḍillɛ`, literally "to me no knowledge"), and yes/no
questions formed by a fused `-a` with sandhi (`undu` → `unda?`, `poya` →
`poyana?`) — the same clitic as Tamil and Kannada, not a separate particle as
first assumed.

## App changes

- **Variety toggle** in Settings: Mangalore city (`-ro`, default) or Udupi and
  north (`-ḍo`). It rewrites dictionary output, the results panel and the
  dictionary lines in the prompt, and it redraws live without retyping.
  Conversion is mechanical, not a lookup: apply `ro` only after a vowel, never
  after a nasal. 1,244 entries are affected — 980 the Lexicon brackets plus 264
  recorded in one form only, which previously could not be shown in the other
  variety at all.
- **Search accepts either variety** regardless of the setting, so `arudo` and
  `aruro` both reach the same entry.
- **Case suffixes are stripped on lookup.** `abbaro` is not a headword; `abba`
  is. Typing `abbaro` now answers "Father" and says why: *abbaro = abba + -ro
  (genitive)*.
- **Function words outrank homographs.** Since the Academy tags only nouns and
  verbs, an untagged entry is the likelier function word. `nakku` now answers
  "To me" first instead of "Press; crush down".
- **The prompt carries the speaker grammar**: case, the verb paradigm,
  negation, dative subjects, question formation and the dialect rule, plus a
  negative constraint against agreeing the verb for 1st vs 2nd person and two
  extra self-check items.

## Still open

- The paradigm rests on **two verbs from one speaker**. Shape is trustworthy,
  coverage is thin, and the prompt says so.
- Whether `nanga ponday` is valid alongside `poi` — i.e. whether number is
  marked at all, or `poi` is a hortative. Left unstated rather than guessed.
- The dialect line is drawn between Udupi and Mangalore city on the speaker's
  evidence. Puttur, Sullia and Kasargod were deliberately left out of scope.
- The speaker's own romanisation (`ng` for ṅ, `w` for v, `ee` for ī, dropped
  final `ụ`) still misses the search index on about a third of words. Parked as
  a later simple/phonetic toggle.
