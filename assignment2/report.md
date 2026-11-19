# Assignment 2 report

Team: Victor Shi, Shintaro Sakai, and Zhanerke Asset, L665 (Fall 2026).

This builds a small knowledge graph from six papers in the Assignment 1 CP-dysarthria corpus. The schema, with examples, is `schema.md`. Provenance for the six documents is `sources_sample.csv`. The paper texts and the NER weights are not in git. Paths and the exact commands are in `README.md`.

## Extractors

`scripts/spacy_extract.py` loads `en_core_web_sm` for sentences and dependencies, and Assignment 1's `model-best` for the six domain labels. Those labels are the domain NER output. The predicate comes from a cue lemma in the same sentence, not from either NER model. General spaCy types such as `ORG` are not mapped into the schema. The run produced 29 triples.

`scripts/llm_extract.py` calls IU REALLMS the same way as `code/LLMs/REALLMS.ipynb` and `L645/src/llm_tagger.py`: base URL `https://reallms.rescloud.iu.edu/direct/v1`, model `qwen3.8-27b`, temperature 0. The prompt is `prompts/extraction_prompt.md`. The key is read from `REALLMS_API_KEY` and is not stored. The run on 19 November 2026 produced 186 triples. A quote that is not in the passage is dropped.

Negated or modal statements are `rdf:Statement` nodes with `ex:polarity` and `ex:modality`. They are not asserted as bare triples. Every statement has the document id and a short evidence sentence.

## Graphs

- `graphs/spacy_output.ttl` and `graphs/llm_output.ttl`
- `graphs/spacy_search_subgraph.ttl` and `graphs/llm_search_subgraph.ttl`, from a case-insensitive label search for dysarthria
- `evaluation/inspection_notes.md` has the triple counts and the `has_feature` SPARQL query

Open the Turtle files in Turtle Graph Studio and Protégé to see the same graphs. The notes are the inspection record from this run. A Turtle file that Protégé can open is not, by itself, an OWL ontology.

## Evaluation

The question is how to judge the two graphs. The plan and the 16 reviewed triples are in `evaluation/results.md`. Correct means the sentence supports the subject, predicate, object, types, and polarity. The Assignment 1 entity rules are not used as relation gold. On the reviewed sample, 3 of 8 spaCy triples and 4 of 8 LLM triples were correct. The spaCy errors are mostly co-occurrence in titles and tables. The LLM errors include one wrong polarity and relations the sentence does not state. Those fractions are not corpus-wide precision.
