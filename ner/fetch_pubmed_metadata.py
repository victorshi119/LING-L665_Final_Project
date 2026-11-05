#!/usr/bin/env python
"""
Download source metadata for the PubMed papers in the read-only corpus folder.

  NCBI E-utilities esummary -> sources_raw/pubmed_esummary.json
      (title, journal, publication date, DOI, PMCID)
  Europe PMC REST search    -> sources_raw/europepmc_licenses.json
      (license, open-access flag, journal)

Both services are public and need no API key; requests are rate-limited.
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBMED_DIR = Path("/N/project/ontology_learning/L665/data/CP_Dysarthria/Pubmed")  # read-only input
OUT = HERE / "sources_raw"


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.load(response)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pmids = sorted(path.stem.removeprefix("PMID") for path in PUBMED_DIR.glob("PMID*.md"))
    print(f"{len(pmids)} PMIDs")

    summary = get_json(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&id={','.join(pmids)}&retmode=json"
    )
    (OUT / "pubmed_esummary.json").write_text(json.dumps(summary, indent=1))

    licenses = {}
    for pmid in pmids:
        results = get_json(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            f"?query=EXT_ID:{pmid}%20AND%20SRC:MED&resultType=core&format=json"
        )["resultList"]["result"]
        record = results[0] if results else {}
        licenses[pmid] = {
            "license": record.get("license", ""),
            "isOpenAccess": record.get("isOpenAccess", ""),
            "journal": record.get("journalInfo", {}).get("journal", {}).get("title", ""),
        }
        time.sleep(0.2)
    (OUT / "europepmc_licenses.json").write_text(json.dumps(licenses, indent=1))
    print("Wrote", OUT / "pubmed_esummary.json", "and", OUT / "europepmc_licenses.json")


if __name__ == "__main__":
    main()
