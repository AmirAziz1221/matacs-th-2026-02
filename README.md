# AI Proposal Triage Design

- **Name:** Amir Aziz
- **Reference:** MATACS-TH-2026-02
- **Role:** Associate Software Developer
- **Time actually spent:** 2-4 hour's

## How I used AI tools

I disagreed with Claude's first suggestion to treat C only as "flagged with a score of about 79". I checked the sub-scores myself, saw the number was not backed by a calculation, and had it recomputed (83.3). I also kept C unranked until a human clears the hidden instruction in its text, rather than letting the tool rank it automatically.

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
