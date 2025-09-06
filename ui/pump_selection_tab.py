from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QProgressBar, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PumpSelectionTab(QWidget):
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
        title = QLabel("Подбор насоса")
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
        
        # Левая колонка - критерии подбора
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_widget.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Группа критериев
        criteria_group = QGroupBox("Критерии подбора")
        criteria_group.setStyleSheet("""
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
        criteria_form = QFormLayout(criteria_group)
        criteria_form.setSpacing(8)
        
        self.required_flow = self._spin(criteria_form, "Требуемый дебит, м³/сут:", 80, 1)
        self.required_head = self._spin(criteria_form, "Требуемый напор, м:", 740, 1)
        self.efficiency_min = self._spin(criteria_form, "Мин. КПД, %:", 70, 1, 0, 100)
        self.power_max = self._spin(criteria_form, "Макс. мощность, кВт:", 100, 1)
        
        # Кнопка подбора
        self.select_btn = QPushButton("ПОДОБРАТЬ НАСОС")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9800, stop:1 #f57c00);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffb74d, stop:1 #ff8f00);
            }
        """)
        
        left_layout.addWidget(criteria_group)
        left_layout.addWidget(self.select_btn)
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
                    stop:0 #ff9800, stop:1 #f57c00);
                border-radius: 3px;
            }
        """)
        
        # Статус
        self.status = QLabel("Заполните критерии и запустите подбор")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #ff9800;
                font-size: 14px;
                padding: 10px;
                background: #fff3e0;
                border-radius: 6px;
                border: 1px solid #ffcc02;
            }
        """)
        
        # Таблица насосов
        self.pump_table = QTableWidget()
        self.pump_table.setColumnCount(5)
        self.pump_table.setHorizontalHeaderLabels([
            "Модель", "Дебит, м³/сут", "Напор, м", "КПД, %", "Мощность, кВт"
        ])
        self.pump_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pump_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background: #e3f2fd;
            }
            QHeaderView::section {
                background: #f5f5f5;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # График
        self.chart = FigureCanvasQTAgg(Figure(figsize=(8, 4)))
        self.chart.setMinimumSize(600, 300)
        self.chart.setMaximumSize(800, 400)
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
        right_layout.addWidget(self.pump_table)
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
        self.select_btn.clicked.connect(self._on_select)
        
        # Автоматически запускаем подбор
        self._run_initial_selection()
        
    def _run_initial_selection(self):
        """Запуск начального подбора"""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, self._on_select)
        
    def _on_select(self):
        """Выполнение подбора насоса"""
        self.progress.setValue(10)
        self.status.setText("Выполняется подбор насоса...")
        
        # Данные для подбора
        required_flow = self.required_flow.value()
        required_head = self.required_head.value()
        efficiency_min = self.efficiency_min.value()
        power_max = self.power_max.value()
        
        self.progress.setValue(30)
        
        # Имитация подбора насосов
        pumps = [
            ["ЭЦН-5-160", 60, 800, 75, 45],
            ["ЭЦН-6-200", 80, 740, 82, 55],
            ["ЭЦН-8-320", 100, 900, 78, 65],
            ["ЭЦН-10-400", 120, 1000, 80, 75],
        ]
        
        # Фильтруем насосы по критериям
        suitable_pumps = []
        for pump in pumps:
            if (pump[1] >= required_flow * 0.9 and 
                pump[2] >= required_head * 0.9 and 
                pump[3] >= efficiency_min and 
                pump[4] <= power_max):
                suitable_pumps.append(pump)
        
        self.progress.setValue(60)
        
        # Заполняем таблицу
        self.pump_table.setRowCount(len(suitable_pumps))
        for i, pump in enumerate(suitable_pumps):
            for j, value in enumerate(pump):
                item = QTableWidgetItem(str(value))
                if j == 0:  # Модель
                    item.setBackground(Qt.lightGray)
                self.pump_table.setItem(i, j, item)
        
        self.progress.setValue(80)
        
        # Строим график
        self.ax.clear()
        if suitable_pumps:
            flows = [pump[1] for pump in suitable_pumps]
            heads = [pump[2] for pump in suitable_pumps]
            self.ax.scatter(flows, heads, s=100, c='blue', alpha=0.7)
            self.ax.scatter([required_flow], [required_head], s=150, c='red', marker='x', linewidth=3, label='Требования')
            self.ax.set_xlabel('Дебит, м³/сут')
            self.ax.set_ylabel('Напор, м')
            self.ax.grid(True, alpha=0.3)
            self.ax.legend()
        self.chart.draw()
        
        self.progress.setValue(100)
        self.status.setText(f"Найдено {len(suitable_pumps)} подходящих насосов")
        
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
                border: 2px solid #ff9800;
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
