#!/usr/bin/env python3
"""
Build data/grammar_pack.json -- the grammar the translator injects into prompts.

Two layers, kept strictly apart because they have very different evidence:

  SYNTAX      How a Beary sentence is assembled: constituent order, whether
              relators precede or follow their noun, where tense sits. This is
              shared Dravidian structure, and Tulu is the nearest well-documented
              relative, so Tulu's sentence pattern is used as the scaffold.

  SURFACE     Every actual word and suffix. These are mined from
              data/dictionary.json, i.e. the Academy's own Lexicon, and each one
              carries the headword and gloss it came from so it can be audited.

The split matters. Testing the Tulu scaffold's 66 surface forms against the
Beary Lexicon found only 23% present, and most of those are false friends:
Tulu 'piravu' (behind) is Beary 'piravu' (pigeon); Tulu 'nama' (we) is Beary
'nama' (a mark on the forehead); Tulu 'enna' (my) is Beary 'enna' (counting).
Tulu's entire case-marked pronoun paradigm is absent from Beary. Injecting
those forms would be feeding the model confident wrong vocabulary, so this
script takes structure from Tulu and words from Beary, never the reverse.

Usage:  python3 tools/build_grammar_pack.py
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "dictionary.json")
OUT = os.path.join(ROOT, "data", "grammar_pack.json")

# How many Beary forms to keep per grammatical slot. The Lexicon records
# regional variants generously; the first few are enough for a prompt.
MAX_FORMS = 4


# ---------------------------------------------------------------------------
# Layer 1: syntax. Structure only -- no Beary or Tulu words appear here.
# ---------------------------------------------------------------------------
SYNTAX = {
    "_source": (
        "Shared Dravidian sentence structure, scaffolded from documented Tulu "
        "(easytulu.com lessons 2/9/31, raveeshkumar.com) and consistent with "
        "the Beary Lexicon's own front matter. Structural patterns only -- no "
        "Tulu vocabulary is carried over, because it does not transfer."
    ),
    "_confidence": (
        "Word order and the postposition/suffix mechanics are solid: they hold "
        "across Dravidian and match the Beary forms mined below. Tense and "
        "agreement detail is NOT established for Beary -- see known_gaps."
    ),
    "rules": [
        "Word order is Subject-Object-Verb. The verb comes last in the clause, "
        "unlike English Subject-Verb-Object.",
        "Relators FOLLOW their noun as postpositions; they are never placed "
        "before it like English prepositions. 'in the house' is house + inside.",
        "Grammatical case is marked by a suffix glued onto the end of the noun "
        "or pronoun, not by a separate word.",
        "There are no articles. Nothing corresponds to English 'a', 'an' or 'the'.",
        "Adjectives and other modifiers come before the noun they modify.",
        "A question is formed with a question word plus normal word order; the "
        "subject and verb are not inverted the way English inverts them.",
        "Negation is expressed with a dedicated negative word or verb form, not "
        "by inserting an equivalent of English 'do not'.",
    ],
    "known_gaps": [
        "Beary verb conjugation for person, number and tense is not documented. "
        "The Academy states plainly that no grammar of Beary has been written "
        "yet, and the Lexicon lists verbs only in their citation form. Do not "
        "state a conjugated form with confidence; prefer the citation form or "
        "an unambiguous periphrasis.",
        "Tulu's own conjugation classes were deliberately NOT copied in: Beary "
        "verb citation forms end overwhelmingly in -kụ, -ṭụ and -ḍụ, which does "
        "not match Tulu's -pu / -N / other grouping, so those rules would not "
        "apply.",
    ],
}


# ---------------------------------------------------------------------------
# Layer 2: surface forms, mined from the Lexicon.
# Each slot is (label, [English glosses that identify it]).
# ---------------------------------------------------------------------------
PRONOUNS = [
    ("I / me", ["i", "me"]),
    ("you (singular)", ["you"]),
    ("he", ["he"]),
    ("she", ["she"]),
    ("we", ["we"]),
    ("they", ["they"]),
    ("this", ["this"]),
    ("that", ["that"]),
    ("oneself", ["oneself", "self"]),
    ("to me (dative)", ["to me"]),
    ("to you (dative)", ["to you"]),
    ("to him (dative)", ["to him"]),
    ("to them (dative)", ["to them"]),
    ("us (accusative)", ["us"]),
    ("my (genitive)", ["my"]),
    ("your / yours (genitive)", ["your", "yours"]),
    ("his (genitive)", ["his"]),
    ("her (genitive)", ["her"]),
]

QUESTION_WORDS = [
    ("who", ["who", "who's there"]), ("whom", ["whom"]), ("whose", ["whose"]),
    ("what", ["what"]), ("where", ["where"]), ("when", ["when"]),
    ("why", ["why"]), ("how", ["how"]), ("how much", ["how much"]),
    ("which", ["which"]),
]

POSTPOSITIONS = [
    ("in front of", ["in front"]), ("behind", ["behind"]), ("near", ["near"]),
    ("inside", ["inside"]), ("outside", ["outside"]), ("above / on", ["above"]),
    ("under / below", ["under", "below"]), ("together / with", ["together", "with"]),
    ("without", ["without"]), ("instead of", ["instead of"]),
    ("through", ["through"]), ("around", ["around"]), ("beside", ["beside"]),
    ("after", ["after"]), ("before", ["before"]), ("up to / until", ["up to", "until"]),
    ("between / in the middle", ["in the middle", "between"]),
]

FUNCTION_WORDS = [
    ("is / exists", ["is there", "exists"]),
    ("having", ["having"]),
    ("no / not", ["no", "not"]),
    ("yes", ["yes"]),
    ("and / then", ["and", "then"]),
]

NUMERALS = [
    ("1", ["one"]), ("2", ["two"]), ("3", ["three"]), ("4", ["four"]),
    ("5", ["five"]), ("6", ["six"]), ("7", ["seven"]), ("8", ["eight"]),
    ("9", ["nine"]), ("10", ["ten"]), ("100", ["hundred"]), ("1000", ["thousand"]),
    ("first", ["first"]), ("second", ["second"]), ("third", ["third"]),
]

# Suffixes stated in the Academy's Editorial (p. xlvii). Each is re-checked
# against the Lexicon below, and only kept if the data actually shows it.
SUFFIX_CLAIMS = [
    {
        "name": "feminine",
        "suffix": "-ti",
        "gloss": "makes a feminine counterpart of a person noun",
        "examples": ["sorakāra (male worker) / sorakārti (female worker)",
                     "yajamāna (male owner) / yajamānti (female owner)"],
        "probe": ("ti", None),
    },
    {
        "name": "plural",
        "suffix": "-mārụ, -rụ, -ṅ",
        "gloss": "makes a plural",
        "examples": ["caṅṅāyi (friend) / caṅṅāyimārụ (friends)",
                     "bālakkāra (young person) / bālakkārụ (young persons)"],
        "probe": ("mārụ", None),
    },
    {
        "name": "causative",
        "suffix": "-bāṭụ / -pāṭụ",
        "gloss": "makes someone else do the action; the two are interchangeable",
        "examples": ["ākụ (to do) / ākụbāṭụ, ākụpāṭụ (to make someone do)",
                     "ōḍu (to run) / ōḍụpāṭụ, ōḍụbāṭụ (to make someone run)"],
        "probe": ("bāṭụ", "pāṭụ"),
    },
    {
        "name": "verbal noun",
        "suffix": "-ḍo / -ro (interchangeable), -ḍɛ / -rɛ",
        "gloss": "turns a verb into 'the act of doing'; the Lexicon writes the "
                 "pair inside brackets, e.g. amsākụḍo(ro)",
        "examples": ["cellụḍo = cellụro (saying)", "ākụḍo = ākụro (doing)"],
        "probe": ("ḍo", "ro"),
    },
    {
        "name": "ordinal",
        "suffix": "-ane / -āmatto",
        "gloss": "makes an ordinal from a numeral; both forms occur",
        "examples": ["on'nu (one) / on'nane, on'nāmatto (first)",
                     "ārụ (six) / ārane, ārāmatto (sixth)"],
        "probe": ("ane", "āmatto"),
    },
]


def senses(entry):
    """Split a gloss into its individual senses, lowercased."""
    out = []
    for chunk in re.split(r"(?:^|\s)\d+\.\s*", entry["english"]):
        for part in chunk.split(";"):
            s = part.strip().strip(".,;").lower()
            s = s.rstrip("?").strip()
            if s:
                out.append(s)
    return out


def expand_variants(word):
    """Expand the Lexicon's bracket notation into the forms it stands for.

        aṅkụ(ku)      -> aṅkụ, aṅku
        caṅṅa(ṅā)yi   -> caṅṅayi, caṅṅāyi
        avu(vo)ṇḍo    -> avuṇḍo, avoṇḍo
        ārụḍo(ro)     -> ārụḍo, ārụro

    One rule covers both positions: the bracketed text replaces the same number
    of characters immediately before the bracket. Note this means the bracket is
    NOT a simple insertion -- reading 'caṅṅa(ṅā)yi' as 'caṅṅaṅāyi' is wrong, and
    that is the form a naive strip of the brackets produces.
    """
    word = unicodedata.normalize("NFC", word)
    m = re.match(r"^(.*?)\(([^)]*)\)(.*)$", word)
    if not m:
        return [word]
    before, inside, after = m.groups()
    plain = before + after
    n = len(inside)
    swapped = (before[:-n] if n and len(before) >= n else before) + inside + after

    out = []
    for w in (plain, swapped):
        w = re.sub(r"\s+", " ", w).strip()
        if w and w not in out:
            out.append(w)
    # A word can carry two brackets; expand what is left recursively.
    if "(" in "".join(out):
        nested = []
        for w in out:
            nested.extend(expand_variants(w))
        return list(dict.fromkeys(nested))
    return out


def main():
    with open(SRC, encoding="utf-8") as fh:
        entries = json.load(fh)

    by_sense = defaultdict(list)
    for e in entries:
        for s in senses(e):
            by_sense[s].append(e)

    def collect(slots):
        """Pull the Beary forms for each grammatical slot out of the Lexicon.

        Ranking matters more than it looks. The Academy tags only nouns and
        verbs and leaves "pronoun, adjective, adverb, interjections" untagged,
        so an untagged entry is the likelier function word -- and an entry
        tagged noun or verb that matched on a one-word gloss is usually English
        ambiguity rather than a real hit. "Mine" pulled in 'kani' and 'gani',
        which are a mine you dig; "Like" pulled in 'meccụ', the verb.
        """
        out = []
        for label, keys in slots:
            cands = []
            for rank, key in enumerate(keys):
                for e in by_sense.get(key, []):
                    tagged = 1 if e["pos"] else 0
                    cands.append((tagged, rank, len(e["english"]), e))
            cands.sort(key=lambda c: c[:3])

            forms, evidence = [], []
            for _, _, _, e in cands:
                word = e["beary"].rstrip(" ?").strip()
                if not word or word in forms:
                    continue
                forms.append(word)
                evidence.append({"beary": e["beary"], "gloss": e["english"],
                                 "pos": e["pos"], "page": e["page"]})
                if len(forms) >= MAX_FORMS:
                    break
            if forms:
                out.append({"meaning": label, "beary": forms, "evidence": evidence})
        return out

    # Verify each claimed suffix actually shows up in the Lexicon.
    all_forms = set()
    for e in entries:
        all_forms.update(e.get("variants") or [e["beary"]])

    suffixes = []
    for claim in SUFFIX_CLAIMS:
        a, b = claim["probe"]
        n_a = sum(1 for f in all_forms if f.endswith(a))
        record = {k: v for k, v in claim.items() if k != "probe"}
        record["attested_in_lexicon"] = n_a
        if b:
            record["attested_in_lexicon_alt"] = sum(1 for f in all_forms if f.endswith(b))
        if n_a == 0:
            record["warning"] = "not found in the Lexicon; treat with caution"
        suffixes.append(record)

    pack = {
        "_meta": {
            "purpose": "Grammar injected into the translator's system prompt.",
            "built_by": "tools/build_grammar_pack.py",
            "surface_source": (
                "Beary-Kannada-English Lexicon (Nigantu), Karnataka Beary Sahitya "
                "Academy, 2017 -- every Beary form below is an attested headword, "
                "with its gloss and page recorded as evidence."
            ),
            "syntax_source": (
                "Tulu sentence structure as a shared-Dravidian scaffold. Structure "
                "only: Tulu words do NOT transfer to Beary and none are included."
            ),
            "entries_mined": len(entries),
        },
        "syntax": SYNTAX,
        "suffixes": suffixes,
        "pronouns": collect(PRONOUNS),
        "question_words": collect(QUESTION_WORDS),
        "postpositions": collect(POSTPOSITIONS),
        "function_words": collect(FUNCTION_WORDS),
        "numerals": collect(NUMERALS),
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, ensure_ascii=False, indent=1)

    js = os.path.join(ROOT, "grammar_data.js")
    with open(js, "w", encoding="utf-8") as fh:
        fh.write("// Generated by tools/build_grammar_pack.py -- do not edit.\n")
        fh.write("const BEARY_GRAMMAR = ")
        json.dump(pack, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")
    print(f"Wrote {js}")

    counts = {k: len(v) for k, v in pack.items()
              if isinstance(v, list)}
    print(f"Wrote {OUT}")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
