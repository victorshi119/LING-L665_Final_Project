"""Graph statistics, one SPARQL query, and a label-search subgraph.

This is the script form of the course Graph-query-1.ipynb steps: load a
Turtle file, count nodes and predicates, run a SPARQL query, and export
the triples whose labels contain a search string.
"""

from __future__ import annotations

import sys
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import RDFS

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT

QUERY = """
PREFIX ex: <http://example.org/cp-dysarthria/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?disorder ?feature ?evidence WHERE {
  ?statement a rdf:Statement ;
             rdf:predicate ex:has_feature ;
             rdf:subject ?disorderNode ;
             rdf:object ?featureNode ;
             ex:evidence ?evidence .
  ?disorderNode rdfs:label ?disorder .
  ?featureNode rdfs:label ?feature .
}
LIMIT 25
"""


def stats(graph: Graph) -> str:
    predicates = sorted({str(predicate) for predicate in graph.predicates()})
    subjects = {str(subject) for subject in graph.subjects()}
    return f"{len(graph)} triples, {len(subjects)} subject nodes, {len(predicates)} predicates"


def label_subgraph(graph: Graph, needle: str) -> Graph:
    needle = needle.lower()
    matched = set()
    for subject, _, label in graph.triples((None, RDFS.label, None)):
        if isinstance(label, Literal) and needle in str(label).lower():
            matched.add(subject)
    subgraph = Graph()
    for triple in graph:
        if triple[0] in matched or triple[2] in matched:
            subgraph.add(triple)
    return subgraph


def main() -> None:
    notes = ["# Graph inspection notes", ""]
    for extractor in ("spacy", "llm"):
        path = ROOT / "graphs" / f"{extractor}_output.ttl"
        graph = Graph()
        graph.parse(path, format="turtle")
        notes.append(f"## {extractor}")
        notes.append("")
        notes.append(stats(graph))
        notes.append("")
        notes.append("SPARQL `has_feature` statements:")
        notes.append("")
        found = False
        for row in graph.query(QUERY):
            found = True
            notes.append(f"- {row.disorder} has_feature {row.feature}")
        if not found:
            notes.append("- none")
        notes.append("")
        subgraph = label_subgraph(graph, "dysarthria")
        out = ROOT / "graphs" / f"{extractor}_search_subgraph.ttl"
        subgraph.serialize(out, format="turtle")
        notes.append(f"Label search for 'dysarthria' wrote {subgraph.__len__()} triples to `{out.name}`.")
        notes.append("")
    notes.append("Open `graphs/spacy_output.ttl` and `graphs/llm_output.ttl` in Turtle Graph Studio and Protégé. The files parse as RDF. A Turtle file is not by itself an OWL ontology.")
    notes.append("")
    destination = ROOT / "evaluation" / "inspection_notes.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(notes), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
