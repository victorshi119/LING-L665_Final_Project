#!/usr/bin/env python3

"""
build_pubmed_corpus.py

Merge the PubMed scraper's results.csv with the Docling/spaCy Layout Markdown
and write one cleaned JSONL corpus plus summary statistics.

Cleaning is the same as for arXiv: clean() is imported from
build_arxiv_corpus.py, so this file must sit next to it. Only papers whose
PDF was downloaded are included; how many were not is in "pdf_status".

Usage (needs spaCy for token counts; the spacy-layout env has it):
    source envs/spacy-layout/bin/activate
    python code/processing/build_pubmed_corpus.py data/raw/pubmed data/processed
"""


import argparse
import collections
import csv
import datetime
import json
import sys
from pathlib import Path

import spacy

# python -I leaves this script's folder off sys.path; put it back for the import.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_arxiv_corpus import clean  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument("raw_dir", type=Path, help="scraper output (results.csv, pdfs/)")
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--name", default="pubmed_corpus", help="output file stem")
    args = parser.parse_args()

    with open(args.raw_dir / "results.csv", encoding="utf-8", newline="") as fp:
        papers = list(csv.DictReader(fp))

    tokenizer = spacy.blank("en").tokenizer
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{args.name}.jsonl"

    stats = collections.Counter()
    oa_status = collections.Counter()
    missing, flagged = [], []
    with open(out_path, encoding="utf-8", mode="w") as out:
        for paper in papers:
            if paper["pdf_status"] != "downloaded":
                continue
            md_path = args.raw_dir / "pdfs" / f"PMID{paper['pmid']}.md"
            if not md_path.exists():
                missing.append(paper["pmid"])
                continue
            text, removed_references = clean(md_path.read_text(encoding="utf-8"))
            n_tokens = len(tokenizer(text))
            lowered = text.lower()
            record = {"id": f"pubmed:{paper['pmid']}",
                      "source": "pubmed",
                      "pmid": paper["pmid"],
                      "pmcid": paper["pmcid"] or None,
                      "doi": paper["doi"] or None,
                      "title": paper["title"],
                      "abstract": paper["abstract"],
                      "authors": paper["authors"].split("; ") if paper["authors"] else [],
                      "year": paper["year"],
                      "journal": paper["journal"],
                      "oa_status": paper["oa_status"],
                      "pdf_source": paper["pdf_source"],
                      "url": f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/",
                      "matched_queries": paper["matched_queries"].split("; "),
                      "mentions_cerebral_palsy": "cerebral palsy" in lowered,
                      "mentions_dysarthria": "dysarthri" in lowered,
                      "references_removed": removed_references,
                      "n_replacement_chars": text.count("�"),
                      "n_chars": len(text),
                      "n_tokens": n_tokens,
                      "text": text}
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

            stats["documents"] += 1
            stats["tokens"] += n_tokens
            stats["chars"] += len(text)
            stats["mentions_cerebral_palsy"] += record["mentions_cerebral_palsy"]
            stats["mentions_dysarthria"] += record["mentions_dysarthria"]
            stats["references_removed"] += removed_references
            oa_status[paper["oa_status"]] += 1
            if record["n_replacement_chars"]:
                flagged.append({"pmid": paper["pmid"],
                                "n_replacement_chars": record["n_replacement_chars"]})

    summary = {"built": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               "corpus_file": out_path.name,
               "tokenizer": f"spaCy {spacy.__version__} blank('en')",
               **stats,
               "pdf_status": dict(collections.Counter(p["pdf_status"] for p in papers).most_common()),
               "oa_status": dict(oa_status.most_common()),
               "missing_markdown": missing,
               "with_replacement_chars": sorted(flagged, key=lambda f: -f["n_replacement_chars"])}
    with open(args.out_dir / f"{args.name}_stats.json", encoding="utf-8", mode="w") as fp:
        json.dump(summary, fp, indent=3)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("oa_status", "with_replacement_chars")}, indent=1))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
