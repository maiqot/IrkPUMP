from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog
)
from pathlib import Path
from pump_manager import PumpManager, create_sample_excel


class CatalogTab(QWidget):
    def __init__(self, manager: PumpManager) -> None:
        super().__init__()
        self.manager = manager

        root = QVBoxLayout(self)
        info = QHBoxLayout()
        self.path_label = QLabel(f"Каталог: {self.manager.catalog_dir}")
        self.count_label = QLabel("")
        info.addWidget(self.path_label)
        info.addStretch(1)
        info.addWidget(self.count_label)
        root.addLayout(info)

        actions = QHBoxLayout()
        btn_import = QPushButton("Импорт из Excel...")
        btn_import.clicked.connect(self._import)
        btn_sample = QPushButton("Создать образец Excel")
        btn_sample.clicked.connect(self._sample)
        btn_clear = QPushButton("Очистить базу")
        btn_clear.clicked.connect(self._clear)
        actions.addWidget(btn_import)
        actions.addWidget(btn_sample)
        actions.addWidget(btn_clear)
        actions.addStretch(1)
        root.addLayout(actions)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Модель", "Qmin", "Qnom", "Qmax", "Hnom", "P,кВт", "КПД,%", "Ступени",
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        pumps = self.manager.get_pumps()
        self.table.setRowCount(len(pumps))
        for r, p in enumerate(pumps):
            vals = [
                str(p.get('model','')),
                f"{p.get('min_q_m3',0):.1f}", f"{p.get('nominal_q_m3',0):.1f}", f"{p.get('max_q_m3',0):.1f}",
                f"{p.get('nominal_head_m',0):.1f}", f"{p.get('nominal_power_kw',0):.1f}", f"{p.get('efficiency',0):.1f}",
                str(p.get('stages',0)),
            ]
            for c, v in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(v))
        self.count_label.setText(f"Насосов: {len(pumps)}")

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Excel", str(self.manager.catalog_dir), "Excel (*.xlsx *.xls)")
        if not path:
            return
        res = self.manager.import_from_excel(path)
        self.refresh()

    def _sample(self) -> None:
        sample = self.manager.catalog_dir / "sample_pumps.xlsx"
        create_sample_excel(str(sample))
        self.refresh()

    def _clear(self) -> None:
        self.manager.clear_pumps()
        self.refresh()


