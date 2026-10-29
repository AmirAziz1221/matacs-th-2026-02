"""Optional prototype: runs the two prompts in PROMPTS.md on local proposal text files,
then uses scoring.py (plain rules) to produce a ranking.

Setup:   pip install -r requirements.txt ; copy .env.example to .env and add your key
Samples: put plain-text files named A.txt ... E.txt in prototype/samples/ (this folder is git-ignored,
         because sample proposal text must not be published in the repository)
Run:     python run.py
"""
import json
import os
import pathlib
import re

from anthropic import Anthropic
from dotenv import load_dotenv

import scoring

ROOT = pathlib.Path(__file__).parent
load_dotenv(ROOT / ".env")
MODEL = os.getenv("MODEL", "claude-sonnet-5-5")
CRITERIA = {
    "version": "v1", "min_install_kw": 100, "lookback_years": 5,
    "checklist_criterion": {"id": "team", "name": "Team and approach", "items": [
        {"id": "named_lead", "description": "Named project lead"},
        {"id": "crew_stated", "description": "Crew size or crew described"},
        {"id": "safety_plan", "description": "Site safety plan"},
        {"id": "monitoring_plan", "description": "Performance monitoring plan"},
        {"id": "extra_item", "description": "Other concrete delivery item"}]},
}


def load_prompts():
    text = (ROOT.parent / "PROMPTS.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```text\n(.*?)```", text, re.S)
    return blocks[0], blocks[2]  # extraction system prompt, checklist system prompt


def call(client, system, user):
    reply = client.messages.create(model=MODEL, max_tokens=1500, temperature=0,
                                   system=system, messages=[{"role": "user", "content": user}])
    raw = re.sub(r"^```(?:json)?|```$", "", reply.content[0].text.strip()).strip()
    return json.loads(raw)


def verify_quotes(data, source):
    """Drop evidence quotes that do not appear verbatim in the source; return list of problems."""
    problems = []
    for key, quote in list(data.get("evidence", {}).items()):
        if quote not in source:
            problems.append(f"quote for {key} not found in source")
            del data["evidence"][key]
    return problems


def main():
    client = Anthropic()
    extract_prompt, checklist_prompt = load_prompts()
    results = []
    for path in sorted((ROOT / "samples").glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        ext = call(client, extract_prompt,
                   f"<criteria>{json.dumps(CRITERIA)}</criteria>\n<proposal>{text}</proposal>")
        problems = verify_quotes(ext, text)
        chk = call(client, checklist_prompt,
                   f"<criterion>{json.dumps(CRITERIA['checklist_criterion'])}</criterion>\n<proposal>{text}</proposal>")
        ext["team_checklist"] = {i["id"]: bool(i["met"] and i.get("evidence") and i["evidence"] in text)
                                 for i in chk["items"]}
        ext["injection_flags"] = list(set(ext.get("injection_flags", []) + chk.get("injection_flags", [])))
        ext["proposal"] = path.stem
        ext["quote_problems"] = problems
        results.append(ext)
    ranking, detail = scoring.rank(results)
    print(json.dumps(ranking, indent=1))
    (ROOT / "output.json").write_text(json.dumps({"extracted": results, "scores": detail}, indent=1))


if __name__ == "__main__":
    main()
