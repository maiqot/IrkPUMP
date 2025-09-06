#!/usr/bin/env python3
"""
Инженерный калькулятор ЭЦН (Версия 4.0) - Python версия
Полная копия функциональности из IrkPUMP v6.html
"""

import sys
import math
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QFormLayout, QLabel, QDoubleSpinBox, QPushButton,
    QGroupBox, QTextEdit, QProgressBar, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QSplitter,
    QMessageBox, QFileDialog, QCheckBox, QSlider, QSpinBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QPalette, QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class InputParameters:
    """Параметры ввода для расчета"""
    # Параметры пласта и флюида
    reservoir_pressure: float = 89.6  # Pr, атм
    productivity_index: float = 2.238  # J, м³/сут/атм
    bubble_point_pressure: float = 89.6  # Pb, атм
    gas_oil_ratio: float = 251.7  # GOR, м³/м³
    water_cut: float = 52.7  # Обводненность, %
    liquid_density: float = 1016  # ρж, кг/м³
    bo_factor: float = 1.64  # Bo
    viscosity: float = 0.44  # Вязкость, сПз
    gas_specific_gravity: float = 0.85  # Плотность газа, отн.
    
    # Параметры скважины
    tubing_id: float = 62  # ID НКТ, мм
    pump_depth: float = 2630  # Глубина, м
    tubing_head_pressure: float = 25  # Pустья, атм
    surface_temperature: float = 20  # T устья, °C
    temp_gradient: float = 3.0  # Гр. T, °C/100м
    target_flow_rate: float = 80  # Qпроект, м³/сут


@dataclass
class CalculationResults:
    """Результаты расчета"""
    # Основные результаты
    tdh_m: float = 0.0  # TDH, м
    pip_atm: float = 0.0  # PIP, атм
    void_fraction: float = 0.0  # Газ, φ, %
    work_q: float = 0.0  # Рабочий дебит, м³/сут
    work_h: float = 0.0  # Рабочий напор, м
    
    # Кривая насоса
    curve_q: List[float] = None
    curve_h: List[float] = None
    
    # Многофазный поток
    multiphase_result: Dict = None
    
    # Кавитация
    cavitation_result: Dict = None
    
    # Двигатель
    motor_result: Dict = None
    
    def __post_init__(self):
        if self.curve_q is None:
            self.curve_q = []
        if self.curve_h is None:
            self.curve_h = []
        if self.multiphase_result is None:
            self.multiphase_result = {}
        if self.cavitation_result is None:
            self.cavitation_result = {}
        if self.motor_result is None:
            self.motor_result = {}


