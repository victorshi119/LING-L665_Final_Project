#!/usr/bin/env python
"""
Apply the trained transformer NER model to every corpus document and save the
predicted Docs in a separate DocBin (the rule-annotated DocBins are not touched).

Each predicted Doc's user_data records doc_id, source, split, and the model
name/version/path, so predictions can be traced to their inputs.

Outputs: corpus/predictions.spacy, corpus/predictions_manifest.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import spacy
from spacy.tokens import DocBin

HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=Path, default=HERE / "training" / "ner-transformer" / "model-best")
    parser.add_argument("--output", type=Path, default=HERE / "corpus" / "predictions.spacy")
    parser.add_argument("--gpu-id", type=int, default=0, help="-1 for CPU")
    parser.add_argument("--splits", nargs="+", default=["train", "dev", "test"],
                        help="Which corpus splits to annotate (default: all documents)")
    args = parser.parse_args()

    if args.output.resolve() in {(HERE / "corpus" / f"{s}.spacy").resolve() for s in ("train", "dev", "test")}:
        raise ValueError("Refusing to overwrite a rule-annotated DocBin")
    if args.gpu_id >= 0:
        spacy.require_gpu(args.gpu_id)

    nlp = spacy.load(args.model)
    nlp.max_length = 2_000_000
    model_info = {
        "model_name": nlp.meta.get("name", ""), "model_version": nlp.meta.get("version", ""),
        "model_path": str(args.model.resolve()), "spacy_version": spacy.__version__,
        "predicted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    with (HERE / "corpus" / "splits.csv").open(encoding="utf-8") as file:
        rows = [row for row in csv.DictReader(file) if row["split"] in args.splits]

    doc_bin = DocBin(attrs=["ORTH", "SPACY", "ENT_IOB", "ENT_TYPE", "SENT_START"], store_user_data=True)
    manifest = []
    texts = ((HERE / row["text_file"]).read_text(encoding="utf-8") for row in rows)
    for row, doc in zip(rows, nlp.pipe(texts, batch_size=4)):
        # doc._.trf_data (the transformer's output tensors) lives in user_data; storing it for
        # every document exhausted 64 GB of RAM, and the DocBin only needs the entities.
        for key in [k for k in doc.user_data if isinstance(k, tuple) and k[:2] == ("._.", "trf_data")]:
            del doc.user_data[key]
        doc.user_data.update({"doc_id": row["doc_id"], "source": row["source"], "split": row["split"],
                              "annotation": "transformer model prediction", **model_info})
        doc_bin.add(doc)
        labels = Counter(ent.label_ for ent in doc.ents)
        manifest.append({"doc_id": row["doc_id"], "split": row["split"], "n_tokens": len(doc),
                         "n_predicted_entities": len(doc.ents), **{f"n_{k}": v for k, v in sorted(labels.items())}})
        print(f"{row['doc_id']}: {len(doc.ents)} entities", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc_bin.to_disk(args.output)
    fields = sorted({key for record in manifest for key in record},
                    key=lambda k: (not k.startswith(("doc_id", "split", "n_tokens", "n_predicted")), k))
    with args.output.with_name("predictions_manifest.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields, restval=0)
        writer.writeheader()
        writer.writerows(manifest)
    (args.output.with_name("predictions_model_info.json")).write_text(json.dumps(model_info, indent=1))
    print(f"Wrote {len(manifest)} predicted Docs to {args.output}")


if __name__ == "__main__":
    main()
