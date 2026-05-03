import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QMenuBar, QMenu, QToolBar,
    QStatusBar, QSplitter, QFileDialog, QMessageBox, QDialog,
    QVBoxLayout, QDialogButtonBox, QLabel, QWidget, QStyle,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QHBoxLayout, QFrame, QGroupBox, QScrollArea, QListWidget, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QTextCursor, QColor, QFont, QBrush
from PyQt6.QtCore import Qt, QFileInfo, QDir, QSize

# Импорт лексического анализатора
from lexical_analyzer import LexicalAnalyzer, Token


class HelpDialog(QDialog):
    """Диалоговое окно справки"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>📚 Справка текстового редактора с лексическим анализатором</h2>
        
        <h3>📁 Меню "Файл"</h3>
        <ul>
            <li><b>Создать (Ctrl+N)</b> - создает новый документ</li>
            <li><b>Открыть (Ctrl+O)</b> - открывает существующий файл</li>
            <li><b>Сохранить (Ctrl+S)</b> - сохраняет текущий документ</li>
            <li><b>Сохранить как (Ctrl+Shift+S)</b> - сохраняет документ под новым именем</li>
            <li><b>Выход (Ctrl+Q)</b> - закрывает приложение</li>
        </ul>
        
        <h3>✏️ Меню "Правка"</h3>
        <ul>
            <li><b>Отменить (Ctrl+Z)</b> - отменяет последнее действие</li>
            <li><b>Повторить (Ctrl+Y)</b> - повторяет отмененное действие</li>
            <li><b>Вырезать (Ctrl+X)</b> - вырезает выделенный текст</li>
            <li><b>Копировать (Ctrl+C)</b> - копирует выделенный текст</li>
            <li><b>Вставить (Ctrl+V)</b> - вставляет текст из буфера обмена</li>
            <li><b>Удалить (Del)</b> - удаляет выделенный текст</li>
            <li><b>Выделить все (Ctrl+A)</b> - выделяет весь текст</li>
        </ul>
        
        <h3>▶️ Меню "Пуск"</h3>
        <ul>
            <li><b>Пуск (F5)</b> - запуск лексического анализатора</li>
        </ul>
        
        <h3>❓ Меню "Справка"</h3>
        <ul>
            <li><b>Вызов справки (F1)</b> - открывает это окно</li>
            <li><b>О программе</b> - информация о программе</li>
        </ul>
        
        <h3>🔍 Лексический анализатор (Вариант 5)</h3>
        <p><b>Назначение:</b> Анализ объявления комплексного числа на языке Rust.</p>
        <p><b>Пример входных данных:</b></p>
        <pre><code>let complex_num2 = num::complex::Complex::new(3.1, -4.2);</code></pre>
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
        self.setFixedSize(500, 280)
        
        layout = QVBoxLayout()
        
        info_label = QLabel("""
        <h2>📝 Текстовый редактор с лексическим анализатором</h2>
        <p><b>Версия:</b> 2.0</p>
        <p><b>Разработчик:</b> Студент</p>
        <p><b>Назначение:</b> Языковой процессор для анализа кода на Rust</p>
        <p><b>Вариант:</b> 5 - Объявление комплексного числа с инициализацией</p>
        <p><b>Технологии:</b> Python + PyQt6</p>
        <hr>
        <p>Лабораторная работа №2</p>
        <p>Разработка лексического анализатора (сканера)</p>
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(info_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class TextEditor(QMainWindow):
    """Главное окно текстового редактора с лексическим анализатором"""
    
    def __init__(self):
        super().__init__()
        
        self.current_file_path = None
        self.is_modified = False
        self.lexical_analyzer = LexicalAnalyzer()
        self.current_tokens = []
        self.current_errors = []
        
        # Словарь с информацией для пунктов меню Текст
        self.text_menu_info = {
            "Постановка задачи": """
                <h3>📋 Постановка задачи</h3>
                <hr>
                <p><b>Вариант 5:</b> Объявление комплексного числа с инициализацией на языке Rust</p>
                <p>Разработать лексический анализатор (сканер) для выделения лексем 
                из объявления комплексного числа в синтаксисе Rust.</p>
                <p><b>Пример:</b> <code>let complex_num2 = num::complex::Complex::new(3.1, -4.2);</code></p>
                <p><b>Выделяемые лексемы:</b></p>
                <ul>
                    <li>Ключевые слова: let, new</li>
                    <li>Идентификаторы: complex_num2, num, complex, Complex</li>
                    <li>Числовые литералы: 3.1, -4.2</li>
                    <li>Операторы: =</li>
                    <li>Разделители: ::, ., ,, (, )</li>
                    <li>Конец оператора: ;</li>
                </ul>
                <p><b>Задача:</b> Реализовать сканер, который принимает входную строку и 
                возвращает таблицу лексем с указанием типа, кода и местоположения.</p>
            """,
            
            "Грамматика": """
                <h3>📐 Грамматика языка</h3>
                <hr>
                <p><b>Объявление комплексного числа (Rust-подобный синтаксис):</b></p>
                <pre>
&lt;программа&gt; ::= &lt;объявление&gt;
&lt;объявление&gt; ::= "let" &lt;идентификатор&gt; "=" &lt;выражение&gt; ";"
&lt;выражение&gt; ::= &lt;путь&gt; "::" "new" "(" &lt;аргументы&gt; ")"
&lt;путь&gt; ::= &lt;идентификатор&gt; ("::" &lt;идентификатор&gt;)*
&lt;аргументы&gt; ::= &lt;число&gt; "," &lt;число&gt;
&lt;число&gt; ::= ["-"] &lt;цифры&gt; ["." &lt;цифры&gt;]
&lt;идентификатор&gt; ::= буква (буква | цифра | "_")*
&lt;цифры&gt; ::= цифра+
                </pre>
                <p><b>Терминальные символы:</b> let, =, ::, new, (, ), ,, ;, идентификатор, число</p>
                <p><b>Нетерминальные символы:</b> программа, объявление, выражение, путь, аргументы, число, цифры, идентификатор</p>
            """,
            
            "Классификация грамматики": """
                <h3>🏷️ Классификация грамматики</h3>
                <hr>
                <p><b>По иерархии Хомского:</b></p>
                <ul>
                    <li><b>Тип 2</b> - контекстно-свободная грамматика (КС-грамматика)</li>
                    <li>Все правила имеют вид A → α, где A - нетерминал, α - цепочка из терминалов и нетерминалов</li>
                </ul>
                <br>
                <p><b>Свойства грамматики:</b></p>
                <ul>
                    <li>✓ Однозначная - каждая цепочка имеет единственный левый вывод</li>
                    <li>✓ Не содержит левой рекурсии</li>
                    <li>✓ Допускает нисходящий разбор (LL(1))</li>
                    <li>✓ Регулярные выражения для лексического анализа</li>
                </ul>
                <br>
                <p><b>Классификация лексем:</b></p>
                <ul>
                    <li><b>Ключевые слова:</b> let, new</li>
                    <li><b>Идентификаторы:</b> имена переменных и модулей</li>
                    <li><b>Литералы:</b> целые и вещественные числа</li>
                    <li><b>Операторы:</b> присваивание (=), минус (-)</li>
                    <li><b>Разделители:</b> ::, ., ,, (, ), ;</li>
                </ul>
            """,
            
            "Метод анализа": """
                <h3>🔍 Метод лексического анализа</h3>
                <hr>
                <p><b>Метод:</b> Прямой лексический анализ на основе детерминированного конечного автомата (ДКА)</p>
                <br>
                <p><b>Алгоритм работы сканера:</b></p>
                <ol>
                    <li><b>Инициализация:</b> установка указателя на начало входной строки</li>
                    <li><b>Чтение символа:</b> получение текущего символа из входного потока</li>
                    <li><b>Классификация:</b> определение типа лексемы по первому символу</li>
                    <li><b>Распознавание:</b> последовательное чтение символов до нарушения правила</li>
                    <li><b>Формирование токена:</b> создание объекта Token с атрибутами</li>
                    <li><b>Обработка ошибок:</b> если символ недопустим - формирование токена ошибки</li>
                </ol>
                <br>
                <p><b>Состояния конечного автомата:</b></p>
                <ul>
                    <li><b>START</b> - начальное состояние</li>
                    <li><b>IDENT</b> - чтение идентификатора или ключевого слова</li>
                    <li><b>NUMBER</b> - чтение числового литерала</li>
                    <li><b>OPERATOR</b> - распознавание оператора</li>
                    <li><b>DELIMITER</b> - распознавание разделителя</li>
                    <li><b>ERROR</b> - состояние ошибки</li>
                </ul>
                <br>
                <p><b>Сложность:</b> O(n), где n - длина входной строки</p>
            """,
            
            "Тестовый пример": """
                <h3>🧪 Тестовые примеры</h3>
                <hr>
                <p>Доступно 10 тестовых примеров для проверки работы лексического анализатора.</p>
                <p>Вы можете загрузить их в редактор через меню <b>Текст → Тестовый пример</b>.</p>
                <br>
                <p><b>Доступные примеры:</b></p>
                <ul>
                <li>Пример 1: Корректное объявление комплексного числа</li>
                <li>Пример 2: Простое объявление переменной</li>
                <li>Пример 3: Код с недопустимым символом @</li>
                <li>Пример 4: Многострочный код</li>
                <li>Пример 5: Несколько ошибок</li>
                <li>Пример 6-10: Дополнительные тесты</li>
            </ul>
            <br>
            <p><b>Базовый синтаксис:</b></p>
            <pre><code>let complex_num2 = num::complex::Complex::new(3.1, -4.2);</code></pre>
                """,
            
            "Список литературы": """
                <h3>📚 Список литературы</h3>
                <hr>
                <ol>
                    <li><b>Ахо А., Лам М., Сети Р., Ульман Дж.</b> 
                    Компиляторы: принципы, технологии и инструментарий. 
                    - 2-е изд. - М.: Вильямс, 2008. - 1184 с.</li>
                    <br>
                    <li><b>Грис Д.</b> 
                    Конструирование компиляторов для цифровых вычислительных машин. 
                    - М.: Мир, 1975. - 544 с.</li>
                    <br>
                    <li><b>Хантер Р.</b> 
                    Основные концепции компиляторов. 
                    - М.: Вильямс, 2002. - 256 с.</li>
                    <br>
                    <li><b>Касьянов В.Н., Поттосин И.В.</b> 
                    Методы построения трансляторов. 
                    - Новосибирск: Наука, 1986. - 344 с.</li>
                    <br>
                    <li><b>Rust Documentation.</b> 
                    The Rust Programming Language. 
                    - URL: https://doc.rust-lang.org/book/</li>
                    <br>
                    <li><b>Mogensen T.E.</b> 
                    Introduction to Compiler Design. 
                    - Springer, 2017. - 258 p.</li>
                </ol>
            """,
            
            "Исходный код программы": """
                <h3>💻 Исходный код программы</h3>
                <hr>
                <p><b>Структура проекта:</b></p>
                <pre>
project/
├── main.py              # Главный файл с GUI интерфейсом
├── lexical_analyzer.py  # Модуль лексического анализатора
├── requirements.txt     # Зависимости проекта
└── README.md           # Документация
                </pre>
                <br>
                <p><b>main.py</b> - содержит:</p>
                <ul>
                    <li>Класс TextEditor - главное окно приложения</li>
                    <li>Графический интерфейс на PyQt6</li>
                    <li>Интеграцию лексического анализатора</li>
                    <li>Таблицы для отображения результатов</li>
                    <li>Навигацию по ошибкам</li>
                </ul>
                <br>
                <p><b>lexical_analyzer.py</b> - содержит:</p>
                <ul>
                    <li>Класс Token - представление лексемы</li>
                    <li>Класс LexicalAnalyzer - сканер</li>
                    <li>Метод analyze() - основной метод анализа</li>
                    <li>Обработку всех типов лексем</li>
                </ul>
                <br>
                <p><b>Язык программирования:</b> Python 3.8+</p>
                <p><b>GUI Framework:</b> PyQt6 6.5+</p>
                <p><b>Лицензия:</b> MIT</p>
                <p><b>GitHub:</b> <a href='https://github.com/student/rust-lexer'>https://github.com/student/rust-lexer</a></p>
            """
        }
        # Словарь с тестовыми примерами для загрузки в редактор
        self.test_examples = {
            "Пример 1: Корректное объявление": "let complex_num2 = num::complex::Complex::new(3.1, -4.2);",
            
            "Пример 2: Простое объявление": "let x = 123;",
            
            "Пример 3: С ошибкой (@)": "let x = 123 @ 456;",
            
            "Пример 4: Многострочный код": "let a = Complex::new(\n    1.5,\n    -2.7\n);",
            
            "Пример 5: Несколько ошибок": "let x = 123 # 456 @ 789;",
            
            "Пример 6: Только идентификатор": "let my_var = 42;",
            
            "Пример 7: С плавающей точкой": "let pi = 3.14159;",
            
            "Пример 8: Отрицательные числа": "let neg = -42;",
            
            "Пример 9: Сложный путь": "let c = std::complex::Complex::new(0.0, 1.0);",
            
            "Пример 10: С недопустимым символом": "let a = 10 $ 20;"
        }
        
        self.init_ui()
        
    def get_icon(self, standard_icon):
        """Получение стандартной иконки из темы ОС"""
        return self.style().standardIcon(standard_icon)
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Текстовый редактор - Лексический анализатор")
        self.setMinimumSize(1100, 800)
        
        # Установка иконки приложения
        self.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_FileIcon))
        
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Верхний splitter для редактора и текстового вывода
        upper_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Область редактирования
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Введите текст программы на Rust...\n"
            "Пример: let complex_num2 = num::complex::Complex::new(3.1, -4.2);"
        )
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.setFont(QFont("Courier New", 12))
        
        # Область вывода текстовых сообщений
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Область вывода сообщений лексического анализатора...")
        self.output_area.setStyleSheet("background-color: #f8f8f8;")
        self.output_area.setMaximumHeight(150)
        
        upper_splitter.addWidget(self.editor)
        upper_splitter.addWidget(self.output_area)
        upper_splitter.setSizes([500, 150])
        
        # Создание панели с двумя таблицами
        tables_widget = QWidget()
        tables_layout = QVBoxLayout()
        tables_widget.setLayout(tables_layout)
        
        # Группа с таблицей лексем
        tokens_group = QGroupBox("📊 Таблица лексем")
        tokens_layout = QVBoxLayout()
        tokens_group.setLayout(tokens_layout)
        
        # Таблица для вывода лексем
        self.token_table = QTableWidget()
        self.token_table.setColumnCount(4)
        self.token_table.setHorizontalHeaderLabels([
            "Условный код", "Тип лексемы", "Лексема", "Местоположение"
        ])
        
        # Настройка таблицы лексем
        self.token_table.horizontalHeader().setStretchLastSection(True)
        self.token_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.token_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.token_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.token_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.token_table.setAlternatingRowColors(True)
        
        # Обработка клика по таблице лексем
        self.token_table.cellClicked.connect(self.on_token_table_clicked)
        
        tokens_layout.addWidget(self.token_table)
        
        # Группа с таблицей ошибок
        errors_group = QGroupBox("❌ Таблица ошибок")
        errors_layout = QVBoxLayout()
        errors_group.setLayout(errors_layout)
        
        # Таблица для вывода ошибок
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(4)
        self.error_table.setHorizontalHeaderLabels([
            "№", "Строка", "Позиция", "Сообщение"
        ])
        
        # Настройка таблицы ошибок
        self.error_table.horizontalHeader().setStretchLastSection(True)
        self.error_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.error_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.error_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.error_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.error_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.error_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.error_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.error_table.setAlternatingRowColors(True)
        
        # Обработка клика по таблице ошибок
        self.error_table.cellClicked.connect(self.on_error_table_clicked)
        
        errors_layout.addWidget(self.error_table)
        
        # Размещение таблиц с использованием splitter
        tables_splitter = QSplitter(Qt.Orientation.Vertical)
        tables_splitter.addWidget(tokens_group)
        tables_splitter.addWidget(errors_group)
        tables_splitter.setSizes([300, 150])
        
        tables_layout.addWidget(tables_splitter)
        
        # Добавление виджетов в основной layout
        main_layout.addWidget(upper_splitter, 2)
        main_layout.addWidget(tables_widget, 3)
        
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
        self.new_action.setStatusTip("Создать новый документ")
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogOpenButton), "Открыть...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.setStatusTip("Открыть существующий файл")
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Сохранить", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Сохранить текущий документ")
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Сохранить как...", self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.setStatusTip("Сохранить документ под новым именем")
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogCloseButton), "Выход", self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.setStatusTip("Выйти из приложения")
        self.exit_action.triggered.connect(self.close)
        
        # Правка
        self.undo_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_ArrowBack), "Отменить", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setStatusTip("Отменить последнее действие")
        self.undo_action.triggered.connect(self.editor.undo)
        
        self.redo_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_ArrowForward), "Повторить", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setStatusTip("Повторить отмененное действие")
        self.redo_action.triggered.connect(self.editor.redo)
        
        self.cut_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_CommandLink), "Вырезать", self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.setStatusTip("Вырезать выделенный текст")
        self.cut_action.triggered.connect(self.editor.cut)
        
        self.copy_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Копировать", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.setStatusTip("Копировать выделенный текст")
        self.copy_action.triggered.connect(self.editor.copy)
        
        self.paste_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogContentsView), "Вставить", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.setStatusTip("Вставить текст из буфера обмена")
        self.paste_action.triggered.connect(self.editor.paste)
        
        self.delete_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_TrashIcon), "Удалить", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.setStatusTip("Удалить выделенный текст")
        self.delete_action.triggered.connect(self.delete_text)
        
        self.select_all_action = QAction("Выделить все", self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_action.setStatusTip("Выделить весь текст")
        self.select_all_action.triggered.connect(self.editor.selectAll)
        
        # Текст
        self.task_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Постановка задачи", self)
        self.task_action.triggered.connect(lambda: self.show_text_menu_info("Постановка задачи"))
        
        self.grammar_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Грамматика", self)
        self.grammar_action.triggered.connect(lambda: self.show_text_menu_info("Грамматика"))
        
        self.classification_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Классификация грамматики", self)
        self.classification_action.triggered.connect(lambda: self.show_text_menu_info("Классификация грамматики"))
        
        self.analysis_method_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Метод анализа", self)
        self.analysis_method_action.triggered.connect(lambda: self.show_text_menu_info("Метод анализа"))
        
        self.test_example_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Тестовый пример", self)
        self.test_example_action.setShortcut(QKeySequence("Ctrl+T"))
        self.test_example_action.setStatusTip("Загрузить тестовый пример в редактор")
        self.test_example_action.triggered.connect(lambda: self.show_text_menu_info("Тестовый пример"))
        
        self.literature_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Список литературы", self)
        self.literature_action.triggered.connect(lambda: self.show_text_menu_info("Список литературы"))
        
        self.source_code_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView), "Исходный код программы", self)
        self.source_code_action.triggered.connect(lambda: self.show_text_menu_info("Исходный код программы"))
        
        # Пуск
        self.run_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_MediaPlay), "Пуск", self)
        self.run_action.setShortcut(QKeySequence("F5"))
        self.run_action.setStatusTip("Запустить лексический анализатор")
        self.run_action.triggered.connect(self.run_analyzer)
        
        # Справка
        self.help_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogHelpButton), "Вызов справки", self)
        self.help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.help_action.setStatusTip("Открыть справочную систему")
        self.help_action.triggered.connect(self.show_help)
        
        self.about_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_MessageBoxInformation), "О программе", self)
        self.about_action.setStatusTip("Информация о программе")
        self.about_action.triggered.connect(self.show_about)
        
    def create_menus(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("📁 Файл")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Меню Правка
        edit_menu = menubar.addMenu("✏️ Правка")
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
        text_menu = menubar.addMenu("📝 Текст")
        text_menu.addAction(self.task_action)
        text_menu.addAction(self.grammar_action)
        text_menu.addAction(self.classification_action)
        text_menu.addAction(self.analysis_method_action)
        text_menu.addSeparator()
        text_menu.addAction(self.test_example_action)
        text_menu.addAction(self.literature_action)
        text_menu.addAction(self.source_code_action)
        
        # Меню Пуск
        run_menu = menubar.addMenu("▶️ Пуск")
        run_menu.addAction(self.run_action)
        
        # Меню Справка
        help_menu = menubar.addMenu("❓ Справка")
        help_menu.addAction(self.help_action)
        help_menu.addAction(self.about_action)
        
    def create_toolbar(self):
        """Создание панели инструментов с иконками и подписями"""
        toolbar = QToolBar("Панель инструментов")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # Кнопки панели инструментов
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
        toolbar.addSeparator()
        
        toolbar.addAction(self.help_action)
        toolbar.addAction(self.about_action)
        
    def create_statusbar(self):
        """Создание строки состояния"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Готов к работе")
        
    def on_text_changed(self):
        """Обработчик изменения текста"""
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
            
    def update_title(self):
        """Обновление заголовка окна"""
        if self.current_file_path:
            filename = os.path.basename(self.current_file_path)
            title = f"📝 {filename}{'*' if self.is_modified else ''} - Текстовый редактор - Лексический анализатор"
        else:
            title = f"📝 Новый документ{'*' if self.is_modified else ''} - Текстовый редактор - Лексический анализатор"
        self.setWindowTitle(title)
        
    def new_file(self):
        """Создание нового файла"""
        if self.maybe_save():
            self.editor.clear()
            self.current_file_path = None
            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage("✅ Создан новый документ")
            
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
                    self.statusbar.showMessage(f"📂 Открыт файл: {os.path.basename(file_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "❌ Ошибка", f"Не удалось открыть файл:\n{e}")
                    self.statusbar.showMessage("❌ Ошибка при открытии файла")
                    
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
            self.statusbar.showMessage(f"💾 Файл сохранен: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сохранить файл:\n{e}")
            self.statusbar.showMessage("❌ Ошибка при сохранении файла")
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
            
    def show_text_menu_info(self, title):
        """Показать информацию из меню Текст"""
        # Для тестового примера - специальная обработка
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
        
        # Добавляем возможность прокрутки для длинного текста
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
        from PyQt6.QtWidgets import QListWidget, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Тестовые примеры")
        dialog.setMinimumSize(600, 450)
        dialog.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView))
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("<h3>🧪 Выберите тестовый пример для загрузки в редактор</h3>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Список примеров
        list_widget = QListWidget()
        for example_name in self.test_examples.keys():
            list_widget.addItem(example_name)
        
        # Предпросмотр
        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setFont(QFont("Courier New", 11))
        preview.setMaximumHeight(150)
        preview.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc;")
        
        # Обработчик выбора примера
        def on_selection_changed():
            selected = list_widget.currentItem()
            if selected:
                example_name = selected.text()
                preview.setText(self.test_examples[example_name])
        
        list_widget.currentItemChanged.connect(on_selection_changed)
        
        # Кнопки
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
                self.statusbar.showMessage(f"✅ Загружен: {example_name}", 5000)
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
        
    def run_analyzer(self):
        """Запуск лексического анализатора"""
        # Очистка предыдущих результатов
        self.output_area.clear()
        self.token_table.setRowCount(0)
        self.error_table.setRowCount(0)
        self.current_tokens = []
        self.current_errors = []
        
        # Получение текста из редактора
        text = self.editor.toPlainText()
        
        if not text.strip():
            self.output_area.append("⚠️ Нет текста для анализа.")
            self.statusbar.showMessage("⚠️ Нет текста для анализа", 3000)
            return
        
        # Запуск анализатора
        self.output_area.append("🚀 " + "="*60)
        self.output_area.append("ЛЕКСИЧЕСКИЙ АНАЛИЗАТОР ЗАПУЩЕН")
        self.output_area.append("="*64 + "\n")
        self.output_area.append(f"📝 Анализируемый текст:\n{text}\n")
        self.output_area.append("-"*64)
        
        try:
            tokens, errors = self.lexical_analyzer.analyze(text)
            self.current_tokens = tokens
            self.current_errors = errors
            
            # Заполнение таблицы лексем
            self.token_table.setRowCount(len(tokens))
            
            for i, token in enumerate(tokens):
                # Условный код
                code_item = QTableWidgetItem(str(token.code))
                code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Тип лексемы
                type_item = QTableWidgetItem(token.token_type)
                
                # Лексема
                lexeme_item = QTableWidgetItem(token.lexeme)
                
                # Местоположение
                location_text = f"строка {token.line}, позиция {token.start_pos}-{token.end_pos}"
                location_item = QTableWidgetItem(location_text)
                
                # Подсветка ошибок красным
                if token.is_error:
                    error_color = QColor(255, 220, 220)
                    code_item.setBackground(QBrush(error_color))
                    type_item.setBackground(QBrush(error_color))
                    lexeme_item.setBackground(QBrush(error_color))
                    location_item.setBackground(QBrush(error_color))
                    
                    # Жирный шрифт для ошибок
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
            
            # Заполнение таблицы ошибок
            if errors:
                self.error_table.setRowCount(len(errors))
                
                for i, error in enumerate(errors):
                    # Номер ошибки
                    num_item = QTableWidgetItem(str(i + 1))
                    num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Строка
                    line_item = QTableWidgetItem(str(error['line']))
                    line_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Позиция
                    pos_item = QTableWidgetItem(str(error['position']))
                    pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Сообщение
                    msg_item = QTableWidgetItem(error['message'])
                    
                    # Подсветка ошибок
                    error_color = QColor(255, 200, 200)
                    num_item.setBackground(QBrush(error_color))
                    line_item.setBackground(QBrush(error_color))
                    pos_item.setBackground(QBrush(error_color))
                    msg_item.setBackground(QBrush(error_color))
                    
                    # Жирный шрифт
                    font = QFont()
                    font.setBold(True)
                    num_item.setFont(font)
                    line_item.setFont(font)
                    pos_item.setFont(font)
                    msg_item.setFont(font)
                    
                    self.error_table.setItem(i, 0, num_item)
                    self.error_table.setItem(i, 1, line_item)
                    self.error_table.setItem(i, 2, pos_item)
                    self.error_table.setItem(i, 3, msg_item)
                    
                    # Вывод в текстовую область
                    self.output_area.append(
                        f"❌ {error['message']} "
                        f"(строка {error['line']}, позиция {error['position']})"
                    )
            
            # Статистика
            valid_tokens = [t for t in tokens if not t.is_error]
            error_tokens = [t for t in tokens if t.is_error]
            
            self.output_area.append(f"\n{'='*64}")
            self.output_area.append(f"✅ Анализ завершен.")
            self.output_area.append(f"📊 Всего лексем: {len(tokens)}")
            self.output_area.append(f"✓ Корректных лексем: {len(valid_tokens)}")
            
            if error_tokens:
                self.output_area.append(f"❌ Ошибок: {len(error_tokens)}")
                self.statusbar.showMessage(
                    f"⚠️ Анализ завершен: {len(valid_tokens)} лексем, {len(error_tokens)} ошибок"
                )
            else:
                self.output_area.append("✅ Ошибок не обнаружено")
                self.statusbar.showMessage(
                    f"✅ Анализ успешно завершен: {len(valid_tokens)} лексем"
                )
                
        except Exception as e:
            self.output_area.append(f"❌ Критическая ошибка анализа: {str(e)}")
            self.statusbar.showMessage("❌ Ошибка анализа")
    
    def on_token_table_clicked(self, row, column):
        """Обработка клика по строке таблицы лексем"""
        if 0 <= row < len(self.current_tokens):
            token = self.current_tokens[row]
            self._navigate_to_position(token.line, token.start_pos, token.end_pos)
    
    def on_error_table_clicked(self, row, column):
        """Обработка клика по строке таблицы ошибок"""
        if 0 <= row < len(self.current_errors):
            error = self.current_errors[row]
            self._navigate_to_position(error['line'], error['position'], error['position'])
    
    def _navigate_to_position(self, line, start_pos, end_pos):
        """Перемещение курсора к указанной позиции в редакторе"""
        cursor = self.editor.textCursor()
        
        # Вычисление абсолютной позиции в тексте
        lines = self.editor.toPlainText().split('\n')
        position = 0
        
        # Добавляем длину предыдущих строк + символы новой строки
        for i in range(min(line - 1, len(lines))):
            position += len(lines[i]) + 1
        
        # Добавляем позицию в строке
        position += start_pos - 1
        
        # Ограничиваем позицию размером текста
        text_length = len(self.editor.toPlainText())
        position = min(position, text_length)
        
        # Устанавливаем курсор
        cursor.setPosition(position)
        
        # Выделяем фрагмент
        if start_pos != end_pos:
            end_position = position + (end_pos - start_pos + 1)
            end_position = min(end_position, text_length)
            cursor.setPosition(end_position, QTextCursor.MoveMode.KeepAnchor)
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        
        self.statusbar.showMessage(
            f"🔍 Переход: строка {line}, позиция {start_pos}", 5000
        )
    
    def show_help(self):
        """Показать окно справки"""
        help_dialog = HelpDialog(self)
        help_dialog.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_DialogHelpButton))
        help_dialog.exec()
        self.statusbar.showMessage("📚 Открыта справочная система", 3000)
        
    def show_about(self):
        """Показать окно 'О программе'"""
        about_dialog = AboutDialog(self)
        about_dialog.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        about_dialog.exec()
        self.statusbar.showMessage("ℹ️ Информация о программе", 3000)
        
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()


def main():
    """Главная функция запуска приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("Текстовый редактор с лексическим анализатором")
    app.setApplicationDisplayName("Лексический анализатор")
    
    # Настройка стиля
    app.setStyle("Fusion")
    
    editor = TextEditor()
    editor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()