"""LLM extractor using the course REALLMS client.

The client matches code/LLMs/REALLMS.ipynb and L645/src/llm_tagger.py:
OpenAI-compatible chat completions at
https://reallms.rescloud.iu.edu/direct/v1, model qwen3.8-27b, key from
REALLMS_API_KEY. The key is never written to disk.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ENTITY_TYPES, PREDICATES, load_sources, read_text, write_triples

REALLMS_BASE_URL = "https://reallms.rescloud.iu.edu/direct/v1"
MODEL_ID = "qwen3.8-27b"
CHUNK_CHARS = 6000
THINK = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


def load_api_key() -> str:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    key = os.getenv("REALLMS_API_KEY")
    if not key:
        secret = Path.home() / ".reallms_secrets"
        if secret.exists():
            for line in secret.read_text(encoding="utf-8").splitlines():
                if line.startswith("export REALLMS_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        raise SystemExit("REALLMS_API_KEY is not set. Do not write the key into this script.")
    return key


def chunks(text: str) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    grouped: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > CHUNK_CHARS:
            grouped.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        grouped.append(current)
    return grouped or [text[:CHUNK_CHARS]]


def parse_payload(content: str) -> list[dict]:
    content = THINK.sub("", content)
    content = content.replace("```json", "").replace("```", "").strip()
    start = content.find("{")
    end = content.rfind("}")
    if start < 0 or end < start:
        return []
    try:
        payload = json.loads(content[start : end + 1])
    except json.JSONDecodeError:
        return []
    triples = payload.get("triples") if isinstance(payload, dict) else None
    return triples if isinstance(triples, list) else []


def valid(row: dict) -> bool:
    predicate = row.get("predicate")
    if predicate not in PREDICATES:
        return False
    subject_type, object_type = PREDICATES[predicate]
    if row.get("subject_type") != subject_type or row.get("object_type") != object_type:
        return False
    if row.get("subject_type") not in ENTITY_TYPES or row.get("object_type") not in ENTITY_TYPES:
        return False
    if not str(row.get("subject", "")).strip() or not str(row.get("object", "")).strip():
        return False
    evidence = str(row.get("evidence", "")).strip()
    return bool(evidence)


def system_prompt() -> str:
    lines = [
        "You extract a knowledge graph from a passage about dysarthria and cerebral palsy.",
        "Use only the entity types and predicates below. Do not add facts that the passage does not support.",
        "Copy the evidence as a short quote from the passage.",
        "Entity types: " + ", ".join(ENTITY_TYPES) + ".",
        "Predicates, with the required subject type and object type:",
    ]
    for name, (subject_type, object_type) in PREDICATES.items():
        lines.append(f"- {name}: {subject_type} -> {object_type}")
    lines.append('polarity is "positive" or "negative". modality is an empty string, or one of may, might, could, would.')
    lines.append(
        'Return JSON only, no markdown: {"triples":[{"subject":"","subject_type":"","predicate":"","object":"","object_type":"","polarity":"positive","modality":"","evidence":""}]}'
    )
    lines.append('If there are no supported triples, return {"triples":[]}.')
    return "\n".join(lines)


def main() -> None:
    from openai import OpenAI

    client = OpenAI(base_url=REALLMS_BASE_URL, api_key=load_api_key())
    prompt = system_prompt()
    rows = []
    for source in load_sources():
        doc_id = source["doc_id"]
        doc_rows = []
        for index, passage in enumerate(chunks(read_text(doc_id)), start=1):
            response = client.chat.completions.create(
                model=MODEL_ID,
                temperature=0,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Document id: {doc_id}\n\nPassage:\n{passage}"},
                ],
            )
            content = response.choices[0].message.content or ""
            for item in parse_payload(content):
                if not valid(item):
                    continue
                evidence = " ".join(str(item["evidence"]).split())[:500]
                if evidence.lower() not in passage.lower() and evidence[:80].lower() not in passage.lower():
                    continue
                doc_rows.append(
                    {
                        "doc_id": doc_id,
                        "extractor": "llm",
                        "subject": " ".join(str(item["subject"]).split()),
                        "subject_type": item["subject_type"],
                        "predicate": item["predicate"],
                        "object": " ".join(str(item["object"]).split()),
                        "object_type": item["object_type"],
                        "polarity": item.get("polarity") or "positive",
                        "modality": item.get("modality") or "",
                        "evidence": evidence,
                        "entity_source": "llm",
                    }
                )
            print(f"{doc_id} chunk {index}: {len(doc_rows)} kept so far", flush=True)
            time.sleep(0.5)
        rows.extend(doc_rows)
    path = write_triples("llm", rows)
    print(f"wrote {len(rows)} triples to {path}")


if __name__ == "__main__":
    main()
