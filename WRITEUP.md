# Write-up: AI Proposal Triage Design (MATACS-TH-2026-02)

See `diagram/flow.png` for the full flow.

## 1. AI vs. rules

**AI is used for two things only:**
- Reading messy proposal text and turning it into structured fields, each with a quote.
- Answering yes/no checklist questions for a judgement criterion (here, Team and approach), again with a quote.

**Plain code handles everything else:** file checks, schema validation, checking that quotes exist in the source, the mandatory pass/fail gate, all arithmetic, weights, ranking, tie-breaks and the audit log.

**Why this line:** AI is good at understanding language. It is not reliable at exact maths or at applying a hard rule the same way every time. If a result must be exact, repeatable and checkable, it is code. Even for judgement, the AI answers small yes/no questions and code assigns the points, so the AI never invents a score.

## 2. Consistency and explainability

- Temperature 0, fixed JSON schema, pinned model and prompt versions.
- Extraction is cached by file hash. Same file gives the same extracted data, and everything after that is deterministic code. Ranking the same proposals twice therefore gives the same result. If a file is re-extracted and a field differs, the tool flags the difference instead of silently changing it.
- Every extracted value needs a verbatim quote. Code checks the quote is really in the proposal. If not, the value is dropped and flagged.
- Price, timeline, warranty and experience use published formulas (for example price score = 10 x lowest eligible price / this price). Anyone can recompute them.
- The reviewer sees, for each proposal: each criterion, its weight, the points, the formula or checklist used, and the quote with its page. A one-line reason is generated from these facts, not from the AI's opinion.

## 3. Human in the loop

A person acts at these points:
1. **Extraction check:** low-confidence or unquoted fields are highlighted for the reviewer to confirm or correct.
2. **Ineligible list:** shown with the reason. The reviewer can reinstate a bid (for example if the bidder clarifies).
3. **Flagged list:** missing data or suspicious text. The reviewer decides to request clarification, accept, or exclude.
4. **Override:** any score or status can be changed with a required comment. Code re-ranks.
5. **Final award decision:** made by a person only. The tool recommends nothing beyond the ranked list.

**Audit log:** file hash, model and prompt versions, criteria version, extracted values and quotes, every flag, every score and formula input, overrides (who, when, old value, new value, comment), and the final decision. The log is append-only.

## 4. Changing criteria

- Criteria are versioned. A version that has been used for scoring is never edited. An edit creates a new version, and weights must sum to 100 (checked by code).
- Existing results stay labelled "scored under v1". The screen shows a notice that v2 exists. Nothing is silently re-scored and versions are never mixed in one ranking.
- Re-scoring is a new run under v2. It is cheap because stored extraction is reused. The AI is called again only if v2 needs a field that was never extracted.
- The reviewer sees v1 and v2 rankings side by side. Earlier overrides are shown and must be re-confirmed, since they were made under v1. An award decision stays linked to the version it was made under.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| Wrong extraction (misread number, bad PDF text) | Quote required and verified in code, schema and range checks, scanned PDFs flagged for OCR check, reviewer sees the quote beside the value |
| Made-up facts | "Not stated" is an allowed answer; no quote means no value; the AI never produces numbers that affect the score |
| Bias (company name, style, length) | Scored against the admin's rubric only, with an explicit checklist; reviewers can audit every reason |
| Manipulation / prompt injection | Proposal text is treated as untrusted data in a separate block; the AI is told to report, not obey, instructions inside it; a code-side pattern scan adds a second check; flagged proposals are scored on content only, never rewarded, and a human decides what to do. One sample proposal contains such a note, which is handled this way. |
| Gaming by missing info (leaving out a bad fact) | Missing data is flagged for clarification, not scored as a pass |
| Cost | Cache extraction, use a smaller model for extraction, cap pages and tokens per file, re-score without new AI calls |
| Model drift | Pinned versions; a fixed test set is re-run before any model or prompt change |

## Sample set result

- **A: rank 1 (96.5). E: rank 2 (85.7).**
- **B: ineligible.** Licensed electrical work is only promised after award: a mandatory fail, even though B is cheapest.
- **D: flagged.** No completion time, so the 16-week limit cannot be checked. Provisional score about 72.
- **C: flagged.** Contains a note aimed at automated reviewers, ignored. Real content scores 83.3 (3rd if cleared).

## Assumptions

- "Last 5 years" counts from the review date. C's count starts earlier and may include older installs, so it is marked low confidence.
- Price and timeline scores are relative to the best eligible bid, so the pool used is recorded in the audit log.
- Missing timeline is "flagged", not "ineligible", because it is not one of the admin's mandatory criteria.
