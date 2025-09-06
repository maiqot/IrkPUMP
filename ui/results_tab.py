from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QProgressBar, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ResultsTab(QWidget):
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
        title = QLabel("Результаты расчёта")
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
        
        # Левая колонка - сводка результатов
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_widget.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Группа основных результатов
        results_group = QGroupBox("Основные результаты")
        results_group.setStyleSheet("""
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
        results_form = QFormLayout(results_group)
        results_form.setSpacing(8)
        
        # Поля результатов (только для чтения)
        self.tdh_result = self._create_result_field(results_form, "TDH, м:", "740.0")
        self.pip_result = self._create_result_field(results_form, "PIP, атм:", "32.1")
        self.gas_fraction = self._create_result_field(results_form, "Газ, φ, %:", "18.4")
        self.efficiency = self._create_result_field(results_form, "КПД, %:", "82.5")
        self.power = self._create_result_field(results_form, "Мощность, кВт:", "45.2")
        
        # Кнопка экспорта
        self.export_btn = QPushButton("ЭКСПОРТИРОВАТЬ РЕЗУЛЬТАТЫ")
        self.export_btn.setStyleSheet("""
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
        
        left_layout.addWidget(results_group)
        left_layout.addWidget(self.export_btn)
        left_layout.addStretch()
        
        # Правая колонка - детальные результаты и графики
        right_widget = QWidget()
        right_widget.setMinimumWidth(800)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Статус
        self.status = QLabel("Расчёт завершён успешно")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #4caf50;
                font-size: 14px;
                padding: 10px;
                background: #e8f5e8;
                border-radius: 6px;
                border: 1px solid #4caf50;
            }
        """)
        
        # Детальная таблица результатов
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(2)
        self.details_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.details_table.setMaximumHeight(200)
        self.details_table.setStyleSheet("""
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
        
        # График результатов
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
        
        right_layout.addWidget(self.status)
        right_layout.addWidget(self.details_table)
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
        self.export_btn.clicked.connect(self._on_export)
        
        # Загружаем результаты
        self._load_results()
        
    def _load_results(self):
        """Загрузка результатов расчёта"""
        # Заполняем детальную таблицу
        details = [
            ("Пластовое давление", "89.6 атм"),
            ("Давление насыщения", "89.6 атм"),
            ("Газосодержание", "251.7 м³/м³"),
            ("Обводненность", "52.7 %"),
            ("Плотность жидкости", "1016 кг/м³"),
            ("Вязкость", "0.44 сПз"),
            ("Глубина насоса", "2630 м"),
            ("Устьевое давление", "25.0 атм"),
            ("Проектный дебит", "80.0 м³/сут"),
            ("Рабочий дебит", "80.0 м³/сут"),
            ("Рабочий напор", "740.0 м"),
            ("КПД насоса", "82.5 %"),
            ("Мощность", "45.2 кВт"),
            ("NPSH доступный", "18.4 м"),
            ("NPSH требуемый", "3.0 м"),
        ]
        
        self.details_table.setRowCount(len(details))
        for i, (param, value) in enumerate(details):
            param_item = QTableWidgetItem(param)
            value_item = QTableWidgetItem(value)
            value_item.setBackground(Qt.lightGray)
            self.details_table.setItem(i, 0, param_item)
            self.details_table.setItem(i, 1, value_item)
        
        # Строим график
        self._draw_chart()
        
    def _draw_chart(self):
        """Построение графика результатов"""
        self.ax.clear()
        
        # Данные для графика
        q = [20, 40, 60, 80, 100, 120]
        h = [900, 850, 800, 740, 660, 560]
        work_q = 80
        work_h = 740
        
        # Кривая насоса
        self.ax.plot(q, h, 'b-', linewidth=2, label='H(Q)')
        
        # Рабочая точка
        self.ax.scatter([work_q], [work_h], s=100, c='red', zorder=5, label='Рабочая точка')
        
        # Зона оптимальной работы
        optimal_q = [work_q * 0.7, work_q * 1.1]
        optimal_h = [max(h) * 1.1, max(h) * 1.1]
        self.ax.fill_between(optimal_q, 0, optimal_h, alpha=0.2, color='green', label='Оптимальная зона')
        
        self.ax.set_xlabel('Q, м³/сут')
        self.ax.set_ylabel('H, м')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.ax.set_title('Характеристика насоса')
        
        self.chart.draw()
        
    def _on_export(self):
        """Экспорт результатов"""
        self.status.setText("Экспорт результатов...")
        # Здесь можно добавить логику экспорта
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.status.setText("Результаты экспортированы"))
        
    def _create_result_field(self, layout: QFormLayout, label: str, value: str) -> QLabel:
        """Создание поля результата (только для чтения)"""
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                font-weight: bold;
                color: #1976d2;
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
        
        layout.addRow(label_widget, value_label)
        return value_label
