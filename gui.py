from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from pump_manager import PumpManager
from ui.design_tab import DesignTab
from ui.catalog_tab import CatalogTab


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("IrkPUMP (Python)")
        self.resize(1200, 800)

        self.pump_manager = PumpManager()

        # Menubar
        self._setup_menu()
        # Toolbar
        self._setup_toolbar()
        # Central widget
        self._setup_central()
        # Status bar
        self.setStatusBar(QStatusBar(self))
        self._refresh_table()

    def _setup_menu(self) -> None:
        menubar = QMenuBar(self)
        file_menu = QMenu("Файл", self)
        import_action = QAction("Импортировать насосы из Excel...", self)
        import_action.triggered.connect(self._action_import_excel)
        export_action = QAction("Экспорт каталога в текст...", self)
        export_action.triggered.connect(self._action_export_text)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        data_menu = QMenu("Данные", self)
        clear_action = QAction("Очистить базу насосов", self)
        clear_action.triggered.connect(self._action_clear)
        data_menu.addAction(clear_action)

        menubar.addMenu(file_menu)
        menubar.addMenu(data_menu)
        self.setMenuBar(menubar)

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Основные действия", self)
        toolbar.setMovable(False)

        import_btn = QAction(QIcon(), "Импорт Excel", self)
        import_btn.triggered.connect(self._action_import_excel)
        toolbar.addAction(import_btn)

        export_btn = QAction(QIcon(), "Экспорт TXT", self)
        export_btn.triggered.connect(self._action_export_text)
        toolbar.addAction(export_btn)

        clear_btn = QAction(QIcon(), "Очистить", self)
        clear_btn.triggered.connect(self._action_clear)
        toolbar.addAction(clear_btn)

        self.addToolBar(toolbar)

    def _setup_central(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)

        # Top info row (catalog)
        info_row = QHBoxLayout()
        self.catalog_label = QLabel(f"Каталог: {self.pump_manager.catalog_dir}")
        self.count_label = QLabel("Насосов в базе: 0")
        info_row.addWidget(self.catalog_label)
        info_row.addStretch(1)
        info_row.addWidget(self.count_label)
        layout.addLayout(info_row)

        # Tabs container
        tabs_container = QWidget()
        tabs_layout = QVBoxLayout(tabs_container)
        # For now, stack two key sections vertically to keep simple
        tabs_layout.addWidget(DesignTab())
        tabs_layout.addWidget(CatalogTab(self.pump_manager))
        layout.addWidget(tabs_container)

        self.setCentralWidget(container)

    # --- Actions ---
    def _action_import_excel(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите Excel-файл",
            str(self.pump_manager.catalog_dir),
            "Excel Files (*.xlsx *.xls)",
        )
        if not file_path:
            return
        result = self.pump_manager.import_from_excel(file_path)
        if result.get("success"):
            self.statusBar().showMessage(
                f"Импортировано насосов: {result.get('imported', 0)}", 5000
            )
            if result.get("errors"):
                QMessageBox.warning(self, "Предупреждения", "\n".join(result["errors"]))
            self._refresh_table()
        else:
            QMessageBox.critical(
                self, "Ошибка импорта", "\n".join(result.get("errors", ["Неизвестная ошибка"]))
            )

    def _action_export_text(self) -> None:
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить каталог в TXT", str(Path.cwd() / "pumps.txt"), "Text (*.txt)"
        )
        if not save_path:
            return
        ok = self.pump_manager.export_to_text(save_path)
        if ok:
            self.statusBar().showMessage(f"Экспортировано: {save_path}", 5000)
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось экспортировать каталог")

    def _action_create_sample(self) -> None:
        from pump_manager import create_sample_excel

        sample_path = self.pump_manager.catalog_dir / "sample_pumps.xlsx"
        create_sample_excel(str(sample_path))
        self.statusBar().showMessage(f"Создан образец: {sample_path}", 5000)

    def _action_clear(self) -> None:
        if QMessageBox.question(
            self, "Подтверждение", "Удалить все насосы из базы?"
        ) == QMessageBox.Yes:
            self.pump_manager.clear_pumps()
            self._refresh_table()

    def _refresh_table(self) -> None:
        pumps = self.pump_manager.get_pumps()
        self.count_label.setText(f"Насосов в базе: {len(pumps)}")


def run_gui() -> None:
    app = QApplication(sys.argv)
    # Polished dark theme via QSS
    app.setStyleSheet("""
    QWidget { font-family: 'Segoe UI', sans-serif; font-size: 12px; }
    QMainWindow, QWidget { background-color: #1f1f1f; color: #e6e6e6; }
    QGroupBox { border: 1px solid #333; border-radius: 6px; margin-top: 10px; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 2px 4px; color: #a0c4ff; }
    QLabel { color: #d0d0d0; }
    QLineEdit, QDoubleSpinBox, QSpinBox { background: #2a2a2a; border: 1px solid #3b3b3b; border-radius: 4px; padding: 2px 6px; }
    QPushButton { background: #2b6cb0; border: 1px solid #2b6cb0; color: #fff; padding: 6px 12px; border-radius: 4px; }
    QPushButton:hover { background: #2c7ad6; }
    QPushButton:disabled { background: #3a3a3a; border-color: #3a3a3a; }
    QTableWidget { background: #242424; gridline-color: #3a3a3a; }
    QHeaderView::section { background: #2b2b2b; color: #ddd; border: 1px solid #3a3a3a; padding: 4px; }
    QProgressBar { border: 1px solid #3a3a3a; border-radius: 4px; text-align: center; }
    QProgressBar::chunk { background-color: #38bdf8; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()


