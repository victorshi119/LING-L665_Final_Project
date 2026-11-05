# Inspected examples (test split)

Reference = rule-generated weak labels. Contexts are 12 tokens either side; the entity is in bold.

## Agreements (model = rules)

- `pubmed_39682602` SPEECH_FEATURE: of feature extraction relevant to naturalness, causing significant degradation in both **naturalness** Figure 7. Effect of removing speaker-encoder on naturalness
- `arxiv_2506.01618` SPEECH_FEATURE: preventing artifacts. Further, these methods do not require highly precise **speaking rate** calculations, as long as the overall speaking rate is increased for
- `pubmed_39682602` SPEECH_TECH: the articulation errors described in the condition. Figure 5 is a **Mel-spectrogram** of the same speech sample. This plot visualizes the frequency content
- `pubmed_36480697` SPEECH_FEATURE: speaker condition. Paired samples t-tests showed there were significant **intelligibility** improvements for each speaker from pretest to posttest (all p <
- `arxiv_2601.21205` SPEECH_FEATURE: segmental breakdown, making it well suited as a global proxy for **intelligibility** severity. PFER, in contrast, models phoneme errors as graded
- `arxiv_2506.01618` SPEECH_TECH: particularly beneficial for the LF-MMI model, leading to noticeable **WER** reductions, especially for speakers with severe and moderately severe dysarthria.
- `pubmed_39682602` SPEECH_TECH: . Randomly initialize the centers for K - 1 clusters using the **MFCC** features. 2. Set the center for the K-th
- `arxiv_2506.16528` SPEECH_TECH: LLMs with Whisper [7] and WavLM [15] for **ASR** tasks, and (2) the GPT-4 API [16]
- `arxiv_2110.08213` SPEECH_TECH: The reference is compared to the VC utterances transcribed by the trained **ASR** . 4.4. Subjective evaluation protocols Subjective evaluation was carried
- `pubmed_2629622` DISORDER: cate was cerebral palsy. Little, Osler, and Freud described **cerebral palsy** not The definition of cerebral palsy used was that as a disease
- `arxiv_2506.16528` SPEECH_TECH: Wavllm ; 35.85 ; 0.9718 ; 0.5334 ; -0.5769 ; 0.1976 **Whisper** ; 34.72 ; 0.9387 ; 0.6516 ; 0.0183 ; 0.1700 w/
- `arxiv_2306.10588` DISORDER: speaking individual into an atypical one. Atypical speech in people with **dysarthria** or dysphonia can be caused by a traumatic injury or a neurological
- `arxiv_2505.22072` SPEECH_TECH: obtained without domain knowledge. 2. Batch-Mode MoE **Speaker Adaptation** Backbone Speech Foundation Models (SFMs): SSL speech foundation models
- `arxiv_2201.05845` SPEECH_TECH: INTRODUCTION D ESPITE the rapid progress of automatic speech recognition ( **ASR** ) technologies in the past few decades, recognition of disordered speech
- `arxiv_2209.13260` SPEECH_FEATURE: , with lower values for PCC, PCV, PCP, triangular **VSA** , quadrilateral VSA, VAI, F2-ratio, and higher

## Label conflicts (same span, different label)

- none

## Model-only spans (most frequent; candidate glossary additions or model errors)

- **hts** → SPEECH_TECH ×22 — `arxiv_2408.03399`: -of-the-art algorithms for hierarchical time series ( **HTS** ) forecasting rely on both the autocorrelation of each time series and
- **asr** → SPEECH_TECH ×12 — `arxiv_2606.20266`: on a reference transcript at inference time, obtained from an external **ASR** system. This dependency makes zero-shot TTS brittle for accented
- **moss** → SPEECH_TECH ×4 — `pubmed_39682602`: phoneme prediction accuracy and overall voice conversion quality. It achieved higher **MOSs** for naturalness, intelligibility, and speaker similarity compared to existing models
- **thria** → DISORDER ×4 — `pubmed_39682602`: closely resembles normal speech patterns while effectively mitigating the effects of dysar- **thria** . Figure 1 illustrates the structure of the FEMPPDM-DVC framework
- **pc** → DISORDER ×3 — `arxiv_2606.20266`: predicted by UTMOS [31]. Model ; LibriSpeech- **PC** - WER↓ ; LibriSpeech-PC - SIM↑ ; LibriSpeech-PC
- **cerebral vascular** → DISORDER ×2 — `arxiv_1807.10948`: 's Disease (PD), four patients who have had a **Cerebral Vascular** Accident (CVA), one patient who suffered Traumatic Brain Injury
- **imprecise speakers** → SPEECH_FEATURE ×2 — `arxiv_1911.11360`: These results also indicate that our objective hypernasality ratings for the most **imprecise speakers** are not reliable. While this is a limitation of the approach
- **imprecise segmentation** → SPEECH_FEATURE ×2 — `arxiv_2506.01618`: approach used was not specifically adapted to dysarthric speech, resulting in **imprecise segmentation** and rhythm modification. Furthermore, while ASR performance improved, it
- **text-speech** → SPEECH_TECH ×2 — `arxiv_2606.20266`: 14, 15]. A major challenge for these models is **text-speech** alignment: parallel generation requires inferring phoneme durations to align text with
- **speech recognition** → SPEECH_TECH ×2 — `arxiv_2609.28877`: LEARNING NEW WORDS FROM UNLABELED TEST DATA IN AUTOMATIC **SPEECH RECOGNITION** Mengqi Wang⋆ Mark A. Hasegawa-Johnson⋆ Haolong Zheng⋆ Chang D.
- **voice synthesis** → SPEECH_TECH ×2 — `arxiv_cmp-lg_9506018`: their speech, etc. For all these people, no **voice synthesis** with an interface based on letter or word selection would make up
- **text-tospeech (** → SPEECH_TECH ×2 — `pubmed_38606392`: individuals following standard clinical procedures, or that have been synthesized using **text-tospeech (** TTS). Particularly, we hypothesize that 1) fine-
- **dnn-hidden markov model** → SPEECH_TECH ×1 — `arxiv_1807.10948`: [18], we described a solution to train a better **DNN-hidden Markov model** (HMM) system for the Dutch language, a language that
- **cerebral vascular accident** → DISORDER ×1 — `arxiv_1905.06533`: of neurological disorders such as Parkinson's disease (PD), **cerebral vascular accident** (CVA or stroke) and traumatic brain injury (TBI)
- **formant amplitude** → SPEECH_FEATURE ×1 — `arxiv_1911.11360`: [70]. These formant features (FF) included F1 **formant amplitude** , P0 nasality peak amplitude, and normalized and raw A1 -
- **perceptual hypernasality** → ASSESSMENT ×1 — `arxiv_1911.11360`: , when evaluated on disordered speech, track the expected trends in **perceptual hypernasality** ratings, and can be used with ridge regression to estimate a
- **speed-perturbation** → SPEECH_TECH ×1 — `arxiv_2201.05562`: different data augmentation techniques for disordered speech recognition. It suggests that **speed-perturbation** based augmentation produces the largest improvement in system performance despite the huge
- **oracle error rates** → SPEECH_FEATURE ×1 — `arxiv_2201.05845`: found in UASpeech training data. Similar performance rank in terms of **oracle error rates** (last column in Table II) between the CTC and LAS
- **imprecise articulators** → SPEECH_FEATURE ×1 — `arxiv_2201.05845`: the spectral envelope to simulate different vocal tract lengths potentially resulted from **imprecise articulators** ' movements while keeping the speech duration fixed; ii) tempo
- **cerebral palsy(cp** → DISORDER ×1 — `arxiv_2208.03648`: in language, cognition, motor, intelligence, and even cause **cerebral palsy(CP** ) [16]. Diagnoses of CP are critical for early
- **f0s** → SPEECH_FEATURE ×1 — `arxiv_2209.13260`: Pitch and loudness measurements manifest dysarthric speakers have limitations in producing stable **F0s** and need greater minimum energy for speech production. Lastly, rhythmmeasurements
- **sgd** → TREATMENT ×1 — `arxiv_2210.15387`: , relu, logistic, identity function, optimizer between Adam and **SGD** , and learning rate between 10-4 and 10-1
- **strangled voice** → SPEECH_FEATURE ×1 — `arxiv_2306.10588`: quality, harsh voice, hoarse voice, breathiness, strained/ **strangled voice** , stoppages and flutter. The ratings ranged between 0 and 4
- **speed rate** → SPEECH_TECH ×1 — `arxiv_2306.10588`: we added random Gaussian noises, SpecAugment [30] and changed **speed rate** with ratio {0.9, 1.0, 1.1} for data augmentation
- **pi-gita** → DATASET ×1 — `arxiv_2410.09289`: MM-Score for all datasets and QCP Glottal flow on the **PI-GITA** . This advantage is largely because these baselines neglect the benefits of
- **vc** → SPEECH_TECH ×1 — `arxiv_2505.22072`: offline batch-mode MoE-based method, JHU-2023 DuTa- **VC** (Diffusion) + Conformer [40] 6 The RAB
- **imprecise pronunciation** → SPEECH_FEATURE ×1 — `arxiv_2506.16127`: . As a result, affected individuals may experience slurred articulation, **imprecise pronunciation** , reduced speech volume, and altered speech rhythm, making verbal
- **self-supervised asr** → SPEECH_TECH ×1 — `arxiv_2508.08027`: ASR) particularly challenging [1, 2, 3]. **Self-supervised ASR** models such as HuBERT [4], and Wav2Vec 2.0 [
- **automatic speech recognizers** → SPEECH_TECH ×1 — `arxiv_2601.21205`: phone annotations, which are difficult to obtain for dysarthric speech. **Automatic speech recognizers** (ASR) have also been used, with Word Error Rate
- **librispeechpc** → DATASET ×1 — `arxiv_2606.20266`: . For typical speakers, we use test-clean split of **LibriSpeechPC** [25] and test-en split of SeedTTS [26
- **imprecise phonation** → SPEECH_FEATURE ×1 — `arxiv_2609.20875`: manifests itself as hypophonia, monoprosody, reduced articulation rate, and **imprecise phonation** , often emerging early and evolving with disease progression and medication state
- **pd** → DISORDER ×1 — `arxiv_2609.20875`: visited: 2026-09-15.](https://github.com/simon-hjp/ **pd** -speech-embedding-severity-classification) Fig.
- **mds-updrss** → ASSESSMENT ×1 — `arxiv_2609.20875`: [20]. The top row indicates the ground-truth **MDS-UPDRSS** speech scores, or HC where applicable. Fig. 7
- **acquired cerebral palsy** → DISORDER ×1 — `pubmed_2629622`: **Acquired cerebral palsy** P O D PHAROAH, T COOKE, AND L ROSENBLOOM
- **cerebral palsy.⁵** → DISORDER ×1 — `pubmed_2629622`: the insult occurs for differentiating between congenital' and 'acquired' **cerebral palsy.⁵** Blair and Stanley included individuals born free of brain damage who cerebral
- **audibility** → SPEECH_FEATURE ×1 — `pubmed_38606392`: 24]. Factors such as speech variability, articulation, **audibility** , and accent can manifest different impacts on the performance of ASR
- **mel-spectrogramvisualization** → SPEECH_TECH ×1 — `pubmed_39682602`: of juvenile dysphonia.  Mel-spectrogram Visualization: · **Mel-spectrogramVisualization** Diagnostics 2024, 14, x FOR PEER REVIEW Figure

## Rule-only spans (most frequent; missed by the model)

- **spastic quadriplegia** (DISORDER) ×5 — `pubmed_2629622`: that was not self propelled. The cases were grouped into **spastic quadriplegia** , spastic hemiplegia, and 'others'. Spastic quadriplegia included
- **spastic hemiplegia** (DISORDER) ×5 — `pubmed_2629622`: self propelled. The cases were grouped into spastic quadriplegia, **spastic hemiplegia** , and 'others'. Spastic quadriplegia included quadriplegia, double
- **speech accessibility project** (DATASET) ×4 — `arxiv_2506.16127`: 3.4.2. Finetuning We finetuned the pretrained model on the **Speech Accessibility Project** dataset [16]. The fine-tuning process follows the
- **voice conversion** (SPEECH_TECH) ×3 — `arxiv_2110.08213`: TOWARDS IDENTITY PRESERVING NORMAL TO DYSARTHRIC **VOICE CONVERSION** Wen-Chin Huang1*, Bence Mark Halpern2,3,4*,
- **i-vector** (SPEECH_TECH) ×3 — `arxiv_2201.05845`: PERFORMANCE COMPARISON BETWEEN DIFFERENT ADAPTATION METHODS INCLUDING AUXILIARY SPEAKER EMBEDDING ( **I-VECTOR** ) AND MODEL BASED ADAPTATION (LHUC, HUB AND PACT)
- **hypernasal speech** (SPEECH_FEATURE) ×2 — `arxiv_1911.11360`: 34] [35] have been proposed to detect or evaluate **hypernasal speech** . These spectral modifications in hypernasal speech will have an impact on
- **speed perturbation** (SPEECH_TECH) ×2 — `arxiv_2201.05562`: including vocal tract length perturbation (VTLP), tempo perturbation and **speed perturbation** . Both normal and disordered speech were exploited in the augmentation process
- **severity classifications** (SPEECH_TECH) ×2 — `arxiv_2512.17474`: to the dysarthric subset and stratified analyses by the corpus-provided **severity classifications** : mild (speakers F04, M03), moderate (speakers
- **automatic speech recognition** (SPEECH_TECH) ×2 — `arxiv_2609.28877`: LEARNING NEW WORDS FROM UNLABELED TEST DATA IN **AUTOMATIC SPEECH RECOGNITION** Mengqi Wang⋆ Mark A. Hasegawa-Johnson⋆ Haolong Zheng⋆ Chang D.
- **hidden markov model** (SPEECH_TECH) ×1 — `arxiv_1807.10948`: ], we described a solution to train a better DNN- **hidden Markov model** (HMM) system for the Dutch language, a language that
- **gmm-hmm** (SPEECH_TECH) ×1 — `arxiv_1905.06533`: the performance of a speaker-dependent and a speaker-adaptive **GMM-HMM** systems on the Nemours database [46]. Later, Rudzicz
- **formant** (SPEECH_FEATURE) ×1 — `arxiv_1911.11360`: [70]. These formant features (FF) included F1 **formant** amplitude, P0 nasality peak amplitude, and normalized and raw A1
- **hypernasality** (SPEECH_FEATURE) ×1 — `arxiv_1911.11360`: when evaluated on disordered speech, track the expected trends in perceptual **hypernasality** ratings, and can be used with ridge regression to estimate a
- **pc-gita** (DATASET) ×1 — `arxiv_2011.07545`: databases. Database ; CNN ; AUC ; Accuracy Spanish **PC-GITA** Spanish PC-GITA Spanish PC-GITA ; Baseline B-
- **nemours** (DATASET) ×1 — `arxiv_2201.05845`: ] ; 6.3 ; 16 ; - ; 2016 English ( **Nemours** ) [18] ; 2.5-3 ; 11 ; -
- **tempo perturbation** (SPEECH_TECH) ×1 — `arxiv_2201.05845`: TABLE III COMPARISON OF THE IMPLEMENTATION DOMAIN AND EFFECTS OF VTLP, **TEMPO PERTURBATION** AND SPEED PERTURBATION ON MODIFIED SPEECH SIGNAL. "3" INDICATES
- **hnr** (SPEECH_FEATURE) ×1 — `arxiv_2209.13260`: 0.59 3.48 ; 0.60 3.39 ; 0.54 3.34 ; 0.73 4.14 **HNR** ; 9.95 ; 12.94 ; 11.39 ; 18.03 ; 11.96 ; 16.27
- **vsas** (SPEECH_FEATURE) ×1 — `arxiv_2209.13260`: the opposite trend. English healthy speakers have slightly smaller sizes of **VSAs** and higher FCR, lower VAI, and lower F2Ratio compared to
- **severity classification** (SPEECH_TECH) ×1 — `arxiv_2210.15387`: AUTOMATIC **SEVERITY CLASSIFICATION** OF DYSARTHRIC SPEECH BY USING SELF-SUPERVISED MODEL WITH MULTI-
- **phone error rate** (SPEECH_TECH) ×1 — `arxiv_2210.15387`: α and e. Bigger the α and later the e, the **phone error rate** (PER) consistently drops, since the emphasis on the LCTC
- **ctc** (SPEECH_TECH) ×1 — `arxiv_2306.07090`: LASR,Trans is the loss from transformer decoder, LASR, **CTC** is the loss fromCTC decoder. If we train the fusion
- **parkinson disease** (DISORDER) ×1 — `arxiv_2410.09289`: RESULTS ON THE COVID-19 (COSWARA, SOUND-DR) AND **PARKINSON DISEASE** (IPVS, PC-GITA) DATASETS IN TERMS OF AVERAGE
- **x-vector** (SPEECH_TECH) ×1 — `arxiv_2505.22072`: / 21.87† ; / 11.98 / 2.68 ; 20.69† ; 0.36 **x-vector** ; - ; ✓ ; 55.20† / ; 21.19† / 11.53 ;
- **mel-spectrograms** (SPEECH_TECH) ×1 — `arxiv_2506.16127`: show that acoustic discrete units not only achieve significantly faster convergence than **mel-spectrograms** but also produce speech with higher intelligibility. Additionally, we demonstrate
- **asr** (SPEECH_TECH) ×1 — `arxiv_2508.08027`: challenging [1, 2, 3]. Self-supervised **ASR** models such as HuBERT [4], and Wav2Vec 2.0 [
