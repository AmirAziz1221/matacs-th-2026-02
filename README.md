# AI Proposal Triage Design

- **Name:** Amir Aziz
- **Reference:** MATACS-TH-2026-02
- **Role:** Associate Software Developer
- **Time actually spent:** [FILL IN: your real time, e.g. "about 1 hour 30 minutes"]

## How I used AI tools

I used Claude to help draft the design, the prompts and the write-up, and I reviewed and edited the result myself. [FILL IN: one real place you disagreed with or corrected the AI. Example if it is true for you: "Claude's first draft gave rough scores (96 / 87 / 79) without showing how they were calculated. I asked for explicit formulas, and recalculating changed them to 96.5 / 85.7 / 83.3, so I used the recalculated numbers and put the formulas in prototype/scoring.py." Replace this with your own honest example.]

## Files

| File | What it is |
|---|---|
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions |
| [diagram/flow.png](diagram/flow.png) | Process flow from upload to ranked output (AI, rule and human steps) |
| [PROMPTS.md](PROMPTS.md) | The two prompts (extraction and judgement checklist) exactly as sent |
| [ranking.json](ranking.json) | Expected ranking of proposals A to E |
| [prototype/](prototype/) | Optional: `scoring.py` (rules), `run.py` (runs the prompts), `example_extracted.json` (structured values only), `.env.example` |

## Prototype (optional)

`python prototype/scoring.py prototype/example_extracted.json` reproduces `ranking.json` with no API key.
`prototype/run.py` runs the prompts on local text files placed in `prototype/samples/` (git-ignored, because proposal text is not published here). Copy `.env.example` to `.env` and add a key; keys are never committed.
