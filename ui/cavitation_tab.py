from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class CavitationTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Проверка на кавитацию")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ff5252;
                padding: 10px 0;
                border-bottom: 2px solid #ff5252;
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
        
        # Группа параметров жидкости
        fluid_group = QGroupBox("Параметры жидкости")
        fluid_group.setStyleSheet("""
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
                color: #ff5252;
            }
        """)
        fluid_layout = QFormLayout(fluid_group)
        
        self.pip_pressure = QDoubleSpinBox()
        self.pip_pressure.setRange(0, 500)
        self.pip_pressure.setValue(32.1)
        self.pip_pressure.setSuffix(" атм")
        self.pip_pressure.setDecimals(1)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0, 200)
        self.temperature.setValue(95)
        self.temperature.setSuffix(" °C")
        self.temperature.setDecimals(1)
        
        self.bubble_point = QDoubleSpinBox()
        self.bubble_point.setRange(0, 500)
        self.bubble_point.setValue(89.6)
        self.bubble_point.setSuffix(" атм")
        self.bubble_point.setDecimals(1)
        
        self.gas_oil_ratio = QDoubleSpinBox()
        self.gas_oil_ratio.setRange(0, 2000)
        self.gas_oil_ratio.setValue(251.7)
        self.gas_oil_ratio.setSuffix(" м³/м³")
        self.gas_oil_ratio.setDecimals(1)
        
        fluid_layout.addRow("Давление на входе (PIP):", self.pip_pressure)
        fluid_layout.addRow("Температура на забое:", self.temperature)
        fluid_layout.addRow("Давление насыщения:", self.bubble_point)
        fluid_layout.addRow("Газовый фактор:", self.gas_oil_ratio)
        
        # Группа параметров насоса
        pump_group = QGroupBox("Параметры насоса")
        pump_group.setStyleSheet(fluid_group.styleSheet())
        pump_layout = QFormLayout(pump_group)
        
        self.flow_rate = QDoubleSpinBox()
        self.flow_rate.setRange(0, 1000)
        self.flow_rate.setValue(80)
        self.flow_rate.setSuffix(" м³/сут")
        self.flow_rate.setDecimals(1)
        
        self.separator_loss = QDoubleSpinBox()
        self.separator_loss.setRange(0, 10)
        self.separator_loss.setValue(0.5)
        self.separator_loss.setSuffix(" атм")
        self.separator_loss.setDecimals(1)
        
        self.npsh_required = QDoubleSpinBox()
        self.npsh_required.setRange(0, 50)
        self.npsh_required.setValue(3.0)
        self.npsh_required.setSuffix(" м")
        self.npsh_required.setDecimals(1)
        
        pump_layout.addRow("Дебит жидкости:", self.flow_rate)
        pump_layout.addRow("Потери в сепараторе:", self.separator_loss)
        pump_layout.addRow("Требуемый NPSH:", self.npsh_required)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton("ПРОВЕРИТЬ КАВИТАЦИЮ")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5252, stop:1 #d32f2f);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #e53935);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d32f2f, stop:1 #b71c1c);
            }
        """)
        self.calc_btn.clicked.connect(self._on_calculate)
        
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addStretch()
        
        left_layout.addWidget(fluid_group)
        left_layout.addWidget(pump_group)
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
                    stop:0 #ff5252, stop:1 #d32f2f);
                border-radius: 3px;
            }
        """)
        
        # Статус
        self.status = QLabel("Заполните параметры и запустите проверку")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #ff5252;
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
        """Расчёт NPSH и проверка на кавитацию"""
        self.progress.setValue(10)
        self.status.setText("Выполняется проверка на кавитацию...")
        
        try:
            # Получаем входные данные
            pip_atm = self.pip_pressure.value()
            temp_c = self.temperature.value()
            pb_atm = self.bubble_point.value()
            gor = self.gas_oil_ratio.value()
            flow_rate = self.flow_rate.value()
            separator_loss = self.separator_loss.value()
            npsh_req = self.npsh_required.value()
            
            self.progress.setValue(30)
            
            # Расчёт NPSH
            result = self._calculate_npsh(
                pip_atm, temp_c, pb_atm, gor, 
                separator_loss, npsh_req
            )
            
            self.progress.setValue(70)
            
            # Отображение результатов
            self._display_results(result)
            
            # Построение графика
            self._plot_results(result)
            
            self.progress.setValue(100)
            self.status.setText("Проверка завершена")
            
        except Exception as e:
            self.status.setText(f"Ошибка расчёта: {str(e)}")
            self.progress.setValue(0)
    
    def _calculate_npsh(self, pip_atm, temp_c, pb_atm, gor, separator_loss, npsh_req):
        """Расчёт NPSH и проверка на кавитацию"""
        import math
        
        # Расчёт давления паров
        vapor_pressure = self._calculate_vapor_pressure(temp_c, pb_atm, gor)
        
        # Давление на входе в насос
        pump_inlet_pressure = pip_atm - separator_loss
        
        # Доступный NPSH
        npsh_available = pump_inlet_pressure - vapor_pressure
        
        # Запас по кавитации
        cavitation_margin = npsh_available - npsh_req
        
        # Статус кавитации
        if cavitation_margin >= 1.0:
            cavitation_status = "БЕЗОПАСНО"
            status_color = "green"
        elif cavitation_margin >= 0.5:
            cavitation_status = "ВНИМАНИЕ"
            status_color = "orange"
        else:
            cavitation_status = "ОПАСНО"
            status_color = "red"
        
        return {
            'vapor_pressure': vapor_pressure,
            'pump_inlet_pressure': pump_inlet_pressure,
            'npsh_available': npsh_available,
            'npsh_required': npsh_req,
            'cavitation_margin': cavitation_margin,
            'cavitation_status': cavitation_status,
            'status_color': status_color,
            'temp_c': temp_c,
            'pip_atm': pip_atm
        }
    
    def _calculate_vapor_pressure(self, temp_c, pb_atm, gor):
        """Расчёт давления паров по уравнению Антуана"""
        import math
        
        # Коэффициенты уравнения Антуана для углеводородов
        A = 6.834
        B = 948.2
        C = 239.7
        
        # Давление паров в мм рт.ст.
        log10_pv_mmHg = A - B / (temp_c + C)
        pv_mmHg = 10 ** log10_pv_mmHg
        
        # Пересчёт в атм
        pv_atm = pv_mmHg / 760
        
        # Ограничение давлением насыщения
        return min(pb_atm, max(0.03, pv_atm))
    
    def _display_results(self, result):
        """Отображение результатов расчёта"""
        status_emoji = {
            "БЕЗОПАСНО": "✅",
            "ВНИМАНИЕ": "⚠️", 
            "ОПАСНО": "❌"
        }
        
        text = f"""
СТАТУС КАВИТАЦИИ: {status_emoji.get(result['cavitation_status'], '❓')} {result['cavitation_status']}

ДАВЛЕНИЯ:
• Давление на входе (PIP): {result['pip_atm']:.2f} атм
• Давление на входе в насос: {result['pump_inlet_pressure']:.2f} атм
• Давление паров: {result['vapor_pressure']:.3f} атм

NPSH АНАЛИЗ:
• Доступный NPSH: {result['npsh_available']:.2f} м
• Требуемый NPSH: {result['npsh_required']:.2f} м
• Запас по кавитации: {result['cavitation_margin']:.2f} м

РЕКОМЕНДАЦИИ:
{self._get_recommendations(result)}
        """
        self.results.setText(text.strip())
    
    def _get_recommendations(self, result):
        """Получение рекомендаций по результатам"""
        margin = result['cavitation_margin']
        
        if margin >= 1.0:
            return "• Насос работает в безопасном режиме\n• Дополнительные меры не требуются"
        elif margin >= 0.5:
            return "• Рекомендуется мониторинг параметров\n• Рассмотреть снижение дебита при необходимости"
        else:
            return "• КРИТИЧЕСКАЯ СИТУАЦИЯ!\n• Немедленно снизить дебит\n• Проверить герметичность системы\n• Рассмотреть замену насоса"
    
    def _plot_results(self, result):
        """Построение графика NPSH"""
        self.ax.clear()
        
        # Данные для графика
        pressures = [
            result['pip_atm'],
            result['pump_inlet_pressure'], 
            result['vapor_pressure']
        ]
        labels = ['PIP', 'Вход насоса', 'Давление паров']
        colors = ['#4caf50', '#2196f3', '#ff5252']
        
        # Столбчатая диаграмма
        bars = self.ax.bar(labels, pressures, color=colors, alpha=0.7)
        
        # Линия требуемого NPSH
        self.ax.axhline(y=result['npsh_required'], color='orange', 
                       linestyle='--', linewidth=2, label=f'NPSH треб. = {result["npsh_required"]:.1f} м')
        
        # Настройка графика
        self.ax.set_ylabel('Давление, атм', color='#e0e0e0')
        self.ax.set_title('Анализ NPSH', color='#e0e0e0')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        # Цветовая индикация статуса
        status_color = result['status_color']
        if status_color == 'green':
            self.ax.set_facecolor('#1b5e20')
        elif status_color == 'orange':
            self.ax.set_facecolor('#e65100')
        else:
            self.ax.set_facecolor('#b71c1c')
        
        self.chart.draw()
