import pandas as pd
import json

def write_output_data(documents_csv, matched_json, output_csv):
    df_docs = pd.read_csv(documents_csv)
    with open(matched_json, 'r') as f:
        entities = json.load(f)

    rows = []
    for ent in entities:
        doc = df_docs[df_docs["uuid"] == ent["uuid"]].iloc[0].to_dict()
        doc.update({
            "entity_type": ent["label"],
            "entity_text": ent["text"],
            "start_pos": ent["start"],
            "end_pos": ent["end"],
            "is_matched": ent["is_matched"],
            "matched_entity_id": ent["matched_entity_id"],
            "matched_entity_name": ent["matched_entity_name"]
        })
        rows.append(doc)

    pd.DataFrame(rows).to_csv(output_csv, index=False)
