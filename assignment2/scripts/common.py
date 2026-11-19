"""Shared paths, schema, and Turtle writing for Assignment 2."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = Path("/N/project/CoRSAL/L665_Assignment2_work")
TEXT_DIR = WORK / "texts"
MODEL_DIR = WORK / "model-best"
SOURCES = ROOT / "sources_sample.csv"

PREDICATES = {
    "has_feature": ("DISORDER", "SPEECH_FEATURE"),
    "measures": ("ASSESSMENT", "SPEECH_FEATURE"),
    "treats": ("TREATMENT", "DISORDER"),
    "evaluated_on": ("SPEECH_TECH", "DATASET"),
    "applied_to": ("SPEECH_TECH", "DISORDER"),
}

ENTITY_TYPES = sorted({side for pair in PREDICATES.values() for side in pair})


def slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return cleaned or "entity"


def load_sources(path: Path = SOURCES) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_text(doc_id: str) -> str:
    return (TEXT_DIR / f"{doc_id}.txt").read_text(encoding="utf-8")


def _rdf():
    from rdflib import Graph, Literal, Namespace, URIRef
    from rdflib.namespace import DCTERMS, PROV, RDF, RDFS

    return Graph, Literal, Namespace, URIRef, DCTERMS, PROV, RDF, RDFS


def entity_uri(entity_type: str, label: str):
    _, _, Namespace, URIRef, *_ = _rdf()
    ex = Namespace("http://example.org/cp-dysarthria/")
    return URIRef(ex[f"entity/{entity_type}/{slug(label)}"])


def document_uri(doc_id: str):
    _, _, Namespace, URIRef, *_ = _rdf()
    ex = Namespace("http://example.org/cp-dysarthria/")
    return URIRef(ex[f"doc/{doc_id}"])


def triples_path(extractor: str) -> Path:
    return ROOT / "graphs" / f"{extractor}_triples.jsonl"


def load_triples(extractor: str) -> list[dict]:
    path = triples_path(extractor)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_triples(extractor: str, rows: list[dict]) -> Path:
    path = triples_path(extractor)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def add_documents(graph, sources: list[dict[str, str]]) -> None:
    _, Literal, Namespace, URIRef, DCTERMS, _, RDF, RDFS = _rdf()
    ex = Namespace("http://example.org/cp-dysarthria/")
    for source in sources:
        doc = document_uri(source["doc_id"])
        graph.add((doc, RDF.type, ex.SourceDocument))
        graph.add((doc, RDFS.label, Literal(source["title"])))
        graph.add((doc, DCTERMS.identifier, Literal(source["doc_id"])))
        if source.get("url"):
            graph.add((doc, DCTERMS.source, URIRef(source["url"])))
        if source.get("year"):
            graph.add((doc, DCTERMS.date, Literal(source["year"])))
        if source.get("license"):
            graph.add((doc, DCTERMS.license, Literal(source["license"])))


def add_statements(graph, rows: list[dict]) -> None:
    _, Literal, Namespace, _, _, PROV, RDF, RDFS = _rdf()
    ex = Namespace("http://example.org/cp-dysarthria/")
    for row in rows:
        subject = entity_uri(row["subject_type"], row["subject"])
        obj = entity_uri(row["object_type"], row["object"])
        predicate = ex[row["predicate"]]
        graph.add((subject, RDF.type, ex[row["subject_type"]]))
        graph.add((subject, RDFS.label, Literal(row["subject"])))
        graph.add((obj, RDF.type, ex[row["object_type"]]))
        graph.add((obj, RDFS.label, Literal(row["object"])))

        polarity = row.get("polarity") or "positive"
        modality = row.get("modality") or ""
        if polarity == "positive" and not modality:
            graph.add((subject, predicate, obj))

        digest = hashlib.sha1(
            "|".join(
                [
                    row["doc_id"],
                    row["extractor"],
                    row["subject"],
                    row["predicate"],
                    row["object"],
                    polarity,
                    modality,
                    row.get("evidence", "")[:180],
                ]
            ).encode("utf-8")
        ).hexdigest()[:16]
        statement = ex[f"stmt/{digest}"]
        graph.add((statement, RDF.type, RDF.Statement))
        graph.add((statement, RDF.subject, subject))
        graph.add((statement, RDF.predicate, predicate))
        graph.add((statement, RDF.object, obj))
        graph.add((statement, ex.polarity, Literal(polarity)))
        graph.add((statement, ex.modality, Literal(modality)))
        graph.add((statement, ex.extractor, Literal(row["extractor"])))
        graph.add((statement, ex.evidence, Literal(row.get("evidence", "")[:500])))
        graph.add((statement, PROV.wasDerivedFrom, document_uri(row["doc_id"])))
        if row.get("entity_source"):
            graph.add((statement, ex.entitySource, Literal(row["entity_source"])))


def build_graph(extractor: str):
    Graph, _, Namespace, _, DCTERMS, PROV, _, _ = _rdf()
    graph = Graph()
    ex = Namespace("http://example.org/cp-dysarthria/")
    graph.bind("ex", ex)
    graph.bind("prov", PROV)
    graph.bind("dcterms", DCTERMS)
    add_documents(graph, load_sources())
    add_statements(graph, load_triples(extractor))
    return graph


def write_turtle(extractor: str) -> Path:
    path = ROOT / "graphs" / f"{extractor}_output.ttl"
    path.parent.mkdir(parents=True, exist_ok=True)
    build_graph(extractor).serialize(path, format="turtle")
    return path
