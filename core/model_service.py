from core.model_list_logic import merge_models, filter_models

class ModelService:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def build_model_items(self, api_models, search_text, favorites_only, hidden_only):
        custom_models = self.config_manager.get_custom_models()
        merged_models = merge_models(api_models, custom_models)

        filtered_models = filter_models(
            merged_models,
            search_text,
            favorites_only,
            hidden_only,
            self.config_manager.is_favorite,
            self.config_manager.is_invisible,
        )

        items = []
        for model_id in filtered_models:
            items.append(
                {
                    "model_id": model_id,
                    "is_favorite": self.config_manager.is_favorite(model_id),
                    "is_custom": self.config_manager.is_custom_model(model_id),
                    "is_hidden": self.config_manager.is_invisible(model_id),
                }
            )
        return items

    def get_cached_quota(self):
        return self.config_manager.get_last_quota()

    def update_quota_from_list(self, quota_info):
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        updated = False

        if user_remaining != "N/A" and user_limit != "N/A":
            self.config_manager.set_last_quota(user_remaining, user_limit)
            self.config_manager.save_config()
            updated = True

        return {
            "user_limit": user_limit,
            "user_remaining": user_remaining,
            "updated": updated,
        }

    def update_quota_from_check(self, quota_info):
        user_limit = quota_info.get("user_limit", "N/A")
        user_remaining = quota_info.get("user_remaining", "N/A")
        model_limit = quota_info.get("model_limit", "N/A")
        model_remaining = quota_info.get("model_remaining", "N/A")
        status_code = quota_info.get("status_code", "Unknown")
        updated = False

        if user_remaining != "N/A" and user_limit != "N/A":
            self.config_manager.set_last_quota(user_remaining, user_limit)
            self.config_manager.save_config()
            updated = True

        return {
            "user_limit": user_limit,
            "user_remaining": user_remaining,
            "model_limit": model_limit,
            "model_remaining": model_remaining,
            "status_code": status_code,
            "updated": updated,
        }

    def toggle_favorite(self, model_id):
        if self.config_manager.is_favorite(model_id):
            self.config_manager.remove_favorite(model_id)
            message = f"已取消收藏: {model_id}"
        else:
            self.config_manager.add_favorite(model_id)
            message = f"已收藏: {model_id}"
        self.config_manager.save_config()
        return message

    def toggle_hidden(self, model_id):
        if self.config_manager.is_invisible(model_id):
            self.config_manager.remove_invisible(model_id)
            message = f"已取消隐藏: {model_id}"
        else:
            self.config_manager.add_invisible(model_id)
            message = f"已隐藏: {model_id}"
        self.config_manager.save_config()
        return message

    def add_custom_model(self, model_id, api_models):
        if model_id in api_models:
            return {"ok": False, "message": "该模型已在 API 列表中。"}
        if self.config_manager.is_custom_model(model_id):
            return {"ok": False, "message": "该模型已存在。"}

        self.config_manager.add_custom_model(model_id)
        self.config_manager.save_config()
        return {"ok": True, "message": f"已添加: {model_id}"}

    def delete_custom_model(self, model_id):
        self.config_manager.remove_custom_model(model_id)
        self.config_manager.save_config()
        return f"已删除: {model_id}"
