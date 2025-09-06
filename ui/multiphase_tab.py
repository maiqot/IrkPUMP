from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MultiphaseTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Анализ многофазного потока (Beggs-Brill)")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #90caf9;
                padding: 10px 0;
                border-bottom: 2px solid #90caf9;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)
        
        # Основной контент в две колонки
        main_layout = QHBoxLayout()
        
        # Левая колонка - параметры
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        
        # Группа параметров потока
        flow_group = QGroupBox("Параметры потока")
        flow_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #90caf9;
            }
        """)
        flow_layout = QFormLayout(flow_group)
        
        self.flow_rate = QDoubleSpinBox()
        self.flow_rate.setRange(0, 1000)
        self.flow_rate.setValue(80)
        self.flow_rate.setSuffix(" м³/сут")
        self.flow_rate.setDecimals(1)
        
        self.gas_rate = QDoubleSpinBox()
        self.gas_rate.setRange(0, 10000)
        self.gas_rate.setValue(200)
        self.gas_rate.setSuffix(" м³/сут")
        self.gas_rate.setDecimals(1)
        
        self.liquid_density = QDoubleSpinBox()
        self.liquid_density.setRange(800, 1200)
        self.liquid_density.setValue(1016)
        self.liquid_density.setSuffix(" кг/м³")
        self.liquid_density.setDecimals(1)
        
        self.gas_density = QDoubleSpinBox()
        self.gas_density.setRange(0.5, 2.0)
        self.gas_density.setValue(0.85)
        self.gas_density.setSuffix(" отн.возд.")
        self.gas_density.setDecimals(2)
        
        flow_layout.addRow("Дебит жидкости:", self.flow_rate)
        flow_layout.addRow("Дебит газа:", self.gas_rate)
        flow_layout.addRow("Плотность жидкости:", self.liquid_density)
        flow_layout.addRow("Плотность газа:", self.gas_density)
        
        # Группа геометрии
        geometry_group = QGroupBox("Геометрия скважины")
        geometry_group.setStyleSheet(flow_group.styleSheet())
        geometry_layout = QFormLayout(geometry_group)
        
        self.tubing_id = QDoubleSpinBox()
        self.tubing_id.setRange(40, 200)
        self.tubing_id.setValue(62)
        self.tubing_id.setSuffix(" мм")
        self.tubing_id.setDecimals(1)
        
        self.pump_depth = QDoubleSpinBox()
        self.pump_depth.setRange(100, 5000)
        self.pump_depth.setValue(2630)
        self.pump_depth.setSuffix(" м")
        self.pump_depth.setDecimals(0)
        
        geometry_layout.addRow("ID НКТ:", self.tubing_id)
        geometry_layout.addRow("Глубина насоса:", self.pump_depth)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton("РАСЧИТАТЬ МНОГОФАЗНЫЙ ПОТОК")
        self.calc_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e7d32, stop:1 #1b5e20);
            }
        """)
        self.calc_btn.clicked.connect(self._on_calculate)
        
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addStretch()
        
        left_layout.addWidget(flow_group)
        left_layout.addWidget(geometry_group)
        left_layout.addLayout(btn_layout)
        left_layout.addStretch()
        
        # Правая колонка - результаты
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        
        # Прогресс
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #333;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:1 #2e7d32);
                border-radius: 3px;
            }
        """)
        
        # Статус
        self.status = QLabel("Заполните параметры и запустите расчёт")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #90caf9;
                font-size: 14px;
                padding: 10px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border: 1px solid #555;
            }
        """)
        
        # Результаты
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setMaximumHeight(200)
        self.results.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # График
        self.chart = FigureCanvasQTAgg(Figure(figsize=(6, 4)))
        self.chart.figure.patch.set_facecolor('#2a2a2a')
        self.ax = self.chart.figure.add_subplot(111)
        self.ax.set_facecolor('#2a2a2a')
        self.ax.tick_params(colors='#e0e0e0')
        self.ax.spines['bottom'].set_color('#555')
        self.ax.spines['top'].set_color('#555')
        self.ax.spines['right'].set_color('#555')
        self.ax.spines['left'].set_color('#555')
        
        right_layout.addWidget(self.progress)
        right_layout.addWidget(self.status)
        right_layout.addWidget(self.results)
        right_layout.addWidget(self.chart)
        
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 2)
        layout.addLayout(main_layout)
        
    def _on_calculate(self):
        """Расчёт многофазного потока по методу Beggs-Brill"""
        self.progress.setValue(10)
        self.status.setText("Выполняется расчёт...")
        
        try:
            # Получаем входные данные
            flow_rate_m3 = self.flow_rate.value()
            gas_rate_m3 = self.gas_rate.value()
            liquid_density = self.liquid_density.value()
            gas_density = self.gas_density.value() * 1.225  # кг/м³
            tubing_id_mm = self.tubing_id.value()
            pump_depth = self.pump_depth.value()
            
            self.progress.setValue(30)
            
            # Расчёт по Beggs-Brill
            result = self._calculate_beggs_brill(
                flow_rate_m3, gas_rate_m3, liquid_density, 
                gas_density, tubing_id_mm, pump_depth
            )
            
            self.progress.setValue(70)
            
            # Отображение результатов
            self._display_results(result)
            
            # Построение графика
            self._plot_results(result)
            
            self.progress.setValue(100)
            self.status.setText("Расчёт завершён успешно")
            
        except Exception as e:
            self.status.setText(f"Ошибка расчёта: {str(e)}")
            self.progress.setValue(0)
    
    def _calculate_beggs_brill(self, flow_rate_m3, gas_rate_m3, rho_l, rho_g, tubing_id_mm, depth):
        """Расчёт многофазного потока по методу Beggs-Brill"""
        import math
        
        # Константы
        G = 9.81  # м/с²
        
        # Пересчёт единиц
        tubing_id_m = tubing_id_mm / 1000
        flow_rate_m3_s = flow_rate_m3 / (24 * 3600)
        gas_rate_m3_s = gas_rate_m3 / (24 * 3600)
        
        # Геометрия
        area = math.pi * (tubing_id_m / 2) ** 2
        
        # Скорости
        v_sl = flow_rate_m3_s / area  # скорость жидкости
        v_sg = gas_rate_m3_s / area   # скорость газа
        v_m = v_sl + v_sg             # смешанная скорость
        
        # Объёмные доли
        lambda_l = v_sl / v_m if v_m > 0 else 0
        
        # Число Фруда
        froude = v_m ** 2 / (G * tubing_id_m) if tubing_id_m > 0 else 0
        
        # Определение режима течения
        if froude < 0.01:
            flow_pattern = "Сегментный"
        elif froude < 0.1:
            flow_pattern = "Переходный"
        elif froude < 1.0:
            flow_pattern = "Пробковый"
        else:
            flow_pattern = "Рассеянный"
        
        # Коэффициенты Beggs-Brill
        L1 = 316 * lambda_l ** 0.302
        L2 = 0.00091 * lambda_l ** -2.843
        L3 = 0.1 * lambda_l ** -1.538
        L4 = 0.5 * lambda_l ** -6.389
        
        # Объёмная доля газа
        if froude < L1:
            void_fraction = L2 * froude ** L3
        else:
            void_fraction = L4 * froude ** L3
        
        void_fraction = max(0, min(1, void_fraction))
        
        # Смешанная плотность
        rho_m = rho_l * (1 - void_fraction) + rho_g * void_fraction
        
        # Потери давления на трение (упрощённо)
        reynolds = rho_m * v_m * tubing_id_m / (0.001)  # вязкость ~1 мПа·с
        friction_factor = 0.005 if reynolds > 0 else 0.005
        pressure_drop = friction_factor * (depth / tubing_id_m) * (rho_m * v_m ** 2) / 2
        
        # Гидростатическое давление
        hydrostatic_pressure = rho_m * G * depth
        
        # Общие потери давления
        total_pressure_drop = pressure_drop + hydrostatic_pressure
        
        return {
            'flow_pattern': flow_pattern,
            'void_fraction': void_fraction * 100,
            'mixed_density': rho_m,
            'liquid_velocity': v_sl,
            'gas_velocity': v_sg,
            'mixed_velocity': v_m,
            'froude_number': froude,
            'reynolds_number': reynolds,
            'friction_pressure_drop': pressure_drop / 101325,  # в атм
            'hydrostatic_pressure': hydrostatic_pressure / 101325,  # в атм
            'total_pressure_drop': total_pressure_drop / 101325,  # в атм
            'depth': depth
        }
    
    def _display_results(self, result):
        """Отображение результатов расчёта"""
        text = f"""
РЕЖИМ ТЕЧЕНИЯ: {result['flow_pattern']}

ОСНОВНЫЕ ПАРАМЕТРЫ:
• Объёмная доля газа: {result['void_fraction']:.1f}%
• Смешанная плотность: {result['mixed_density']:.1f} кг/м³
• Скорость жидкости: {result['liquid_velocity']:.3f} м/с
• Скорость газа: {result['gas_velocity']:.3f} м/с
• Смешанная скорость: {result['mixed_velocity']:.3f} м/с

ЧИСЛА ПОДОБИЯ:
• Число Фруда: {result['froude_number']:.4f}
• Число Рейнольдса: {result['reynolds_number']:.0f}

ПОТЕРИ ДАВЛЕНИЯ:
• На трение: {result['friction_pressure_drop']:.2f} атм
• Гидростатическое: {result['hydrostatic_pressure']:.2f} атм
• ОБЩИЕ ПОТЕРИ: {result['total_pressure_drop']:.2f} атм
        """
        self.results.setText(text.strip())
    
    def _plot_results(self, result):
        """Построение графика распределения давления"""
        self.ax.clear()
        
        # Данные для графика
        depths = [0, result['depth']]
        pressures = [0, result['total_pressure_drop']]
        
        # График
        self.ax.plot(pressures, depths, 'b-', linewidth=2, label='Общее давление')
        self.ax.fill_between(pressures, depths, alpha=0.3, color='blue')
        
        # Настройка графика
        self.ax.set_xlabel('Давление, атм', color='#e0e0e0')
        self.ax.set_ylabel('Глубина, м', color='#e0e0e0')
        self.ax.set_title('Распределение давления по глубине', color='#e0e0e0')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        # Инвертировать ось Y (глубина увеличивается вниз)
        self.ax.invert_yaxis()
        
        self.chart.draw()
