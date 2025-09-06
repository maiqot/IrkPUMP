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
    QScrollArea,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.calc import run_full_calc


class PumpChart(FigureCanvasQTAgg):
    def __init__(self) -> None:
        fig = Figure(figsize=(8, 5), tight_layout=True)
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.setMinimumSize(600, 400)
        self.setMaximumSize(800, 500)

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
        self.setMinimumSize(1200, 600)
        
        # Главный контейнер с прокруткой
        main_widget = QWidget()
        main_widget.setMinimumSize(1200, 600)
        
        root = QHBoxLayout(main_widget)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)
        
        # Добавляем скроллинг
        scroll_area = QScrollArea()
        scroll_area.setWidget(main_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        # Устанавливаем скролл как основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Left controls - фиксированная ширина
        left_widget = QWidget()
        left_widget.setFixedWidth(350)
        left_widget.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Группа параметров пласта
        reservoir_group = QGroupBox("1. Параметры пласта и флюида")
        reservoir_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #1976d2;
            }
        """)
        reservoir_form = QFormLayout(reservoir_group)
        
        self.reservoirPressure = self._spin(reservoir_form, "Pr, атм:", 89.6, 0.1)
        self.productivityIndex = self._spin(reservoir_form, "J, м³/сут/атм:", 2.238, 0.001)
        self.bubblePointPressure = self._spin(reservoir_form, "Pb, атм:", 89.6, 0.1)
        self.gor = self._spin(reservoir_form, "GOR, м³/м³:", 251.7, 0.1)
        self.waterCut = self._spin(reservoir_form, "Обводн., %:", 52.7, 0.1, 0, 100)
        self.liquidDensity = self._spin(reservoir_form, "ρж, кг/м³:", 1016, 1)
        self.bo = self._spin(reservoir_form, "Bo:", 1.64, 0.01)
        self.viscosity = self._spin(reservoir_form, "Вязк., cПз:", 0.44, 0.01)
        self.gasSG = self._spin(reservoir_form, "Плотн. газа, отн.:", 0.85, 0.01)
        
        # Группа параметров скважины
        well_group = QGroupBox("2. Параметры скважины")
        well_group.setStyleSheet(reservoir_group.styleSheet())
        well_form = QFormLayout(well_group)
        
        self.tubingId = self._spin(well_form, "ID НКТ, мм:", 62, 1)
        self.pumpDepth = self._spin(well_form, "Глубина, м:", 2630, 1)
        self.thp = self._spin(well_form, "Pустья, атм:", 25, 0.1)
        self.surfaceT = self._spin(well_form, "T устья, °C:", 20, 0.1)
        self.gradT = self._spin(well_form, "Гр. T, °C/100м:", 3.0, 0.1)
        self.targetQ = self._spin(well_form, "Qпроект, м³/сут:", 80, 1)

        # Кнопки
        buttons_row = QHBoxLayout()
        self.btn_calc = QPushButton("ЗАПУСТИТЬ РАСЧЕТ")
        self.btn_calc.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #2e7d32);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #388e3c);
            }
        """)
        self.btn_export = QPushButton("ЭКСПОРТИРОВАТЬ")
        self.btn_export.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196f3, stop:1 #1976d2);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42a5f5, stop:1 #1565c0);
            }
        """)
        buttons_row.addWidget(self.btn_calc)
        buttons_row.addWidget(self.btn_export)

        left_layout.addWidget(reservoir_group)
        left_layout.addWidget(well_group)
        left_layout.addLayout(buttons_row)
        left_layout.addStretch()

        root.addWidget(left_widget)

        # Right results - фиксированная ширина
        right_widget = QWidget()
        right_widget.setMinimumWidth(800)
        right = QVBoxLayout(right_widget)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(15)
        
        # Статус и прогресс
        status_layout = QHBoxLayout()
        self.status = QLabel("Заполните поля и запустите расчет")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #1976d2;
                font-size: 14px;
                padding: 10px;
                background: #e3f2fd;
                border-radius: 6px;
                border: 1px solid #90caf9;
            }
        """)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:1 #2e7d32);
                border-radius: 3px;
            }
        """)
        status_layout.addWidget(self.status)
        status_layout.addWidget(self.progress)
        
        # График
        self.chart = PumpChart()
        
        # Результаты
        self.results = QLabel("")
        self.results.setTextFormat(Qt.RichText)
        self.results.setStyleSheet("""
            QLabel { 
                padding: 15px; 
                border: 1px solid #e0e0e0; 
                border-radius: 8px; 
                background: #f9f9f9;
                font-size: 12px;
            }
        """)
        self.results.setMaximumHeight(100)

        right.addLayout(status_layout)
        right.addWidget(self.chart)
        right.addWidget(self.results)

        root.addWidget(right_widget)

        self.btn_calc.clicked.connect(self.on_calc)
        
        # Автоматически запускаем расчёт при инициализации
        self._run_initial_calculation()

    def _run_initial_calculation(self):
        """Запуск начального расчёта с данными по умолчанию"""
        # Небольшая задержка чтобы интерфейс успел отрисоваться
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, self.on_calc)

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
        self.status.setText("Выполняется расчёт...")
        
        params = self._collect()
        out = run_full_calc(params)
        
        self.progress.setValue(50)
        self.chart.draw_pump(out.get("curve_q", []), out.get("curve_h", []), out.get("work_q"), out.get("work_h"))
        
        self.progress.setValue(80)
        self.results.setText(
            f"<b>TDH:</b> {out['tdh_m']:.1f} м | <b>PIP:</b> {out['pip_atm']:.1f} атм | <b>Газ, φ:</b> {out['void_fraction']:.1f}%"
        )
        
        self.status.setText("Готово")
        self.progress.setValue(100)


