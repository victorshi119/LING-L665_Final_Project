# Evaluation

Team: Victor Shi, Shintaro Sakai, and Zhanerke Asset. Both extractors ran on the same six documents. A reviewer judged 16 triples, 8 from each system, against the quoted sentence and the source text. The sheet is `reviewed_sample.csv`.

## What counts as correct

A triple is correct when the sentence supports that subject, that predicate, and that object, the entity types match the schema, and the polarity and modality match the sentence. The reviewer uses the evidence quote first and the source file when the quote is ambiguous. Equivalent names of one glossary concept, such as `CP` and `cerebral palsy`, count as the same entity. A different surface form is not an error by itself.

Partial means the entities are in the sentence but the predicate, the span, or the type is off. Unsupported means the sentence does not state the relation. Wrong polarity means the relation is real and the sign is not.

## Reference set

There is no pre-existing relation gold standard. Assignment 1's rule labels mark entity mentions only, and scoring relations against those labels would repeat the rule biases. The reference set is this reviewed sample. One reviewer (Victor) marked it. It is not a double-annotated test set.

## Scores on the reviewed sample

| System | Reviewed | Correct | Partial | Unsupported | Wrong polarity |
|---|---|---|---|---|---|
| spaCy | 8 | 3 | 2 | 3 | 0 |
| LLM | 8 | 4 | 2 | 1 | 1 |

These counts describe the 16 reviewed triples. They are not precision on all 29 spaCy triples or all 186 LLM triples.

## What the two systems did

The spaCy graph is small because a triple is emitted only when the domain NER model finds both entity types in one sentence and a cue lemma for that predicate is present. That misses paraphrases, which is why `arxiv_1811.11101` produced no triples. It also fires on layout accidents: `GMFCS measures Speech Intelligibility` comes from adjacent table columns, and `Speech and Language Therapy treats Cerebral Palsy` comes from the title block. Where the sentence is a straightforward characterization, such as spastic dysarthria and harshness, the triple is right. Negation and `would` are stored as qualified statements rather than bare facts.

The LLM graph is larger and covers paraphrases the cues miss, including hypernasality and the UA-Speech experiment. It also states relations the sentence does not, such as pharmacological interventions treating Parkinson's disease, and it marks a positive feature sentence as negative. It sometimes stretches a predicate so a speech-technology method is filed as `treats`.

On this sample the LLM has more correct triples and more unsupported or mistyped ones. The spaCy graph is stricter and more often empty or tied to a cue that happens to sit near two entities. Neither score says the graph is medically reliable.

## Fairness and limits

Both systems used the same documents, the same five predicates, and the same identifier scheme. They did not use the same mechanism. spaCy needs a cue lemma and two NER spans. The LLM sees a prompt and can paraphrase. Comparing raw triple counts would favor the LLM for that reason, so the review judges each triple against its sentence rather than against the other system's output.

The sample is 16 triples from six papers. One reviewer. Case variants such as `Dysarthria` and `dysarthria` collapse to one identifier, but near-duplicates can still be counted twice before that collapse. Missing facts were not enumerated, so this is not recall. Turtle Graph Studio and Protégé were not opened in this run. `evaluation/inspection_notes.md` is the inspection record: the files parse, the `has_feature` query returns statements, and a label search for dysarthria writes a subgraph for each extractor.