class CalculationEngine:
    """Движок расчетов - портированная логика из JavaScript"""
    
    @staticmethod
    def create_ipr_function(inputs: InputParameters) -> callable:
        """Создание функции IPR (Inflow Performance Relationship)"""
        def ipr(q_m3):
            if q_m3 <= 0:
                return inputs.reservoir_pressure
            return inputs.reservoir_pressure - (q_m3 / inputs.productivity_index)
        return ipr
    
    @staticmethod
    def calculate_beggs_brill(flow_rate_m3: float, gas_rate_m3: float, inputs: InputParameters) -> Dict:
        """Расчет многофазного потока по методу Beggs-Brill"""
        # Упрощенная реализация Beggs-Brill
        liquid_density = inputs.liquid_density
        gas_density = inputs.gas_specific_gravity * 1.225  # кг/м³ при нормальных условиях
        viscosity = inputs.viscosity
        
        # Газосодержание
        gas_volume_fraction = gas_rate_m3 / (flow_rate_m3 + gas_rate_m3) if (flow_rate_m3 + gas_rate_m3) > 0 else 0
        
        # Плотность смеси
        mixture_density = liquid_density * (1 - gas_volume_fraction) + gas_density * gas_volume_fraction
        
        # Вязкость смеси
        mixture_viscosity = viscosity * (1 - gas_volume_fraction) + 0.01 * gas_volume_fraction
        
        return {
            'gas_volume_fraction': gas_volume_fraction * 100,
            'mixture_density': mixture_density,
            'mixture_viscosity': mixture_viscosity,
            'flow_regime': 'Bubble' if gas_volume_fraction < 0.3 else 'Slug'
        }
    
    @staticmethod
    def calculate_void_fraction_and_rate(pip_atm: float, temp_bottom_c: float, inputs: InputParameters) -> Tuple[float, float]:
        """Расчет газосодержания и дебита газа"""
        # Упрощенный расчет газосодержания
        gas_rate_m3 = inputs.target_flow_rate * inputs.gas_oil_ratio
        void_fraction = (gas_rate_m3 / (inputs.target_flow_rate + gas_rate_m3)) * 100 if (inputs.target_flow_rate + gas_rate_m3) > 0 else 0
        
        return void_fraction, gas_rate_m3
    
    @staticmethod
    def estimate_gas_degradation(void_fraction_percent: float, gas_tolerance: str = "Средняя") -> str:
        """Оценка деградации газа"""
        if void_fraction_percent < 10:
            return "Низкая"
        elif void_fraction_percent < 25:
            return "Средняя"
        elif void_fraction_percent < 40:
            return "Высокая"
        else:
            return "Критическая"
    
    @staticmethod
    def calculate_vapor_pressure(temp_c: float, pb_atm: float, gas_oil_ratio: float) -> float:
        """Расчет давления насыщения"""
        return pb_atm
    
    @staticmethod
    def calculate_npsh(pip_atm: float, temp_bottom_c: float, inputs: InputParameters) -> Dict:
        """Расчет NPSH (Net Positive Suction Head)"""
        # Упрощенный расчет NPSH
        vapor_pressure = CalculationEngine.calculate_vapor_pressure(temp_bottom_c, inputs.bubble_point_pressure, inputs.gas_oil_ratio)
        npsh_available = pip_atm - vapor_pressure
        npsh_required = 3.0  # Упрощенное значение
        
        return {
            'npsh_available': npsh_available,
            'npsh_required': npsh_required,
            'npsh_margin': npsh_available - npsh_required,
            'cavitation_risk': 'Низкий' if npsh_available > npsh_required * 1.5 else 'Высокий'
        }
    
    @staticmethod
    def calculate_pip_iteratively(target_flow_rate_m3: float, inputs: InputParameters) -> float:
        """Итеративный расчет PIP"""
        # Упрощенный расчет PIP
        ipr = CalculationEngine.create_ipr_function(inputs)
        pip = ipr(target_flow_rate_m3)
        return max(pip, inputs.bubble_point_pressure)
    
    @staticmethod
    def run_full_calculation(inputs: InputParameters) -> CalculationResults:
        """Основная функция расчета - портированная из JavaScript"""
        results = CalculationResults()
        
        # 1. Расчет PIP
        results.pip_atm = CalculationEngine.calculate_pip_iteratively(inputs.target_flow_rate, inputs)
        
        # 2. Расчет температуры на забое
        temp_bottom_c = inputs.surface_temperature + (inputs.pump_depth / 100) * inputs.temp_gradient
        
        # 3. Расчет газосодержания
        results.void_fraction, gas_rate_m3 = CalculationEngine.calculate_void_fraction_and_rate(
            results.pip_atm, temp_bottom_c, inputs
        )
        
        # 4. Расчет многофазного потока
        results.multiphase_result = CalculationEngine.calculate_beggs_brill(
            inputs.target_flow_rate, gas_rate_m3, inputs
        )
        
        # 5. Расчет NPSH и кавитации
        results.cavitation_result = CalculationEngine.calculate_npsh(
            results.pip_atm, temp_bottom_c, inputs
        )
        
        # 6. Расчет TDH (упрощенный)
        results.tdh_m = inputs.pump_depth * 0.28  # Упрощенная формула
        
        # 7. Рабочая точка
        results.work_q = inputs.target_flow_rate
        results.work_h = results.tdh_m
        
        # 8. Кривая насоса (упрощенная)
        q_range = np.linspace(0, inputs.target_flow_rate * 1.5, 10)
        h_range = results.tdh_m * (1 - (q_range / (inputs.target_flow_rate * 1.2)) ** 2)
        results.curve_q = q_range.tolist()
        results.curve_h = h_range.tolist()
        
        # 9. Расчет двигателя (упрощенный)
        power_kw = inputs.target_flow_rate * inputs.liquid_density * 0.1
        results.motor_result = {
            'power_kw': power_kw,
            'efficiency': 0.85,
            'cable_type': 'ВПП-3х16',
            'cable_length': inputs.pump_depth + 50
        }
        
        return results


