# Graph inspection notes

## spacy

418 triples, 68 subject nodes, 20 predicates

SPARQL `has_feature` statements:

- Dysarthria has_feature harsh voice
- dysarthria has_feature harsh voice
- Mixed dysarthria has_feature breathy voice
- Ataxic dysarthria has_feature phonation
- amyotrophic lateral sclerosis has_feature vowel space areas
- Mixed dysarthria has_feature harshness
- Hypokinetic dysarthria has_feature monoloudness
- Dysarthria has_feature speech rate
- dysarthria has_feature speech rate
- parkinsons disease has_feature monopitch
- Hypokinetic dysarthria has_feature monopitch
- Ataxic dysarthria has_feature articulation
- Spastic dysarthria has_feature harshness
- Dysarthria has_feature formant
- dysarthria has_feature formant
- CP has_feature articulation rate
- parkinsons disease has_feature monoloudness
- Dysarthria has_feature speech rate
- dysarthria has_feature speech rate
- Flaccid dysarthria has_feature harsh voice
- Dysarthria has_feature formants
- dysarthria has_feature formants
- Dysarthria has_feature intelligibility
- dysarthria has_feature intelligibility
- Parkinson's disease has_feature F0

Label search for 'dysarthria' wrote 83 triples to `spacy_search_subgraph.ttl`.

## llm

2407 triples, 364 subject nodes, 20 predicates

SPARQL `has_feature` statements:

- Dysarthria has_feature repetition of phoneme
- dysarthria has_feature repetition of phoneme
- Dysarthria has_feature speech rate
- dysarthria has_feature speech rate
- Ataxic dysarthria has_feature pitch break
- ataxic dysarthria has_feature pitch break
- dysarthria due to CP has_feature inappropriate loudness levels
- Dysarthria has_feature intelligibility
- dysarthria has_feature intelligibility
- Extrapyramidal dysarthria has_feature F1 and F2 transition rates
- extrapyramidal dysarthria has_feature F1 and F2 transition rates
- PD has_feature F2 transition rates
- Parkinson's disease has_feature F0 variability
- dysarthria due to CP has_feature hypernasality
- Dysarthria has_feature pausing
- dysarthria has_feature pausing
- Dysarthria has_feature fluency
- dysarthria has_feature fluency
- Spastic dysarthria has_feature F0 jitter
- spastic dysarthria has_feature F0 jitter
- Parkinson's disease has_feature reduced F1-F2 vowel space
- Extrapyramidal dysarthria has_feature flatter F1 and F2 transition rates
- extrapyramidal dysarthria has_feature flatter F1 and F2 transition rates
- Dysarthria has_feature abnormal prosodic patterns
- dysarthria has_feature abnormal prosodic patterns

Label search for 'dysarthria' wrote 378 triples to `llm_search_subgraph.ttl`.

Open `graphs/spacy_output.ttl` and `graphs/llm_output.ttl` in Turtle Graph Studio and Protégé. The files parse as RDF. A Turtle file is not by itself an OWL ontology.
