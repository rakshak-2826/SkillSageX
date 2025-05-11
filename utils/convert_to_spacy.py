import spacy
from spacy.tokens import DocBin
import json

nlp = spacy.blank("en")  # blank English model
db = DocBin()

def has_overlap(span, span_list):
    for existing in span_list:
        if span.start < existing.end and span.end > existing.start:
            return True
    return False

with open("admin.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        text = data["text"]
        labels = data.get("label", [])
        doc = nlp.make_doc(text)
        ents = []

        for start, end, label in labels:
            span = doc.char_span(start, end, label=label)
            if span is None:
                print(f"⚠️ Skipping invalid span: [{start}, {end}] → '{text[start:end]}'")
            elif has_overlap(span, ents):
                print(f"⚠️ Skipping overlapping span: {span.text} ({label})")
            else:
                ents.append(span)

        doc.ents = ents
        db.add(doc)

db.to_disk("admin.spacy")
print("✅ Successfully created admin.spacy")
