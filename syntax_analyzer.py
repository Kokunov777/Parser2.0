"""
Синтаксический анализатор (парсер) для объявления комплексного числа на языке Rust
Вариант 5: Объявление комплексного числа с инициализацией

Грамматика G[Z]:
Z → "let" ID "=" PATH "::" "new" "(" ARGS ")" ";"
PATH → ID ("::" ID)*
ARGS → NUM "," NUM
NUM → ["-"] DIGITS ["." DIGITS]
ID → LETTER (LETTER | DIGIT | "_")*
DIGITS → DIGIT+
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
        """Получить текущий значащий токен (без пробелов и ошибок)"""
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.token_type in ['разделитель (пробел)', 'разделитель (новая строка)']:
                self.pos += 1
            elif t.is_error:
                self.pos += 1
            else:
                return t
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
        """Главный метод анализа"""
        self.errors = []
        
        if not text or not text.strip():
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return False, self.errors
        
        all_tokens, lex_errors = self.lexical_analyzer.analyze(text)
        self.tokens = all_tokens
        self.pos = 0
        
        self.parse_Z()
        
        success = len(self.errors) == 0
        return success, self.errors
    
    def parse_Z(self):
        """
        Z → "let" ID "=" PATH "::" "new" "(" ARGS ")" ";"
        """
        token = self._get_token()
        
        if token is None:
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return
        
        # 1. Проверка "let"
        if token is None:
            return
        
        if token.lexeme != 'let':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ключевое слово 'let', получено '{token.lexeme}'"
            )
            # НЕ продвигаемся! Токен остаётся как идентификатор
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
            # Ищем идентификатор дальше
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme == '=' or t.token_type == 'идентификатор':
                    break
                self.pos += 1
            token = self._get_token()
            if token and token.token_type == 'идентификатор':
                self._next()
            elif token and token.lexeme == '=':
                pass  # пропустим идентификатор, перейдем к =
            else:
                return
        
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
            # Ищем '='
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme in {'=', ';'} or t.token_type == 'идентификатор':
                    break
                self.pos += 1
            token = self._get_token()
            if token and token.lexeme == '=':
                self._next()
        
        # 4. Разбираем: PATH "::" "new" "(" ARGS ")" ";"
        self.parse_PATH()
        self.parse_double_colon_new()
        self.parse_paren_args()
        self.parse_close_paren()
        self.parse_semicolon()
        
        # Проверка на лишние токены
        token = self._get_token()
        if token is not None:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Неожиданный токен '{token.lexeme}' после конца выражения"
            )
    
    def parse_PATH(self):
        """
        PATH → ID ("::" ID)*
        Читаем: ID, потом (:: ID)* пока не встретим ::new
        """
        token = self._get_token()
        
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался идентификатор в пути")
            return False
        
        if token.token_type != 'идентификатор':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался идентификатор в пути, получено '{token.lexeme}'"
            )
            return False
        
        self._next()
        
        # Цикл: "::" ID (но НЕ "::new")
        while True:
            saved_pos = self.pos
            
            t1 = self._get_token()
            if t1 is None or t1.lexeme != '::':
                break
            
            self._next()
            t2 = self._get_token()
            self.pos = saved_pos  # откат
            
            if t2 is None:
                break
            
            # КЛЮЧ: если после :: идет 'new' — это НЕ часть пути
            if t2.lexeme == 'new':
                break
            
            if t2.token_type == 'идентификатор':
                self._next()  # пропускаем ::
                self._next()  # пропускаем ID
            else:
                break
        
        return True
    
    def parse_double_colon_new(self):
        """Разбор: "::" "new" """
        # ::
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался '::'")
            return False
        
        if token.lexeme != '::':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался '::', получено '{token.lexeme}'"
            )
            # Ищем new или (
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme in {'new', '(', ';'}:
                    break
                self.pos += 1
        else:
            self._next()
        
        # new
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось ключевое слово 'new'")
            return False
        
        if token.lexeme != 'new':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ключевое слово 'new', получено '{token.lexeme}'"
            )
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme in {'(', ';'}:
                    break
                self.pos += 1
        else:
            self._next()
        
        return True
    
    def parse_paren_args(self):
        """Разбор: "(" ARGS """
        # (
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалась '('")
            return False
        
        if token.lexeme != '(':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалась '(', получено '{token.lexeme}'"
            )
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme in {')', ';'}:
                    break
                self.pos += 1
            return False
        
        self._next()
        
        # ARGS
        self.parse_ARGS()
        return True
    
    def parse_close_paren(self):
        """Разбор: ')' """
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалась ')'")
            return False
        
        if token.lexeme != ')':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалась ')', получено '{token.lexeme}'"
            )
            while self.pos < len(self.tokens):
                t = self.tokens[self.pos]
                if t.lexeme == ';':
                    break
                self.pos += 1
        else:
            self._next()
        
        return True
    
    def parse_semicolon(self):
        """Разбор: ';' """
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался ';' (конец оператора)")
            return False
        
        if token.lexeme != ';':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался ';', получено '{token.lexeme}'"
            )
        else:
            self._next()
        
        return True
    
    def parse_ARGS(self):
        """ARGS → NUM "," NUM"""
        if not self._parse_num():
            return
        
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
        
        if not self._parse_num():
            return
    
    def _parse_num(self):
        """NUM → ["-"] DIGITS ["." DIGITS]"""
        token = self._get_token()
        
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось число")
            return False
        
        if self._is_number_token(token):
            lex = token.lexeme
            
            if lex.startswith('.'):
                self._add_error(
                    lex, token.line, token.start_pos,
                    "Ожидалась цифра перед десятичной точкой"
                )
                self._next()
                return False
            
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