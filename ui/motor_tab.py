from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QProgressBar, QComboBox
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MotorTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Подбор двигателя и кабеля")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffd740;
                padding: 10px 0;
                border-bottom: 2px solid #ffd740;
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
        
        # Группа параметров насоса
        pump_group = QGroupBox("Параметры насоса")
        pump_group.setStyleSheet("""
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
                color: #ffd740;
            }
        """)
        pump_layout = QFormLayout(pump_group)
        
        self.power_required = QDoubleSpinBox()
        self.power_required.setRange(0, 1000)
        self.power_required.setValue(45.2)
        self.power_required.setSuffix(" кВт")
        self.power_required.setDecimals(1)
        
        self.voltage = QComboBox()
        self.voltage.addItems(["1000", "1500", "2000", "3000", "5000"])
        self.voltage.setCurrentText("1500")
        
        self.frequency = QDoubleSpinBox()
        self.frequency.setRange(30, 70)
        self.frequency.setValue(50)
        self.frequency.setSuffix(" Гц")
        self.frequency.setDecimals(1)
        
        self.efficiency = QDoubleSpinBox()
        self.efficiency.setRange(0.5, 1.0)
        self.efficiency.setValue(0.85)
        self.efficiency.setSuffix(" %")
        self.efficiency.setDecimals(2)
        
        pump_layout.addRow("Требуемая мощность:", self.power_required)
        pump_layout.addRow("Напряжение:", self.voltage)
        pump_layout.addRow("Частота:", self.frequency)
        pump_layout.addRow("КПД насоса:", self.efficiency)
        
        # Группа параметров кабеля
        cable_group = QGroupBox("Параметры кабеля")
        cable_group.setStyleSheet(pump_group.styleSheet())
        cable_layout = QFormLayout(cable_group)
        
        self.cable_length = QDoubleSpinBox()
        self.cable_length.setRange(100, 5000)
        self.cable_length.setValue(2630)
        self.cable_length.setSuffix(" м")
        self.cable_length.setDecimals(0)
        
        self.cable_type = QComboBox()
        self.cable_type.addItems(["Cu 4мм²", "Cu 6мм²", "Cu 10мм²", "Cu 16мм²", "Cu 25мм²"])
        self.cable_type.setCurrentText("Cu 6мм²")
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0, 200)
        self.temperature.setValue(95)
        self.temperature.setSuffix(" °C")
        self.temperature.setDecimals(1)
        
        cable_layout.addRow("Длина кабеля:", self.cable_length)
        cable_layout.addRow("Тип кабеля:", self.cable_type)
        cable_layout.addRow("Температура:", self.temperature)
        
        # Группа параметров двигателя
        motor_group = QGroupBox("Параметры двигателя")
        motor_group.setStyleSheet(pump_group.styleSheet())
        motor_layout = QFormLayout(motor_group)
        
        self.motor_power = QDoubleSpinBox()
        self.motor_power.setRange(0, 1000)
        self.motor_power.setValue(55)
        self.motor_power.setSuffix(" кВт")
        self.motor_power.setDecimals(1)
        
        self.motor_efficiency = QDoubleSpinBox()
        self.motor_efficiency.setRange(0.5, 1.0)
        self.motor_efficiency.setValue(0.92)
        self.motor_efficiency.setSuffix(" %")
        self.motor_efficiency.setDecimals(2)
        
        self.power_factor = QDoubleSpinBox()
        self.power_factor.setRange(0.5, 1.0)
        self.power_factor.setValue(0.88)
        self.power_factor.setDecimals(2)
        
        motor_layout.addRow("Мощность двигателя:", self.motor_power)
        motor_layout.addRow("КПД двигателя:", self.motor_efficiency)
        motor_layout.addRow("Коэффициент мощности:", self.power_factor)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton("РАССЧИТАТЬ ДВИГАТЕЛЬ")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffd740, stop:1 #f57f17);
                color: #000;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fff176, stop:1 #fbc02d);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f57f17, stop:1 #e65100);
            }
        """)
        self.calc_btn.clicked.connect(self._on_calculate)
        
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addStretch()
        
        left_layout.addWidget(pump_group)
        left_layout.addWidget(cable_group)
        left_layout.addWidget(motor_group)
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
                    stop:0 #ffd740, stop:1 #f57f17);
                border-radius: 3px;
            }
        """)
        
        # Статус
        self.status = QLabel("Заполните параметры и запустите расчёт")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #ffd740;
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
        """Расчёт параметров двигателя и кабеля"""
        self.progress.setValue(10)
        self.status.setText("Выполняется расчёт двигателя...")
        
        try:
            # Получаем входные данные
            power_req = self.power_required.value()
            voltage = float(self.voltage.currentText())
            frequency = self.frequency.value()
            pump_eff = self.efficiency.value()
            cable_length = self.cable_length.value()
            cable_type = self.cable_type.currentText()
            temp = self.temperature.value()
            motor_power = self.motor_power.value()
            motor_eff = self.motor_efficiency.value()
            power_factor = self.power_factor.value()
            
            self.progress.setValue(30)
            
            # Расчёт параметров
            result = self._calculate_motor_parameters(
                power_req, voltage, frequency, pump_eff,
                cable_length, cable_type, temp,
                motor_power, motor_eff, power_factor
            )
            
            self.progress.setValue(70)
            
            # Отображение результатов
            self._display_results(result)
            
            # Построение графика
            self._plot_results(result)
            
            self.progress.setValue(100)
            self.status.setText("Расчёт завершён")
            
        except Exception as e:
            self.status.setText(f"Ошибка расчёта: {str(e)}")
            self.progress.setValue(0)
    
    def _calculate_motor_parameters(self, power_req, voltage, frequency, pump_eff,
                                  cable_length, cable_type, temp, motor_power, 
                                  motor_eff, power_factor):
        """Расчёт параметров двигателя и кабеля"""
        
        # Расчёт тока двигателя
        current = (power_req * 1000) / (voltage * power_factor * motor_eff)
        
        # Расчёт сопротивления кабеля
        cable_resistance = self._get_cable_resistance(cable_type, cable_length, temp)
        
        # Потери в кабеле
        cable_losses = current ** 2 * cable_resistance
        
        # Напряжение на двигателе
        voltage_drop = current * cable_resistance
        motor_voltage = voltage - voltage_drop
        
        # Мощность на валу
        shaft_power = power_req / pump_eff
        
        # Общий КПД системы
        total_efficiency = pump_eff * motor_eff * (1 - cable_losses / (power_req * 1000))
        
        # Запас мощности
        power_margin = (motor_power - power_req) / power_req * 100
        
        # Статус подбора
        if power_margin >= 20:
            status = "ОТЛИЧНО"
            status_color = "green"
        elif power_margin >= 10:
            status = "ХОРОШО"
            status_color = "orange"
        else:
            status = "ВНИМАНИЕ"
            status_color = "red"
        
        return {
            'current': current,
            'cable_resistance': cable_resistance,
            'cable_losses': cable_losses,
            'voltage_drop': voltage_drop,
            'motor_voltage': motor_voltage,
            'shaft_power': shaft_power,
            'total_efficiency': total_efficiency,
            'power_margin': power_margin,
            'status': status,
            'status_color': status_color,
            'voltage': voltage,
            'motor_power': motor_power,
            'power_req': power_req
        }
    
    def _get_cable_resistance(self, cable_type, length, temp):
        """Получение сопротивления кабеля"""
        # Сопротивление на 1 км при 20°C (Ом/км)
        resistance_20 = {
            "Cu 4мм²": 4.61,
            "Cu 6мм²": 3.08,
            "Cu 10мм²": 1.83,
            "Cu 16мм²": 1.15,
            "Cu 25мм²": 0.727
        }
        
        base_resistance = resistance_20.get(cable_type, 3.08)
        
        # Температурная коррекция
        temp_coeff = 0.004  # для меди
        resistance = base_resistance * (1 + temp_coeff * (temp - 20))
        
        # Сопротивление для заданной длины
        return resistance * (length / 1000)
    
    def _display_results(self, result):
        """Отображение результатов расчёта"""
        status_emoji = {
            "ОТЛИЧНО": "✅",
            "ХОРОШО": "⚠️", 
            "ВНИМАНИЕ": "❌"
        }
        
        text = f"""
СТАТУС ПОДБОРА: {status_emoji.get(result['status'], '❓')} {result['status']}

ЭЛЕКТРИЧЕСКИЕ ПАРАМЕТРЫ:
• Ток двигателя: {result['current']:.1f} А
• Напряжение на двигателе: {result['motor_voltage']:.0f} В
• Падение напряжения: {result['voltage_drop']:.1f} В
• Сопротивление кабеля: {result['cable_resistance']:.2f} Ом

МОЩНОСТЬ И КПД:
• Мощность на валу: {result['shaft_power']:.1f} кВт
• Потери в кабеле: {result['cable_losses']:.1f} Вт
• Общий КПД системы: {result['total_efficiency']:.1%}
• Запас мощности: {result['power_margin']:.1f}%

РЕКОМЕНДАЦИИ:
{self._get_motor_recommendations(result)}
        """
        self.results.setText(text.strip())
    
    def _get_motor_recommendations(self, result):
        """Получение рекомендаций по подбору двигателя"""
        margin = result['power_margin']
        voltage_drop = result['voltage_drop']
        
        recommendations = []
        
        if margin >= 20:
            recommendations.append("• Двигатель подобран с хорошим запасом")
        elif margin >= 10:
            recommendations.append("• Запас мощности достаточный")
        else:
            recommendations.append("• Рекомендуется увеличить мощность двигателя")
        
        if voltage_drop > result['voltage'] * 0.05:
            recommendations.append("• Рассмотреть увеличение сечения кабеля")
        
        if result['total_efficiency'] < 0.7:
            recommendations.append("• Низкий общий КПД системы")
        
        return "\n".join(recommendations) if recommendations else "• Система подобрана оптимально"
    
    def _plot_results(self, result):
        """Построение графика распределения мощности"""
        self.ax.clear()
        
        # Данные для графика
        categories = ['Требуемая', 'Двигатель', 'На валу', 'Потери']
        values = [
            result['power_req'],
            result['motor_power'],
            result['shaft_power'],
            result['cable_losses'] / 1000  # в кВт
        ]
        colors = ['#4caf50', '#ffd740', '#2196f3', '#ff5252']
        
        # Столбчатая диаграмма
        bars = self.ax.bar(categories, values, color=colors, alpha=0.7)
        
        # Настройка графика
        self.ax.set_ylabel('Мощность, кВт', color='#e0e0e0')
        self.ax.set_title('Распределение мощности в системе', color='#e0e0e0')
        self.ax.grid(True, alpha=0.3)
        
        # Добавление значений на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{value:.1f}', ha='center', va='bottom', color='#e0e0e0')
        
        self.chart.draw()
