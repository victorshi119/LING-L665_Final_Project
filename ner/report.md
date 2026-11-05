# CP Dysarthria NER: Report

**Team:** Victor & Shintaro, L665 (Fall 2026) · Assignment 1, Domain Glossary and Transformer NER

This report covers the topic and labels, the glossary, rules, corpus and DocBins, the transformer
training, the prediction DocBin, the evaluation against the rule labels, inspected examples,
limitations, and how to reproduce everything. All paths are relative to `ner_assignment1/`.

| Deliverable | Where |
| --- | --- |
| Topic and entity-label description | [topic_and_labels.md](topic_and_labels.md) |
| JSON glossary with provenance | [glossary.json](glossary.json), checks in [glossary_verification.json](glossary_verification.json), [glossary_stats.csv](glossary_stats.csv) |
| Rule-generation code and demonstration | [rules.py](rules.py), [demo_rules.py](demo_rules.py) → [rules_demo.md](rules_demo.md), [rules_demo.html](rules_demo.html) |
| Documented corpus | [texts/](texts/) (378 `.txt` files), [sources.csv](sources.csv) |
| Rule-annotated DocBins with IDs and splits | [corpus/](corpus/) `train.spacy`, `dev.spacy`, `test.spacy`, [splits.csv](corpus/splits.csv), [corpus_stats.json](corpus/corpus_stats.json) |
| Trained model, configuration, logs | [training/config.cfg](training/config.cfg), `training/ner-transformer/model-best/`, `training/ner-transformer/train.log` |
| Prediction DocBin | `corpus/predictions.spacy`, `corpus/predictions_manifest.csv`, `corpus/predictions_model_info.json` |
| Evaluation and inspected examples | `evaluation/` |

## 1. Topic and labels

The topic is **dysarthria associated with cerebral palsy (CP)**: its clinical description,
assessment and treatment, and the speech technology built for dysarthric speech. Because the
literature shares instruments and methods across causes, the corpus also covers dysarthria in
Parkinson's disease, ALS and stroke. There are six labels, defined with examples and boundary rules in
[topic_and_labels.md](topic_and_labels.md):

| Label | Covers |
| --- | --- |
| `DISORDER` | dysarthria and its subtypes, CP and its subtypes, other causes, related speech/language/swallowing disorders |
| `SPEECH_FEATURE` | perceptual or acoustic properties of speech (intelligibility, hypernasality, speech rate, F0, jitter) |
| `ASSESSMENT` | named clinical instruments and classification systems (Frenchay Dysarthria Assessment, GMFCS, Viking Speech Scale) |
| `TREATMENT` | interventions, therapies, devices, drugs (speech therapy, AAC, LSVT LOUD, botulinum toxin) |
| `SPEECH_TECH` | speech-technology tasks, models, representations, metrics (ASR, wav2vec 2.0, Whisper, MFCC, WER) |
| `DATASET` | named speech corpora (UASpeech, TORGO, Speech Accessibility Project) |

## 2. Glossary

[glossary.json](glossary.json) (version 0.2) has **105 concepts**. Each entry has a stable id
(e.g. `DIS001`), label, preferred and alternate terms, acronyms, a definition paraphrased from its
sources, a hypernym, a MeSH id where one exists, and source URLs. Version 0.2 corrects three errors
found in the team's category check (Section 5); version 0.1 (103 concepts) is kept as
[glossary_v0.1.json](glossary_v0.1.json).

| Label | Concepts | Terms | Acronyms | MeSH ids | Corpus mentions |
| --- | ---: | ---: | ---: | ---: | ---: |
| DISORDER | 28 | 52 | 9 | 21 | 13,283 |
| SPEECH_FEATURE | 22 | 40 | 6 | 8 | 7,073 |
| SPEECH_TECH | 24 | 46 | 16 | 2 | 17,198 |
| ASSESSMENT | 11 | 22 | 15 | 0 | 807 |
| TREATMENT | 10 | 23 | 7 | 9 | 477 |
| DATASET | 10 | 16 | 3 | 0 | 3,574 |
| **Total** | **105** | **199** | **56** | **40** | **42,412** |

