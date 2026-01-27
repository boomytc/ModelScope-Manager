def merge_models(api_models, custom_models):
    merged = []
    seen = set()

    for model_id in list(api_models) + list(custom_models):
        if not model_id or model_id in seen:
            continue
        seen.add(model_id)
        merged.append(model_id)

    return merged


def filter_models(models, search_text, favorites_only, hidden_only, is_favorite, is_hidden):
    filtered = []

    for model_id in models:
        if search_text and search_text not in model_id.lower():
            continue

        if favorites_only and not is_favorite(model_id):
            continue

        hidden = is_hidden(model_id)
        if hidden_only:
            if not hidden:
                continue
        else:
            if hidden:
                continue

        filtered.append(model_id)

    return filtered
