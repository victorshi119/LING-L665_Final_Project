# Topic and Entity Labels

**Team:** Victor & Shintaro, L665 (Fall 2026)

## Topic

Our topic is **dysarthria associated with cerebral palsy (CP)**: the motor speech disorder that most people with CP have, how clinicians assess and treat it, and the speech technology used to recognize, assess, and support dysarthric speech.

Cerebral palsy is a group of non-progressive movement disorders caused by injury to the developing brain. Many people with CP, especially those with the spastic and dyskinetic subtypes, have dysarthria: weak, slow, or poorly coordinated speech muscles make their speech hard to understand. The research literature on this topic has two sides:

* **Clinical:** speech-language pathology research describes the speech features (hypernasality, imprecise consonants, reduced intelligibility), measures them with standard instruments (Frenchay Dysarthria Assessment, Viking Speech Scale, GMFCS), and evaluates treatments (speech therapy, AAC).
* **Technical:** speech-technology research builds automatic speech recognition (ASR), dysarthria detection, and voice conversion systems, mostly trained and tested on dysarthric speech corpora such as UASpeech and TORGO, whose speakers mostly have CP.

The corpus includes papers on dysarthria from other causes (Parkinson's disease, ALS, stroke), because the clinical features, instruments, and technology are shared. We therefore also label those disorders.

## Entity labels

We use six labels. Each glossary concept has exactly one label.

| Label | What it covers | Examples | Not included |
|---|---|---|---|
| `DISORDER` | Diseases, disorders, and clinical motor signs: dysarthria and its subtypes, CP and its subtypes, other conditions that cause dysarthria, and related speech, language, and swallowing disorders. | spastic dysarthria, cerebral palsy (CP), Parkinson's disease, apraxia of speech, dysphagia, spasticity | Symptoms of speech itself (→ `SPEECH_FEATURE`) |
| `SPEECH_FEATURE` | Perceptual or acoustic properties of speech that are affected in dysarthria or used to describe it. | speech intelligibility, hypernasality, imprecise consonants, speech rate, F0, jitter, vowel space area | The disorder (→ `DISORDER`) or the test that measures the feature (→ `ASSESSMENT`) |
| `ASSESSMENT` | Named clinical instruments, rating scales, and classification systems for speech, communication, or motor function. | Frenchay Dysarthria Assessment (FDA), GMFCS, Viking Speech Scale, ALSFRS-R, auditory-perceptual assessment | Automatic metrics such as WER (→ `SPEECH_TECH`) |
| `TREATMENT` | Clinical interventions, therapies, devices, and drugs. | speech therapy, AAC, speech-generating device, LSVT LOUD, botulinum toxin | Speech technology not used as a clinical intervention (→ `SPEECH_TECH`) |
| `SPEECH_TECH` | Speech-technology tasks, models, acoustic representations, and evaluation metrics. | automatic speech recognition (ASR), wav2vec 2.0, Whisper, MFCC, word error rate (WER), voice conversion | Named corpora (→ `DATASET`) |
| `DATASET` | Named speech corpora and databases. | UASpeech, TORGO, EasyCall, Speech Accessibility Project, LibriSpeech | |

### Why these labels

* They follow the structure of the domain: a **disorder** produces **speech features**, which are measured by **assessments**, managed by **treatments**, and modelled by **speech technology** trained on **datasets**. In Assignment 2 this gives the knowledge graph typed relations (e.g. DISORDER → *has feature* → SPEECH_FEATURE, ASSESSMENT → *measures* → SPEECH_FEATURE, SPEECH_TECH → *evaluated on* → DATASET).
* We first planned five labels. We added `DATASET` after counting candidate terms in the corpus: TORGO (1,161 mentions) and UASpeech (821) are among the most frequent domain terms, and datasets behave differently from methods.
* Labels are kept small (6). Every label has at least 10 glossary concepts, so the model sees enough examples of each.

## Ambiguity decisions

* **Acronyms** match with exact case only (`CP` but not `cp`).
* Acronyms with other common readings in the corpus (`FDA`, `SGD`, `SLT`, `MS`, `VC`, `AIDS`, `SAP`, ...) are only labelled in a document that also contains the concept's full name.
* Borderline concepts were assigned by their main use in the corpus. For example, `dysphonia` is a `DISORDER` (a voice disorder), while `breathiness` is a `SPEECH_FEATURE`. `Mean opinion score` is `SPEECH_TECH` (a synthesis evaluation metric), not `ASSESSMENT`.