* **Provenance.** 98 distinct source URLs (MeSH, ASHA Practice Portal, DOIs of the papers that
  define an instrument, model, metric or dataset, arXiv pages). [verify_glossary.py](verify_glossary.py)
  fetched every URL; on 2026-11-03, 97 of 98 resolved. The exception is the Speech and Language
  Processing textbook page (`web.stanford.edu/~jurafsky/slp3/`, cited by five SPEECH_TECH concepts).
  The page is up (HTTP 200 when the certificate check is skipped), but its new TLS certificate
  (valid from 2026-10-27) could not be verified from Quartz.
* **Duplicates and ambiguity.** The same script fails if a surface form belongs to two concepts and
  flags acronyms that are ordinary words. 12 concepts (acronyms such as `FDA`, `SGD`, `VC`, `SAP`,
  `MS`, `PER`) are marked `acronym_requires_long_form` because they have common unrelated readings
  in the corpus (US Food and Drug Administration, stochastic gradient descent, the word *per* in
  capitalised captions).
* **Coverage.** Every concept occurs in the corpus; the rarest are *Consensus Auditory-Perceptual
  Evaluation of Voice* (CAPE-V) and *ataxic cerebral palsy* (1 document each), then *Manual Ability
  Classification System*, *Communication Function Classification System* and the *Dysarthric
  Expressed Emotional Database* (2 each). Two drafted concepts (selective dorsal rhizotomy,
  nonspeech oral motor exercises) were removed because they never occur.
* **Candidate terms.** [extract_candidates.py](extract_candidates.py) runs spaCy + TextRank (as in
  `keywords.ipynb`) over the corpus. It was run after the glossary was built, as a coverage check:
  of the top 500 phrases, 24 are fully and 37 partly covered. Most uncovered phrases are generic
  (*models*, *training data*); the domain phrases among them are listed in Section 9.

## 3. Rules

[rules.py](rules.py) turns the glossary into a spaCy pipeline: `sentencizer` → `paragraph_sentences`
(a sentence also starts after each line break) → `entity_ruler` (514 patterns) → `long_form_filter`.

* Terms are phrase patterns on `LOWER`, expanded with singular/plural forms (reusing the course
  `build_ner_corpus.py`) and hyphen/space variants (*self-supervised* ~ *self supervised*).
* Acronyms are token patterns on `ORTH`, so they match with exact case (`CP` but not `cp`).
* Every pattern carries its concept id, so all names of a concept share one `ent_id_`.
* `long_form_filter` drops a guarded acronym from a document in which none of the concept's terms occur.

[demo_rules.py](demo_rules.py) applies the rules to five corpus passages and eight probe sentences
([rules_demo.md](rules_demo.md), displaCy view in [rules_demo.html](rules_demo.html)). The probes
show the intended behaviour (FDA kept next to *Frenchay Dysarthria Assessment* and dropped next to
*approved by the FDA*; `cp` and `als` not matched; *MFCCs* and *mel-frequency cepstral coefficients*
mapped to one concept) and three known failure types:

* **Misses:** terms not in the glossary (*velopharyngeal dysfunction*, *nasal emission*, *eye-gaze systems*).
* **False matches:** everyday senses (*the articulation of this argument*, *a stroke of the pen*).
* **Boundaries:** modifiers outside the span (*Severe* [*spastic dysarthria*]).

## 4. Corpus

378 documents, one UTF-8 `.txt` file each in [texts/](texts/), exported by
[prepare_corpus.py](prepare_corpus.py) from the course corpus (`L665/data/CP_Dysarthria`, read-only).
[sources.csv](sources.csv) records for each document its title, year, URL, DOI, access date,
license, reuse note, the search topic it was collected under, and its length.

| | Documents | Notes |
| --- | ---: | --- |
| arXiv papers | 321 | cleaned full text |
| PubMed papers | 57 | Docling conversions of the PDFs; metadata from NCBI E-utilities, licenses from Europe PMC |
| Total | 378 | 2.15M words; median 4,262 words per document (649 – 92,119); published 1989–2026, median 2024 |

Licenses: 151 open with attribution (CC BY), 150 arXiv non-exclusive (course research use only),
42 CC NoDerivatives, 25 CC NonCommercial, 10 publisher copyright (course research use only). The
texts and DocBins are for course use and should not be redistributed.

