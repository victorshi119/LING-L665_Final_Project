#!/usr/bin/env python
"""
Export the CP-dysarthria corpus as one UTF-8 .txt file per source document and
write the source list (sources.csv).

Inputs (read-only, collected earlier; see DATA/CORPUS.md):
  DATA/processed/arxiv_corpus.jsonl            cleaned arXiv papers (321)
  DATA/Pubmed/PMID*.md                         Docling conversions of PubMed papers (60)
  sources_raw/pubmed_esummary.json           NCBI E-utilities metadata for the PMIDs
  sources_raw/europepmc_licenses.json        Europe PMC license metadata for the PMIDs

Outputs:
  texts/<doc_id>.txt
  sources.csv
  sources_raw/near_duplicates.json           document pairs with high text overlap
"""

from __future__ import annotations

import csv
import html
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = Path("/N/project/ontology_learning/L665/data/CP_Dysarthria")  # read-only input
TEXTS = HERE / "texts"

ARXIV_ACCESSED = "2026-10-13"  # arxiv/manifest.json last_run

# PMIDs whose downloaded PDF is byte-identical to another PMID's PDF (the whole
# 2019 "Speech Disorders Classification System" supplement was saved for each
# article). Only the supplement's introduction, PMID 31221008, is kept.
IDENTICAL_PDF_OF = {"30987467": "31221008", "31221009": "31221008", "31221010": "31221008"}
# Different versions of one study (preprint vs. journal article, conference paper
# vs. its extension); kept, but assigned to the same split by build_corpus.py.
# The arXiv pair share 26% of their long sentences but fall under the containment
# threshold below; found with check_split_overlap.py.
SAME_STUDY_GROUPS = [["pubmed_39257968", "pubmed_40993520"], ["arxiv_1807.10948", "arxiv_1905.06533"]]

# Sections after which nothing is useful running text (cut everything from here on).
CUT_HEADINGS = re.compile(r"^(references?|bibliography|literature cited)\b", re.I)
# Back-matter sections that are dropped, but text after them is kept.
DROP_HEADINGS = re.compile(
    r"^(acknowledge?ments?|funding( sources| statement)?|author contributions?|"
    r"conflicts? of interest|competing interests?|declarations?|disclosure statement|"
    r"data availability( statement)?|ethics( statement| approval.*)?|statement of ethics|"
    r"supplementary (information|material.*|files)|abbreviations|consent for publication)\b",
    re.I,
)
COPYRIGHT_LINE = re.compile(
    r"(©|\bcopyright\b|all rights reserved|journals\.permissions|accepted manuscript)", re.I
)


def normalise(text: str) -> str:
    text = html.unescape(text).replace("<!-- image -->", "")
    return unicodedata.normalize("NFC", text)


def table_row_to_text(line: str) -> str | None:
    """Turn a Markdown table row into plain text; drop separator rows."""
    if re.fullmatch(r"\|[\s\-:|]*\|", line):
        return None
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    cells = [cell for cell in cells if cell]
    # Docling often repeats a merged cell across columns.
    deduped = [cell for i, cell in enumerate(cells) if i == 0 or cell != cells[i - 1]]
    return " ; ".join(deduped)


def clean_markdown(raw: str) -> str:
    lines = normalise(raw).splitlines()
    numbered = sum(1 for line in lines if re.fullmatch(r"\s*\d{1,4}\s*", line))
    manuscript = numbered > 20  # line-numbered accepted manuscript

    out: list[str] = []
    dropping = False
    for line in lines:
        stripped = line.strip()
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        heading = re.match(r"^#+\s*(.*)$", stripped)
        if heading:
            title = re.sub(r"^[\dIVX.\s]+", "", heading.group(1)).strip(" :")
            if CUT_HEADINGS.match(title):
                break
            dropping = bool(DROP_HEADINGS.match(title))
            if not dropping:
                out.append(title)
            continue
        if dropping:
            continue
        if COPYRIGHT_LINE.search(stripped) and len(stripped) < 400:
            continue
        if stripped.startswith("|"):
            row = table_row_to_text(stripped)
            if row:
                out.append(row)
            continue
        if manuscript:
            # Line numbers that Docling appended to the end of a text line.
            stripped = re.sub(r"\s+\d{1,4}$", "", stripped)
        stripped = re.sub(r"^- ", "", stripped)
        out.append(stripped)

    text = "\n".join(out)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def clean_arxiv_text(text: str) -> str:
    """The arXiv text is already cleaned; only flatten tables and headings."""
    out = []
    for line in normalise(text).splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            row = table_row_to_text(stripped)
            if row:
                out.append(row)
            continue
        out.append(re.sub(r"^#+\s*", "", stripped))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def shingles(text: str, n: int = 8) -> set[int]:
    words = re.findall(r"\w+", text.lower())
    return {hash(" ".join(words[i : i + n])) for i in range(0, max(0, len(words) - n), 3)}


