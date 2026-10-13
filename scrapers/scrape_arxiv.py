#!/usr/bin/env python3

"""
scrape_arxiv.py

Collect arXiv papers for the CP-associated spastic dysarthria corpus.

Runs a set of named queries against the arXiv API, merges the hits by arXiv
id, and records which queries matched each paper so the corpus can later be
narrowed (e.g. to papers that mention cerebral palsy) without re-scraping.
Optionally looks up each paper's license via OAI-PMH and downloads PDFs.

Standard library only; needs Python >= 3.8 (module load python/3.12.11).

Output layout in OUT_DIR:
    metadata.jsonl   one JSON record per paper
    pdfs/<id>.pdf    with --pdfs ("/" in old-style ids becomes "_")
    manifest.json    queries, counts and timestamp of the last run

Re-running is safe: papers already in metadata.jsonl keep their record
(new query matches are merged in) and existing PDFs are not re-downloaded.

arXiv asks for at most one request every 3 seconds:
https://info.arxiv.org/help/api/tou.html
"""


import argparse
import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API_URL = "https://export.arxiv.org/api/query"
OAI_URL = "https://oaipmh.arxiv.org/oai"
PAGE_SIZE = 100

NS = {"atom": "http://www.w3.org/2005/Atom",
      "arxiv": "http://arxiv.org/schemas/atom",
      "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
      "oai": "http://www.openarchives.org/OAI/2.0/",
      "oai_arxiv": "http://arxiv.org/OAI/arXiv/"}


class Client:
    """HTTP client that enforces arXiv's delay between requests."""

    def __init__(self, delay, contact):
        self.delay = delay
        self.last = 0.0
        agent = "L665-corpus-scraper/1.0"
        self.headers = {"User-Agent": f"{agent} (mailto:{contact})" if contact else agent}

    def get(self, url, attempts=4):
        for attempt in range(attempts):
            wait = self.last + self.delay - time.time()
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            try:
                request = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(request, timeout=60) as response:
                    return response.read()
            except Exception as error:
                if attempt == attempts - 1:
                    raise
                log(f"  request failed ({error}), retrying")
                time.sleep(5 * 2 ** attempt)


def log(message):
    print(message, file=sys.stderr, flush=True)


def text(node, path):
    found = node.find(path, NS)
    return " ".join(found.text.split()) if found is not None and found.text else None


def parse_entry(entry):
    """Turn one Atom <entry> into a metadata record."""
    abs_url = text(entry, "atom:id")
    versioned = abs_url.split("/abs/")[-1]
    arxiv_id, _, version = versioned.rpartition("v")
    if not arxiv_id or not version.isdigit():
        arxiv_id, version = versioned, None
    pdf_url = next((link.get("href") for link in entry.findall("atom:link", NS)
                    if link.get("title") == "pdf"), None)
    primary = entry.find("arxiv:primary_category", NS)
    return {"arxiv_id": arxiv_id,
            "version": f"v{version}" if version else None,
            "title": text(entry, "atom:title"),
            "abstract": text(entry, "atom:summary"),
            "authors": [text(a, "atom:name") for a in entry.findall("atom:author", NS)],
            "published": text(entry, "atom:published"),
            "updated": text(entry, "atom:updated"),
            "primary_category": primary.get("term") if primary is not None else None,
            "categories": [c.get("term") for c in entry.findall("atom:category", NS)],
            "doi": text(entry, "arxiv:doi"),
            "journal_ref": text(entry, "arxiv:journal_ref"),
            "comment": text(entry, "arxiv:comment"),
            "abs_url": abs_url,
            "pdf_url": pdf_url,
            "license": None,
            "matched_queries": []}


def search(client, query, limit):
    """Yield all entries for one query, paging through the API."""
    start, total = 0, None
    empty_retries = 0
    while total is None or start < min(total, limit):
        params = urllib.parse.urlencode({"search_query": query, "start": start,
                                         "max_results": min(PAGE_SIZE, limit - start),
                                         "sortBy": "submittedDate", "sortOrder": "ascending"})
        feed = ET.fromstring(client.get(f"{API_URL}?{params}"))
        total = int(text(feed, "opensearch:totalResults") or 0)
        entries = feed.findall("atom:entry", NS)
        # The API occasionally returns an empty page mid-query; retry it.
        if not entries and start < total:
            empty_retries += 1
            if empty_retries > 3:
                log(f"  giving up at {start}/{total}: repeated empty pages")
                return
            continue
        empty_retries = 0
        for entry in entries:
            yield parse_entry(entry)
        start += len(entries)
        log(f"  {start}/{min(total, limit)}")


def fetch_license(client, arxiv_id):
    params = urllib.parse.urlencode({"verb": "GetRecord", "metadataPrefix": "arXiv",
                                     "identifier": f"oai:arXiv.org:{arxiv_id}"})
    record = ET.fromstring(client.get(f"{OAI_URL}?{params}"))
    return text(record, ".//oai_arxiv:license")