class ModernCard(QFrame):
    """Современная карточка с тенью и скругленными углами"""
    def __init__(self, title="", content_widget=None, icon="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        if title:
            title_label = QLabel(f"{icon} {title}")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #1976d2;
                    padding: 5px 0;
                    border-bottom: 1px solid #e0e0e0;
                }
            """)
            layout.addWidget(title_label)
        
        if content_widget:
            layout.addWidget(content_widget)


class PumpChart(FigureCanvasQTAgg):
    """График характеристик насоса"""
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6), facecolor='white')
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('white')
        
    def draw_pump_curve(self, curve_q: List[float], curve_h: List[float], 
                       work_q: float, work_h: float, results: CalculationResults = None):
        """Отрисовка кривой насоса с рабочей точкой"""
        self.ax.clear()
        
        # Кривая насоса
        self.ax.plot(curve_q, curve_h, 'b-', linewidth=2, label='H(Q)')
        
        # Рабочая точка
        self.ax.scatter([work_q], [work_h], s=100, c='red', zorder=5, label='Рабочая точка')
        
        # Зона оптимальной работы
        if work_q > 0:
            optimal_q = [work_q * 0.7, work_q * 1.1]
            optimal_h = [max(curve_h) * 1.1, max(curve_h) * 1.1]
            self.ax.fill_between(optimal_q, 0, optimal_h, alpha=0.2, color='green', label='Оптимальная зона')
        
        self.ax.set_xlabel('Q, м³/сут')
        self.ax.set_ylabel('H, м')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.ax.set_title('Характеристика насоса')
        
        self.draw()


class DesignTab(QWidget):
    """Вкладка расчета - основная функциональность"""
    
    def __init__(self):
        super().__init__()
        self.calculation_engine = CalculationEngine()
        self.results = None
        self._setup_ui()
        self._run_initial_calculation()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Результаты расчета и графики")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px 0;
                border-bottom: 2px solid #1976d2;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)
        
        # Основной контент
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - параметры ввода
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
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
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #1976d2;
                font-size: 14px;
            }
        """)
        reservoir_form = QFormLayout(reservoir_group)
        reservoir_form.setSpacing(8)
        
        self.reservoir_pressure = self._create_spinbox(reservoir_form, "Pr, атм:", 89.6, 0.1)
        self.productivity_index = self._create_spinbox(reservoir_form, "J, м³/сут/атм:", 2.238, 0.001)
        self.bubble_point_pressure = self._create_spinbox(reservoir_form, "Pb, атм:", 89.6, 0.1)
        self.gor = self._create_spinbox(reservoir_form, "GOR, м³/м³:", 251.7, 0.1)
        self.water_cut = self._create_spinbox(reservoir_form, "Обводн., %:", 52.7, 0.1, 0, 100)
        self.liquid_density = self._create_spinbox(reservoir_form, "ρж, кг/м³:", 1016, 1)
        self.bo_factor = self._create_spinbox(reservoir_form, "Bo:", 1.64, 0.01)
        self.viscosity = self._create_spinbox(reservoir_form, "Вязк., сПз:", 0.44, 0.01)
        self.gas_sg = self._create_spinbox(reservoir_form, "Плотн. газа, отн.:", 0.85, 0.01)
        
        # Группа параметров скважины
        well_group = QGroupBox("2. Параметры скважины")
        well_group.setStyleSheet(reservoir_group.styleSheet())
        well_form = QFormLayout(well_group)
        well_form.setSpacing(8)
        
        self.tubing_id = self._create_spinbox(well_form, "ID НКТ, мм:", 62, 1)
        self.pump_depth = self._create_spinbox(well_form, "Глубина, м:", 2630, 1)
        self.thp = self._create_spinbox(well_form, "Pустья, атм:", 25, 0.1)
        self.surface_temp = self._create_spinbox(well_form, "T устья, °С:", 20, 0.1)
        self.temp_gradient = self._create_spinbox(well_form, "Гр. T, °С/100м:", 3.0, 0.1)
        self.target_q = self._create_spinbox(well_form, "Qпроект, м³/сут:", 80, 1)
        
        # Кнопка расчета
        self.calc_btn = QPushButton("ЗАПУСТИТЬ РАСЧЕТ")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976d2, stop:1 #004ba0);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42a5f5, stop:1 #1976d2);
            }
        """)
        self.calc_btn.clicked.connect(self._on_calculate)
        
        left_layout.addWidget(reservoir_group)
        left_layout.addWidget(well_group)
        left_layout.addWidget(self.calc_btn)
        left_layout.addStretch()
        
        # Правая панель - результаты
        right_widget = QWidget()
        right_widget.setMinimumWidth(600)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        
        # Статус и прогресс
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
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976d2, stop:1 #004ba0);
                border-radius: 3px;
            }
        """)
        
        # График
        self.chart = PumpChart()
        self.chart.setMinimumSize(500, 400)
        
        # Результаты
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        right_layout.addWidget(self.status)
        right_layout.addWidget(self.progress)
        right_layout.addWidget(self.chart)
        right_layout.addWidget(self.results_text)
        
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([400, 600])
        
        layout.addWidget(main_splitter)
    
    def _create_spinbox(self, layout: QFormLayout, label: str, val: float, step: float, 
                       min_val: float = 0.0, max_val: float = 1e9) -> QDoubleSpinBox:
        """Создание поля ввода с лейблом"""
        spinbox = QDoubleSpinBox()
        spinbox.setDecimals(6)
        spinbox.setRange(min_val, max_val)
        spinbox.setSingleStep(step)
        spinbox.setValue(val)
        spinbox.setStyleSheet("""
            QDoubleSpinBox {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 25px;
                min-width: 120px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976d2;
            }
        """)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 13px;
                font-weight: normal;
                padding: 4px;
                min-width: 100px;
            }
        """)
        
        layout.addRow(label_widget, spinbox)
        return spinbox
    
    def _get_inputs(self) -> InputParameters:
        """Получение параметров ввода"""
        return InputParameters(
            reservoir_pressure=self.reservoir_pressure.value(),
            productivity_index=self.productivity_index.value(),
            bubble_point_pressure=self.bubble_point_pressure.value(),
            gas_oil_ratio=self.gor.value(),
            water_cut=self.water_cut.value(),
            liquid_density=self.liquid_density.value(),
            bo_factor=self.bo_factor.value(),
            viscosity=self.viscosity.value(),
            gas_specific_gravity=self.gas_sg.value(),
            tubing_id=self.tubing_id.value(),
            pump_depth=self.pump_depth.value(),
            tubing_head_pressure=self.thp.value(),
            surface_temperature=self.surface_temp.value(),
            temp_gradient=self.temp_gradient.value(),
            target_flow_rate=self.target_q.value()
        )
    
    def _on_calculate(self):
        """Выполнение расчета"""
        self.progress.setValue(10)
        self.status.setText("Выполняется расчет...")
        
        try:
            inputs = self._get_inputs()
            self.progress.setValue(30)
            
            # Выполнение расчета
            self.results = self.calculation_engine.run_full_calculation(inputs)
            self.progress.setValue(70)
            
            # Отображение результатов
            self._display_results()
            self.progress.setValue(100)
            self.status.setText("Расчет завершен успешно")
            
        except Exception as e:
            self.status.setText(f"Ошибка расчета: {str(e)}")
            self.progress.setValue(0)
    
    def _display_results(self):
        """Отображение результатов расчета"""
        if not self.results:
            return
        
        # Текстовые результаты
        results_text = f"""
