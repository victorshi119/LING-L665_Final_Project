# Rule-label inspection (Assignment 1, step 5)

The glossary rules labelled 32,793 entity mentions in the 301 training documents. These are weak
labels, so the assignment asks us to inspect a sample by hand and correct or document obvious errors.

Full pipeline, DocBins and model: `/N/u/shinsaka/BigRed200/CP_Dysarthria_Pubmed_md/ner_assignment1/`
on Quartz (not in this repo: the texts' licenses don't allow redistribution).

## Files

* `rule_sample.csv`: 120 mentions, 20 random ones per label (seed 665), each with about 12 words of
  context on either side and the match in **bold**. Made by `inspect_rule_labels.py`.
* `rule_surface_forms.md`: the 15 most frequent matched forms per label, with mention and document
  counts. One wrong pattern here affects hundreds of mentions.

## What to do

For each row of `rule_sample.csv`, check two things against the label definitions in
[`../topic_and_labels.md`](../topic_and_labels.md):

1. Is it an entity of this label? (e.g. *stroke* the disease, not *a stroke of the pen*)
2. Is the span right? (**Whisper**-large is too short; **spastic dysarthria** is right)

Then keep or change `verdict`:

| verdict | meaning |
| --- | --- |
| `ok` | right label and span |
| `wrong_label` | an entity, but of another label |
| `wrong_span` | right label, but the bold part is too short or too long |
| `not_entity` | should not be labelled at all |

Add a `note` for anything not `ok`. The verdicts already filled in are a first pass by Claude Code
(112 ok, 6 wrong_span, 1 wrong_label, 1 not_entity); the non-ok rows are 2, 53, 54, 88, 91, 92, 100
and 119 (file line numbers). Check those first, then skim the rest.

Then skim `rule_surface_forms.md` for a frequent form that is often wrong. That kind of error is a
reason to fix the glossary and retrain; occasional errors in the sample are only documented in the
report.
