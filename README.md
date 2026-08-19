# Beary Translator (starter build)

A single-page, AI-powered English ↔ Beary (Byari) translator. Beary output is
always shown in Roman/English script. Works on words, sentences, and
paragraphs.

## Quick start

1. Open `docs/index.html` directly in your browser (double-click it, or
   drag it into a browser tab) — or visit the deployed GitHub Pages site.
2. Click the gear icon (top right) → paste your **DeepSeek API key** → Save.
3. Type in the left box, click **Translate**. Use the swap button (⇅) to
   flip English → Beary vs Beary → English.

Your API key is never written to disk by this app. It's kept in the page's
memory for that session, unless you tick **"Remember on this device"**, in
which case it's saved in your browser's local storage on your machine only
— it is never sent anywhere except directly to the API endpoint you
configured. DeepSeek's API accepts direct browser requests, so no backend
or proxy is needed.

## Deploying

The app is fully static, so `docs/` can be served as-is by GitHub Pages:
Settings → Pages → Deploy from a branch → Branch `main`, folder `/docs`.

## Files

| File | Purpose |
|---|---|
| `docs/index.html` | The app itself — open this. |
| `docs/lexicon_data.js` | Starter ~100-word English↔Beary lexicon, loaded by the app and injected into every AI request so translations stay grounded instead of the model guessing freely. |
| `lexicon.json` | Same data, plain JSON (for editing/regenerating). |
| `build_lexicon.py` | Script that generated `lexicon.json` from documented Malayalam→Beary sound-shift rules. Re-run after editing the word list at the top of the file. |
| `grammar_notes.md` | Grammar/phonology reference used to ground the AI's translations. |

## ⚠️ Current limitation: starter vocabulary only

There is no public digitized Beary dictionary. This build's lexicon
(`lexicon.json`) is a **best-effort ~100-word starter set**, derived by
applying documented sound-shift rules to known Malayalam vocabulary — it is
**not** sourced from the real Nigantu dictionary (Karnataka Beary Sahitya
Academy, 2017, ~20,000 words), which wasn't accessible for extraction yet
(too large to fetch/upload in one piece). Each entry is tagged:

- `attested` — directly documented from a real source (only a few: e.g.
  "Rabbu" = God, "saan" = plate, "bellam" = water)
- `derived` — rule-derived approximation, plausible but unverified
- `uncertain` — flagged because it involves a Malayalam sound (retroflex
  "zh") that Beary handles differently and the exact rendering isn't
  confirmed

Translation quality outside the lexicon depends entirely on the underlying
AI model's own (limited, unreliable) knowledge of Beary. **Treat all output
as draft quality until real dictionary data replaces the starter lexicon.**

### To upgrade the vocabulary later

Send a smaller excerpt of the Nigantu dictionary (a page range as its own
PDF, or clear photos of a few pages) and the entries can be extracted and
merged into `lexicon.json` directly — no app changes needed, since
`lexicon_data.js` is just that JSON re-exported as a JS constant.
