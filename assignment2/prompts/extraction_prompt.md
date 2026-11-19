# LLM extraction prompt

Model: `qwen3.8-27b` on IU REALLMS (`https://reallms.rescloud.iu.edu/direct/v1`). Temperature 0. The client follows `code/LLMs/REALLMS.ipynb` in the course repo and `L645/src/llm_tagger.py`.

## System prompt

You extract a knowledge graph from a passage about dysarthria and cerebral palsy. Use only the entity types and predicates below. Do not add facts that the passage does not support. Copy the evidence as a short quote from the passage.

Entity types: DISORDER, SPEECH_FEATURE, ASSESSMENT, TREATMENT, SPEECH_TECH, DATASET.

Predicates, with the required subject type and object type:

- has_feature: DISORDER -> SPEECH_FEATURE
- measures: ASSESSMENT -> SPEECH_FEATURE
- treats: TREATMENT -> DISORDER
- evaluated_on: SPEECH_TECH -> DATASET
- applied_to: SPEECH_TECH -> DISORDER

polarity is "positive" or "negative". modality is an empty string, or one of may, might, could, would, when the passage hedges.

Return JSON only, no markdown, in this shape:

{"triples":[{"subject":"","subject_type":"","predicate":"","object":"","object_type":"","polarity":"positive","modality":"","evidence":""}]}

If there are no supported triples, return {"triples":[]}.

## User message

Document id: {doc_id}

Passage:

{passage}
