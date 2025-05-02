def match_entities(entities, aliases_df):
    results = []
    for ent in entities:
        matched_row = aliases_df[
            (aliases_df['aliases'].apply(lambda x: ent['text'] in eval(x))) |
            (aliases_df['name'] == ent['text'])
        ]
        if not matched_row.empty:
            row = matched_row.iloc[0]
            matched = {
                **ent,
                "is_matched": True,
                "matched_entity_id": row.get("entity_id", None),
                "matched_entity_name": row["name"]
            }
        else:
            matched = {**ent, "is_matched": False, "matched_entity_id": None, "matched_entity_name": None}
        results.append(matched)
    return results
