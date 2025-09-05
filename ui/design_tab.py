from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QPushButton,
    QLabel,
    QGroupBox,
    QProgressBar,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.calc import run_full_calc


class PumpChart(FigureCanvasQTAgg):
    def __init__(self) -> None:
        fig = Figure(figsize=(6, 4), tight_layout=True)
        super().__init__(fig)
        self.ax = fig.add_subplot(111)

    def draw_pump(self, curve_q, curve_h, work_q, work_h) -> None:
        ax = self.ax
        ax.clear()
        if curve_q and curve_h:
            ax.plot(curve_q, curve_h, label="H(Q)")
        if work_q is not None and work_h is not None:
            ax.scatter([work_q], [work_h], s=60, label="Рабочая точка")
        ax.set_xlabel("Q, м³/сут")
        ax.set_ylabel("H, м")
        ax.grid(True, alpha=0.25)
        ax.legend(loc='best')
        self.draw()


class DesignTab(QWidget):
    def __init__(self) -> None:
        super().__init__()

        root = QHBoxLayout(self)

        # Left controls
        left_layout = QFormLayout()
        self.reservoirPressure = self._spin(left_layout, "Pr, атм:", 89.6, 0.1)
        self.productivityIndex = self._spin(left_layout, "J, м³/сут/атм:", 2.238, 0.001)
        self.bubblePointPressure = self._spin(left_layout, "Pb, атм:", 89.6, 0.1)
        self.gor = self._spin(left_layout, "GOR, м³/м³:", 251.7, 0.1)
        self.waterCut = self._spin(left_layout, "Обводн., %:", 52.7, 0.1, 0, 100)
        self.liquidDensity = self._spin(left_layout, "ρж, кг/м³:", 1016, 1)
        self.bo = self._spin(left_layout, "Bo:", 1.64, 0.01)
        self.viscosity = self._spin(left_layout, "Вязк., cПз:", 0.44, 0.01)
        self.gasSG = self._spin(left_layout, "Плотн. газа, отн.:", 0.85, 0.01)
        self.tubingId = self._spin(left_layout, "ID НКТ, мм:", 62, 1)
        self.pumpDepth = self._spin(left_layout, "Глубина, м:", 2630, 1)
        self.thp = self._spin(left_layout, "Pустья, атм:", 25, 0.1)
        self.surfaceT = self._spin(left_layout, "T устья, °C:", 20, 0.1)
        self.gradT = self._spin(left_layout, "Гр. T, °C/100м:", 3.0, 0.1)
        self.targetQ = self._spin(left_layout, "Qпроект, м³/сут:", 80, 1)

        buttons_row = QHBoxLayout()
        self.btn_calc = QPushButton("ЗАПУСТИТЬ РАСЧЕТ")
        self.btn_export = QPushButton("ЭКСПОРТИРОВАТЬ")
        buttons_row.addWidget(self.btn_calc)
        buttons_row.addWidget(self.btn_export)

        left_box = QVBoxLayout()
        left_box.addLayout(left_layout)
        left_box.addLayout(buttons_row)

        left_wrap = QWidget()
        left_wrap.setLayout(left_box)
        root.addWidget(left_wrap, 1)

        # Right results
        right = QVBoxLayout()
        self.status = QLabel("Заполните поля и запустите расчет")
        self.status.setAlignment(Qt.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.chart = PumpChart()
        self.results = QLabel("")
        self.results.setTextFormat(Qt.RichText)

        grp = QGroupBox("Шаг 3: Итоговый расчет и рабочая точка")
        grp.setCheckable(True)
        grp.setChecked(True)
        grp_layout = QVBoxLayout(grp)
        grp_layout.addWidget(self.chart)
        grp_layout.addWidget(self.results)

        right.addWidget(self.status)
        right.addWidget(self.progress)
        right.addWidget(grp)

        right_wrap = QWidget()
        right_wrap.setLayout(right)
        root.addWidget(right_wrap, 2)

        self.btn_calc.clicked.connect(self.on_calc)

    def _spin(self, layout: QFormLayout, label: str, val: float, step: float, mn: float = 0.0, mx: float = 1e9) -> QDoubleSpinBox:
        w = QDoubleSpinBox()
        w.setDecimals(6)
        w.setRange(mn, mx)
        w.setSingleStep(step)
        w.setValue(val)
        layout.addRow(label, w)
        return w

    def _collect(self) -> Dict:
        return dict(
            reservoirPressure=self.reservoirPressure.value(),
            productivityIndex=self.productivityIndex.value(),
            bubblePointPressure=self.bubblePointPressure.value(),
            gasOilRatio=self.gor.value(),
            waterCut=self.waterCut.value(),
            liquidDensity=self.liquidDensity.value(),
            boFactor=self.bo.value(),
            viscosity=self.viscosity.value(),
            gasSpecificGravity=self.gasSG.value(),
            tubingId=self.tubingId.value(),
            pumpDepth=self.pumpDepth.value(),
            tubingHeadPressure=self.thp.value(),
            surfaceTemperature=self.surfaceT.value(),
            tempGradient=self.gradT.value(),
            targetFlowRate=self.targetQ.value(),
        )

    def on_calc(self) -> None:
        self.progress.setValue(10)
        params = self._collect()
        out = run_full_calc(params)
        self.progress.setValue(70)
        self.chart.draw_pump(out.get("curve_q", []), out.get("curve_h", []), out.get("work_q"), out.get("work_h"))
        self.results.setText(
            f"<b>TDH:</b> {out['tdh_m']:.1f} м | <b>PIP:</b> {out['pip_atm']:.1f} атм | <b>Газ, φ:</b> {out['void_fraction']:.1f}%"
        )
        self.status.setText("Готово")
        self.progress.setValue(100)


