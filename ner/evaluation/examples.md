# Inspected examples (test split)

Reference = rule-generated weak labels. Contexts are 12 tokens either side; the entity is in bold.

## Agreements (model = rules)

- `pubmed_39682602` SPEECH_TECH: for restoring intelligibility in dysarthric speech, as reflected in its lower **WER** scores. Figure 6 showcases the WER scores for different voice
- `arxiv_2506.01618` DISORDER: the original and vocoded data, particularly for speakers with more severe **dysarthria** . Combining these methods further reduces WER, except for speaker M04
- `pubmed_39682602` SPEECH_FEATURE: voice conversion or dysarthria classification. Juvenile dysphonia manifests in various **articulation** errors, including sound substitutions (e.g., saying "wabbit"
- `pubmed_36480697` DISORDER: selected from a database of speakers with dysarthria, collected in the **Motor Speech Disorders** Lab at Arizona State University (see Liss et al.,
- `arxiv_2601.21205` SPEECH_FEATURE: , these results indicate that non-contrastive features contribute little to **intelligibility** prediction within this framework and, when influential, tend to reduce
- `arxiv_2506.01618` SPEECH_TECH: alone and outperforms rhythm conversion alone. Figure 5 presents the **WER** results per speaker for different configurations. For sentences, the vocoded
- `pubmed_39682602` SPEECH_FEATURE: level of speech intelligibility, along with specific patterns of articulation and **phonation** disruption. By tailoring the model to the individual characteristics of each
- `arxiv_2506.16528` SPEECH_TECH: whether phonetic similarity, semantic similarity, and WER contribute to predicting **ASR** correctability. To investigate this, we tested two LLM-based
- `arxiv_2110.08213` SPEECH_TECH: RQ1 and RQ3). We use a pre-trained Kaldi **ASR** model with the same specifications as the one used in [22
- `pubmed_24301005` DISORDER: ask parents for assessment of feeding/swallowing problems in children with **cerebral palsy** Questions ; Red flags How long does it take to
- `arxiv_2506.16528` SPEECH_TECH: (0.9919 vs. 0.9831). Table 3: Evaluation of **ASR** Systems on Dysarthric Speech, w/ and w/o GPT corrections. "
- `arxiv_2306.10588` DATASET: is applied to reconstruct the waveform. Objective evaluations conducted on the **UASpeech** show that DuTa-VC is able to capture severity characteristics of
- `arxiv_2505.22072` DATASET: and feedforward. 2) Performance: Experimental results on the **UASpeech** [33] dysarthric corpus suggest that i) the proposed on
- `arxiv_2201.05845` SPEECH_TECH: search, data augmentation using spectra-temporal perturbation, model based **speaker adaptation** and cross-domain generation of visual features within an audio-
- `arxiv_2209.13260` SPEECH_FEATURE: FCR, lower VAI and F2-Ratio are found as the **intelligibility** level gets lower. While Korean and Tamil healthy speakers keep these

## Label conflicts (same span, different label)

- none

## Model-only spans (most frequent; candidate glossary additions or model errors)