**Duplicates.** Three PubMed records pointed to a byte-identical PDF (a whole journal supplement)
and were dropped, keeping one. Pairs that are versions of one study are kept but always placed in the
same split (Section 5).

## 5. Rule-annotated DocBins

[build_corpus.py](build_corpus.py) runs the rule pipeline over every document and writes one Doc per
source document. Each Doc's `user_data` stores `doc_id`, source, split, title, URL, license, and the
glossary version; entity ids (`ENT_ID`) and sentence boundaries are stored as well.
[corpus/splits.csv](corpus/splits.csv) lists every document with its split and entity counts per label.

The split is by document, 80/10/10 within each source (arXiv/PubMed), seed 665. Documents in the
same *split group* are assigned together.

| Split | Docs | Tokens | Entities | DISORDER | SPEECH_FEATURE | SPEECH_TECH | DATASET | ASSESSMENT | TREATMENT | Concepts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 301 | 2,226,259 | 32,758 | 10,405 | 5,317 | 13,038 | 2,937 | 624 | 437 | 105 |
| dev | 38 | 237,139 | 3,200 | 1,045 | 662 | 1,119 | 216 | 144 | 14 | 79 |
| test | 39 | 239,782 | 4,409 | 882 | 880 | 2,267 | 326 | 28 | 26 | 80 |

The table shows the final DocBins, built with glossary v0.2. The v0.1 DocBins are kept in
`corpus_v0.1/`.

**Leakage check.** `spacy debug data` warned that 358 training sentences also occur in the dev data.
[check_split_overlap.py](check_split_overlap.py) showed that most of these are headings, numbers and
license boilerplate, but one test paper (arXiv 1807.10948, 2018) shared 26% of its sentences of 8+
words with a training paper (arXiv 1905.06533, its 2019 extension by the same authors). We added
the pair as a split group and rebuilt the DocBins (the table above is after the fix). The largest
remaining overlap is 6.8% (shared method descriptions between two papers from one group); our rule
is to group pairs above 10%. Results are in [inspection/split_overlap.csv](inspection/split_overlap.csv).

**Manual inspection of the weak labels.** [inspect_rule_labels.py](inspect_rule_labels.py) sampled
20 random rule mentions per label from the training split with their context
([inspection/rule_sample.csv](inspection/rule_sample.csv)) and listed the most frequent surface forms
per label ([inspection/rule_surface_forms.md](inspection/rule_surface_forms.md)). Of the 120 sampled
mentions, 112 are correct, 6 have the right label but a wrong span (a model name or subscale
suffix outside the span: *Whisper*-large, Grad-*TTS*, Qwen3-*ASR*, *UPDRS* IV; or a modifier:
extrapyramidal *dysarthria*), 1 has the wrong label (*Hungarian Dysarthria*, a dataset name, labelled
DISORDER), and 1 is not an entity (*Physical Therapy* as a journal title in a reference list). We also
checked the ambiguous acronyms in context (FDA, SGD, SAP, VC, PD, CAS, SSL, DEED); the long-form
guard kept them correct. None of these errors was frequent enough to justify changing the rules
before training, so they are documented here instead. The sample was drawn from the v0.1 DocBins.
Only one sampled mention is affected by the v0.2 corrections: *automated dysarthria severity
assessments* (SPEECH_TECH in v0.1, where the label was right in context; in v0.2 only *dysarthria*
is labelled, as DISORDER).

