from core.model_service import ModelService
from gui.controllers.app.workers import ModelListWorker, QuotaWorker

class ModelListApp:
    def __init__(self, config_manager):
        self.model_service = ModelService(config_manager)
        self.list_worker = None
        self.quota_worker = None

    def get_cached_quota(self):
        return self.model_service.get_cached_quota()

    def update_quota_from_list(self, quota_info):
        return self.model_service.update_quota_from_list(quota_info)

    def update_quota_from_check(self, quota_info):
        return self.model_service.update_quota_from_check(quota_info)

    def build_model_items(self, api_models, search_text, favorites_only, hidden_only):
        return self.model_service.build_model_items(
            api_models,
            search_text,
            favorites_only,
            hidden_only,
        )

    def load_models(self, api_key, on_loaded, on_error):
        self.list_worker = ModelListWorker(api_key)
        self.list_worker.finished.connect(on_loaded)
        self.list_worker.error.connect(on_error)
        self.list_worker.start()

    def check_quota(self, model_id, api_key, on_checked, on_error):
        self.quota_worker = QuotaWorker(model_id, api_key)
        self.quota_worker.finished.connect(on_checked)
        self.quota_worker.error.connect(on_error)
        self.quota_worker.start()

    def is_list_worker(self, sender):
        return sender is self.list_worker

    def is_quota_worker(self, sender):
        return sender is self.quota_worker

    def toggle_favorite(self, model_id):
        return self.model_service.toggle_favorite(model_id)

    def toggle_hidden(self, model_id):
        return self.model_service.toggle_hidden(model_id)

    def add_custom_model(self, model_id, api_models):
        return self.model_service.add_custom_model(model_id, api_models)

    def delete_custom_model(self, model_id):
        return self.model_service.delete_custom_model(model_id)