- **hts** → SPEECH_TECH ×22 — `arxiv_2408.03399`: -of-the-art algorithms for hierarchical time series ( **HTS** ) forecasting rely on both the autocorrelation of each time series and
- **asr** → SPEECH_TECH ×12 — `arxiv_2606.20266`: on a reference transcript at inference time, obtained from an external **ASR** system. This dependency makes zero-shot TTS brittle for accented
- **mltcs** → SPEECH_TECH ×5 — `arxiv_2503.08378`: is a lack of comprehensive studies examining the co-occurrences of **MLTCs** in adults with intellectual disability[4]. Moreover, sex differences in
- **thria** → DISORDER ×5 — `pubmed_39682602`: closely resembles normal speech patterns while effectively mitigating the effects of dysar- **thria** . Figure 1 illustrates the structure of the FEMPPDM-DVC framework
- **moss** → SPEECH_TECH ×4 — `pubmed_39682602`: phoneme prediction accuracy and overall voice conversion quality. It achieved higher **MOSs** for naturalness, intelligibility, and speaker similarity compared to existing models
- **pc -** → DATASET ×3 — `arxiv_2606.20266`: predicted by UTMOS [31]. Model ; LibriSpeech- **PC -** WER↓ ; LibriSpeech-PC - SIM↑ ; LibriSpeech-PC -
- **ters** → SPEECH_TECH ×3 — `pubmed_39682602`: :  Calculate the distance between the previous and current cluster cen- **ters** .  If the distance is less than a predefined threshold:
- **hypernasal speakers** → SPEECH_FEATURE ×2 — `arxiv_1911.11360`: of AP(Xpj ) for unvoiced phonemes to be high, whereas for **hypernasal speakers** , we expect it to be lower. Fig. 4
- **sgd** → TREATMENT ×2 — `arxiv_2011.07545`: representations. All networks are trained using the stochastic gradient descent ( **SGD** ) algorithm and the cross-entropy loss. The batch size
- **informer** → SPEECH_TECH ×2 — `arxiv_2412.14435`: cases are included. Other models, such as TCN and **Informer** , exhibit much larger variances, with rankings ranging from 1 to
- **lm** → SPEECH_TECH ×2 — `arxiv_2609.28877`: hypotheses for an input utterance. Word spans with strong CTC- **LM** preference disagreement are selected as potential OOV regions (one span here
- **voice synthesis** → SPEECH_TECH ×2 — `arxiv_cmp-lg_9506018`: their speech, etc. For all these people, no **voice synthesis** with an interface based on letter or word selection would make up
- **dnn-hidden markov model** → SPEECH_TECH ×1 — `arxiv_1807.10948`: [18], we described a solution to train a better **DNN-hidden Markov model** (HMM) system for the Dutch language, a language that
- **cerebral vascular** → DISORDER ×1 — `arxiv_1807.10948`: 's Disease (PD), four patients who have had a **Cerebral Vascular** Accident (CVA), one patient who suffered Traumatic Brain Injury
- **cerebral vascular accident** → DISORDER ×1 — `arxiv_1905.06533`: of neurological disorders such as Parkinson's disease (PD), **cerebral vascular accident** (CVA or stroke) and traumatic brain injury (TBI)
- **hmm** → SPEECH_TECH ×1 — `arxiv_1905.06533`: of a speaker-dependent and a speaker-adaptive GMM- **HMM** systems on the Nemours database [46]. Later, Rudzicz
- **motor-speech disorders** → DISORDER ×1 — `arxiv_1911.11360`: the oral and nasal cavities. Hypernasality is a common symptom in **motor-speech disorders** such as Parkinson's Disease (PD), Huntington's Disease
- **universal access speech** → DATASET ×1 — `arxiv_2201.05562`: an extended version of the Kaldi toolkit [35] for the **Universal Access Speech** (UASpeech) database. Learning hidden unit contributions (LHUC
- **speed-perturbation** → SPEECH_TECH ×1 — `arxiv_2201.05562`: different data augmentation techniques for disordered speech recognition. It suggests that **speed-perturbation** based augmentation produces the largest improvement in system performance despite the huge
- **oracle error rates** → SPEECH_FEATURE ×1 — `arxiv_2201.05845`: found in UASpeech training data. Similar performance rank in terms of **oracle error rates** (last column in Table II) between the CTC and LAS
- **speaker level adaptation** → SPEECH_TECH ×1 — `arxiv_2201.05845`: IN BRACKETS). THE BOLD RESULTS INDICATE THE SMALLEST AMOUNTS OF **SPEAKER LEVEL ADAPTATION** DATA THAT CAN PRODUCE PERFORMANCE IMPROVEMENTS OVER THE UN-ADAPTED SYSTEMS
- **cerebral palsy(cp** → DISORDER ×1 — `arxiv_2208.03648`: in language, cognition, motor, intelligence, and even cause **cerebral palsy(CP** ) [16]. Diagnoses of CP are critical for early
- **dysarthria** → DISORDER ×1 — `arxiv_2209.13260`: to investigate acoustic indicators with high discrimination power for intelligibility classification ( **dysarthria** severity classification). Features from diverse speech dimensions, such as
- **f0s** → SPEECH_FEATURE ×1 — `arxiv_2209.13260`: Pitch and loudness measurements manifest dysarthric speakers have limitations in producing stable **F0s** and need greater minimum energy for speech production. Lastly, rhythmmeasurements
- **v-vectors** → SPEECH_TECH ×1 — `arxiv_2306.07090`: be initialize close to the identity matrix, we use couples of **v-vectors** : <!-- formula-not-decoded -->
- **c** → SPEECH_TECH ×1 — `arxiv_2306.07090`: its parameters. Table 2 compares the CER for using different **C** values in model Fusion-WC with the baseline case Fusion-
- **articulation,** → SPEECH_FEATURE ×1 — `arxiv_2309.09329`: sclerosis (ALS). Individuals with dysarthria encounter difficulties related to **articulation,** speech rate, breath control, resonance, and overall communication [
- **tc** → SPEECH_TECH ×1 — `arxiv_2410.09289`: first embedded by mul- tiple 1-D temporal convolution ( **TC** ) layers to obtain convo- luted unimodal feature sequences with the
- **frequency cepstral coefficients** → SPEECH_TECH ×1 — `arxiv_2410.09289`: Mel Spectrogram, Mel Frequency Cepstral Coefficients (MFCC), GammaTone **Frequency Cepstral Coefficients** (GFCC), and Constant Q Cepstral Coefficients (CQCC)
- **pi-gita** → DATASET ×1 — `arxiv_2410.09289`: MM-Score for all datasets and QCP Glottal flow on the **PI-GITA** . This advantage is largely because these baselines neglect the benefits of
- **ltcs** → SPEECH_TECH ×1 — `arxiv_2503.08378`: patient demographics, and Supp. Table S.0 presents the list of **LTCs** . Data collected at GPs were recorded using Read codes v2,
- **ers** → SPEECH_TECH ×1 — `arxiv_2505.22072`: dysarthric speech dataset containing 16 dysarthric and 13 control speak- **ers** . It includes 155 common and 300 uncommon words and is
- **vc** → SPEECH_TECH ×1 — `arxiv_2505.22072`: offline batch-mode MoE-based method, JHU-2023 DuTa- **VC** (Diffusion) + Conformer [40] 6 The RAB
- **mel-spectrogrambased** → SPEECH_TECH ×1 — `arxiv_2506.16127`: acoustic units in improving intelligibility while achieving faster convergence compared to traditional **mel-spectrogrambased** approaches. Index Terms: dysarthric speech, conditional-flow
- **bert** → SPEECH_TECH ×1 — `arxiv_2506.16528`: In contrast, Whisper generates hypotheses with higher lexical semantic similarity ( **BERT** and BLEURT) to the reference transcript but not necessarily with high
- **automatic speech recognizers** → SPEECH_TECH ×1 — `arxiv_2601.21205`: phone annotations, which are difficult to obtain for dysarthric speech. **Automatic speech recognizers** (ASR) have also been used, with Word Error Rate
- **updrsspeech** → ASSESSMENT ×1 — `arxiv_2601.21205`: Participants produced 25 isolated words. Each speaker was evaluated using the **UPDRSspeech** scale, which rates speech impairment severity from 0 (normal)
- **text-speech** → SPEECH_TECH ×1 — `arxiv_2606.20266`: -level zero-shot TTS. F5-TTS further improves **text-speech** alignment by refining the padded character sequence with an additional text encoder
- **-supervised learning** → SPEECH_TECH ×1 — `arxiv_2606.20266`: reference transcripts, we replace text-based reference features with self **-supervised learning** (SSL) speech representations. Given a reference waveform aref ,
- **pc** → SPEECH_TECH ×1 — `arxiv_2606.20266`: -shot TTS benchmarks with typical speakers. On LibriSpeech- **PC** , RTFree-F5 (Stage 2) achieves a WER of

## Rule-only spans (most frequent; missed by the model)

- **whisper** (SPEECH_TECH) ×17 — `arxiv_2309.09329`: Very-Low ; 2 ; 72 B. Whisper Model **Whisper** [15] is an Automatic Speech Recognition (ASR) system
- **spastic quadriplegia** (DISORDER) ×5 — `pubmed_2629622`: that was not self propelled. The cases were grouped into **spastic quadriplegia** , spastic hemiplegia, and 'others'. Spastic quadriplegia included
- **spastic hemiplegia** (DISORDER) ×5 — `pubmed_2629622`: self propelled. The cases were grouped into spastic quadriplegia, **spastic hemiplegia** , and 'others'. Spastic quadriplegia included quadriplegia, double
- **voice conversion** (SPEECH_TECH) ×3 — `arxiv_2110.08213`: TOWARDS IDENTITY PRESERVING NORMAL TO DYSARTHRIC **VOICE CONVERSION** Wen-Chin Huang1*, Bence Mark Halpern2,3,4*,
- **hubert** (SPEECH_TECH) ×3 — `arxiv_2508.08027`: otl omner shrugg Whisper ; 0.18 ; the hotel man **HuBERT** -BART ; 0.14 ; The otel owner shrug Whisper-
- **ctc** (SPEECH_TECH) ×2 — `arxiv_2306.07090`: LASR,Trans is the loss from transformer decoder, LASR, **CTC** is the loss fromCTC decoder. If we train the fusion
- **asr** (SPEECH_TECH) ×2 — `arxiv_2506.01618`: to 5 epochs. There is no additional language model. **ASR** performance is assessed using the word error rate (WER).
- **speech recognition** (SPEECH_TECH) ×2 — `arxiv_2512.17474`: Benchmarking Commercial **Speech Recognition** and Multimodal Large Language Models on Dysarthric Speech: SeverityStratified Baselines and
- **hidden markov model** (SPEECH_TECH) ×1 — `arxiv_1807.10948`: ], we described a solution to train a better DNN- **hidden Markov model** (HMM) system for the Dutch language, a language that
- **log-mel filterbank** (SPEECH_TECH) ×1 — `arxiv_1807.10948`: on the alignments from the GMM-HMM system. The 40dimensional **log-mel filterbank** (FB) features with the deltas and delta-deltas are
- **gmm-hmm** (SPEECH_TECH) ×1 — `arxiv_1905.06533`: the performance of a speaker-dependent and a speaker-adaptive **GMM-HMM** systems on the Nemours database [46]. Later, Rudzicz
- **tempo perturbation** (SPEECH_TECH) ×1 — `arxiv_2201.05845`: TABLE III COMPARISON OF THE IMPLEMENTATION DOMAIN AND EFFECTS OF VTLP, **TEMPO PERTURBATION** AND SPEED PERTURBATION ON MODIFIED SPEECH SIGNAL. "3" INDICATES
- **dysarthria severity classification** (SPEECH_TECH) ×1 — `arxiv_2209.13260`: to investigate acoustic indicators with high discrimination power for intelligibility classification ( **dysarthria severity classification** ). Features from diverse speech dimensions, such as features related
- **vsas** (SPEECH_FEATURE) ×1 — `arxiv_2209.13260`: the opposite trend. English healthy speakers have slightly smaller sizes of **VSAs** and higher FCR, lower VAI, and lower F2Ratio compared to
- **articulation** (SPEECH_FEATURE) ×1 — `arxiv_2309.09329`: sclerosis (ALS). Individuals with dysarthria encounter difficulties related to **articulation** , speech rate, breath control, resonance, and overall communication
- **wavlm** (SPEECH_TECH) ×1 — `arxiv_2506.16127`: ], which require additional enhancement stages before source separation. **WavLM** employs a feature encoder consisting of local temporal convolutional blocks, where
- **mel-spectrograms** (SPEECH_TECH) ×1 — `arxiv_2506.16127`: show that acoustic discrete units not only achieve significantly faster convergence than **mel-spectrograms** but also produce speech with higher intelligibility. Additionally, we demonstrate
- **speech recognizers** (SPEECH_TECH) ×1 — `arxiv_2601.21205`: annotations, which are difficult to obtain for dysarthric speech. Automatic **speech recognizers** (ASR) have also been used, with Word Error Rate
- **per** (SPEECH_TECH) ×1 — `arxiv_2601.21205`: KENDALL'S τ BETWEEN BASELINE FEATURES AND INTELLIGIBILITY SCORES. BEST PERFORMANCE **PER** LANGUAGE IS HIGHLIGHTED IN BOLD. Features ; English ; Spanish
- **self-supervised learning** (SPEECH_TECH) ×1 — `arxiv_2606.20266`: on reference transcripts, we replace text-based reference features with **self-supervised learning** (SSL) speech representations. Given a reference waveform aref ,
- **phonation** (SPEECH_FEATURE) ×1 — `arxiv_2609.20875`: itself as hypophonia, monoprosody, reduced articulation rate, and imprecise **phonation** , often emerging early and evolving with disease progression and medication state
- **automatic speech recognition** (SPEECH_TECH) ×1 — `arxiv_2609.28877`: LEARNING NEW WORDS FROM UNLABELED TEST DATA IN **AUTOMATIC SPEECH RECOGNITION** Mengqi Wang⋆ Mark A. Hasegawa-Johnson⋆ Haolong Zheng⋆ Chang D.
- **cerebral palsy** (DISORDER) ×1 — `pubmed_2629622`: Acquired **cerebral palsy** P O D PHAROAH, T COOKE, AND L ROSENBLOOM
- **speech rate** (SPEECH_FEATURE) ×1 — `pubmed_39682602`: movements. This type is characterized by irregular articulatory breakdowns, variable **speech rate** , and a jerky, uneven quality of speech [10]
