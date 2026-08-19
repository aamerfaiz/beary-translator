# Beary (Byari) Language — Grammar & Phonology Notes

Compiled from public linguistic sources (Wikipedia's Byari dialect article, Omniglot,
The Better India, The News Minute, and community sources) as of Aug 2026. This is a
**working reference for building translation logic**, not an academic grammar — it
should be corrected against the Nigantu dictionary (Karnataka Beary Sahitya Academy,
2017) once that data is available.

## 1. Classification & relationship to neighboring languages

- Beary/Byari is a Southern Dravidian dialect spoken by ~1.5 million people
  (some sources say up to 15 lakh) along the Dakshina Kannada / Udupi coast
  (Karnataka) and Manjeshwaram taluk, Kasaragod (Kerala).
- Best described as: **Malayalam vocabulary/idiom base + Tulu phonology and
  grammar**, with Kannada influence (from centuries of contact) and a layer of
  nativized Arabic and Persian loanwords (from the community's Arab-trader
  ancestry).
- Mutual intelligibility: Malayalam and Tamil speakers reportedly understand
  ~75% of spoken Beary. It shares ~60% vocabulary with Kodava.
- No historic dedicated script — written in Kannada or Malayalam script, or
  informally in Roman letters. (A new dedicated Beary script was proposed by
  the Academy in Sept 2022 but is not in common use — not relevant to this
  project since the deliverable is Roman-script transliteration.)

## 2. Sound changes (Malayalam → Beary), i.e. phonological rules

These are the most concrete, citable rules found, useful as transformation
rules when deriving a Beary form from a known Malayalam cognate:

| Rule | Example pattern |
|---|---|
| Initial **v → b** | Malayalam *veḷḷam* (water) → Beary-style *beḷḷam*-ish forms |
| Word-final **a → e** | Malayalam *-a* endings often surface as *-e* in Beary |
| **Geminate (doubled) consonants simplify** | e.g. *-cc-* → *-c-* |
| **Retroflex/lateral sounds dropped or merged**: ḻ (zha), ṇ, ṟ are not distinguished the way Malayalam distinguishes them | these collapse toward simpler alveolar/dental equivalents |
| **No verbal person-agreement suffixes** | unlike literary Malayalam, Beary verbs don't inflect for person/number the way older Malayalam forms do — this is a Tulu-grammar trait |

These rules are documented at the phoneme level but not exhaustively
demonstrated with worked examples in public sources — treat derived words
as **approximate / best-effort**, not verified.

## 3. Vocabulary layers

1. **Dravidian core** (shared with Malayalam/Tamil/Tulu) — pronouns, numbers,
   kinship terms, body parts, basic verbs.
2. **Tulu-influenced grammar/function words** — sentence structure, some
   postpositions, verb structure.
3. **Kannada influence** — from long contact in Dakshina Kannada/Udupi.
4. **Nativized Arabic/Persian loanwords** — common in everyday speech,
   especially religious/household vocabulary. Documented examples:
   - *saan* (from Arabic ṣaḥn) = "plate"
   - *Rabbu* (from Arabic rabb) = "God"
   - Other attested Arabic-root words (meaning not confirmed from sources):
     *pinhana, gubboosu, dabboosu, pattir, rakkasi, seintaan, kayeen*

## 4. Sentence structure

- Follows the general Dravidian pattern: **Subject – Object – Verb (SOV)**,
  same as Malayalam, Tamil, Kannada, Tulu (this is inferred from Beary's
  classification as Dravidian + Malayalam-based; not separately confirmed
  with a worked Beary sentence example in the sources found).
- Postpositions rather than prepositions (again, inferred from the Dravidian
  family pattern).
- No definite/indefinite articles (like other Dravidian languages).
- Verb typically does not change for person the way standard Malayalam does
  (see phonology table above) — this simplifies verb handling somewhat
  compared to literary Malayalam.

## 5. What this means for the translator

- **Ground the model, don't let it free-associate.** Beary is under-documented
  online; a general LLM's raw knowledge of it is unreliable. The app should
  inject (a) this grammar summary and (b) the lexicon (starter list now, real
  dictionary data later) into every translation request as context, and
  instruct the model to flag low-confidence output rather than inventing
  fluent-sounding but wrong Beary.
- **Roman-script output only** — per the project's scope, Beary output is
  always romanized, not Kannada/Malayalam/Arabic script, using a consistent
  phonetic spelling (the dictionary's own Roman transliteration column,
  once available, should become the canonical spelling authority).
- **Word-for-word lexicon lookups should take priority over the model's own
  guesses** whenever an exact/near match exists in the lexicon, since that
  data is more trustworthy than model-generated vocabulary.

## Sources
- https://en.wikipedia.org/wiki/Byari_dialect
- https://www.omniglot.com/writing/beary.htm
- https://thebetterindia.com/111400/beary-language-dictionary-glimpse-language/
- https://www.thenewsminute.com/features/tulu-nadus-bashe-byari-language-and-its-struggle-identity-102414
- https://pyaribeary.blogspot.com/2012/01/byari-palkabashe-byari-language.html
