from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QProgressBar, QScrollArea
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class CalculationTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        # Главный контейнер с прокруткой
        main_widget = QWidget()
        main_widget.setMinimumSize(1200, 600)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Расчёт основных параметров")
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
        
        # Основной контент в две колонки
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        
        # Левая колонка - параметры
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_widget.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Группа параметров расчёта
        calc_group = QGroupBox("Параметры расчёта")
        calc_group.setStyleSheet("""
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
        calc_form = QFormLayout(calc_group)
        calc_form.setSpacing(8)
        
        self.pressure = self._spin(calc_form, "Давление, атм:", 89.6, 0.1)
        self.temperature = self._spin(calc_form, "Температура, °C:", 95, 0.1)
        self.flow_rate = self._spin(calc_form, "Дебит, м³/сут:", 80, 1)
        self.density = self._spin(calc_form, "Плотность, кг/м³:", 1016, 1)
        
        # Кнопка расчёта
        self.calc_btn = QPushButton("ВЫПОЛНИТЬ РАСЧЁТ")
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
        """)
        
        left_layout.addWidget(calc_group)
        left_layout.addWidget(self.calc_btn)
        left_layout.addStretch()
        
        # Правая колонка - результаты
        right_widget = QWidget()
        right_widget.setMinimumWidth(800)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Прогресс
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
                    stop:0 #4caf50, stop:1 #2e7d32);
                border-radius: 3px;
            }
        """)
        
        # Статус
        self.status = QLabel("Заполните параметры и запустите расчёт")
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
        
        # Результаты
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setMaximumHeight(200)
        self.results.setStyleSheet("""
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
        
        # График
        self.chart = FigureCanvasQTAgg(Figure(figsize=(8, 5)))
        self.chart.setMinimumSize(600, 400)
        self.chart.setMaximumSize(800, 500)
        self.chart.figure.patch.set_facecolor('#ffffff')
        self.ax = self.chart.figure.add_subplot(111)
        self.ax.set_facecolor('#ffffff')
        self.ax.tick_params(colors='#333333')
        self.ax.spines['bottom'].set_color('#e0e0e0')
        self.ax.spines['top'].set_color('#e0e0e0')
        self.ax.spines['right'].set_color('#e0e0e0')
        self.ax.spines['left'].set_color('#e0e0e0')
        
        right_layout.addWidget(self.progress)
        right_layout.addWidget(self.status)
        right_layout.addWidget(self.results)
        right_layout.addWidget(self.chart)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        layout.addLayout(main_layout)
        
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
        main_layout_final = QVBoxLayout(self)
        main_layout_final.setContentsMargins(0, 0, 0, 0)
        main_layout_final.addWidget(scroll_area)
        
        # Подключаем кнопку
        self.calc_btn.clicked.connect(self._on_calculate)
        
        # Автоматически запускаем расчёт
        self._run_initial_calculation()
        
    def _run_initial_calculation(self):
        """Запуск начального расчёта"""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, self._on_calculate)
        
    def _on_calculate(self):
        """Выполнение расчёта"""
        self.progress.setValue(10)
        self.status.setText("Выполняется расчёт...")
        
        # Простой расчёт
        pressure = self.pressure.value()
        temperature = self.temperature.value()
        flow_rate = self.flow_rate.value()
        density = self.density.value()
        
        # Имитация расчёта
        result_pressure = pressure * 1.1
        result_temperature = temperature + 5
        efficiency = 0.85
        
        self.progress.setValue(50)
        
        # Отображаем результаты
        self.results.setText(f"""
РЕЗУЛЬТАТЫ РАСЧЁТА:
• Выходное давление: {result_pressure:.1f} атм
• Выходная температура: {result_temperature:.1f} °C
• КПД системы: {efficiency:.1%}
• Мощность: {flow_rate * density * 0.1:.1f} кВт
        """)
        
        # Простой график
        self.ax.clear()
        x = [0, 1, 2, 3, 4]
        y = [pressure, result_pressure, pressure*0.9, pressure*0.8, pressure*0.7]
        self.ax.plot(x, y, 'b-', linewidth=2, label='Давление')
        self.ax.set_xlabel('Время, ч')
        self.ax.set_ylabel('Давление, атм')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.chart.draw()
        
        self.progress.setValue(100)
        self.status.setText("Расчёт завершён")
        
    def _spin(self, layout: QFormLayout, label: str, val: float, step: float, mn: float = 0.0, mx: float = 1e9) -> QDoubleSpinBox:
        w = QDoubleSpinBox()
        w.setDecimals(6)
        w.setRange(mn, mx)
        w.setSingleStep(step)
        w.setValue(val)
        w.setStyleSheet("""
            QDoubleSpinBox {
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                min-height: 20px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976d2;
            }
        """)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                font-weight: normal;
                padding: 2px;
            }
        """)
        
        layout.addRow(label_widget, w)
        return w
