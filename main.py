import sys
import os
import re as re_module
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QMenuBar, QMenu, QToolBar,
    QStatusBar, QSplitter, QFileDialog, QMessageBox, QDialog,
    QVBoxLayout, QDialogButtonBox, QLabel, QWidget, QStyle,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QHBoxLayout, QFrame, QGroupBox, QScrollArea, QListWidget, QPushButton,
    QTabWidget, QComboBox
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QTextCursor, QColor, QFont, QBrush
from PyQt6.QtCore import Qt, QFileInfo, QDir, QSize

# Импорт анализаторов
from lexical_analyzer import LexicalAnalyzer, Token
from syntax_analyzer import SyntaxAnalyzer, SyntaxError
from regular_expressions import RegularExpressionSearcher, SearchResult
from expression_analyzer import ExpressionAnalyzer, SyntaxErrorExpr, TokenType as ExprTokenType


class RegexSearchDialog(QDialog):
    """Диалоговое окно поиска по регулярным выражениям"""
    def __init__(self, parent=None, text_editor=None):
        super().__init__(parent)
        self.parent = parent
        self.text_editor = text_editor
        self.regex_searcher = RegularExpressionSearcher()
        self.setWindowTitle("Поиск по регулярным выражениям")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Верхняя панель с выбором типа поиска
        control_panel = QHBoxLayout()
        
        control_panel.addWidget(QLabel("Тип поиска:"))
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItem("Годы между 2000 и 2010", RegularExpressionSearcher.SEARCH_YEARS)
        self.search_type_combo.addItem("Номера карт Maestro", RegularExpressionSearcher.SEARCH_MAESTRO)
        self.search_type_combo.addItem("IP-адрес (v4) с маской подсети", RegularExpressionSearcher.SEARCH_IP_MASK)
        control_panel.addWidget(self.search_type_combo)
        
        control_panel.addStretch()
        
        self.search_button = QPushButton("🔍 Найти")
        self.search_button.clicked.connect(self.perform_search)
        control_panel.addWidget(self.search_button)
        
        layout.addLayout(control_panel)
        
        # Таблица результатов
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels([
            "Найденная подстрока", "Начальная позиция (строка:символ)", "Длина", "Тип поиска"
        ])
        
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.result_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.cellClicked.connect(self.on_result_clicked)
        
        layout.addWidget(self.result_table)
        
        # Нижняя панель с кнопками
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Выполняем поиск автоматически при открытии
        self.perform_search()
    
    def perform_search(self):
        """Выполнить поиск по выбранному типу"""
        if not self.text_editor:
            return
        
        text = self.text_editor.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Информация", "Текст для поиска пуст")
            return
        
        search_type = self.search_type_combo.currentData()
        search_type_name = self.search_type_combo.currentText()
        
        results = self.regex_searcher.search(text, search_type)
        
        # Очищаем таблицу
        self.result_table.setRowCount(0)
        
        if not results:
            self.result_table.setRowCount(1)
            no_results_item = QTableWidgetItem("❌ Ничего не найдено")
            no_results_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setBold(True)
            no_results_item.setFont(font)
            self.result_table.setItem(0, 0, no_results_item)
            self.result_table.setSpan(0, 0, 1, 4)
            return
        
        # Заполняем таблицу результатами
        self.result_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            substring_item = QTableWidgetItem(result.substring)
            substring_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            position_text = f"{result.line}:{result.start_pos}"
            position_item = QTableWidgetItem(position_text)
            position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            length_item = QTableWidgetItem(str(result.length))
            length_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            type_item = QTableWidgetItem(search_type_name)
            
            # Подсветка найденного (светло-желтый фон)
            highlight_color = QColor(255, 255, 200)
            substring_item.setBackground(QBrush(highlight_color))
            position_item.setBackground(QBrush(highlight_color))
            length_item.setBackground(QBrush(highlight_color))
            type_item.setBackground(QBrush(highlight_color))
            
            self.result_table.setItem(i, 0, substring_item)
            self.result_table.setItem(i, 1, position_item)
            self.result_table.setItem(i, 2, length_item)
            self.result_table.setItem(i, 3, type_item)
        
        # Автоматически подгоняем ширину колонок
        self.result_table.resizeColumnsToContents()
    
    def on_result_clicked(self, row, column):
        """Обработка клика по строке таблицы результатов"""
        if self.text_editor:
            # Получаем результат из памяти
            search_type = self.search_type_combo.currentData()
            results = self.regex_searcher.results
            
            if 0 <= row < len(results):
                result = results[row]
                
                # Перемещаем курсор к найденной позиции
                cursor = self.text_editor.textCursor()
                
                lines = self.text_editor.toPlainText().split('\n')
                position = 0
                
                for i in range(min(result.line - 1, len(lines))):
                    position += len(lines[i]) + 1
                
                position += result.start_pos - 1
                
                text_length = len(self.text_editor.toPlainText())
                position = min(position, max(0, text_length - 1))
                
                cursor.setPosition(position)
                
                if result.length > 1:
                    end_position = position + result.length
                    end_position = min(end_position, text_length)
                    cursor.setPosition(end_position, QTextCursor.MoveMode.KeepAnchor)
                
                self.text_editor.setTextCursor(cursor)
                self.text_editor.setFocus()
                
                if self.parent:
                    self.parent.statusbar.showMessage(
                        f"Переход: строка {result.line}, позиция {result.start_pos}", 3000
                    )