**Category check of the glossary.** A wrong category affects every occurrence of a term, so the team
also checked, concept by concept, that each glossary term belongs in its label
([inspection/glossary_review.md](inspection/glossary_review.md), made by
[make_glossary_review.py](make_glossary_review.py)). Eleven assignments were flagged as borderline,
for example *perceptual evaluation* in ASSESSMENT (defined as *named* instruments) and *severity
classification* in SPEECH_TECH (it can also mean a clinician's rating).

Victor's check found three errors. All other assignments were kept, including the remaining
borderline ones.

1. *Phoneme error rate* / *phone error rate* were listed as names of character error rate (CER,
   TEC003). PER is a different metric, so it is now its own concept (TEC024, acronym `PER`).
2. Concept TEC023 (automatic dysarthria detection/classification) included *severity
   classification* and *dysarthria severity assessment*. These also mean a clinician's severity
   rating, which is the human gold label that the automatic systems predict. Both terms were
   removed.
3. ASM010 merged CAPE-V and GRBAS, two different perceptual voice-rating instruments. GRBAS is now
   ASM011. The old source (the ASHA voice disorders page) named neither instrument, so each now
   cites its own: Kempster et al. (2009) for CAPE-V, and Wuyts et al. (1999), a reliability study
   of GRBAS (the scale was introduced in Hirano's 1981 book, which has no DOI).

[update_glossary_v0_2.py](update_glossary_v0_2.py) applies these changes to v0.1, and the
`metadata.changes` field of `glossary.json` records them. We then rebuilt the DocBins with the
same split, retrained, and predicted again. All results below are for v0.2. The changes are small:
train lost 35 rule entities (SPEECH_TECH −68 and DISORDER +33, because *dysarthria* inside the
removed *dysarthria severity assessment* is now labelled DISORDER), and test gained 27 SPEECH_TECH
entities, mostly `PER`.

## 6. Transformer training

Following the course workflow (`train_transformer_quartz.py`), the config was generated with
`spacy init config --lang en --pipeline transformer,ner --optimize accuracy --gpu`
([training/config.cfg](training/config.cfg)): `roberta-base` with strided spans (window 128,
stride 96), transition-based NER, Adam with linear warmup (250 steps) and peak rate 5e-5,
`batch_by_padded` size 2000, gradient accumulation 3, dropout 0.1, up to 20,000 steps, evaluation on
dev every 200 steps, patience 1,600 steps, seed 0. Papers are thousands of tokens long, so training
and dev documents are split into sentences (`--corpora.*.max_length 500`).

[train.slurm](train.slurm) runs `spacy debug data`, `spacy train`, and `spacy evaluate` on the
test DocBin on one H100 (Quartz `h100-single`, 8 CPUs, 64 GB RAM).
Software: Python 3.12.15, spaCy 3.8.16, spacy-transformers 1.3.9, PyTorch 2.15.0 (CUDA 13.2), CuPy
(CUDA 12), NVIDIA driver 595.91.

| Run | Glossary, split | Steps | Runtime | Dev ENTS_F | Test P / R / F (vs rules) |
| --- | --- | ---: | ---: | ---: | --- |
| Test run (job 12530148, `training/ner-smoke/`) | v0.1, before the leakage fix | 300 | 14 min 34 s | 75.4 | 79.3 / 67.2 / 72.7 |
| Full run 1 (job 12530351, `training/ner-transformer_v0.1/`) | v0.1, final split | 7,800 (best 6,200) | 1 h 05 min | 98.6 | 98.1 / 98.8 / 98.5 |
| **Full run 2, final model** (job 12606993, `training/ner-transformer/`) | v0.2, final split | 7,600 (best 6,000) | 1 h 45 min | 98.5 | 97.7 / 98.8 / 98.2 |

The test run confirmed that the files, labels and GPU setup work. A first full run on the old
split was cancelled after ~1,000 steps when the leakage was found
(`training/ner-transformer_cancelled_old_split/`). Full run 1 used glossary v0.1. Full run 2 is
the same configuration on the DocBins rebuilt with glossary v0.2 (Section 5), and it is the model
we submit. Its `model-best` directory (for `DOMAIN_SPECIFIC_MODEL_PATH` in Assignment 2) is
`/N/u/shinsaka/BigRed200/CP_Dysarthria_Pubmed_md/ner_assignment1/training/ner-transformer/model-best`. The two test scores are not strictly comparable, because the corrections changed some
test labels.

In full run 2, dev F rose quickly (89.5 at step 1,000, 95.4 at 2,000, 96.9 at 4,000) and peaked at
98.54 at step 6,000 (P 98.1, R 98.9). Training stopped at step 7,600, after 1,600 steps without
improvement, and `model-best` is the step-6,000 model. Run 1 followed almost the same curve (best
98.57 at step 6,200). The 1 h 45 min job time includes `debug data` and the test evaluation. Run 2
was slower per step than run 1 (1 h 05 min for 7,800 steps) with the same configuration and data
size. We did not find the cause; that day the login node and file system were also slow (Section
10). Peak memory was 5.6 GB of the 64 GB requested. `debug data`
(`training/ner-transformer/debug_data.log`) reports 326 sentences shared between train and dev
(headings, numbers, boilerplate; see Section 5) and 1 misaligned token.

## 7. Prediction DocBin

[predict.py](predict.py) loads `model-best` and annotates every corpus document (all splits), writing
`corpus/predictions.spacy`, separate from the rule-labelled DocBins (the script refuses to overwrite
them). Each predicted Doc's `user_data` records `doc_id`, source, split, model name, version and path,
spaCy version and prediction time; `corpus/predictions_manifest.csv` lists the entity counts per
document. Run by [predict.slurm](predict.slurm), chained after training.

The final model annotated all 378 documents with **40,502 entities** (the rules found 40,367) in
3 min 34 s on one H100 (job 12606994); `predictions.spacy` is 11.5 MB. The first prediction attempt
(for run 1) ran out of memory (64 GB). spacy-transformers keeps the transformer's output tensors in
`doc._.trf_data`, which lives in `user_data` and was being serialised for every document;
`predict.py` now drops it before adding a Doc (peak memory afterwards: 2.4 GB). spaCy records the
trained pipeline as `pipeline` 0.0.0, so predictions are traced to the model by its path
(`predictions_model_info.json`) and training job. Run 1's predictions are kept in `corpus_v0.1/`.

## 8. Evaluation and inspected examples

[evaluate.py](evaluate.py) compares the model's predictions with the rule labels on the 39 test
documents. The rule labels are weak labels, not human gold, so "precision" and "recall" measure
agreement with the rules: a model-only span can be a model error or a correct entity the rules
missed.

On the 39 test documents the rules have 4,409 entities and the final model 4,457
([evaluation/scores.json](evaluation/scores.json)):

| Label | Test mentions (rules) | P | R | F |
| --- | ---: | ---: | ---: | ---: |
| SPEECH_TECH | 2,267 | 96.9 | 98.2 | 97.6 |
| DISORDER | 882 | 98.4 | 98.8 | 98.6 |
| SPEECH_FEATURE | 880 | 99.1 | 99.5 | 99.3 |
| DATASET | 326 | 98.2 | 100.0 | 99.1 |
| ASSESSMENT | 28 | 93.3 | 100.0 | 96.6 |
| TREATMENT | 26 | 92.9 | 100.0 | 96.3 |
| **All** | **4,409** | **97.7** | **98.8** | **98.2** |

The model reproduces the rules almost exactly. 4,354 of its 4,457 test entities match a rule entity
exactly. Examples with context are in the *Agreements* section of
[evaluation/examples.md](evaluation/examples.md): *WER* and *ASR* in results sections, *UASpeech*,
*dysarthria*, *intelligibility*, *phonation*, *speaker adaptation*. (Not every agreement is
correct: the same list has *Motor Speech Disorders* inside a lab's name.) On spans where both found an entity with the same
boundaries, the label never differs ([evaluation/confusion.json](evaluation/confusion.json)). The
disagreements are 103 model-only and 55 rule-only spans (run 1: 84 and 51).
[analyze_disagreements.py](analyze_disagreements.py) separates them
([evaluation/disagreements.json](evaluation/disagreements.json); every span with its context in
[evaluation/disagreement_spans.csv](evaluation/disagreement_spans.csv)). Each model-only span type
was judged in its context ([evaluation/model_only_review.csv](evaluation/model_only_review.csv),
made by [make_model_only_review.py](make_model_only_review.py)). The judgments are a first pass by
Claude Code that reuses run 1's judgments where the same span recurs; contexts are in
[evaluation/examples.md](evaluation/examples.md).

* **Boundary differences (9 pairs).** Four times the model takes a longer, better span than the
  rules: *Acquired* cerebral palsy, *DNN-*hidden Markov model, *imprecise* phonation, *Automatic*
  speech recognizers. Four times its span is worse: shorter (*HMM* inside *GMM-HMM*, SPEECH
  RECOGNITION inside AUTOMATIC SPEECH RECOGNITION), a fragment (*-supervised learning*), or one
  that includes a comma (*articulation,*). Once it changes the label: in *intelligibility
  classification (dysarthria severity classification)*, the rules label the whole automatic task
  SPEECH_TECH, which is right here, while the model labels only *dysarthria* as DISORDER.
* **New model spans (94).** 30 are correct entities the rules missed: *ASR* ×12 in a paper that
  never spells out "automatic speech recognition" (the long-form guard is too strict for ASR),
  plural acronyms (*MOSs*, *F0s*), terms missing from the glossary (*LM* for language model,
  *motor-speech disorders*, *monoprosody*, *speaker level adaptation*), variants and synonyms
  (*speed-perturbation*, *voice synthesis*, *cerebral vascular accident*, *Universal Access
  Speech*), and source typos (*PI-GITA*, *UPDRSspeech*, *MDS-UPDRSS*). 13 have the right label but
  a wrong boundary (*Cerebral Vascular* without *Accident*, *Frequency Cepstral Coefficients*
  without *GammaTone*, pieces of *LibriSpeech-PC*, a footnote marker). 51 are errors:
  * 30 come from three off-topic papers in the corpus (two on time-series forecasting, one on
    comorbidity): *HTS* (hierarchical time series) ×22, *MLTCs*/*LTCs* (long-term conditions) ×6,
    and the forecasting model *Informer* ×2, all labelled SPEECH_TECH.
  * 9 are fragments of words hyphenated at a line break (*thria* from "dysar- thria" ×5, *ters*,
    *ers*).
  * The rest are short acronyms and words out of context (*SGD* the optimizer as TREATMENT, *PD*
    inside a URL, *C* and *TC*, *v-vectors* in a matrix formula, *BERT*) and two phrases that are
    not features (*hypernasal speakers*, *oracle error rates*).
* **Rule spans the model missed (46).** 17 are *Whisper* in four papers: 12 in table rows and 5
  at the start of a sentence. Run 1 missed none of these, so the model's handling of rare contexts
  varies between runs. 10 are *spastic quadriplegia/hemiplegia* in the oldest document (a 1989
  scanned paper). Only 2 are in capitals (VOICE CONVERSION, TEMPO PERTURBATION; run 1: 8). The
  rest are single cases, often in tables (*HuBERT*, *CTC*, *WavLM*). One miss is a rule error:
  in the caption *BEST PERFORMANCE PER LANGUAGE*, the rules label the word *per* as the metric
  PER (the long-form guard passes because the paper also defines phoneme error rate). The model
  correctly leaves it out.

So the 97.7% precision understates the model. Of its 94 new spans, 30 are correct entities the
glossary does not cover and 13 more have the right label. Its real errors are concentrated in
off-topic papers and in acronyms it has learned without the rules' context checks.

**The corrected concepts.** [check_v0_2_concepts.py](check_v0_2_concepts.py)
([evaluation/v0_2_concepts.json](evaluation/v0_2_concepts.json)) counts how the rules and the
model label the forms changed in v0.2 over all 378 documents. The model learned the new PER
concept: on test it labels 43 of the 44 rule mentions of `PER`, all except the caption above,
plus all 9 long forms. CER keeps its own label (68 test mentions of `CER`, the same as the rules).
GRBAS is labelled ASSESSMENT. CAPE-V, now its own concept, occurs in only one training paper
(5 mentions), and the model labels none of them, not even in that training paper. A concept that
rare is not learned.

## 9. Limitations and improvements

* **Weak labels.** Training data and the reference are the same rules, so the model mainly learns
  to reproduce the glossary; the scores measure agreement with the rules, not correctness. A small
  human-annotated test sample would give a true estimate.
* **Spans.** Exact phrase matching cannot attach modifiers or suffixes (*Whisper-large*,
  *UPDRS-III*, *extrapyramidal dysarthria*). Token patterns with optional suffixes, or a merge rule
  for adjacent hyphenated tokens, would fix most of these.
* **Coverage.** Frequent domain phrases are missing from the glossary: *dysarthric speech*
  (171 documents), *disordered / pathological / impaired speech*, *speech impairment*, *data
  augmentation*, *speech enhancement*, *dysarthric speech reconstruction*, *speaker similarity*,
  *spontaneous / connected / read speech*, *large language models*.
* **Context.** The rules label everywhere, including reference lists, tables and journal titles.
  Detecting and skipping the reference section would remove a class of false matches.
* **Imbalance.** TREATMENT and ASSESSMENT are rare (437 and 624 training mentions), and test has only
  26 TREATMENT and 28 ASSESSMENT mentions, so their scores are unstable.
* **Corpus.** 85% of the documents are arXiv speech-technology papers, so SPEECH_TECH dominates;
  more clinical PubMed papers would balance the labels. The keyword search also brought in a few
  off-topic papers (time-series forecasting, comorbidity), which cause most model errors on test
  (Section 8). A relevance filter on titles and abstracts would remove them.
* **Model errors.** The model applies acronyms it learned without the rules' long-form check
  (*HTS*, *SGD*), labels fragments of hyphenated line breaks, misses terms in table rows and in old
  scanned text, and does not learn very rare concepts (CAPE-V, one training paper). Two runs with
  the same settings differ in which rare contexts they miss (capitals in run 1, *Whisper* in table
  rows in run 2). De-hyphenating line breaks during corpus preparation, and case-augmenting part
  of the training text, would address the first two.
* **Remaining ambiguity.** The long-form guard checks only that the long form occurs somewhere in
  the paper, so the word *per* in a capitalised caption is still labelled PER in a paper that
  defines phoneme error rate. TEC023 keeps *dysarthria severity classification*, which in this
  corpus names the automatic task, but could also mean a clinician's rating.
* **Long windows.** Some 128-token windows (tables, URLs) exceed roberta-base's 512 word pieces and
  are truncated, so a few tokens in such passages get no transformer context.
* **Review.** The glossary definitions, the occurrence-level inspection verdicts and the judgments
  of model-only spans were drafted with Claude Code. The team checked the glossary categories
  (Section 5), and the three errors found were corrected before the final run.

## 10. Reproducing

On Quartz, from `ner_assignment1/`. The course folder `/N/project/ontology_learning` is only read.

```bash
bash setup_env.sh                       # Python 3.12 venv in /N/slate/$USER/envs/spacy-ner
source /N/slate/$USER/envs/spacy-ner/bin/activate

python prepare_corpus.py                # texts/, sources.csv, sources_raw/near_duplicates.json
python update_glossary_v0_2.py          # glossary_v0.1.json -> glossary.json (v0.2 corrections)
python verify_glossary.py               # glossary checks, URL resolution, corpus coverage
python extract_candidates.py            # TextRank candidate terms (coverage check)
python rules.py && python demo_rules.py # rule summary, rules_demo.md/.html
python build_corpus.py                  # corpus/{train,dev,test}.spacy, splits.csv, corpus_stats.json
                                        #   (or: sbatch build_corpus.slurm, on a CPU node)
python check_split_overlap.py           # inspection/split_overlap.csv
python inspect_rule_labels.py           # inspection/rule_sample.csv, rule_surface_forms.md
python make_glossary_review.py          # inspection/glossary_review.csv/.md (category check sheet)

sbatch gpu_check.slurm                  # optional: GPU/CUDA check (h100-debug, ~1 min)
OUT=training/ner-smoke SKIP_DEBUG_DATA=1 sbatch --partition=h100-debug --time=00:55:00 \
    train.slurm --training.max_steps 300 --training.eval_frequency 100   # short test run
T=$(sbatch --parsable train.slurm)      # full training + test evaluation
sbatch --dependency=afterok:$T predict.slurm   # predictions.spacy + evaluation/

# after predict.slurm:
python analyze_disagreements.py         # evaluation/disagreements.json, disagreement_spans.csv
python make_model_only_review.py        # evaluation/model_only_review.csv (judged span types)
python check_v0_2_concepts.py           # evaluation/v0_2_concepts.json (the corrected concepts)
```

Run spaCy training commands inside Slurm jobs: on the login node the Hugging Face tokenizer fails to
start its thread pool (per-user thread limit). On 2026-11-03 the login node was also so busy that
CPU scripts got about 5% of a core, so we ran `build_corpus.py` with
[build_corpus.slurm](build_corpus.slurm). We ran the three analysis scripts with `sbatch --wrap`
on the `general` partition (about 2 minutes each). Fixed seeds: split 665, inspection sample 665,
training 0. Glossary v0.1 and everything built from it are kept as `glossary_v0.1.json`,
`corpus_v0.1/`, `training/ner-transformer_v0.1/` and `evaluation_v0.1/`.