def main() -> None:
    TEXTS.mkdir(exist_ok=True)
    rows: list[dict[str, object]] = []

    with (DATA / "processed" / "arxiv_corpus.jsonl").open(encoding="utf-8") as file:
        for line in file:
            paper = json.loads(line)
            doc_id = "arxiv_" + paper["arxiv_id"].replace("/", "_")
            text = clean_arxiv_text(paper["text"])
            (TEXTS / f"{doc_id}.txt").write_text(text, encoding="utf-8")
            rows.append(
                {
                    "doc_id": doc_id,
                    "source": "arXiv",
                    "title": " ".join(paper["title"].split()),
                    "year": paper["published"][:4],
                    "url": paper["url"],
                    "doi": paper.get("doi") or "",
                    "date_accessed": ARXIV_ACCESSED,
                    "license": paper["license"] or "arxiv-default",
                    "reuse_note": reuse_note(paper["license"] or ""),
                    "query_or_topic": ";".join(paper["matched_queries"]),
                    "original_file": f"arxiv/pdfs/{paper['arxiv_id'].replace('/', '_')}.pdf",
                    "text_file": f"texts/{doc_id}.txt",
                    "n_chars": len(text),
                    "n_words": len(text.split()),
                }
            )

    summary = json.loads((HERE / "sources_raw" / "pubmed_esummary.json").read_text())["result"]
    licenses = json.loads((HERE / "sources_raw" / "europepmc_licenses.json").read_text())
    for md_path in sorted((DATA / "Pubmed").glob("PMID*.md")):
        pmid = md_path.stem.removeprefix("PMID")
        if pmid in IDENTICAL_PDF_OF:
            continue
        meta = summary[pmid]
        ids = {a["idtype"]: a["value"] for a in meta["articleids"]}
        doc_id = f"pubmed_{pmid}"
        text = clean_markdown(md_path.read_text(encoding="utf-8"))
        (TEXTS / f"{doc_id}.txt").write_text(text, encoding="utf-8")
        license_ = licenses.get(pmid, {}).get("license") or "publisher copyright (no open license recorded)"
        accessed = datetime.fromtimestamp(
            md_path.with_suffix(".pdf").stat().st_mtime, tz=timezone.utc
        ).date().isoformat()
        rows.append(
            {
                "doc_id": doc_id,
                "source": "PubMed",
                "title": html.unescape(meta["title"]).rstrip("."),
                "year": meta["pubdate"][:4],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "doi": ids.get("doi", ""),
                "date_accessed": accessed,
                "license": license_,
                "reuse_note": reuse_note(license_),
                "query_or_topic": meta.get("fulljournalname", ""),
                "original_file": f"Pubmed/PMID{pmid}.pdf",
                "text_file": f"texts/{doc_id}.txt",
                "n_chars": len(text),
                "n_words": len(text.split()),
            }
        )

    # Near-duplicate check so that overlapping texts can be kept in one split.
    sigs = {row["doc_id"]: shingles((HERE / str(row["text_file"])).read_text()) for row in rows}
    ids_sorted = sorted(sigs)
    duplicates = []
    for i, a in enumerate(ids_sorted):
        for b in ids_sorted[i + 1 :]:
            union = len(sigs[a] | sigs[b])
            containment = len(sigs[a] & sigs[b]) / max(1, min(len(sigs[a]), len(sigs[b])))
            if union and containment > 0.2:
                duplicates.append({"a": a, "b": b, "containment": round(containment, 3)})
    groups = SAME_STUDY_GROUPS + [[pair["a"], pair["b"]] for pair in duplicates]
    (HERE / "sources_raw" / "near_duplicates.json").write_text(
        json.dumps(
            {"identical_pdf_dropped": IDENTICAL_PDF_OF, "pairs": duplicates, "split_groups": groups},
            indent=1,
        )
    )

    with (HERE / "sources.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} documents to {TEXTS}")
    print(f"Near-duplicate pairs: {duplicates}")


def reuse_note(license_: str) -> str:
    lic = license_.lower()
    if "nonexclusive" in lic or "arxiv-default" in lic or not lic:
        return "arXiv non-exclusive license: course research use only, do not redistribute"
    if "publisher" in lic:
        return "publisher copyright: course research use only, do not redistribute"
    if "nd" in lic.replace("cc by-", "").split("-") or "by-nc-nd" in lic:
        return "CC NoDerivatives: do not redistribute modified/annotated text; attribution required"
    if "nc" in lic:
        return "CC NonCommercial: non-commercial reuse with attribution"
    return "open license: reuse with attribution"


if __name__ == "__main__":
    main()
