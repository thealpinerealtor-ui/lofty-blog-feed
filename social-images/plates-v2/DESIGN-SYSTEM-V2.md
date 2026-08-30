# Plates v2 — Design System

Four-template social image system for **West and Company | Brokered by eXp Realty**
(Ryan Berner Group, Kalispell/Whitefish MT). Adopted **2026-08-26**, replacing the
"Big Sky Ledger" survey plates (retired — do not run `make_plates.py` or any
`week-of-*/make_week.py`).

Output: 1080x1080 PNG, one per day, rendered by `render.py` from a weekly JSON spec.

## Setup (once per machine/sandbox)

```
cd social-images/plates-v2
npm i                       # local fonts (@fontsource) — no network needed at render time
python3 render.py week-YYYY-MM-DD.json
```

Requires python3 with `playwright` (chromium installed) and `Pillow`.

## The rule that matters: CONTENT PICKS THE TEMPLATE

Never random, never round-robin. Subject always wins over variety.

| Template    | Use for                                                                 | Never for |
|-------------|-------------------------------------------------------------------------|-----------|
| `frontpage` | Hard buyer/seller education, market truths, pricing reality, Sunday ethos/discipline pieces | — |
| `bigsky`    | Seasonal, lifestyle, town spotlights, valley/place content              | — |
| `fieldnotes`| SENSITIVE ONLY: divorce, estate/probate, family disputes, clear-outs    | anything loud |
| `signal`    | Myth-busting, contrarian market takes, punchy either/or framings        | **divorce/estate — forbidden.** A loud plate on a hard season reads as shouting at someone in pain. |

Aim for at least three different templates across a seven-day week.

## Weekly spec format

```json
{
  "outdir": "out/week-of-2026-08-31",
  "phone": "(406) 709-5404",
  "plates": [
    {"file": "plate-1-mon-something.png", "template": "signal", "vars": {"...": "..."}}
  ]
}
```

`phone` is REQUIRED and must be read from POSITIONING.md at generation time —
never hardcoded from memory. It fills every plate's footer.

Re-render a single plate after a fix:
`python3 render.py week-YYYY-MM-DD.json plate-3-wed-something.png`

## Inline markup (inside any var value)

- `\n` — line break
- `[[i]]…[[/i]]` — italic (bigsky headline second line looks best italic)
- `[[strike]]…[[/strike]]` — red strike-through (signal LINE1 only)
- `[[circle]]…[[/circle]]` — red hand-drawn circle (fieldnotes only; size via CIRCLE_W)
- `[[gap]]` — one empty ruled line (fieldnotes LINES only)

## Per-template variables

Values are plain text; sizes are numbers-as-strings. Anything omitted uses the default.

### frontpage — Anton condensed caps on cream, gold bar
| Var | Default | Notes |
|-----|---------|-------|
| TAG | `West and Company · Flathead Valley` | masthead strip, keep short |
| KICKER | — | small gold caps above the bar |
| HEADLINE | — | Anton, ALL CAPS automatically. 3–8 words per line reads best |
| DECK | — | 1–2 sentence supporting line |
| HEADLINE_SIZE | 96 | drop to 76–84 for long headlines; raise to 110 for 2–3 words |

### bigsky — dusk mountain gradient, DM Serif Display
| Var | Default | Notes |
|-----|---------|-------|
| KICKER | — | small gold caps, centered |
| HEADLINE | — | serif, centered; use `\n` + `[[i]]…[[/i]]` for a two-line title |
| SUB | — | 1–2 lines max — the mountains need room |
| HEADLINE_SIZE | 84 | |

### fieldnotes — ruled notebook, typewriter + red pen
| Var | Default | Notes |
|-----|---------|-------|
| TITLE | — | typewritten heading, underlined |
| LINES | — | the note body; short lines, use `[[gap]]` for beats, `[[circle]]` once |
| NOTE | — | red handwritten margin note (Caveat), slightly rotated |
| NOTE_TOP | 845 | px from top; pull up to ~780 if NOTE wraps to 2 lines |
| CIRCLE_W | auto | auto = word width + margin. Override (e.g. 230 for `???`, 300 for a word) only if the auto circle clips |

Keep LINES to ≤ 9 rows (including gaps) or it crowds the note and footer.

### signal — gold/black blocks, Archivo Black
| Var | Default | Notes |
|-----|---------|-------|
| KICKER | — | small gold caps top-left |
| LINE1 | — | cream on black; wrap the myth in `[[strike]]…[[/strike]]` |
| LINE2 | — | black on the gold block — the counterpunch |
| SUB | — | quiet payoff line under the block |
| LINE1_SIZE / LINE2_SIZE | 92 | drop to 76–84 if a line wraps past 2 rows |

## Palette & type (locked)

Cream `#EEE7D8` · paper `#F5EFDF` · ink `#211D16` · gold `#C6A35C` · gold-hi `#DEBE78`
· night `#16233A` · pen red `#C3271B`.
Anton (frontpage headline) · DM Serif Display (bigsky) · Courier Prime (fieldnotes)
· Caveat 700 (fieldnotes pen) · Archivo Black (signal) · Inter (kickers, decks, footers).
Every plate carries the same footer: `RYAN BERNER · WEST AND COMPANY` + office phone.

## Quality bar (check EVERY plate by eye before delivering)

View each rendered PNG. Nothing may clip, crowd an edge, wrap awkwardly, or overlap.
Headline sizes are per-post — fix by lowering the `*_SIZE` var and re-rendering that
one plate. Files land ~30–85 KB after the renderer's built-in 256-color quantize; if
one comes out larger, re-quantizing again is harmless.