class HelpDialog(QDialog):
    """Диалоговое окно справки"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка")
        self.setMinimumSize(750, 650)
        
        layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>📚 Справка языкового процессора</h2>
        
        <h3>КУРСОВАЯ РАБОТА: лексический и синтаксический анализ</h3>
        <p><b>Вариант:</b> объявление комплексного числа с инициализацией (синтаксис Rust-подобный)</p>
        
        <hr>
        
        <h3>СИНТАКСИС ОПЕРАТОРА:</h3>
        <pre><code>let идентификатор = num::complex::Complex::new(число, число);</code></pre>
        <ul>
            <li><b>идентификатор</b> — имя переменной (начинается с буквы или _, может содержать буквы, цифры и _)</li>
            <li><b>число</b> — целый или вещественный литерал (например: 1, 3.1, -4.2, 0.0)</li>
        </ul>
        
        <h3>ПРАВИЛА:</h3>
        <ol>
            <li>Строка должна начинаться с ключевого слова <b>let</b>.</li>
            <li>После <b>let</b> должен идти идентификатор (имя переменной).</li>
            <li>После идентификатора должен идти оператор присваивания <b>=</b>.</li>
            <li>После <b>=</b> должен идти путь к типу: <b>num::complex::Complex::new</b>.</li>
            <li>Аргументы должны быть записаны в круглых скобках через запятую: <b>(число, число)</b>.</li>
            <li>Оператор должен завершаться точкой с запятой <b>;</b>.</li>
        </ol>
        
        <h3>ВЫВОД:</h3>
        <p>В таблицу выводятся только лексические и синтаксические ошибки. Формат позиции: строка N, позиция M.</p>
        
        <hr>
        
        <h3>ПРИМЕРЫ КОРРЕКТНЫХ СТРОК:</h3>
        <ul>
            <li><code>let complex_num2 = num::complex::Complex::new(3.1, -4.2);</code></li>
            <li><code>let x = num::complex::Complex::new(1, 2);</code></li>
            <li><code>let z = num::complex::Complex::new(0.0, -1.5);</code></li>
            <li><code>let my_var = num::complex::Complex::new(2.5, 0.5);</code></li>
        </ul>
        
        <h3>ПРИМЕРЫ С ОШИБКАМИ (синтаксис / лексика):</h3>
        <ul>
            <li><code>complex_num2 = num::complex::Complex::new(3.1, -4.2);</code> — пропущено <b>let</b></li>
            <li><code>let x num::complex::Complex::new(1, 2);</code> — пропущен <b>=</b></li>
            <li><code>let x = num::comlex::Complex::new(1, 2);</code> — опечатка в <b>complex</b></li>
            <li><code>let x = num::complex::Complex::nw(1, 2);</code> — опечатка в <b>new</b></li>
            <li><code>let x = num::complex::Complex::new(1, 2)</code> — пропущен <b>;</b></li>
        </ul>
        
        <hr>
        
        <h3>📁 Меню "Файл"</h3>
        <ul>
            <li><b>Создать (Ctrl+N)</b> — создает новый документ</li>
            <li><b>Открыть (Ctrl+O)</b> — открывает существующий файл</li>
            <li><b>Сохранить (Ctrl+S)</b> — сохраняет текущий документ</li>
            <li><b>Сохранить как (Ctrl+Shift+S)</b> — сохраняет под новым именем</li>
            <li><b>Выход (Ctrl+Q)</b> — закрывает приложение</li>
        </ul>
        
        <h3>✏️ Меню "Правка"</h3>
        <ul>
            <li><b>Отменить (Ctrl+Z)</b> — отмена действия</li>
            <li><b>Повторить (Ctrl+Y)</b> — повтор действия</li>
            <li><b>Вырезать (Ctrl+X)</b> — вырезать текст</li>
            <li><b>Копировать (Ctrl+C)</b> — копировать текст</li>
            <li><b>Вставить (Ctrl+V)</b> — вставить текст</li>
            <li><b>Удалить (Del)</b> — удалить текст</li>
            <li><b>Выделить все (Ctrl+A)</b> — выделить всё</li>
        </ul>
        
        <h3>▶️ Меню "Пуск"</h3>
        <ul>
            <li><b>Пуск (F5)</b> — полный анализ (лексический + синтаксический)</li>
            <li><b>Анализ выражения (F6)</b> — анализ арифметического выражения</li>
        </ul>
        
        <h3>📝 Меню "Текст"</h3>
        <ul>
            <li>Информационные пункты и тестовые примеры</li>
        </ul>
        
        <h3>🖱️ НАВИГАЦИЯ ПО ТАБЛИЦЕ ОШИБОК:</h3>
        <p>Щёлкните строку — курсор перейдёт к ошибочному фрагменту, он будет подсвечен.</p>
        """)
        
        layout.addWidget(help_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class AboutDialog(QDialog):
    """Диалоговое окно 'О программе'"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(600, 520)
        
        layout = QVBoxLayout()
        
        info_label = QLabel("""
        <h2>📝 Языковой процессор</h2>
        <p><b>Версия:</b> 3.0</p>
        <p><b>Студент: Кокунов Андрей АВТ-313</b></p>
        <p><b>Назначение:</b> Лексический и синтаксический анализ</p>
        <p><b>Вариант:</b> 5 - Комплексное число (Rust)</p>
        <p><b>Технологии:</b> Python + PyQt6</p>
        <hr>
        <h3>Функционал</h3>
        <p>Лексический анализ</p>
        <p>Синтаксический анализ</p>
        <p>Таблица ошибок с этапом и позицией</p>
        <p>Подсветка фрагментов в редакторе</p>
        <p>Синтаксический анализатор (метод Айронса)</p>
        <p>Поиск по регулярным выражениям</p>
        <p>Анализ арифметических выражений с генерацией тетрад и ПОЛИЗ</p>
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(info_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class TextEditor(QMainWindow):
    """Главное окно текстового редактора с языковым процессором"""
    
    def __init__(self):
        super().__init__()
        
        self.current_file_path = None
        self.is_modified = False
        self.lexical_analyzer = LexicalAnalyzer()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.regex_searcher = RegularExpressionSearcher()
        self.expression_analyzer = ExpressionAnalyzer()
        self.current_tokens = []
        self.current_errors = []
        self.current_expr_tokens = []  # Токены арифметического выражения
        
        # Словарь с информацией для пунктов меню Текст
        self.text_menu_info = {
            "Постановка задачи": """
                <h3>📋 Постановка задачи</h3>
                <hr>
                <p><b>Вариант 5:</b> Объявление комплексного числа с инициализацией на языке Rust</p>
                <p>Разработать языковой процессор, включающий:</p>
                <ol>
                    <li><b>Лексический анализатор</b> - выделение лексем</li>
                    <li><b>Синтаксический анализатор</b> - проверка структуры</li>
                </ol>
                <p><b>Пример:</b></p>
                <pre><code>let complex_num2 = num::complex::Complex::new(3.1, -4.2);</code></pre>
                <p><b>Метод нейтрализации ошибок:</b> Айронса</p>
            """,
            
            "Грамматика": """
                <h3>📐 Грамматика G[Z]</h3>
                <hr>
                <pre>
Z → "let" ID "=" PATH "::" "new" "(" ARGS ")" ";"
PATH → ID ("::" ID)*
ARGS → NUM "," NUM
NUM → ["-"] DIGITS ["." DIGITS]
ID → LETTER (LETTER | DIGIT | "_")*
DIGITS → DIGIT+
LETTER → "a".."z" | "A".."Z" | "_"
DIGIT → "0".."9"
                </pre>
                <p><b>Терминалы:</b> let, =, ::, new, (, ), ,, ;, идентификатор, число</p>
            """,
            
            "Классификация грамматики": """
                <h3>🏷️ Классификация грамматики</h3>
                <hr>
                <p><b>По Хомскому:</b> Тип 2 - контекстно-свободная</p>
                <ul>
                    <li>✓ Однозначная</li>
                    <li>✓ Без левой рекурсии</li>
                    <li>✓ Допускает нисходящий разбор LL(1)</li>
                </ul>
                <p><b>Метод анализа:</b> Рекурсивный спуск</p>
            """,
            
            "Метод анализа": """
                <h3>🔍 Метод анализа</h3>
                <hr>
                <p><b>Метод:</b> Нисходящий разбор + метод Айронса</p>
                <p><b>Алгоритм:</b></p>
                <ol>
                    <li>Получение токенов от лексического анализатора</li>
                    <li>Рекурсивный спуск по правилам грамматики</li>
                    <li>При ошибке - восстановление методом Айронса</li>
                </ol>
                <p><b>Восстанавливающие символы:</b> ';', ')', ','</p>
            """,
            
            "Грамматика выражений": """
                <h3>📐 Грамматика арифметических выражений</h3>
                <hr>
                <pre>
E → TA
A → ε | + TA | - TA
T → FB
B → ε | * FB | / FB | % FB
F → num | id | (E)
id → letter {letter | digit | _}
num → digit {digit}
                </pre>
                <p><b>Приоритет операций:</b> *, /, % выше +, -</p>
                <p><b>Метод анализа:</b> Рекурсивный спуск</p>
            """,
            
            "Тестовый пример": """
                <h3>🧪 Тестовые примеры</h3>
                <hr>
                <p>Доступно 16 тестовых примеров.</p>
                <p>Загрузить через меню <b>Текст → Тестовый пример</b>.</p>
                <br>
                <p><b>Базовый синтаксис:</b></p>
                <pre><code>let complex_num2 = num::complex::Complex::new(3.1, -4.2);</code></pre>
            """,
            
            "Список литературы": """
                <h3>📚 Список литературы</h3>
                <hr>
                <ol>
                    <li><b>Ахо А., Ульман Дж.</b> Теория синтаксического анализа, перевода и компиляции. - М.: Мир, 1978.</li>
                    <br>
                    <li><b>Грис Д.</b> Конструирование компиляторов. - М.: Мир, 1975.</li>
                    <br>
                    <li><b>Хантер Р.</b> Основные концепции компиляторов. - М.: Вильямс, 2002.</li>
                    <br>
                    <li><b>Rust Documentation.</b> URL: https://doc.rust-lang.org/book/</li>
                </ol>
            """,
            
            "Исходный код программы": """
                <h3>💻 Исходный код</h3>
                <hr>
                <pre>
project/
├── main.py
├── lexical_analyzer.py
├── syntax_analyzer.py
├── expression_analyzer.py
├── regular_expressions.py
└── requirements.txt
                </pre>
                <p><b>Язык:</b> Python 3.8+</p>
                <p><b>GUI:</b> PyQt6</p>
                <p><b>Лицензия:</b> MIT</p>
            """
        }
        
        # Словарь с тестовыми примерами
        self.test_examples = {
            "Пример 1: Корректное объявление": 
                "let complex_num2 = num::complex::Complex::new(3.1, -4.2);",
            
            "Пример 2: С годами (2000-2010)": 
                "В 2000 году, 2005 и 2010 были важные события. Также 1999 и 2011 не входят в диапазон.",
            
            "Пример 3: Номера карт Maestro": 
                "Номера карт: 5012345678901234, 5612345678901234567, 6012345678901234",
            
            "Пример 4: IP-адреса с маской": 
                "IP адреса: 192.168.1.1/24, 10.0.0.1/8, 172.16.0.1/16, 255.255.255.0/32",
            
            "Пример 5: Арифметическое выражение 1": 
                "3 + 5 * 2",
            
            "Пример 6: Арифметическое выражение 2": 
                "(3 + 5) * 2",
            
            "Пример 7: Арифметическое выражение 3": 
                "10 - 4 / 2 + 7 % 3",
            
            "Пример 8: Арифметическое с идентификаторами": 
                "a + b * 3 - (x + y) / 2",
        }
        
        self.init_ui()
        
    def get_icon(self, standard_icon):
        """Получение стандартной иконки из темы ОС"""
        return self.style().standardIcon(standard_icon)
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Языковой процессор")
        self.setMinimumSize(1100, 750)
        
        # Установка иконки приложения
        self.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_FileIcon))
        
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Верхняя часть: редактор
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Введите текст программы на Rust...\n"
            "Пример: let complex_num2 = num::complex::Complex::new(3.1, -4.2);\n\n"
            "Или арифметическое выражение:\n"
            "Пример: 3 + 5 * 2"
        )
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.setFont(QFont("Courier New", 12))
        
        # Создание вкладок для результатов
        self.tab_widget = QTabWidget()
        
        # Вкладка "Лог"
        self.log_tab = QWidget()
        log_layout = QVBoxLayout()
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Лог выполнения анализаторов...")
        self.output_area.setStyleSheet("background-color: #f8f8f8; font-family: 'Courier New';")
        log_layout.addWidget(self.output_area)
        self.log_tab.setLayout(log_layout)
        self.tab_widget.addTab(self.log_tab, "📋 Лог")
        
        # Вкладка "Ошибки"
        self.errors_tab = QWidget()
        errors_layout = QVBoxLayout()
        
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(3)
        self.error_table.setHorizontalHeaderLabels([
            "Неверный фрагмент", "Местоположение", "Описание ошибки"
        ])
        
        self.error_table.horizontalHeader().setStretchLastSection(True)
        self.error_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.error_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.error_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.error_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.error_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.error_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.error_table.setAlternatingRowColors(True)
        self.error_table.cellClicked.connect(self.on_error_table_clicked)
        
        errors_layout.addWidget(self.error_table)
        self.errors_tab.setLayout(errors_layout)
        self.tab_widget.addTab(self.errors_tab, "❌ Ошибки")
        
        # Вкладка "Лексемы"
        self.tokens_tab = QWidget()
        tokens_layout = QVBoxLayout()
        
        self.token_table = QTableWidget()
        self.token_table.setColumnCount(4)
        self.token_table.setHorizontalHeaderLabels([
            "Условный код", "Тип лексемы", "Лексема", "Местоположение"
        ])
        
        self.token_table.horizontalHeader().setStretchLastSection(True)
        self.token_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.token_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.token_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.token_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.token_table.setAlternatingRowColors(True)
        self.token_table.cellClicked.connect(self.on_token_table_clicked)
        
        tokens_layout.addWidget(self.token_table)
        self.tokens_tab.setLayout(tokens_layout)
        self.tab_widget.addTab(self.tokens_tab, "🔤 Лексемы")
        
        # Вкладка "Тетрады и ПОЛИЗ"
        self.tetrads_tab = QWidget()
        tetrads_layout = QVBoxLayout()
        
        # Таблица тетрад
        tetrads_group = QGroupBox("Тетрады (op, arg1, arg2, result)")
        tetrads_inner_layout = QVBoxLayout()
        
        self.tetrad_table = QTableWidget()
        self.tetrad_table.setColumnCount(4)
        self.tetrad_table.setHorizontalHeaderLabels(["op", "arg1", "arg2", "result"])
        
        self.tetrad_table.horizontalHeader().setStretchLastSection(True)
        self.tetrad_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tetrad_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tetrad_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tetrad_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.tetrad_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tetrad_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tetrad_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tetrad_table.setAlternatingRowColors(True)
        
        tetrads_inner_layout.addWidget(self.tetrad_table)
        tetrads_group.setLayout(tetrads_inner_layout)
        tetrads_layout.addWidget(tetrads_group)
        
        # ПОЛИЗ и результат
        poliz_group = QGroupBox("ПОЛИЗ и результат вычисления")
        poliz_inner_layout = QVBoxLayout()
        
        self.poliz_label = QLabel("ПОЛИЗ: ")
        self.poliz_label.setWordWrap(True)
        self.poliz_label.setFont(QFont("Courier New", 11))
        
        self.result_label = QLabel("Результат: ")
        self.result_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        
        poliz_inner_layout.addWidget(self.poliz_label)
        poliz_inner_layout.addWidget(self.result_label)
        poliz_group.setLayout(poliz_inner_layout)
        tetrads_layout.addWidget(poliz_group)
        
        tetrads_layout.addStretch()
        self.tetrads_tab.setLayout(tetrads_layout)
        self.tab_widget.addTab(self.tetrads_tab, "📐 Тетрады и ПОЛИЗ")
        
        # Вкладка "Поиск по РВ"
        self.regex_tab = QWidget()
        regex_layout = QVBoxLayout()
        
        # Кнопка поиска
        regex_button_layout = QHBoxLayout()
        self.regex_search_button = QPushButton("🔍 Поиск по регулярным выражениям")
        self.regex_search_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.regex_search_button.clicked.connect(self.open_regex_search)
        regex_button_layout.addStretch()
        regex_button_layout.addWidget(self.regex_search_button)
        regex_button_layout.addStretch()
        regex_layout.addLayout(regex_button_layout)
        
        # Таблица результатов поиска по РВ
        self.regex_result_table = QTableWidget()
        self.regex_result_table.setColumnCount(4)
        self.regex_result_table.setHorizontalHeaderLabels([
            "Найденная подстрока", "Начальная позиция (строка:символ)", "Длина", "Тип поиска"
        ])
        
        self.regex_result_table.horizontalHeader().setStretchLastSection(True)
        self.regex_result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.regex_result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.regex_result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.regex_result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.regex_result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.regex_result_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.regex_result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.regex_result_table.setAlternatingRowColors(True)
        self.regex_result_table.cellClicked.connect(self.on_regex_result_clicked)
        
        regex_layout.addWidget(self.regex_result_table)
        self.regex_tab.setLayout(regex_layout)
        self.tab_widget.addTab(self.regex_tab, "🔍 Поиск по РВ")
        
        # Размещение виджетов
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(self.editor)
        main_splitter.addWidget(self.tab_widget)
        main_splitter.setSizes([300, 400])
        
        main_layout.addWidget(main_splitter)
        
        # Создание меню и тулбара
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
        
    def create_actions(self):
        """Создание действий с иконками"""
        # Файл
        self.new_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileIcon), "Создать", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogOpenButton), "Открыть...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Сохранить", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Сохранить как...", self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogCloseButton), "Выход", self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.triggered.connect(self.close)
        
        # Правка
        self.undo_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_ArrowBack), "Отменить", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.editor.undo)
        
        self.redo_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_ArrowForward), "Повторить", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.editor.redo)
        
        self.cut_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_CommandLink), "Вырезать", self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.triggered.connect(self.editor.cut)
        
        self.copy_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Копировать", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.editor.copy)
        
        self.paste_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogContentsView), "Вставить", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(self.editor.paste)
        
        self.delete_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_TrashIcon), "Удалить", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.triggered.connect(self.delete_text)
        
        self.select_all_action = QAction("Выделить все", self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_action.triggered.connect(self.editor.selectAll)
        
        # Текст
        self.task_action = QAction("Постановка задачи", self)
        self.task_action.triggered.connect(lambda: self.show_text_menu_info("Постановка задачи"))
        
        self.grammar_action = QAction("Грамматика", self)
        self.grammar_action.triggered.connect(lambda: self.show_text_menu_info("Грамматика"))
        
        self.classification_action = QAction("Классификация грамматики", self)
        self.classification_action.triggered.connect(lambda: self.show_text_menu_info("Классификация грамматики"))
        
        self.analysis_method_action = QAction("Метод анализа", self)
        self.analysis_method_action.triggered.connect(lambda: self.show_text_menu_info("Метод анализа"))
        
        self.grammar_expr_action = QAction("Грамматика выражений", self)
        self.grammar_expr_action.triggered.connect(lambda: self.show_text_menu_info("Грамматика выражений"))
        
        self.test_example_action = QAction("Тестовый пример", self)
        self.test_example_action.setShortcut(QKeySequence("Ctrl+T"))
        self.test_example_action.triggered.connect(lambda: self.show_text_menu_info("Тестовый пример"))
        
        self.literature_action = QAction("Список литературы", self)
        self.literature_action.triggered.connect(lambda: self.show_text_menu_info("Список литературы"))
        
        self.source_code_action = QAction("Исходный код программы", self)
        self.source_code_action.triggered.connect(lambda: self.show_text_menu_info("Исходный код программы"))
        
        # Пуск
        self.run_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_MediaPlay), "Пуск (анализ программы)", self)
        self.run_action.setShortcut(QKeySequence("F5"))
        self.run_action.setStatusTip("Запустить полный анализ программы")
        self.run_action.triggered.connect(self.run_analyzer)
        
        self.expression_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_MediaPlay), "Анализ выражения", self)
        self.expression_action.setShortcut(QKeySequence("F6"))
        self.expression_action.setStatusTip("Анализировать арифметическое выражение")
        self.expression_action.triggered.connect(self.run_expression_analyzer)
        
        # Справка
        self.help_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogHelpButton), "Вызов справки", self)
        self.help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.help_action.triggered.connect(self.show_help)
        
        self.about_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_MessageBoxInformation), "О программе", self)
        self.about_action.triggered.connect(self.show_about)
        
    def create_menus(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Меню Правка
        edit_menu = menubar.addMenu("Правка")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addAction(self.delete_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)
        
        # Меню Текст
        text_menu = menubar.addMenu("Текст")
        text_menu.addAction(self.task_action)
        text_menu.addAction(self.grammar_action)
        text_menu.addAction(self.classification_action)
        text_menu.addAction(self.analysis_method_action)
        text_menu.addSeparator()
        text_menu.addAction(self.grammar_expr_action)
        text_menu.addSeparator()
        text_menu.addAction(self.test_example_action)
        text_menu.addAction(self.literature_action)
        text_menu.addAction(self.source_code_action)
        
        # Меню Пуск
        run_menu = menubar.addMenu("Пуск")
        run_menu.addAction(self.run_action)
        run_menu.addSeparator()
        run_menu.addAction(self.expression_action)
        
        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        help_menu.addAction(self.help_action)
        help_menu.addAction(self.about_action)
        
    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Панель инструментов")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.cut_action)
        toolbar.addAction(self.paste_action)
        toolbar.addSeparator()
        
        toolbar.addAction(self.run_action)
        toolbar.addAction(self.expression_action)
        toolbar.addSeparator()
        
        toolbar.addAction(self.help_action)
        toolbar.addAction(self.about_action)
        
    def create_statusbar(self):
        """Создание строки состояния"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Готов к работе | F5 - анализ программы | F6 - анализ выражения")
        
    def on_text_changed(self):
        """Обработчик изменения текста"""
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
            
    def update_title(self):
        """Обновление заголовка окна"""
        if self.current_file_path:
            filename = os.path.basename(self.current_file_path)
            title = f"{filename}{'*' if self.is_modified else ''} - Языковой процессор"
        else:
            title = f"Без имени{'*' if self.is_modified else ''} - Языковой процессор"
        self.setWindowTitle(title)
        
    def new_file(self):
        """Создание нового файла"""
        if self.maybe_save():
            self.editor.clear()
            self.current_file_path = None
            self.is_modified = False
            self.update_title()
            self.clear_results()
            self.statusbar.showMessage("Создан новый документ")
            
    def open_file(self):
        """Открытие файла"""
        if self.maybe_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Открыть файл", "",
                "Текстовые файлы (*.txt);;Файлы Rust (*.rs);;Все файлы (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        self.editor.setText(file.read())
                    self.current_file_path = file_path
                    self.is_modified = False
                    self.update_title()
                    self.clear_results()
                    self.statusbar.showMessage(f"Открыт файл: {os.path.basename(file_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{e}")
                    
    def save_file(self):
        """Сохранение файла"""
        if self.current_file_path:
            return self.save_file_to_path(self.current_file_path)
        else:
            return self.save_file_as()
            
    def save_file_as(self):
        """Сохранение файла как"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "",
            "Текстовые файлы (*.txt);;Файлы Rust (*.rs);;Все файлы (*.*)"
        )
        if file_path:
            return self.save_file_to_path(file_path)
        return False
        
    def save_file_to_path(self, file_path):
        """Сохранение файла по указанному пути"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())
            self.current_file_path = file_path
            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Файл сохранен: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
            return False
            
    def maybe_save(self):
        """Проверка необходимости сохранения изменений"""
        if not self.is_modified:
            return True
            
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Сохранение изменений")
        dialog.setText("Документ был изменен.")
        dialog.setInformativeText("Сохранить изменения?")
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Save)
        
        result = dialog.exec()
        
        if result == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif result == QMessageBox.StandardButton.Cancel:
            return False
        else:
            return True
            
    def delete_text(self):
        """Удаление выделенного текста"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
    
    def clear_results(self):
        """Очистка всех результатов"""
        self.output_area.clear()
        self.token_table.setRowCount(0)
        self.error_table.setRowCount(0)
        self.tetrad_table.setRowCount(0)
        self.poliz_label.setText("ПОЛИЗ: ")
        self.result_label.setText("Результат: ")
        self.current_tokens = []
        self.current_errors = []
        self.current_expr_tokens = []
    
    def show_text_menu_info(self, title):
        """Показать информацию из меню Текст"""
        if title == "Тестовый пример":
            self.show_test_examples_dialog()
            return
        
        info_html = self.text_menu_info.get(title, f"<h3>{title}</h3><p>Информация будет добавлена позже.</p>")
        
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(550, 400)
        dialog.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        
        layout = QVBoxLayout()
        
        info_label = QLabel(info_html)
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setStyleSheet("padding: 10px;")
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_label)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_test_examples_dialog(self):
        """Показать диалог выбора тестового примера"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Тестовые примеры")
        dialog.setMinimumSize(600, 450)
        dialog.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView))
        
        layout = QVBoxLayout()
        
        title_label = QLabel("<h3>🧪 Выберите тестовый пример для загрузки в редактор</h3>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        list_widget = QListWidget()
        for example_name in self.test_examples.keys():
            list_widget.addItem(example_name)
        
        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setFont(QFont("Courier New", 11))
        preview.setMaximumHeight(150)
        preview.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc;")
        
        def on_selection_changed():
            selected = list_widget.currentItem()
            if selected:
                example_name = selected.text()
                preview.setText(self.test_examples[example_name])
        
        list_widget.currentItemChanged.connect(on_selection_changed)
        
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)
        
        button_layout = QHBoxLayout()
        
        load_button = QPushButton("📂 Загрузить в редактор")
        load_button.setStyleSheet("padding: 8px; font-weight: bold; background-color: #4CAF50; color: white;")
        
        close_button = QPushButton("Закрыть")
        close_button.setStyleSheet("padding: 8px;")
        
        def load_example():
            selected = list_widget.currentItem()
            if selected:
                example_name = selected.text()
                example_text = self.test_examples[example_name]
                self.editor.setText(example_text)
                self.clear_results()
                self.statusbar.showMessage(f"Загружен: {example_name}", 5000)
                dialog.accept()
        
        load_button.clicked.connect(load_example)
        close_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(close_button)
        
        layout.addWidget(QLabel("<b>Доступные примеры:</b>"))
        layout.addWidget(list_widget)
        layout.addWidget(QLabel("<b>Предпросмотр:</b>"))
        layout.addWidget(preview)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def open_regex_search(self):
        """Открыть окно поиска по регулярным выражениям"""
        # Выполняем поиск по текущему тексту
        if not self.editor.toPlainText().strip():
            QMessageBox.information(self, "Информация", "Текст для поиска пуст")
            return
        
        # Сохраняем текущий тип поиска из комбобокса
        dialog = RegexSearchDialog(self, self.editor)
        
        # После закрытия диалога обновляем таблицу на вкладке "Поиск по РВ"
        self.update_regex_results()
        
        dialog.exec()
    
    def update_regex_results(self):
        """Обновить таблицу результатов поиска по РВ на главной вкладке"""
        # Получаем текущий тип поиска (для демонстрации используем поиск годов)
        # В реальном приложении можно добавить выбор типа на главной вкладке
        text = self.editor.toPlainText()
        if not text.strip():
            self.regex_result_table.setRowCount(0)
            return
        
        # По умолчанию показываем поиск годов
        search_type = RegularExpressionSearcher.SEARCH_YEARS
        search_type_name = "Годы 2000-2010"
        
        results = self.regex_searcher.search(text, search_type)
        
        self.regex_result_table.setRowCount(0)
        
        if not results:
            self.regex_result_table.setRowCount(1)
            no_results_item = QTableWidgetItem("❌ Ничего не найдено")
            no_results_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setBold(True)
            no_results_item.setFont(font)
            self.regex_result_table.setItem(0, 0, no_results_item)
            self.regex_result_table.setSpan(0, 0, 1, 4)
            return
        
        self.regex_result_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            substring_item = QTableWidgetItem(result.substring)
            substring_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            position_text = f"{result.line}:{result.start_pos}"
            position_item = QTableWidgetItem(position_text)
            position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            length_item = QTableWidgetItem(str(result.length))
            length_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            type_item = QTableWidgetItem(search_type_name)
            
            # Подсветка
            highlight_color = QColor(255, 255, 200)
            substring_item.setBackground(QBrush(highlight_color))
            position_item.setBackground(QBrush(highlight_color))
            length_item.setBackground(QBrush(highlight_color))
            type_item.setBackground(QBrush(highlight_color))
            
            self.regex_result_table.setItem(i, 0, substring_item)
            self.regex_result_table.setItem(i, 1, position_item)
            self.regex_result_table.setItem(i, 2, length_item)
            self.regex_result_table.setItem(i, 3, type_item)
        
        self.regex_result_table.resizeColumnsToContents()
    
    def on_regex_result_clicked(self, row, column):
        """Обработка клика по строке таблицы результатов поиска по РВ"""
        # Поиск годов по умолчанию
        search_type = RegularExpressionSearcher.SEARCH_YEARS
        results = self.regex_searcher.search(self.editor.toPlainText(), search_type)
        
        if 0 <= row < len(results):
            result = results[row]
            
            cursor = self.editor.textCursor()
            
            lines = self.editor.toPlainText().split('\n')
            position = 0
            
            for i in range(min(result.line - 1, len(lines))):
                position += len(lines[i]) + 1
            
            position += result.start_pos - 1
            
            text_length = len(self.editor.toPlainText())
            position = min(position, max(0, text_length - 1))
            
            cursor.setPosition(position)
            
            if result.length > 1:
                end_position = position + result.length
                end_position = min(end_position, text_length)
                cursor.setPosition(end_position, QTextCursor.MoveMode.KeepAnchor)
            
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()
            
            self.statusbar.showMessage(
                f"Переход: строка {result.line}, позиция {result.start_pos}", 3000
            )
        
    def run_analyzer(self):
        """Запуск полного анализа программы"""
        text = self.editor.toPlainText()
        
        # Очистка предыдущих результатов
        self.clear_results()
        
        if not text.strip():
            self.output_area.append("⚠️ Пуск: текст пуст. Добавьте данные для анализа.")
            self.statusbar.showMessage("Текст пуст. Добавьте данные для анализа.")
            self.tab_widget.setCurrentIndex(0)  # Переключаем на вкладку Лог
            return
        
        # Лог анализа
        self.output_area.append("="*60)
        self.output_area.append("ЗАПУСК ПОЛНОГО АНАЛИЗА ПРОГРАММЫ")
        self.output_area.append("="*60)
        self.output_area.append(f"Анализируемый текст:\n{text}\n")
        
        # ЭТАП 1: Лексический анализ
        self.output_area.append("-"*60)
        self.output_area.append("ЭТАП 1: ЛЕКСИЧЕСКИЙ АНАЛИЗ")
        self.output_area.append("-"*60)
        
        try:
            tokens, lexical_errors = self.lexical_analyzer.analyze(text)
            self.current_tokens = tokens
            
            # Заполнение таблицы лексем
            self.token_table.setRowCount(len(tokens))
            
            for i, token in enumerate(tokens):
                code_item = QTableWidgetItem(str(token.code))
                code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                type_item = QTableWidgetItem(token.token_type)
                lexeme_item = QTableWidgetItem(token.lexeme)
                
                location_text = f"строка {token.line}, позиция {token.start_pos}-{token.end_pos}"
                location_item = QTableWidgetItem(location_text)
                
                if token.is_error:
                    error_color = QColor(255, 220, 220)
                    code_item.setBackground(QBrush(error_color))
                    type_item.setBackground(QBrush(error_color))
                    lexeme_item.setBackground(QBrush(error_color))
                    location_item.setBackground(QBrush(error_color))
                    
                    font = QFont()
                    font.setBold(True)
                    code_item.setFont(font)
                    type_item.setFont(font)
                    lexeme_item.setFont(font)
                    location_item.setFont(font)
                
                self.token_table.setItem(i, 0, code_item)
                self.token_table.setItem(i, 1, type_item)
                self.token_table.setItem(i, 2, lexeme_item)
                self.token_table.setItem(i, 3, location_item)
            
            if lexical_errors:
                self.output_area.append(f"Лексических ошибок: {len(lexical_errors)}")
                for err in lexical_errors:
                    self.output_area.append(f"  • {err['message']} (строка {err['line']}, позиция {err['position']})")
            else:
                self.output_area.append("Лексический анализ завершен без ошибок")
                self.output_area.append(f"Выделено лексем: {len(tokens)}")
            
            # ЭТАП 2: Синтаксический анализ
            self.output_area.append("\n" + "-"*60)
            self.output_area.append("ЭТАП 2: СИНТАКСИЧЕСКИЙ АНАЛИЗ")
            self.output_area.append("-"*60)
            
            success, syntax_errors = self.syntax_analyzer.analyze(text)
            self.current_errors = syntax_errors
            
            # Заполнение таблицы ошибок
            if syntax_errors:
                self.error_table.setRowCount(len(syntax_errors))
                
                for i, error in enumerate(syntax_errors):
                    fragment_item = QTableWidgetItem(error.fragment)
                    fragment_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    location_text = f"строка {error.line}, позиция {error.position}"
                    location_item = QTableWidgetItem(location_text)
                    location_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    description_item = QTableWidgetItem(error.description)
                    
                    error_color = QColor(255, 220, 220)
                    fragment_item.setBackground(QBrush(error_color))
                    location_item.setBackground(QBrush(error_color))
                    description_item.setBackground(QBrush(error_color))
                    
                    font = QFont()
                    font.setBold(True)
                    fragment_item.setFont(font)
                    location_item.setFont(font)
                    description_item.setFont(font)
                    
                    self.error_table.setItem(i, 0, fragment_item)
                    self.error_table.setItem(i, 1, location_item)
                    self.error_table.setItem(i, 2, description_item)
                    
                    self.output_area.append(
                        f"  • {error.description} (строка {error.line}, позиция {error.position})"
                    )
                
                # Итоговая строка в таблице ошибок
                current_rows = self.error_table.rowCount()
                self.error_table.setRowCount(current_rows + 1)
                summary_item = QTableWidgetItem(f"Общее количество ошибок: {len(syntax_errors)}")
                summary_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                summary_font = QFont()
                summary_font.setBold(True)
                summary_font.setPointSize(11)
                summary_item.setFont(summary_font)
                summary_item.setBackground(QBrush(QColor(255, 150, 150)))
                self.error_table.setItem(current_rows, 0, summary_item)
                self.error_table.setSpan(current_rows, 0, 1, 3)
                
                self.output_area.append(f"\nОбщее количество синтаксических ошибок: {len(syntax_errors)}")
                self.statusbar.showMessage(f"Анализ завершен: {len(syntax_errors)} синтаксических ошибок")
                
                # Переключаем на вкладку Ошибки
                self.tab_widget.setCurrentIndex(1)
            else:
                # Нет ошибок
                self.error_table.setRowCount(1)
                ok_item = QTableWidgetItem("✅ Синтаксических ошибок нет")
                ok_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                ok_font = QFont()
                ok_font.setBold(True)
                ok_item.setFont(ok_font)
                ok_item.setBackground(QBrush(QColor(200, 255, 200)))
                self.error_table.setItem(0, 0, ok_item)
                self.error_table.setSpan(0, 0, 1, 3)
                
                self.output_area.append("Синтаксический анализ завершен без ошибок")
                self.statusbar.showMessage("Анализ успешно завершен")
                
                # Оставляем на вкладке Ошибки
                self.tab_widget.setCurrentIndex(1)
                
        except Exception as e:
            self.output_area.append(f"\nКритическая ошибка анализа: {str(e)}")
            self.statusbar.showMessage("Ошибка анализа")
            self.tab_widget.setCurrentIndex(0)  # При ошибке - на Лог
    
    def run_expression_analyzer(self):
        """Запуск анализа арифметического выражения"""
        text = self.editor.toPlainText().strip()
        
        if not text:
            self.output_area.clear()
            self.output_area.append("⚠️ Введите арифметическое выражение для анализа.")
            self.tab_widget.setCurrentIndex(0)
            return
        
        # Выполняем анализ выражения
        result = self.expression_analyzer.analyze_with_details(text)
        
        # Выводим результаты в лог
        self.output_area.clear()
        self.output_area.append("=" * 60)
        self.output_area.append("АНАЛИЗ АРИФМЕТИЧЕСКОГО ВЫРАЖЕНИЯ")
        self.output_area.append("=" * 60)
        self.output_area.append(f"Исходное выражение: {text}\n")
        
        # Лексический анализ
        self.output_area.append("-" * 40)
        self.output_area.append("ЭТАП 1: ЛЕКСИЧЕСКИЙ АНАЛИЗ")
        self.output_area.append("-" * 40)
        
        # Заполняем таблицу лексем
        tokens = result['tokens']
        # Исключаем EOF токен из отображения
        display_tokens = [t for t in tokens if t.type != ExprTokenType.EOF]
        self.current_expr_tokens = display_tokens
        
        self.token_table.setRowCount(len(display_tokens))
        
        for i, token in enumerate(display_tokens):
            code_item = QTableWidgetItem(str(i + 1))
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Красивое имя типа токена
            type_names = {
                ExprTokenType.NUMBER: "Число",
                ExprTokenType.IDENTIFIER: "Идентификатор",
                ExprTokenType.PLUS: "Оператор +",
                ExprTokenType.MINUS: "Оператор -",
                ExprTokenType.MUL: "Оператор *",
                ExprTokenType.DIV: "Оператор /",
                ExprTokenType.MOD: "Оператор %",
                ExprTokenType.LPAREN: "Скобка (",
                ExprTokenType.RPAREN: "Скобка )",
                ExprTokenType.ERROR: "ОШИБКА",
            }
            
            type_item = QTableWidgetItem(type_names.get(token.type, token.type.name))
            lexeme_item = QTableWidgetItem(token.value)
            
            location_text = f"позиция {token.position}"
            location_item = QTableWidgetItem(location_text)
            
            if token.is_error:
                error_color = QColor(255, 220, 220)
                code_item.setBackground(QBrush(error_color))
                type_item.setBackground(QBrush(error_color))
                lexeme_item.setBackground(QBrush(error_color))
                location_item.setBackground(QBrush(error_color))
                
                font = QFont()
                font.setBold(True)
                code_item.setFont(font)
                type_item.setFont(font)
                lexeme_item.setFont(font)
                location_item.setFont(font)
            
            self.token_table.setItem(i, 0, code_item)
            self.token_table.setItem(i, 1, type_item)
            self.token_table.setItem(i, 2, lexeme_item)
            self.token_table.setItem(i, 3, location_item)
        
        lexical_errors = [t for t in tokens if t.is_error]
        if lexical_errors:
            self.output_area.append(f"Лексических ошибок: {len(lexical_errors)}")
            for err in lexical_errors:
                self.output_area.append(f"  • Неверный символ '{err.value}' в позиции {err.position}")
        else:
            self.output_area.append("Лексических ошибок нет")
        
        self.output_area.append(f"Выделено лексем: {len(display_tokens)}")
        
        # Синтаксический анализ
        self.output_area.append("\n" + "-" * 40)
        self.output_area.append("ЭТАП 2: СИНТАКСИЧЕСКИЙ АНАЛИЗ (рекурсивный спуск)")
        self.output_area.append("-" * 40)
        
        if result['success']:
            self.output_area.append("✅ Синтаксический анализ успешен")
            
            # Заполняем таблицу ошибок
            self.error_table.setRowCount(1)
            ok_item = QTableWidgetItem("✅ Синтаксических ошибок нет")
            ok_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            ok_font = QFont()
            ok_font.setBold(True)
            ok_item.setFont(ok_font)
            ok_item.setBackground(QBrush(QColor(200, 255, 200)))
            self.error_table.setItem(0, 0, ok_item)
            self.error_table.setSpan(0, 0, 1, 3)
            
            # Тетрады
            self.output_area.append("\n" + "-" * 40)
            self.output_area.append("ЭТАП 3: ГЕНЕРАЦИЯ ТЕТРАД")
            self.output_area.append("-" * 40)
            
            if result['tetrads']:
                self.output_area.append("Тетрады (op, arg1, arg2, result):")
                for i, tetrad in enumerate(result['tetrads'], 1):
                    self.output_area.append(f"  {i}. {tetrad}")
                
                # Заполняем таблицу тетрад
                self.tetrad_table.setRowCount(len(result['tetrads']))
                for i, tetrad in enumerate(result['tetrads']):
                    op_item = QTableWidgetItem(tetrad.op)
                    op_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    arg1_item = QTableWidgetItem(tetrad.arg1)
                    arg1_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    arg2_item = QTableWidgetItem(tetrad.arg2)
                    arg2_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    result_item = QTableWidgetItem(tetrad.result)
                    result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Подсветка временных переменных
                    if tetrad.result.startswith('t'):
                        result_item.setBackground(QBrush(QColor(230, 255, 230)))
                    
                    self.tetrad_table.setItem(i, 0, op_item)
                    self.tetrad_table.setItem(i, 1, arg1_item)
                    self.tetrad_table.setItem(i, 2, arg2_item)
                    self.tetrad_table.setItem(i, 3, result_item)
            else:
                self.output_area.append("Тетрады не созданы (простое выражение)")
                self.tetrad_table.setRowCount(0)
            
            # ПОЛИЗ
            self.output_area.append("\n" + "-" * 40)
            self.output_area.append("ЭТАП 4: ПОЛИЗ (Польская инверсная запись)")
            self.output_area.append("-" * 40)
            self.output_area.append(f"ПОЛИЗ: {result['poliz_str']}")
            
            self.poliz_label.setText(f"ПОЛИЗ: {result['poliz_str']}")
            
            # Вычисление
            if result['eval_result'] is not None:
                self.output_area.append(f"\n✅ Результат вычисления: {result['eval_result']}")
                self.result_label.setText(f"Результат: {result['eval_result']}")
            elif result['has_identifiers']:
                self.output_area.append("\n⚠️ Выражение содержит идентификаторы, вычисление невозможно")
                self.result_label.setText("Результат: невозможно вычислить (есть идентификаторы)")
            else:
                self.result_label.setText("Результат: —")
        else:
            self.output_area.append("❌ Синтаксический анализ завершился с ошибками:")
            
            # Заполняем таблицу ошибок
            errors = result['errors']
            self.error_table.setRowCount(len(errors))
            
            for i, error in enumerate(errors):
                # Парсим сообщение ошибки для извлечения позиции
                pos_match = re_module.search(r'позиция\s*:?\s*(\d+)', error)
                position = pos_match.group(1) if pos_match else "?"
                
                fragment_item = QTableWidgetItem(error[:50] + "..." if len(error) > 50 else error)
                fragment_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                location_item = QTableWidgetItem(f"позиция {position}")
                location_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                description_item = QTableWidgetItem(error)
                
                error_color = QColor(255, 220, 220)
                fragment_item.setBackground(QBrush(error_color))
                location_item.setBackground(QBrush(error_color))
                description_item.setBackground(QBrush(error_color))
                
                self.error_table.setItem(i, 0, fragment_item)
                self.error_table.setItem(i, 1, location_item)
                self.error_table.setItem(i, 2, description_item)
            
            for err in errors:
                self.output_area.append(f"  • {err}")
            
            self.output_area.append(f"\n⚠️ Из-за ошибок тетрады и ПОЛИЗ не генерируются")
            
            # Очищаем таблицу тетрад и ПОЛИЗ
            self.tetrad_table.setRowCount(0)
            self.poliz_label.setText("ПОЛИЗ: —")
            self.result_label.setText("Результат: —")
        
        # Переключаемся на вкладку Лог
        self.tab_widget.setCurrentIndex(0)
        self.statusbar.showMessage("Анализ выражения завершён | F6 для повторного анализа", 5000)
    
    def on_token_table_clicked(self, row, column):
        """Обработка клика по строке таблицы лексем"""
        # Пробуем сначала токены выражения
        if 0 <= row < len(self.current_expr_tokens):
            token = self.current_expr_tokens[row]
            self._navigate_to_position(1, token.position, token.position + len(token.value) - 1)
            return
        
        # Затем токены программы
        if 0 <= row < len(self.current_tokens):
            token = self.current_tokens[row]
            self._navigate_to_position(token.line, token.start_pos, token.end_pos)
    
    def on_error_table_clicked(self, row, column):
        """Обработка клика по строке таблицы ошибок"""
        if 0 <= row < len(self.current_errors):
            error = self.current_errors[row]
            self._navigate_to_position(error.line, error.position, error.position)
    
    def _navigate_to_position(self, line, start_pos, end_pos):
        """Перемещение курсора к указанной позиции в редакторе"""
        cursor = self.editor.textCursor()
        
        lines = self.editor.toPlainText().split('\n')
        position = 0
        
        for i in range(min(line - 1, len(lines))):
            position += len(lines[i]) + 1
        
        position += start_pos - 1
        
        text_length = len(self.editor.toPlainText())
        position = min(position, max(0, text_length - 1))
        
        cursor.setPosition(position)
        
        if start_pos != end_pos:
            end_position = position + (end_pos - start_pos + 1)
            end_position = min(end_position, text_length)
            cursor.setPosition(end_position, QTextCursor.MoveMode.KeepAnchor)
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        
        self.statusbar.showMessage(
            f"Переход: строка {line}, позиция {start_pos}", 5000
        )
    
    def show_help(self):
        """Показать окно справки"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()
        self.statusbar.showMessage("Открыта справочная система", 3000)
        
    def show_about(self):
        """Показать окно 'О программе'"""
        about_dialog = AboutDialog(self)
        about_dialog.exec()
        self.statusbar.showMessage("Информация о программе", 3000)
        
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()


def main():
    """Главная функция запуска приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("Языковой процессор")
    app.setApplicationDisplayName("Языковой процессор")
    
    app.setStyle("Fusion")
    
    editor = TextEditor()
    editor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()