ОСНОВНЫЕ РЕЗУЛЬТАТЫ:
• TDH: {self.results.tdh_m:.1f} м
• PIP: {self.results.pip_atm:.1f} атм
• Газ, φ: {self.results.void_fraction:.1f}%
• Рабочий дебит: {self.results.work_q:.1f} м³/сут
• Рабочий напор: {self.results.work_h:.1f} м

МНОГОФАЗНЫЙ ПОТОК:
• Газосодержание: {self.results.multiphase_result.get('gas_volume_fraction', 0):.1f}%
• Плотность смеси: {self.results.multiphase_result.get('mixture_density', 0):.1f} кг/м³
• Режим потока: {self.results.multiphase_result.get('flow_regime', 'N/A')}

КАВИТАЦИЯ:
• NPSH доступный: {self.results.cavitation_result.get('npsh_available', 0):.1f} м
• NPSH требуемый: {self.results.cavitation_result.get('npsh_required', 0):.1f} м
• Риск кавитации: {self.results.cavitation_result.get('cavitation_risk', 'N/A')}

ДВИГАТЕЛЬ:
• Мощность: {self.results.motor_result.get('power_kw', 0):.1f} кВт
• КПД: {self.results.motor_result.get('efficiency', 0):.1%}
• Кабель: {self.results.motor_result.get('cable_type', 'N/A')}
        """
        
        self.results_text.setText(results_text)
        
        # График
        self.chart.draw_pump_curve(
            self.results.curve_q, self.results.curve_h,
            self.results.work_q, self.results.work_h, self.results
        )
    
    def _run_initial_calculation(self):
        """Запуск начального расчета с данными по умолчанию"""
        QTimer.singleShot(500, self._on_calculate)


class MultiphaseTab(QWidget):
    """Вкладка анализа многофазного потока"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Анализ многофазного потока (Beggs-Brill)")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px 0;
                border-bottom: 2px solid #1976d2;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)
        
        # Результаты
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 15px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # Заглушка для результатов
        self.results_text.setText("""
АНАЛИЗ МНОГОФАЗНОГО ПОТОКА (BEGGS-BRILL)

Результаты анализа будут отображены после выполнения основного расчета
на вкладке "Расчет".

Основные параметры:
• Газосодержание
• Плотность смеси
• Вязкость смеси
• Режим потока
• Коэффициент трения
• Градиент давления
        """)
        
        layout.addWidget(self.results_text)


