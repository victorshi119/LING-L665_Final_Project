# Glossary category check

Our NER labels come from the glossary: every term in `glossary.json` belongs to one of six
categories, and the rules label each occurrence of the term with that category. If a term is in
the wrong category, every occurrence of it in the corpus is labelled wrongly. Before we finalise
the model, we check in [`glossary_review.csv`](glossary_review.csv) (the same list grouped by
category: [`glossary_review.md`](glossary_review.md)) that each term makes sense in its category.

## The six categories (fixed)

| Category | What belongs here | Examples |
| --- | --- | --- |
| `DISORDER` | Diseases, disorders, and clinical motor signs: dysarthria and its subtypes, CP and its subtypes, other conditions that cause dysarthria, related speech, language, and swallowing disorders | spastic dysarthria, cerebral palsy, Parkinson's disease, dysphagia, spasticity |
| `SPEECH_FEATURE` | Perceptual or acoustic properties of speech | intelligibility, hypernasality, speech rate, F0, jitter |
| `ASSESSMENT` | Named clinical instruments, rating scales, and classification systems | Frenchay Dysarthria Assessment, GMFCS, Viking Speech Scale |
| `TREATMENT` | Clinical interventions, therapies, devices, and drugs | speech therapy, AAC, LSVT LOUD, botulinum toxin |
| `SPEECH_TECH` | Speech-technology tasks, models, representations, and metrics | ASR, wav2vec 2.0, Whisper, MFCC, WER |
| `DATASET` | Named speech corpora and databases | UASpeech, TORGO, Speech Accessibility Project |

Full definitions and boundary rules: [`../topic_and_labels.md`](../topic_and_labels.md).
