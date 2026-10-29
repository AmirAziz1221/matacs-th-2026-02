"""Rule-based half of the pipeline: gate, completeness check, formula scores,
weighted sum, ranking. No AI is used here, so the same input always gives the same output.

Usage:  python scoring.py example_extracted.json
"""
import json
import sys

WEIGHTS = {"experience": 30, "price": 25, "timeline": 15, "warranty": 15, "team": 15}
BUDGET_CAD = 260_000
MAX_WEEKS = 16
# Experience bands: (minimum qualifying installs, score out of 10)
EXPERIENCE_BANDS = [(12, 10), (9, 8), (6, 6), (3, 4), (1, 2), (0, 0)]
# Team checklist points (out of 10)
TEAM_POINTS = {"named_lead": 3, "crew_stated": 2, "safety_plan": 2, "monitoring_plan": 2, "extra_item": 1}


def experience_score(count):
    for minimum, score in EXPERIENCE_BANDS:
        if count >= minimum:
            return score


def team_score(checklist):
    return sum(pts for key, pts in TEAM_POINTS.items() if checklist.get(key))


def check_status(e):
    """Return (status, reason). status: ok | ineligible | flagged."""
    for field, label in [("licence_held_by_bidder", "Ontario electrical licence"),
                         ("wsib_clearance", "WSIB clearance"),
                         ("insurance_5m", "$5M liability insurance")]:
        if e.get(field) == "no":
            return "ineligible", f"Fails mandatory criterion: {label} not held/confirmed by the bidder"
    unclear = [l for f, l in [("licence_held_by_bidder", "licence"), ("wsib_clearance", "WSIB"),
                              ("insurance_5m", "insurance")] if e.get(f) != "yes"]
    if unclear:
        return "flagged", f"Mandatory item unclear: {', '.join(unclear)}; needs human check"
    if e.get("price_cad") is not None and e["price_cad"] > BUDGET_CAD:
        return "ineligible", "Price is above the budget ceiling"
    if e.get("completion_weeks") is not None and e["completion_weeks"] > MAX_WEEKS:
        return "ineligible", "Completion time is longer than 16 weeks"
    missing = [k for k in ("price_cad", "completion_weeks", "panel_warranty_years",
                           "workmanship_warranty_years", "qualifying_installs") if e.get(k) is None]
    if missing:
        return "flagged", f"Missing information ({', '.join(missing)}); needs clarification from bidder"
    if e.get("injection_flags"):
        return "flagged", "Contains text aimed at the AI reviewer; ignored and scored on content only"
    return "ok", ""


def score_all(proposals):
    """Score every proposal that passed the mandatory gate (flagged ones get a score too)."""
    pool = [p for p in proposals if check_status(p)[0] != "ineligible"]
    prices = [p["price_cad"] for p in pool if p.get("price_cad")]
    weeks = [p["completion_weeks"] for p in pool if p.get("completion_weeks")]
    lowest_price, shortest = min(prices), min(weeks)
    out = {}
    for p in pool:
        s = {}
        s["experience"] = experience_score(p.get("qualifying_installs") or 0)
        s["price"] = 10 * lowest_price / p["price_cad"] if p.get("price_cad") else 0
        s["timeline"] = 10 * shortest / p["completion_weeks"] if p.get("completion_weeks") else 0
        panel = min(p.get("panel_warranty_years") or 0, 25) / 25 * 10
        work = min(p.get("workmanship_warranty_years") or 0, 12) / 12 * 10
        s["warranty"] = (panel + work) / 2
        s["team"] = team_score(p.get("team_checklist", {}))
        total = sum(s[k] * WEIGHTS[k] / 10 for k in WEIGHTS)
        out[p["proposal"]] = {"criterion_scores": {k: round(v, 2) for k, v in s.items()},
                              "total": round(total, 1)}
    return out


def rank(proposals):
    scores = score_all(proposals)
    rows = []
    for p in proposals:
        status, reason = check_status(p)
        sc = scores.get(p["proposal"])
        if status == "ok":
            rows.append({"proposal": p["proposal"], "status": "ranked", "score": sc["total"],
                         "reason": "", "_tb": (-sc["total"], -sc["criterion_scores"]["experience"], p["price_cad"])})
        elif status == "flagged":
            missing_data = "Missing information" in reason
            rows.append({"proposal": p["proposal"], "rank": None, "status": "flagged",
                         "score": None if missing_data else sc["total"], "reason": reason,
                         "provisional_score": sc["total"] if sc else None})
        else:
            rows.append({"proposal": p["proposal"], "rank": None, "status": "ineligible",
                         "score": None, "reason": reason})
    ranked = sorted([r for r in rows if r["status"] == "ranked"], key=lambda r: r["_tb"])
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
        del r["_tb"]
    return ranked + [r for r in rows if r["status"] != "ranked"], scores


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    result, detail = rank(data)
    print(json.dumps(result, indent=1))
    print(json.dumps(detail, indent=1))