def load_existing(path):
    records = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fp:
            for line in fp:
                if line.strip():
                    record = json.loads(line)
                    records[record["arxiv_id"]] = record
    return records


def write_records(path, records):
    temp = path + ".tmp"
    with open(temp, encoding="utf-8", mode="w") as fp:
        for record in sorted(records.values(), key=lambda r: r["arxiv_id"]):
            fp.write(json.dumps(record, ensure_ascii=False) + "\n")
    os.replace(temp, path)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument("out_dir", help="output directory, e.g. data/raw/arxiv")
    parser.add_argument("--queries", default=os.path.join(here, "arxiv_queries.json"),
                        help="JSON file mapping query names to arXiv search_query strings")
    parser.add_argument("--only", nargs="+", metavar="NAME", help="run only these named queries")
    parser.add_argument("--max-per-query", type=int, default=10000)
    parser.add_argument("--licenses", action="store_true", help="look up licenses via OAI-PMH")
    parser.add_argument("--pdfs", action="store_true", help="download PDFs")
    parser.add_argument("--delay", type=float, default=3.0, help="seconds between requests (>= 3)")
    parser.add_argument("--contact", default=os.environ.get("ARXIV_CONTACT"),
                        help="email for the User-Agent (default: $ARXIV_CONTACT)")
    args = parser.parse_args()

    with open(args.queries, encoding="utf-8") as fp:
        queries = json.load(fp)
    if args.only:
        unknown = set(args.only) - set(queries)
        if unknown:
            parser.error(f"unknown query names: {', '.join(sorted(unknown))}")
        queries = {name: queries[name] for name in args.only}

    client = Client(max(args.delay, 3.0), args.contact)
    os.makedirs(args.out_dir, exist_ok=True)
    meta_path = os.path.join(args.out_dir, "metadata.jsonl")
    records = load_existing(meta_path)
    log(f"{len(records)} papers already in {meta_path}")

    hits = {}
    for name, query in queries.items():
        log(f"query '{name}': {query}")
        ids = set()
        for record in search(client, query, args.max_per_query):
            ids.add(record["arxiv_id"])
            known = records.setdefault(record["arxiv_id"], record)
            if known is not record:
                # Keep the newest metadata but preserve looked-up fields.
                record["license"] = known.get("license")
                record["matched_queries"] = known.get("matched_queries", [])
                records[record["arxiv_id"]] = known = record
            if name not in known["matched_queries"]:
                known["matched_queries"].append(name)
        hits[name] = len(ids)
        log(f"  -> {len(ids)} papers")
        write_records(meta_path, records)

    if args.licenses:
        missing = [r for r in records.values() if not r.get("license")]
        log(f"looking up {len(missing)} licenses")
        for i, record in enumerate(missing, 1):
            try:
                record["license"] = fetch_license(client, record["arxiv_id"]) or "arxiv-default"
            except Exception as error:
                log(f"  license lookup failed for {record['arxiv_id']}: {error}")
            if i % 25 == 0:
                log(f"  {i}/{len(missing)}")
                write_records(meta_path, records)
        write_records(meta_path, records)

    failed_pdfs = []
    if args.pdfs:
        pdf_dir = os.path.join(args.out_dir, "pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        todo = [r for r in records.values() if r.get("pdf_url")
                and not os.path.exists(os.path.join(pdf_dir, r["arxiv_id"].replace("/", "_") + ".pdf"))]
        log(f"downloading {len(todo)} PDFs")
        for i, record in enumerate(todo, 1):
            target = os.path.join(pdf_dir, record["arxiv_id"].replace("/", "_") + ".pdf")
            try:
                body = client.get(record["pdf_url"])
                if not body.startswith(b"%PDF"):
                    raise ValueError("response is not a PDF")
                with open(target + ".part", mode="wb") as fp:
                    fp.write(body)
                os.replace(target + ".part", target)
            except Exception as error:
                log(f"  PDF failed for {record['arxiv_id']}: {error}")
                failed_pdfs.append(record["arxiv_id"])
            if i % 25 == 0:
                log(f"  {i}/{len(todo)}")

    manifest = {"source": "arXiv API (export.arxiv.org/api/query)",
                "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "queries": queries,
                "hits_per_query": hits,
                "total_papers": len(records),
                "with_license": sum(1 for r in records.values() if r.get("license")),
                "failed_pdfs": failed_pdfs}
    with open(os.path.join(args.out_dir, "manifest.json"), encoding="utf-8", mode="w") as fp:
        json.dump(manifest, fp, indent=3)
    log(f"done: {len(records)} papers in {meta_path}")


if __name__ == "__main__":
    main()
