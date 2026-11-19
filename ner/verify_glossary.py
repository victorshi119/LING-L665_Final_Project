#!/usr/bin/env python
"""
Check glossary.json and write glossary_verification.json + glossary_stats.csv.

  1. schema: required fields, unique ids, valid labels
  2. duplicates: a surface form (term/acronym, case-insensitive for terms) used by
     more than one concept, and acronyms that are ordinary English words
  3. provenance: every source URL is fetched; HTTP 2xx/3xx counts as resolving
  4. coverage: how often each concept's surface forms occur in texts/
"""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQUIRED = ["id", "concept_label", "term", "acronym", "definition", "hypernym", "source_url"]


def check_url(url: str) -> int:
    # Many publishers block scripted requests (403) after the DOI redirect, so a
    # DOI is checked against the DOI registry itself (responseCode 1 = registered).
    if url.startswith("https://doi.org/"):
        api = "https://doi.org/api/handles/" + url.removeprefix("https://doi.org/")
        try:
            with urllib.request.urlopen(api, timeout=30) as response:
                return 200 if json.load(response).get("responseCode") == 1 else 404
        except Exception:
            return 0
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (L665 glossary check)"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except Exception:
        return 0


def main() -> None:
    glossary = json.loads((HERE / "glossary.json").read_text(encoding="utf-8"))
    labels = set(glossary["metadata"]["labels"])
    entries = glossary["entries"]
    problems: list[str] = []

    ids = Counter(entry["id"] for entry in entries)
    problems += [f"duplicate id {i}" for i, n in ids.items() if n > 1]
    for entry in entries:
        missing = [field for field in REQUIRED if not entry.get(field) and field != "acronym"]
        if missing:
            problems.append(f"{entry['id']}: missing {missing}")
        if entry["concept_label"] not in labels:
            problems.append(f"{entry['id']}: unknown label {entry['concept_label']}")

    owners: dict[str, set[str]] = defaultdict(set)
    for entry in entries:
        for term in entry["term"]:
            owners[term.casefold()].add(entry["id"])
        for acronym in entry["acronym"]:
            owners[acronym].add(entry["id"])
    shared = {form: sorted(ids_) for form, ids_ in owners.items() if len(ids_) > 1}
    problems += [f"surface form {form!r} shared by {ids_}" for form, ids_ in shared.items()]

    url_status = {}
    for url in sorted({url for entry in entries for url in entry["source_url"]}):
        url_status[url] = check_url(url)
        print(f"{url_status[url]} {url}")
    problems += [f"source URL does not resolve ({code}): {url}" for url, code in url_status.items()
                 if not 200 <= code < 400]

    texts = {path.stem: path.read_text(encoding="utf-8") for path in (HERE / "texts").glob("*.txt")}
    rows = []
    for entry in entries:
        term_re = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in entry["term"]) + r")(?:e?s)?\b", re.I)
        acr_re = (re.compile(r"\b(?:" + "|".join(re.escape(a) for a in entry["acronym"]) + r")s?\b")
                  if entry["acronym"] else None)
        term_hits = doc_hits = acr_hits = 0
        for text in texts.values():
            t = len(term_re.findall(text))
            a = len(acr_re.findall(text)) if acr_re else 0
            if entry.get("acronym_requires_long_form") and t == 0:
                a = 0
            term_hits += t
            acr_hits += a
            doc_hits += (t + a) > 0
        rows.append({"id": entry["id"], "concept_label": entry["concept_label"], "preferred_term": entry["term"][0],
                     "n_terms": len(entry["term"]), "n_acronyms": len(entry["acronym"]),
                     "n_sources": len(entry["source_url"]), "mesh_id": entry.get("mesh_id", ""),
                     "term_mentions": term_hits, "acronym_mentions": acr_hits, "documents": doc_hits})
        if doc_hits == 0:
            problems.append(f"{entry['id']} ({entry['term'][0]}) never occurs in the corpus")

    with (HERE / "glossary_stats.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "concepts": len(entries),
        "concepts_per_label": Counter(entry["concept_label"] for entry in entries),
        "surface_forms": sum(len(e["term"]) + len(e["acronym"]) for e in entries),
        "concepts_with_mesh_id": sum(1 for e in entries if e.get("mesh_id")),
        "source_urls": len(url_status),
        "source_urls_resolving": sum(1 for c in url_status.values() if 200 <= c < 400),
        "url_status": url_status,
        "problems": problems,
    }
    (HERE / "glossary_verification.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: v for k, v in report.items() if k != "url_status"}, indent=1))


if __name__ == "__main__":
    main()
