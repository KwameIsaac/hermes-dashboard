#!/usr/bin/env python3
import json, os
from datetime import datetime

STATE_DIR = os.path.expanduser("~/.hermes/state")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "template.html")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "index.html")

def load_projects():
    projects = []
    for entry in os.listdir(STATE_DIR):
        state_file = os.path.join(STATE_DIR, entry, "active_state.json")
        if not os.path.isfile(state_file): continue
        with open(state_file) as f:
            data = json.load(f)
        triad = {}
        for t in data.get("registers", {}).get("\u00a73", {}).get("entries", []):
            triad[t["key"]] = t["value"]
        decisions = data.get("registers", {}).get("\u00a78", {}).get("entries", [])
        mechanisms = data.get("registers", {}).get("\u00a72", {}).get("entries", [])
        debt = data.get("registers", {}).get("\u00a77", {}).get("entries", [])
        conventions = data.get("registers", {}).get("\u00a79", {}).get("entries", [])
        audit_log = data.get("audit_log", [])
        projects.append({
            "id": data.get("project_id", entry), "name": data.get("project_name", entry),
            "cycle": data.get("active_cycle", "?"), "status": triad.get("Status", "Unknown"),
            "challenge": triad.get("Presenting Challenge", "None set"),
            "awaiting": triad.get("Awaiting", "Unknown"),
            "decisions": [{"id": d.get("id",""), "title": d.get("content",{}).get("title",""), "rationale": d.get("content",{}).get("rationale","")} for d in decisions],
            "mechanisms": [{"id": m.get("id",""), "name": m.get("content",{}).get("name",""), "description": m.get("content",{}).get("description","")} for m in mechanisms],
            "debt": [{"id": d.get("id",""), "description": d.get("content",{}).get("description","")} for d in debt],
            "conventions": [{"id": c.get("id",""), "text": c.get("content",{}).get("rule_text","")} for c in conventions],
            "audit_count": len(audit_log),
            "updated": audit_log[-1].get("timestamp", "") if audit_log else "",
        })
    return sorted(projects, key=lambda p: p["name"])

def build():
    projects = load_projects()
    data = {"generated": datetime.utcnow().isoformat() + "Z", "projects": projects}
    with open(TEMPLATE_PATH) as f: html = f.read()
    html = html.replace("DASHBOARD_DATA_PLACEHOLDER", json.dumps(data, indent=2))
    with open(OUTPUT_PATH, "w") as f: f.write(html)
    print(f"✓ Built {OUTPUT_PATH} — {len(projects)} projects")

if __name__ == "__main__": build()
