"""
Синтаксический анализатор (парсер) для объявления комплексного числа на языке Rust
Вариант 5: Объявление комплексного числа с инициализацией

Грамматика G[Z]:
Z    → "let" ID "=" E ";"
E    → PATH "::" "new" "(" ARGS ")"
PATH → ID ("::" ID)*
ARGS → NUM "," NUM
NUM  → ["-"] DIGITS ["." DIGITS]
ID   → LETTER (LETTER | DIGIT | "_")*
DIGITS → DIGIT+
LETTER → "a".."z" | "A".."Z" | "_"
DIGIT  → "0".."9"

Метод анализа: нисходящий разбор (рекурсивный спуск)
Нейтрализация ошибок: метод Айронса
"""

from lexical_analyzer import LexicalAnalyzer, Token


class SyntaxError:
    """Класс для хранения информации о синтаксической ошибке"""
    def __init__(self, fragment, line, position, description):
        self.fragment = fragment
        self.line = line
        self.position = position
        self.description = description


class SyntaxAnalyzer:
    """Синтаксический анализатор с методом нейтрализации ошибок Айронса"""
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.errors = []
        self.lexical_analyzer = LexicalAnalyzer()
    
    def _get_token(self):
        """Получить текущий значащий токен (пропуская пробелы и лексические ошибки)"""
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.token_type in ['разделитель (пробел)', 'разделитель (новая строка)']:
                self.pos += 1
            elif t.is_error:
                self.pos += 1
            else:
                return t
        return None
    
    def _peek_next(self):
        """Подсмотреть следующий значащий токен без продвижения"""
        saved = self.pos
        token = self._get_token()
        if token:
            self.pos += 1
            next_token = self._get_token()
            self.pos = saved
            return next_token
        return None
    
    def _next(self):
        """Перейти к следующему токену"""
        self.pos += 1
    
    def _get_last_position(self):
        """Позиция последнего значащего токена"""
        pos = self.pos - 1
        while pos >= 0:
            t = self.tokens[pos]
            if t.token_type not in ['разделитель (пробел)', 'разделитель (новая строка)'] and not t.is_error:
                return t.line, t.end_pos + 1
            pos -= 1
        return 1, 1
    
    def _add_error(self, fragment, line, pos, desc):
        """Добавить синтаксическую ошибку"""
        self.errors.append(SyntaxError(fragment, line, pos, desc))
    
    def _is_number_token(self, token):
        """Проверка: является ли токен числом"""
        if token is None:
            return False
        t = token.token_type.lower() if token.token_type else ''
        if 'число' in t or 'константа' in t or 'целое' in t:
            return True
        lex = token.lexeme
        if lex.startswith('-'):
            lex = lex[1:]
        if lex and all(c.isdigit() or c == '.' for c in lex) and lex.count('.') <= 1:
            return True
        return False
    
    def analyze(self, text):
        """Главный метод анализа. Возвращает (success, errors)"""
        self.errors = []
        
        if not text or not text.strip():
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return False, self.errors
        
        # Лексический анализ
        all_tokens, lex_errors = self.lexical_analyzer.analyze(text)
        self.tokens = all_tokens
        self.pos = 0
        
        # Синтаксический разбор
        self.parse_Z()
        
        success = len(self.errors) == 0
        return success, self.errors
    
    # ==================== МЕТОДЫ РЕКУРСИВНОГО СПУСКА ====================
    
    def parse_Z(self):
        """
        Z → "let" ID "=" E ";"
        """
        token = self._get_token()
        
        if token is None:
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return
        
        # 1. Проверка "let"
        if token.lexeme != 'let':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ключевое слово 'let', получено '{token.lexeme}'"
            )
            # НЕ продвигаемся! Токен остаётся и будет обработан как ID
        else:
            self._next()
        
        # 2. Идентификатор
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался идентификатор")
            return
        
        if token.token_type == 'идентификатор':
            self._next()
        else:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался идентификатор, получено '{token.lexeme}'"
            )
            # Поиск '='
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme == '=':
                    break
                self.pos += 1
        
        # 3. Оператор '='
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался оператор '='")
            return
        
        if token.lexeme == '=':
            self._next()
        else:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался оператор '=', получено '{token.lexeme}'"
            )
            # Поиск идентификатора (начало пути)
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.token_type == 'идентификатор':
                    break
                self.pos += 1
        
        # 4. Выражение E
        self.parse_E()
        
        # 5. Точка с запятой ';'
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался ';' (конец оператора)")
            return
        
        if token.lexeme == ';':
            self._next()
        else:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался ';', получено '{token.lexeme}'"
            )
        
        # Проверка лишних токенов
        token = self._get_token()
        if token is not None:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Неожиданный токен '{token.lexeme}' после конца выражения"
            )
    
    def parse_E(self):
        """
        E → PATH "::" "new" "(" ARGS ")"
        """
        # 1. Разбор пути PATH
        self.parse_PATH()
        
        # 2. '::'
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался '::'")
            return
        
        if token.lexeme != '::':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался '::', получено '{token.lexeme}'"
            )
            # Поиск "new" или "("
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme in {'new', '(', ';'}:
                    break
                self.pos += 1
        else:
            self._next()
        
        # 3. 'new'
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось ключевое слово 'new'")
            return
        
        if token.lexeme != 'new':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ключевое слово 'new', получено '{token.lexeme}'"
            )
            # Поиск '('
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme == '(':
                    break
                self.pos += 1
        else:
            self._next()
        
        # 4. '('
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалась '('")
            return
        
        if token.lexeme != '(':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалась '(', получено '{token.lexeme}'"
            )
            return
        self._next()
        
        # 5. ARGS
        self.parse_ARGS()
        
        # 6. ')'
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалась ')'")
            return
        
        if token.lexeme != ')':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалась ')', получено '{token.lexeme}'"
            )
        else:
            self._next()
    
    def parse_PATH(self):
        """
        PATH → ID ("::" ID)*
        
        Разбирает: num :: complex :: Complex
        Останавливается ПЕРЕД ::new (оставляет :: для parse_E)
        """
        # Первый идентификатор
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался идентификатор в пути")
            return
        
        if token.token_type != 'идентификатор':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался идентификатор в пути, получено '{token.lexeme}'"
            )
            return
        
        self._next()  # пропускаем первый ID
        
        # Цикл: "::" ID
        while True:
            token = self._get_token()
            if token is None:
                break
            
            if token.lexeme != '::':
                break
            
            # Смотрим токен ПОСЛЕ ::
            next_token = self._peek_next()
            
            if next_token is None:
                break
            
            # КЛЮЧЕВОЙ МОМЕНТ:
            # Если после :: идёт 'new' — это НЕ часть пути!
            # Это уже "::new" из правила E
            if next_token.lexeme == 'new':
                break
            
            # Если после :: идёт идентификатор — продолжаем путь
            if next_token.token_type == 'идентификатор':
                self._next()  # пропускаем ::
                self._next()  # пропускаем ID
            else:
                break
    
    def parse_ARGS(self):
        """
        ARGS → NUM "," NUM
        """
        # Первое число
        if not self._parse_num():
            return
        
        # Запятая
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалась ',' между аргументами")
            return
        
        if token.lexeme != ',':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалась ',' между аргументами, получено '{token.lexeme}'"
            )
            return
        
        self._next()
        
        # Второе число
        self._parse_num()
    
    def _parse_num(self):
        """
        NUM → ["-"] DIGITS ["." DIGITS]
        """
        token = self._get_token()
        
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось число")
            return False
        
        if self._is_number_token(token):
            lex = token.lexeme
            
            # Проверка на точку без цифр спереди
            if lex.startswith('.'):
                self._add_error(
                    lex, token.line, token.start_pos,
                    "Ожидалась цифра перед десятичной точкой"
                )
                self._next()
                return False
            
            # Проверка на множественные точки
            if lex.count('.') > 1:
                self._add_error(
                    lex, token.line, token.start_pos,
                    "Некорректное число: множественные точки"
                )
                self._next()
                return False
            
            self._next()
            return True
        else:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось число, получено '{token.lexeme}'"
            )
            return False