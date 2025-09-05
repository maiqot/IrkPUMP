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

        # Info row
        info_row = QHBoxLayout()
        self.catalog_label = QLabel(f"Каталог: {self.pump_manager.catalog_dir}")
        self.count_label = QLabel("Насосов в базе: 0")
        info_row.addWidget(self.catalog_label)
        info_row.addStretch(1)
        info_row.addWidget(self.count_label)
        layout.addLayout(info_row)

        # Table of pumps
        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Модель",
            "Дебит мин",
            "Дебит ном",
            "Дебит макс",
            "Напор ном",
            "Мощн, кВт",
            "КПД, %",
            "Ступени",
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Actions row
        actions_row = QHBoxLayout()
        import_btn = QPushButton("Импорт из Excel...")
        import_btn.clicked.connect(self._action_import_excel)
        sample_btn = QPushButton("Создать образец Excel")
        sample_btn.clicked.connect(self._action_create_sample)
        export_btn = QPushButton("Экспорт каталога в TXT")
        export_btn.clicked.connect(self._action_export_text)
        actions_row.addWidget(import_btn)
        actions_row.addWidget(sample_btn)
        actions_row.addWidget(export_btn)
        actions_row.addStretch(1)
        layout.addLayout(actions_row)

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
        self.table.setRowCount(len(pumps))
        for row_idx, pump in enumerate(pumps):
            def set_cell(col: int, value: str) -> None:
                self.table.setItem(row_idx, col, QTableWidgetItem(value))

            set_cell(0, str(pump.get("model", "")))
            set_cell(1, f"{pump.get('min_q_m3', 0):.1f}")
            set_cell(2, f"{pump.get('nominal_q_m3', 0):.1f}")
            set_cell(3, f"{pump.get('max_q_m3', 0):.1f}")
            set_cell(4, f"{pump.get('nominal_head_m', 0):.1f}")
            set_cell(5, f"{pump.get('nominal_power_kw', 0):.1f}")
            set_cell(6, f"{pump.get('efficiency', 0):.1f}")
            set_cell(7, str(pump.get('stages', 0)))

        self.count_label.setText(f"Насосов в базе: {len(pumps)}")


def run_gui() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()


