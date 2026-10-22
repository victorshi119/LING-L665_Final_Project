"""
scrape_pubmed.py

Collect PubMed papers (metadata, abstracts, open-access PDFs) for the
CP-associated spastic dysarthria corpus, using the arXiv query set
rewritten in PubMed syntax.

Usage: PUBMED_CONTACT=you@iu.edu python3 scrape_pubmed.py [N_PER_QUERY] [OUT_DIR]
    N_PER_QUERY  top hits per query by PubMed relevance (default 50)
    OUT_DIR      default ./pubmed_dysarthria
Needs the third-party package "requests".
"""

import csv, os, re, sys, time
import xml.etree.ElementTree as ET
import requests

OUT = sys.argv[2] if len(sys.argv) > 2 else "pubmed_dysarthria"
PDF_DIR = os.path.join(OUT, "pdfs")
RETMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 50
EMAIL = os.environ.get("PUBMED_CONTACT")  # NCBI/OpenAlex ask for a contact email
if not EMAIL:
    sys.exit("Set PUBMED_CONTACT to your email, e.g. PUBMED_CONTACT=you@iu.edu python3 scrape_pubmed.py")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
S3 = "https://pmc-oa-opendata.s3.amazonaws.com"

QUERIES = {
    "dysarthria": "dysarthria",
    "dysarthric": "dysarthric",
    "cerebral_palsy": '"cerebral palsy"',
    "cp_speech": '"cerebral palsy" AND (speech OR dysarthria OR dysarthric)',
    "spastic_speech": "spastic AND (speech OR dysarthria)",
    "motor_speech_disorder": '"motor speech disorder" OR "motor speech disorders"',
    "dysarthric_corpora": "UASpeech[tiab] OR TORGO[tiab]",
}

s = requests.Session()
s.headers["User-Agent"] = f"pubmed-oa-fetch/1.0 (mailto:{EMAIL})"


def get(url, **kw):
    for attempt in range(3):
        try:
            r = s.get(url, timeout=60, **kw)
            if r.status_code == 429:
                time.sleep(2 + attempt * 3)
                continue
            return r
        except requests.RequestException:
            time.sleep(2)
    return None


# 1. Search
hits, counts = {}, {}
for name, q in QUERIES.items():
    r = get(f"{EUTILS}/esearch.fcgi", params=dict(db="pubmed", term=q, retmax=RETMAX,
            sort="relevance", retmode="json", email=EMAIL, tool="pubmed-oa-fetch"))
    res = r.json()["esearchresult"]
    counts[name] = int(res["count"])
    for pmid in res["idlist"]:
        hits.setdefault(pmid, []).append(name)
    print(f"{name}: {counts[name]} total hits, took {len(res['idlist'])}")
    time.sleep(0.4)
print(f"Unique PMIDs: {len(hits)}")

# 2. Metadata
def text(el):
    return "".join(el.itertext()).strip() if el is not None else ""

records = []
pmids = list(hits)
for i in range(0, len(pmids), 200):
    r = get(f"{EUTILS}/efetch.fcgi", params=dict(db="pubmed", id=",".join(pmids[i:i+200]),
            retmode="xml", email=EMAIL, tool="pubmed-oa-fetch"))
    root = ET.fromstring(r.content)
    for art in root.findall("./PubmedArticle") + root.findall("./PubmedBookArticle"):
        pmid = text(art.find(".//PMID"))
        ids = {a.get("IdType"): text(a) for a in art.findall("./PubmedData/ArticleIdList/ArticleId")
               + art.findall("./PubmedBookData/ArticleIdList/ArticleId")}
        authors = []
        for a in art.findall(".//AuthorList/Author"):
            if a.find("LastName") is not None:
                authors.append(f"{text(a.find('LastName'))}, {text(a.find('ForeName'))}".strip(", "))
            elif a.find("CollectiveName") is not None:
                authors.append(text(a.find("CollectiveName")))
        year = text(art.find(".//PubDate/Year")) or text(art.find(".//PubDate/MedlineDate"))[:4]
        records.append(dict(
            pmid=pmid, pmcid=ids.get("pmc", ""), doi=ids.get("doi", ""),
            title=text(art.find(".//ArticleTitle")) or text(art.find(".//BookTitle")),
            authors="; ".join(authors), year=year,
            journal=text(art.find(".//Journal/Title")) or text(art.find(".//Book/BookTitle")),
            abstract=" ".join(text(a) for a in art.findall(".//Abstract/AbstractText")),
            matched_queries="; ".join(hits[pmid]),
        ))
    time.sleep(0.4)

