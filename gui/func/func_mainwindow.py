from PySide6.QtWidgets import QMessageBox
from gui.ui.ui_mainwindow import MainWindowUI
from gui.utils.config_manager import ConfigManager
from gui.utils.workers import ModelListWorker

class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.restore_geometry()
        self.load_data()

    def restore_geometry(self):
        x, y, w, h = self.config_manager.get_window_geometry()
        self.setGeometry(x, y, w, h)

    def load_data(self):
        self.worker = ModelListWorker()
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_data_loaded(self, models):
        self.status_label.setText(f"Found {len(models)} models")
        self.model_list.clear()
        self.model_list.addItems(models)

    def on_error(self, error_msg):
        self.status_label.setText("Error loading models")
        QMessageBox.critical(self, "Error", error_msg)

    def closeEvent(self, event):
        # 关闭时保存窗口几何信息
        rect = self.geometry()
        self.config_manager.set_window_geometry(
            rect.x(), rect.y(), rect.width(), rect.height()
        )
        self.config_manager.save_config()
        super().closeEvent(event)
