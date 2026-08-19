#!/usr/bin/env python3
"""
Build a starter English -> Beary (Romanized) lexicon.

IMPORTANT CAVEAT (read this before trusting the output):
Beary has no large public digital word list. This script derives approximate
Beary forms from well-known Malayalam vocabulary (which I have reasonable
training knowledge of) by applying the documented Beary sound-shift rules
(see grammar_notes.md, section 2):
  1. word-initial v -> b
  2. word-final single 'a' -> 'e'   (not long 'aa')
  3. doubled/geminate consonants simplify to a single consonant
Two entries (Rabbu = God, saan = plate) are ATTESTED directly from sources,
not derived -- these are marked confidence="attested". Everything else is
confidence="derived" (best-effort, needs verification against the real
Nigantu dictionary) or confidence="uncertain" for a few flagged tricky cases.

This is a TEST/STARTER dataset only. Replace with real dictionary data
extracted from Nigantu.pdf once available.
"""
import json
import os
import re

VOWEL_PAIRS = {"aa", "ee", "ii", "oo", "uu"}

def simplify_geminates(word):
    # collapse any doubled consonant (not vowels) to single
    out = []
    i = 0
    while i < len(word):
        c = word[i]
        if (
            i + 1 < len(word)
            and word[i + 1] == c
            and c not in "aeiou"
        ):
            out.append(c)
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)

def shift_initial_v(word):
    if word.startswith("v"):
        return "b" + word[1:]
    return word

def shift_final_a(word):
    if word.endswith("a") and not word.endswith("aa"):
        return word[:-1] + "e"
    return word

def derive_beary(malayalam_word):
    w = malayalam_word
    w = shift_initial_v(w)
    w = simplify_geminates(w)
    w = shift_final_a(w)
    return w

