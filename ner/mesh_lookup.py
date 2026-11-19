#!/usr/bin/env python
"""Look up MeSH descriptors (ID, scope note, entry terms) for glossary candidates
via NCBI E-utilities; writes sources_raw/mesh_records.json for glossary drafting."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent / "sources_raw" / "mesh_records.json"
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)

def lookup(term):
    q = urllib.parse.quote(f'"{term}"[MeSH Terms]')
    ids = get(f"{E}esearch.fcgi?db=mesh&term={q}&retmode=json")["esearchresult"]["idlist"]
    time.sleep(0.4)
    if not ids:
        return None
    rec = get(f"{E}esummary.fcgi?db=mesh&id={ids[0]}&retmode=json")["result"][ids[0]]
    time.sleep(0.4)
    ui = rec.get("ds_meshui", "")
    return {"query": term, "mesh_ui": ui, "heading": rec.get("ds_meshterms", [""])[0],
            "entry_terms": rec.get("ds_meshterms", []), "scope_note": rec.get("ds_scopenote", "").strip(),
            "url": f"https://meshb.nlm.nih.gov/record/ui?ui={ui}"}

if __name__ == "__main__":
    terms = [line.strip() for line in sys.stdin if line.strip()]
    records = json.loads(OUT.read_text()) if OUT.exists() else {}
    for t in terms:
        records[t] = lookup(t)
        r = records[t]
        print(f"{t:45} -> {r['mesh_ui'] + ' ' + r['heading'] if r else 'NOT FOUND'}")
    OUT.write_text(json.dumps(records, indent=1))
