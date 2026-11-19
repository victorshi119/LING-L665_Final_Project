# Domain schema

Team: Victor Shi, Shintaro Sakai, and Zhanerke Asset, L665 (Fall 2026).

The entity types are the six labels from Assignment 1. A triple is a typed subject, one predicate from the list below, and a typed object. The subject and object are mentions in one source document. The predicate is a relation we defined, not a string copied out of the sentence.

Identifiers look like `http://example.org/cp-dysarthria/entity/DISORDER/dysarthria`. Every entity has `rdfs:label`. Every statement points at its source document and keeps a short evidence sentence.

## Entity types

| Type | What it is | Example |
|---|---|---|
| `DISORDER` | A disease, disorder, or clinical motor sign | dysarthria, cerebral palsy |
| `SPEECH_FEATURE` | A perceptual or acoustic property of speech | hypernasality, speech intelligibility |
| `ASSESSMENT` | A named clinical instrument or scale | Frenchay Dysarthria Assessment |
| `TREATMENT` | An intervention, therapy, device, or drug | speech therapy |
| `SPEECH_TECH` | A speech-technology task, model, representation, or metric | automatic speech recognition, word error rate |
| `DATASET` | A named speech corpus | UASpeech, TORGO |

General spaCy labels such as `ORG` and `PERSON` are not mapped onto these six types. They stay out of the schema triples.

## Relation types

| Predicate | Subject | Object | Example |
|---|---|---|---|
| `has_feature` | `DISORDER` | `SPEECH_FEATURE` | spastic dysarthria, has_feature, hypernasality |
| `measures` | `ASSESSMENT` | `SPEECH_FEATURE` | Frenchay Dysarthria Assessment, measures, speech intelligibility |
| `treats` | `TREATMENT` | `DISORDER` | speech therapy, treats, dysarthria |
| `evaluated_on` | `SPEECH_TECH` | `DATASET` | Whisper, evaluated_on, UASpeech |
| `applied_to` | `SPEECH_TECH` | `DISORDER` | automatic speech recognition, applied_to, dysarthria |

## Polarity, modality, and provenance

A positive, non-modal statement is stored as a direct triple. Negation (`not`, `no`) and modality (`may`, `might`, `could`, `would`) are stored only as a qualified `rdf:Statement` with `ex:polarity` and `ex:modality`. They are not asserted as bare facts.

Each statement has:

- `prov:wasDerivedFrom` the source document
- `ex:evidence` the sentence that supports it
- `ex:extractor` `spacy` or `llm`

Facts are about what that document says. They are not entered as medical truth independent of the paper.
