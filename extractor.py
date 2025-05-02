import pandas as pd
import json
import os
from gliner import GLiNER

def load_model():
    return GLiNER.from_pretrained("urchade/gliner_multi-v2.1")

def extract_entities(model, text, labels=["Person", "Company", "Location"], threshold=0.5):
    return model.predict_entities(text, labels, threshold)

def run_extraction(input_dir: str, output_dir: str):
    model = load_model()
    
    documents_path = os.path.join(input_dir, "documents.csv")
    output_path = os.path.join(output_dir, "entities_extracted.json")

    df = pd.read_csv(documents_path)
    extracted_data = []

    for _, row in df.iterrows():
        uuid = row["uuid"]
        text = row["body_en"]
        entities = extract_entities(model, text)
        for ent in entities:
            extracted_data.append({
                "uuid": uuid,
                "text": ent["text"],
                "start": ent["start"],
                "end": ent["end"],
                "label": ent["label"]
            })

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(extracted_data, f, indent=2)

# Optional: Allow running standalone for testing
if __name__ == "__main__":
    run_extraction("data", "output")