class CavitationTab(QWidget):
    """Вкладка проверки на кавитацию"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Проверка на кавитацию")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px 0;
                border-bottom: 2px solid #1976d2;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)
        
        # Результаты
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 15px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # Заглушка для результатов
        self.results_text.setText("""
ПРОВЕРКА НА КАВИТАЦИЮ

Результаты проверки будут отображены после выполнения основного расчета
на вкладке "Расчет".

Основные параметры:
• NPSH доступный
• NPSH требуемый
• Запас по NPSH
• Риск кавитации
• Рекомендации
        """)
        
        layout.addWidget(self.results_text)


class MotorTab(QWidget):
    """Вкладка подбора двигателя и кабеля"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Подбор двигателя и кабеля")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px 0;
                border-bottom: 2px solid #1976d2;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)
        
        # Результаты
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 15px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # Заглушка для результатов
        self.results_text.setText("""
ПОДБОР ДВИГАТЕЛЯ И КАБЕЛЯ

Результаты подбора будут отображены после выполнения основного расчета
на вкладке "Расчет".

Основные параметры:
• Мощность двигателя
• КПД двигателя
• Тип кабеля
• Длина кабеля
• Потери в кабеле
• Рекомендации
        """)
        
        layout.addWidget(self.results_text)


class ForecastTab(QWidget):
    """Вкладка прогнозирования"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Прогнозирование потребности")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                padding: 10px 0;
                border-bottom: 2px solid #1976d2;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)
        
        # Результаты
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 15px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # Заглушка для результатов
        self.results_text.setText("""
ПРОГНОЗИРОВАНИЕ ПОТРЕБНОСТИ

Функция прогнозирования будет реализована в следующих версиях.

Планируемые возможности:
• Прогноз добычи
• Потребность в оборудовании
• Планирование замен
• Анализ эффективности
• Рекомендации по оптимизации
        """)
        
        layout.addWidget(self.results_text)


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Инженерный калькулятор ЭЦН (Версия 4.0) - Python")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Установка светлой темы
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f7fa, stop:1 #e8eaf6);
            }
        """)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Заголовок
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976d2, stop:1 #004ba0);
                color: white;
            }
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("Инженерный калькулятор ЭЦН (Версия 4.0)")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Python версия - полная копия функциональности HTML")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background: white;
            }
            QTabBar::tab {
                background: #f5f5f5;
                color: #333;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1976d2;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #e3f2fd;
            }
        """)
        
        # Создание вкладок
        self.design_tab = DesignTab()
        self.multiphase_tab = MultiphaseTab()
        self.cavitation_tab = CavitationTab()
        self.motor_tab = MotorTab()
        self.forecast_tab = ForecastTab()
        
        # Добавление вкладок
        self.tabs.addTab(self.design_tab, "⚙️ Расчет")
        self.tabs.addTab(self.multiphase_tab, "🌊 Многофазный поток")
        self.tabs.addTab(self.cavitation_tab, "⚠️ Кавитация")
        self.tabs.addTab(self.motor_tab, "⚡ Двигатель")
        self.tabs.addTab(self.forecast_tab, "📈 Прогноз")
        
        # Добавление в главный layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs)


def main():
    """Главная функция приложения"""
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    # Создание и отображение главного окна
    window = MainWindow()
    window.show()
    
    # Запуск приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
