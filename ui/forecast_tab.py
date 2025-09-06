from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QProgressBar, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class ForecastTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Прогнозирование потребности")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #69f0ae;
                padding: 10px 0;
                border-bottom: 2px solid #69f0ae;
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
        
        # Группа параметров прогноза
        forecast_group = QGroupBox("Параметры прогноза")
        forecast_group.setStyleSheet("""
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
                color: #69f0ae;
            }
        """)
        forecast_layout = QFormLayout(forecast_group)
        
        self.decline_type = QComboBox()
        self.decline_type.addItems(["Экспоненциальное", "Гиперболическое"])
        self.decline_type.currentTextChanged.connect(self._on_decline_type_changed)
        
        self.decline_rate = QDoubleSpinBox()
        self.decline_rate.setRange(0.1, 20.0)
        self.decline_rate.setValue(2.0)
        self.decline_rate.setSuffix(" %/мес")
        self.decline_rate.setDecimals(1)
        
        self.hyperbolic_n = QDoubleSpinBox()
        self.hyperbolic_n.setRange(0.01, 1.0)
        self.hyperbolic_n.setValue(0.5)
        self.hyperbolic_n.setDecimals(2)
        self.hyperbolic_n.setVisible(False)  # Скрыто по умолчанию
        
        self.forecast_period = QSpinBox()
        self.forecast_period.setRange(1, 120)
        self.forecast_period.setValue(24)
        self.forecast_period.setSuffix(" мес")
        
        self.initial_rate = QDoubleSpinBox()
        self.initial_rate.setRange(1, 1000)
        self.initial_rate.setValue(80)
        self.initial_rate.setSuffix(" м³/сут")
        self.initial_rate.setDecimals(1)
        
        forecast_layout.addRow("Тип падения добычи:", self.decline_type)
        forecast_layout.addRow("Коэффициент падения (D):", self.decline_rate)
        forecast_layout.addRow("Параметр гиперболы (n):", self.hyperbolic_n)
        forecast_layout.addRow("Период прогноза:", self.forecast_period)
        forecast_layout.addRow("Начальный дебит:", self.initial_rate)
        
        # Группа экономических параметров
        economic_group = QGroupBox("Экономические параметры")
        economic_group.setStyleSheet(forecast_group.styleSheet())
        economic_layout = QFormLayout(economic_group)
        
        self.oil_price = QDoubleSpinBox()
        self.oil_price.setRange(10, 200)
        self.oil_price.setValue(60)
        self.oil_price.setSuffix(" $/барр")
        self.oil_price.setDecimals(1)
        
        self.operating_cost = QDoubleSpinBox()
        self.operating_cost.setRange(0, 100)
        self.operating_cost.setValue(15)
        self.operating_cost.setSuffix(" $/барр")
        self.operating_cost.setDecimals(1)
        
        self.discount_rate = QDoubleSpinBox()
        self.discount_rate.setRange(0, 50)
        self.discount_rate.setValue(10)
        self.discount_rate.setSuffix(" %")
        self.discount_rate.setDecimals(1)
        
        economic_layout.addRow("Цена нефти:", self.oil_price)
        economic_layout.addRow("Операционные расходы:", self.operating_cost)
        economic_layout.addRow("Ставка дисконтирования:", self.discount_rate)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton("ЗАПУСТИТЬ ПРОГНОЗ")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #69f0ae, stop:1 #2e7d32);
                color: #000;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a5d6a7, stop:1 #388e3c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e7d32, stop:1 #1b5e20);
            }
        """)
        self.calc_btn.clicked.connect(self._on_calculate)
        
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addStretch()
        
        left_layout.addWidget(forecast_group)
        left_layout.addWidget(economic_group)
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
                    stop:0 #69f0ae, stop:1 #2e7d32);
                border-radius: 3px;
            }
        """)
        
        # Статус
        self.status = QLabel("Заполните параметры и запустите прогноз")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #69f0ae;
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
        
    def _on_decline_type_changed(self, text):
        """Обработка изменения типа падения добычи"""
        is_hyperbolic = text == "Гиперболическое"
        self.hyperbolic_n.setVisible(is_hyperbolic)
        
    def _on_calculate(self):
        """Расчёт прогноза добычи"""
        self.progress.setValue(10)
        self.status.setText("Выполняется прогноз добычи...")
        
        try:
            # Получаем входные данные
            decline_type = self.decline_type.currentText()
            decline_rate = self.decline_rate.value() / 100  # в долях
            hyperbolic_n = self.hyperbolic_n.value()
            forecast_period = self.forecast_period.value()
            initial_rate = self.initial_rate.value()
            oil_price = self.oil_price.value()
            operating_cost = self.operating_cost.value()
            discount_rate = self.discount_rate.value() / 100
            
            self.progress.setValue(30)
            
            # Расчёт прогноза
            result = self._calculate_forecast(
                decline_type, decline_rate, hyperbolic_n, forecast_period,
                initial_rate, oil_price, operating_cost, discount_rate
            )
            
            self.progress.setValue(70)
            
            # Отображение результатов
            self._display_results(result)
            
            # Построение графика
            self._plot_results(result)
            
            self.progress.setValue(100)
            self.status.setText("Прогноз завершён")
            
        except Exception as e:
            self.status.setText(f"Ошибка расчёта: {str(e)}")
            self.progress.setValue(0)
    
    def _calculate_forecast(self, decline_type, decline_rate, hyperbolic_n, 
                          forecast_period, initial_rate, oil_price, 
                          operating_cost, discount_rate):
        """Расчёт прогноза добычи"""
        
        # Временной ряд
        months = np.arange(0, forecast_period + 1)
        
        # Расчёт дебитов
        if decline_type == "Экспоненциальное":
            rates = initial_rate * np.exp(-decline_rate * months)
        else:  # Гиперболическое
            rates = initial_rate / (1 + hyperbolic_n * decline_rate * months) ** (1 / hyperbolic_n)
        
        # Конвертация в баррели (1 м³ ≈ 6.29 баррелей)
        rates_bbl = rates * 6.29
        
        # Расчёт доходов и расходов
        revenues = rates_bbl * oil_price
        costs = rates_bbl * operating_cost
        profits = revenues - costs
        
        # Дисконтированные денежные потоки
        discount_factors = 1 / (1 + discount_rate) ** (months / 12)
        discounted_profits = profits * discount_factors
        
        # Накопленные показатели
        cumulative_production = np.cumsum(rates_bbl)
        cumulative_revenue = np.cumsum(revenues)
        cumulative_profit = np.cumsum(profits)
        npv = np.sum(discounted_profits)
        
        # Ключевые показатели
        final_rate = rates[-1]
        total_production = cumulative_production[-1]
        total_revenue = cumulative_revenue[-1]
        total_profit = cumulative_profit[-1]
        
        # Точка безубыточности
        breakeven_month = None
        for i, profit in enumerate(cumulative_profit):
            if profit >= 0:
                breakeven_month = i
                break
        
        return {
            'months': months,
            'rates': rates,
            'rates_bbl': rates_bbl,
            'revenues': revenues,
            'costs': costs,
            'profits': profits,
            'discounted_profits': discounted_profits,
            'cumulative_production': cumulative_production,
            'cumulative_revenue': cumulative_revenue,
            'cumulative_profit': cumulative_profit,
            'final_rate': final_rate,
            'total_production': total_production,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'npv': npv,
            'breakeven_month': breakeven_month,
            'decline_type': decline_type
        }
    
    def _display_results(self, result):
        """Отображение результатов прогноза"""
        text = f"""
ПРОГНОЗНЫЕ ВЫВОДЫ:

ПРОИЗВОДСТВЕННЫЕ ПОКАЗАТЕЛИ:
• Начальный дебит: {result['rates'][0]:.1f} м³/сут
• Конечный дебит: {result['final_rate']:.1f} м³/сут
• Общая добыча: {result['total_production']:.0f} баррелей
• Тип падения: {result['decline_type']}

ЭКОНОМИЧЕСКИЕ ПОКАЗАТЕЛИ:
• Общая выручка: ${result['total_revenue']:,.0f}
• Общая прибыль: ${result['total_profit']:,.0f}
• NPV: ${result['npv']:,.0f}
• Точка безубыточности: {result['breakeven_month']} мес

РЕКОМЕНДАЦИИ:
{self._get_forecast_recommendations(result)}
        """
        self.results.setText(text.strip())
    
    def _get_forecast_recommendations(self, result):
        """Получение рекомендаций по прогнозу"""
        recommendations = []
        
        if result['npv'] > 0:
            recommendations.append("• Проект экономически эффективен")
        else:
            recommendations.append("• Проект убыточен")
        
        if result['breakeven_month'] is not None and result['breakeven_month'] < 12:
            recommendations.append("• Быстрая окупаемость")
        elif result['breakeven_month'] is not None:
            recommendations.append("• Средний срок окупаемости")
        else:
            recommendations.append("• Проект не окупается")
        
        if result['final_rate'] > result['rates'][0] * 0.3:
            recommendations.append("• Стабильная добыча")
        else:
            recommendations.append("• Резкое падение добычи")
        
        return "\n".join(recommendations)
    
    def _plot_results(self, result):
        """Построение графика прогноза"""
        self.ax.clear()
        
        # Основной график - дебит
        ax1 = self.ax
        line1 = ax1.plot(result['months'], result['rates'], 'b-', linewidth=2, label='Дебит, м³/сут')
        ax1.set_xlabel('Время, мес', color='#e0e0e0')
        ax1.set_ylabel('Дебит, м³/сут', color='#e0e0e0')
        ax1.tick_params(axis='y', labelcolor='#e0e0e0')
        ax1.grid(True, alpha=0.3)
        
        # Вторичная ось - накопленная добыча
        ax2 = ax1.twinx()
        line2 = ax2.plot(result['months'], result['cumulative_production'], 'r--', linewidth=2, label='Накопленная добыча, барр')
        ax2.set_ylabel('Накопленная добыча, барр', color='#e0e0e0')
        ax2.tick_params(axis='y', labelcolor='#e0e0e0')
        
        # Объединение легенд
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right')
        
        # Заголовок
        ax1.set_title(f'Прогноз добычи ({result["decline_type"]})', color='#e0e0e0')
        
        # Выделение точки безубыточности
        if result['breakeven_month'] is not None:
            ax1.axvline(x=result['breakeven_month'], color='green', linestyle=':', alpha=0.7, label='Точка безубыточности')
        
        self.chart.draw()