# (english, category, malayalam_base, override_beary_or_None, confidence, note)
ENTRIES = [
    # Pronouns
    ("I", "pronoun", "njan", None, "derived", ""),
    ("you (singular)", "pronoun", "nee", None, "derived", ""),
    ("you (plural/formal)", "pronoun", "ningal", None, "derived", ""),
    ("he", "pronoun", "avan", None, "derived", ""),
    ("she", "pronoun", "aval", None, "derived", ""),
    ("it / that", "pronoun", "athu", None, "derived", "Malayalam 'athu' covers both 'it' and 'that'"),
    ("we", "pronoun", "njangal", None, "derived", ""),
    ("they", "pronoun", "avar", None, "derived", ""),
    ("this", "pronoun", "ithu", None, "derived", ""),
    ("who", "question", "aar", None, "derived", ""),
    ("what", "question", "enthu", None, "derived", ""),
    ("where", "question", "evide", None, "derived", ""),
    ("when", "question", "eppol", None, "derived", ""),
    ("why", "question", "enthinu", None, "derived", ""),
    ("how", "question", "engane", None, "derived", ""),
    ("how much", "question", "ethra", None, "derived", ""),
    ("which", "question", "ethu", None, "derived", ""),
    # Numbers
    ("one", "number", "onnu", None, "derived", ""),
    ("two", "number", "randu", None, "derived", ""),
    ("three", "number", "moonu", None, "derived", ""),
    ("four", "number", "naalu", None, "derived", ""),
    ("five", "number", "anchu", None, "derived", ""),
    ("six", "number", "aaru", None, "derived", ""),
    ("seven", "number", "ezhu", None, "uncertain", "Malayalam 'zh' retroflex sound not distinguished in Beary; exact rendering unconfirmed"),
    ("eight", "number", "ettu", None, "derived", ""),
    ("nine", "number", "ombathu", None, "derived", ""),
    ("ten", "number", "pathu", None, "derived", ""),
    # Family
    ("father", "family", "achan", None, "derived", ""),
    ("mother", "family", "amma", None, "derived", ""),
    ("elder brother", "family", "ettan", None, "derived", ""),
    ("younger brother", "family", "anujan", None, "derived", ""),
    ("elder sister", "family", "chechi", None, "derived", ""),
    ("younger sister", "family", "anujathi", None, "derived", ""),
    ("son", "family", "makan", None, "derived", ""),
    ("daughter", "family", "makal", None, "derived", ""),
    ("husband", "family", "bharthavu", None, "derived", ""),
    ("wife", "family", "bharya", None, "derived", ""),
    ("friend", "family", "kootukaran", None, "derived", ""),
    ("child", "family", "kutty", None, "derived", ""),
    # Common nouns
    ("water", "noun", "vellam", "bellam", "attested", "Documented example veḷḷam -> beḷḷam; note the 'll' here represents the retroflex ḷ sound, not a true geminate, so it is kept doubled (override, not rule-derived)"),
    ("food / cooked rice", "noun", "choru", None, "derived", ""),
    ("house", "noun", "veedu", None, "derived", ""),
    ("road / way", "noun", "vazhi", None, "uncertain", "Contains 'zh' retroflex; exact Beary rendering unconfirmed"),
    ("book", "noun", "pusthakam", None, "derived", ""),
    ("name", "noun", "peru", None, "derived", ""),
    ("day", "noun", "divasam", None, "derived", ""),
    ("night", "noun", "raathri", None, "derived", ""),
    ("sun", "noun", "suryan", None, "derived", ""),
    ("moon", "noun", "chandran", None, "derived", ""),
    ("sky", "noun", "aakaasham", None, "derived", ""),
    ("earth", "noun", "bhoomi", None, "derived", ""),
    ("fire", "noun", "thee", None, "derived", ""),
    ("tree", "noun", "maram", None, "derived", ""),
    ("dog", "noun", "patti", None, "derived", ""),
    ("cat", "noun", "poocha", None, "derived", ""),
    ("bird", "noun", "pakshi", None, "derived", ""),
    ("fish", "noun", "meen", None, "derived", ""),
    ("money", "noun", "panam", None, "derived", ""),
    ("God", "noun", None, "Rabbu", "attested", "Documented nativized Arabic loanword (from 'rabb')"),
    ("plate", "noun", None, "saan", "attested", "Documented nativized Arabic loanword (from 'sahn')"),
    # Time
    ("today", "time", "innu", None, "derived", ""),
    ("tomorrow", "time", "naale", None, "derived", ""),
    ("yesterday", "time", "innale", None, "derived", ""),
    ("now", "time", "ippol", None, "derived", ""),
    ("morning", "time", "raavile", None, "derived", ""),
    ("evening", "time", "vaikunneram", None, "derived", ""),
    ("year", "time", "varsham", None, "derived", ""),
    ("month", "time", "maasam", None, "derived", ""),
    # Verbs
    ("come", "verb", "varuka", None, "derived", ""),
    ("go", "verb", "pokuka", None, "derived", ""),
    ("eat", "verb", "kazhikkuka", None, "uncertain", "Contains 'zh' retroflex; exact Beary rendering unconfirmed"),
    ("drink", "verb", "kudikkuka", None, "derived", ""),
    ("sleep", "verb", "uranguka", None, "derived", ""),
    ("see", "verb", "kaanuka", None, "derived", ""),
    ("hear", "verb", "kelkkuka", None, "derived", ""),
    ("speak / say", "verb", "parayuka", None, "derived", ""),
    ("give", "verb", "kodukkuka", None, "derived", ""),
    ("take", "verb", "edukkuka", None, "derived", ""),
    ("know", "verb", "ariyuka", None, "derived", ""),
    ("want", "verb", "venam", None, "derived", ""),
    ("do", "verb", "cheyyuka", None, "derived", ""),
    ("sit", "verb", "irikkuka", None, "derived", ""),
    ("stand", "verb", "nilkkuka", None, "derived", ""),
    # Adjectives
    ("good", "adjective", "nalla", None, "derived", ""),
    ("bad", "adjective", "chetta", None, "derived", ""),
    ("big", "adjective", "valuthu", None, "derived", ""),
    ("small", "adjective", "cheruthu", None, "derived", ""),
    ("hot", "adjective", "choodu", None, "derived", ""),
    ("cold", "adjective", "thanuppu", None, "derived", ""),
    ("new", "adjective", "puthiya", None, "derived", ""),
    ("old", "adjective", "pazhaya", None, "uncertain", "Contains 'zh' retroflex; exact Beary rendering unconfirmed"),
    ("beautiful", "adjective", "azhaku", None, "uncertain", "Contains 'zh' retroflex; exact Beary rendering unconfirmed"),
    ("happy", "adjective", "santhosham", None, "derived", ""),
    ("sad", "adjective", "dukham", None, "derived", ""),
    ("many", "adjective", "adhikam", None, "derived", ""),
    # Greetings / particles
    ("yes", "particle", "athe", None, "derived", ""),
    ("no", "particle", "illa", None, "derived", ""),
    ("please", "particle", "dayavayi", None, "derived", ""),
    ("thank you", "particle", "nanni", None, "derived", ""),
    ("sorry", "particle", "kshamikkanam", None, "derived", ""),
    # Colors
    ("red", "color", "chuvappu", None, "derived", ""),
    ("white", "color", "velutha", None, "derived", ""),
    ("black", "color", "karutha", None, "derived", ""),
    ("blue", "color", "neela", None, "derived", ""),
    ("green", "color", "pachcha", None, "derived", ""),
]

lexicon = []
for english, category, mal, override, confidence, note in ENTRIES:
    if override is not None:
        beary = override
    else:
        beary = derive_beary(mal)
    lexicon.append({
        "english": english,
        "category": category,
        "malayalam_base": mal,
        "beary_romanized": beary,
        "confidence": confidence,
        "note": note,
    })

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexicon.json")
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(lexicon, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(lexicon)} entries to {OUT_PATH}")
