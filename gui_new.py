#!/usr/bin/env python3
"""
Главное окно приложения IrkPUMP с красивым дизайном
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QFont, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QFrame,
    QScrollArea,
)

from pump_manager import PumpManager
from ui.design_tab import DesignTab
from ui.catalog_tab import CatalogTab
from ui.multiphase_tab import MultiphaseTab
from ui.cavitation_tab import CavitationTab
from ui.motor_tab import MotorTab
from ui.forecast_tab import ForecastTab


class ModernCard(QFrame):
    """Современная карточка с тенью и скругленными углами"""
    def __init__(self, title="", content_widget=None, icon="", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                border: 1px solid #90caf9;
                box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        if title:
            title_layout = QHBoxLayout()
            if icon:
                icon_label = QLabel(icon)
                icon_label.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        color: #1976d2;
                        margin-right: 8px;
                    }
                """)
                title_layout.addWidget(icon_label)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #1976d2;
                    border-bottom: 2px solid #1976d2;
                    padding-bottom: 5px;
                }
            """)
            title_layout.addWidget(title_label)
            title_layout.addStretch()
            layout.addLayout(title_layout)
        
        if content_widget:
            layout.addWidget(content_widget)


class ProgressStep(QWidget):
    """Шаг прогресса"""
    def __init__(self, number, text, active=False, parent=None):
        super().__init__(parent)
        self.active = active
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(10)
        
        # Номер шага
        self.number_label = QLabel(str(number))
        self.number_label.setFixedSize(30, 30)
        self.number_label.setAlignment(Qt.AlignCenter)
        
        # Текст шага
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #666;
            }
        """)
        
        layout.addWidget(self.number_label)
        layout.addWidget(self.text_label)
        layout.addStretch()
        
        self.update_style()
    
    def update_style(self):
        if self.active:
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1976d2, stop:1 #1565c0);
                    border-radius: 25px;
                }
            """)
            self.number_label.setStyleSheet("""
                QLabel {
                    background: white;
                    color: #1976d2;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            self.text_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background: #f5f5f5;
                    border-radius: 25px;
                }
            """)
            self.number_label.setStyleSheet("""
                QLabel {
                    background: #e0e0e0;
                    color: #666;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)


class ModernTabWidget(QTabWidget):
    """Современный виджет вкладок"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background: white;
                border-radius: 8px;
                margin-top: 5px;
            }
            QTabBar::tab {
                background: #f5f5f5;
                color: #666;
                padding: 12px 20px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1976d2;
                border-bottom: 3px solid #1976d2;
            }
            QTabBar::tab:hover {
                background: #e3f2fd;
                color: #1976d2;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.pump_manager = PumpManager()
        self._setup_ui()
        self._update_pump_count()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Инженерный калькулятор ЭЦН (Версия 4.0)")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Установка светлой темы
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f7fa, stop:1 #e8eaf6);
            }
        """)
        
        self._setup_menu()
        self._setup_toolbar()
        self._setup_central()
        self._setup_status()

    def _setup_menu(self) -> None:
        """Настройка меню"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: white;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        # Файл
        file_menu = menubar.addMenu("Файл")
        
        import_action = QAction("📁 Импорт насосов", self)
        import_action.triggered.connect(self._action_import_excel)
        file_menu.addAction(import_action)
        
        export_action = QAction("💾 Экспорт результатов", self)
        export_action.triggered.connect(self._action_export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Справка
        help_menu = menubar.addMenu("Справка")
        
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self._action_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Настройка панели инструментов"""
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background: white;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
                spacing: 5px;
            }
            QToolBar QPushButton {
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                color: #666;
            }
            QToolBar QPushButton:hover {
                background: #e3f2fd;
                color: #1976d2;
                border-color: #90caf9;
            }
        """)
        
        import_btn = QPushButton("📁 Импорт Excel")
        import_btn.clicked.connect(self._action_import_excel)
        toolbar.addWidget(import_btn)
        
        clear_btn = QPushButton("🗑️ Очистить")
        clear_btn.clicked.connect(self._action_clear)
        toolbar.addWidget(clear_btn)
        
        self.addToolBar(toolbar)

    def _setup_central(self) -> None:
        """Настройка центральной области"""
        # Главный контейнер с фиксированными размерами
        main_widget = QWidget()
        main_widget.setMinimumSize(1200, 800)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Заголовок приложения
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Прогресс-бар
        progress = self._create_progress_bar()
        main_layout.addWidget(progress)
        
        # Основной контент с фиксированной высотой
        content_widget = QWidget()
        content_widget.setMinimumHeight(600)
        content_widget.setStyleSheet("""
            QWidget {
                background: white;
                margin: 20px;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Информационная строка
        info_row = self._create_info_row()
        content_layout.addLayout(info_row)
        
        # Вкладки с фиксированной высотой
        self.tabs = self._create_tabs()
        self.tabs.setMinimumHeight(500)
        content_layout.addWidget(self.tabs)
        
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)

    def _create_header(self):
        """Создание заголовка"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976d2, stop:1 #1565c0);
                border: none;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 15, 30, 15)
        
        # Заголовок с иконкой
        title_layout = QHBoxLayout()
        title_icon = QLabel("⚙️")
        title_icon.setStyleSheet("font-size: 24px; color: white;")
        title_text = QLabel("Инженерный калькулятор ЭЦН (Версия 4.0)")
        title_text.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin-left: 10px;
            }
        """)
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        # Кнопка темы
        theme_btn = QPushButton("🌙 Темная тема")
        theme_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        
        layout.addLayout(title_layout)
        layout.addWidget(theme_btn)
        
        return header

    def _create_progress_bar(self):
        """Создание прогресс-бара"""
        progress_widget = QWidget()
        progress_widget.setFixedHeight(60)
        progress_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
                border-bottom: 1px solid #90caf9;
            }
        """)
        
        layout = QHBoxLayout(progress_widget)
        layout.setContentsMargins(30, 10, 30, 10)
        
        # Шаги прогресса
        steps = ["Ввод данных", "Расчет", "Подбор насоса", "Результат"]
        for i, step in enumerate(steps):
            step_widget = ProgressStep(i + 1, step, active=(i == 0))
            layout.addWidget(step_widget)
        
        layout.addStretch()
        return progress_widget

    def _create_info_row(self):
        """Создание информационной строки"""
        info_row = QHBoxLayout()
        
        self.catalog_label = QLabel(f"📁 Каталог: {self.pump_manager.catalog_dir}")
        self.catalog_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 8px 12px;
                background: #f5f5f5;
                border-radius: 6px;
            }
        """)
        
        self.count_label = QLabel("📊 Насосов в базе: 0")
        self.count_label.setStyleSheet("""
            QLabel {
                color: #1976d2;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 12px;
                background: #e3f2fd;
                border-radius: 6px;
            }
        """)
        
        info_row.addWidget(self.catalog_label)
        info_row.addStretch(1)
        info_row.addWidget(self.count_label)
        
        return info_row

    def _create_tabs(self):
        """Создание вкладок"""
        tabs = ModernTabWidget()
        
        # Создание вкладок
        self.design_tab = DesignTab()
        self.multiphase_tab = MultiphaseTab()
        self.cavitation_tab = CavitationTab()
        self.motor_tab = MotorTab()
        self.forecast_tab = ForecastTab()
        self.catalog_tab = CatalogTab(self.pump_manager)
        
        # Добавление вкладок с иконками
        tabs.addTab(self.design_tab, "⚙️ Расчет")
        tabs.addTab(self.multiphase_tab, "🌊 Многофазный поток")
        tabs.addTab(self.cavitation_tab, "⚠️ Кавитация")
        tabs.addTab(self.motor_tab, "⚡ Двигатель")
        tabs.addTab(self.forecast_tab, "📈 Прогноз")
        tabs.addTab(self.catalog_tab, "📚 Каталог")
        
        return tabs

    def _setup_status(self) -> None:
        """Настройка строки состояния"""
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #f5f5f5;
                border-top: 1px solid #e0e0e0;
                color: #666;
                font-size: 12px;
            }
        """)
        self.statusBar().showMessage("Готов к работе")

    # --- Actions ---
    def _action_import_excel(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите Excel-файл",
            str(self.pump_manager.catalog_dir),
            "Excel Files (*.xlsx *.xls)",
        )
        if not file_path:
            return
        result = self.pump_manager.import_from_excel(file_path)
        if result.get("success"):
            QMessageBox.information(self, "Успех", f"Импортировано {result['count']} насосов")
            self._update_pump_count()
        else:
            QMessageBox.warning(self, "Ошибка", result.get("error", "Неизвестная ошибка"))

    def _action_export_results(self) -> None:
        QMessageBox.information(self, "Экспорт", "Функция экспорта в разработке")

    def _action_clear(self) -> None:
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Очистить все данные?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.pump_manager.clear_pumps()
            self._update_pump_count()
            QMessageBox.information(self, "Очистка", "Данные очищены")

    def _action_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            "Инженерный калькулятор ЭЦН (Версия 4.0)\n\n"
            "Программа для расчета и подбора электроцентробежных насосов.\n\n"
            "Разработано с использованием PySide6",
        )

    def _update_pump_count(self) -> None:
        """Обновление счетчика насосов"""
        count = self.pump_manager.get_pump_count()
        self.count_label.setText(f"📊 Насосов в базе: {count}")


def main():
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    # Настройка палитры для светлой темы
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 247, 250))
    palette.setColor(QPalette.WindowText, QColor(33, 33, 33))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(33, 33, 33))
    palette.setColor(QPalette.Text, QColor(33, 33, 33))
    palette.setColor(QPalette.Button, QColor(245, 245, 245))
    palette.setColor(QPalette.ButtonText, QColor(33, 33, 33))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, QColor(25, 118, 210))
    palette.setColor(QPalette.Highlight, QColor(25, 118, 210))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