# 3. PDFs
os.makedirs(PDF_DIR, exist_ok=True)

def try_pdf(url, path):
    r = get(url, allow_redirects=True)
    if r is not None and r.status_code == 200 and r.content[:5] == b"%PDF-":
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    return False

for n, rec in enumerate(records, 1):
    path = os.path.join(PDF_DIR, f"PMID{rec['pmid']}.pdf")
    rec["pdf_status"], rec["pdf_source"], rec["oa_status"] = "not found", "", ""
    if os.path.exists(path):
        rec["pdf_status"], rec["pdf_source"] = "downloaded", "existing file"
        continue
    candidates = []
    if rec["pmcid"]:
        # PMC Open Access subset on AWS (official bulk route; the PMC/EuropePMC sites block scripts)
        ls = get(S3, params={"list-type": "2", "prefix": rec["pmcid"] + "."})
        if ls is not None and ls.status_code == 200:
            keys = sorted(re.findall(r"<Key>([^<]+\.pdf)</Key>", ls.text),
                          key=lambda k: int(re.search(r"\.(\d+)/", k).group(1)), reverse=True)
            if keys:
                candidates.append(("PMC OA (AWS)", f"{S3}/{keys[0]}"))
    oa = get(f"https://api.openalex.org/works/pmid:{rec['pmid']}", params={"mailto": EMAIL})
    if oa is not None and oa.status_code == 200:
        w = oa.json()
        rec["oa_status"] = (w.get("open_access") or {}).get("oa_status", "")
        locs = [w.get("best_oa_location")] + (w.get("locations") or [])
        for loc in locs:
            if loc and loc.get("pdf_url") and loc.get("is_oa"):
                src = ((loc.get("source") or {}).get("display_name") or "OpenAlex")
                candidates.append((f"OpenAlex: {src}", loc["pdf_url"]))
    seen = set()
    for src, url in candidates:
        if url in seen:
            continue
        seen.add(url)
        if try_pdf(url, path):
            rec["pdf_status"], rec["pdf_source"] = "downloaded", src
            break
    if rec["pdf_status"] != "downloaded" and rec["oa_status"] == "closed":
        rec["pdf_status"] = "paywalled"
    print(f"[{n}/{len(records)}] PMID{rec['pmid']}: {rec['pdf_status']} {rec['pdf_source']}")
    time.sleep(0.2)

# 4. Outputs
fields = ["pmid", "pmcid", "doi", "title", "authors", "year", "journal", "matched_queries",
          "oa_status", "pdf_status", "pdf_source", "abstract"]
with open(os.path.join(OUT, "results.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(records)

with open(os.path.join(OUT, "no_pdf.ris"), "w", encoding="utf-8") as f:
    for rec in records:
        if rec["pdf_status"] == "downloaded":
            continue
        f.write("TY  - JOUR\n")
        for a in rec["authors"].split("; "):
            if a:
                f.write(f"AU  - {a}\n")
        f.write(f"TI  - {rec['title']}\nJO  - {rec['journal']}\nPY  - {rec['year']}\n")
        if rec["doi"]:
            f.write(f"DO  - {rec['doi']}\n")
        f.write(f"AN  - PMID:{rec['pmid']}\nAB  - {rec['abstract']}\nER  - \n\n")

print("\nTotal hits per query:", counts)
st = {}
for rec in records:
    st[rec["pdf_status"]] = st.get(rec["pdf_status"], 0) + 1
print("PDF status:", st)
