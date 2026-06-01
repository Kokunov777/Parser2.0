"""
Синтаксический анализатор (парсер) для объявления комплексного числа на языке Rust
Вариант 5: Объявление комплексного числа с инициализацией
"""

from lexical_analyzer import LexicalAnalyzer, Token


class SyntaxError:
    def __init__(self, fragment, line, position, description):
        self.fragment = fragment
        self.line = line
        self.position = position
        self.description = description


class SyntaxAnalyzer:
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.errors = []
        self.lexical_analyzer = LexicalAnalyzer()
        #self.error_count = 0
        #self.max_errors = 1  # ограничение на одну ошибку
    
    def _get_token(self):
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.token_type in ['разделитель (пробел)', 'разделитель (новая строка)']:
                self.pos += 1
            elif t.is_error:
                # Возвращаем токен ошибки, чтобы вызывающий код мог решить, какую ошибку добавить
                return t
            else:
                return t
        return None
    
    def _next(self):
        self.pos += 1
    
    def _add_error(self, fragment, line, pos, desc):
        #if self.error_count < self.max_errors:
            self.errors.append(SyntaxError(fragment, line, pos, desc))
           # self.error_count += 1
    
    def _is_digit(self, s):
        return len(s) == 1 and s.isdigit()
    
    def _is_identifier(self, token):
        if token is None:
            return False
        return token.token_type in ['идентификатор', 'ключевое слово']
    
    def _is_number_token(self, token):
        if token is None:
            return False
        t = token.token_type.lower() if token.token_type else ''
        return 'число' in t or 'целое' in t or 'константа' in t
    
    def analyze(self, text):
        self.errors = []
       # self.error_count = 0
        
        if not text or not text.strip():
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return False, self.errors
        
        all_tokens, lex_errors = self.lexical_analyzer.analyze(text)
        self.tokens = all_tokens
        self.pos = 0
        
        self._parse()
        
        success = len(self.errors) == 0
        return success, self.errors
    
    def _parse(self):
        # 1. 'let'
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return
        
        if token.lexeme == 'let':
            self._next()
        else:
            self._add_error(token.lexeme, token.line, token.start_pos,
                           f"Ожидалось ключевое слово 'let', получено '{token.lexeme}'")
            self._next()
        
        # 2. Идентификатор
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Ожидался идентификатор")
            return
        
        if self._is_identifier(token):
            self._next()
        else:
            self._add_error(token.lexeme, token.line, token.start_pos,
                           f"Ожидался идентификатор, получено '{token.lexeme}'")
            self._next()
        
        # 3. '='
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Ожидался оператор '='")
            return
        
        if token.lexeme == '=':
            self._next()
        else:
            self._add_error(token.lexeme, token.line, token.start_pos,
                           f"Ожидался оператор '=', получено '{token.lexeme}'")
            # НЕ продвигаемся — может быть 'num'
        
        # 4. Путь
        self._parse_path()
        
        # 5. '('
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Ожидалась '('")
            return
        
        if token.lexeme == '(':
            self._next()
        else:
            self._add_error(token.lexeme, token.line, token.start_pos,
                           f"Ожидалась '(', получено '{token.lexeme}'")
            self._next()
        
        # 6. Первое число
        self._parse_number()
        
        # 7. ','
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Ожидалась ','")
            return
        
        if token.lexeme == ',':
            self._next()
        else:
            self._add_error(token.lexeme, token.line, token.start_pos,
                           f"Ожидалась ',', получено '{token.lexeme}'")
            self._next()
        
        # 8. Второе число
        self._parse_number()
        
        # 9. ')'
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Ожидалась ')'")
            return
        
        if token.lexeme == ')':
            self._next()
        else:
            self._add_error(token.lexeme, token.line, token.start_pos,
                           f"Ожидалась ')', получено '{token.lexeme}'")
            self._next()
        
        # 10. ';'
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Ожидался ';' (конец оператора)")
            return
        
        if token.lexeme == ';':
            self._next()
        else:
            self._add_error(token.lexeme, token.line, token.start_pos,
                           f"Ожидался ';', получено '{token.lexeme}'")
    
    def _parse_path(self):
        expected = ['num', '::', 'complex', '::', 'Complex', '::', 'new']
        error_occurred = False
        
        for exp in expected:
            token = self._get_token()
            if token is None:
                if not error_occurred:
                    self._add_error("", 1, 1, f"Ожидался '{exp}'")
                return
            
            if token.is_error:
                # Специальная обработка для одиночного ':' когда ожидается '::'
                # Если после ':' сразу идет '\\', считаем ошибкой '\\'
                if exp == '::' and token.lexeme == ':':
                    # Проверим следующий токен
                    next_pos = self.pos + 1
                    if next_pos < len(self.tokens) and self.tokens[next_pos].lexeme == '\\':
                        # Ошибка в обратном слеше
                        if not error_occurred:
                            self._add_error('\\', self.tokens[next_pos].line, self.tokens[next_pos].start_pos,
                                           f"Ожидалось '::', получилось '\\'")
                            error_occurred = True
                        # Пропускаем оба токена
                        self._next()  # пропускаем ':'
                        self._next()  # пропускаем '\\'
                        continue
                    else:
                        if not error_occurred:
                            self._add_error(token.lexeme, token.line, token.start_pos,
                                           f"Ожидалось '::', получено ':'")
                            error_occurred = True
                elif exp == '::' and token.lexeme == '\\':
                    if not error_occurred:
                        self._add_error(token.lexeme, token.line, token.start_pos,
                                       f"Ожидалось '::', получилось '\\'")
                        error_occurred = True
                else:
                    if not error_occurred:
                        self._add_error(token.lexeme, token.line, token.start_pos,
                                       f"Недопустимый символ: '{token.lexeme}'")
                        error_occurred = True
                self._next()
                continue
            
            if token.lexeme == exp:
                self._next()
            elif exp == '::' and token.lexeme == ':':
                if not error_occurred:
                    self._add_error(token.lexeme, token.line, token.start_pos,
                                   f"Ожидалось '::', получено ':'")
                    error_occurred = True
                self._next()
            else:
                if not error_occurred:
                    self._add_error(token.lexeme, token.line, token.start_pos,
                                   f"Ожидался '{exp}', получено '{token.lexeme}'")
                    error_occurred = True
                self._next()
    
    def _parse_number(self):
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Ожидалось число")
            return False
        
        lex = token.lexeme
        
        # Целое число (лексер объединил)
        if self._is_number_token(token):
            self._next()
            return True
        
        # '-' (отрицательное число)
        if lex == '-':
            self._next()
            token = self._get_token()
            if token is None:
                self._add_error("", 1, 1, "Ожидалась цифра после '-'")
                return False
            lex = token.lexeme
            
            if self._is_digit(lex):
                self._next()
                self._read_digits()
                return True
            elif lex == '.':
                self._add_error(lex, token.line, token.start_pos, "Ожидалась цифра после '-'")
                self._next()
                # Пропускаем до терминала
                self._skip_to_terminal()
                return False
            else:
                self._add_error(lex, token.line, token.start_pos, "Ожидалась цифра после '-'")
                return False
        
        # Цифра
        if self._is_digit(lex):
            self._next()
            self._read_digits()
            return True
        
        # Точка в начале числа (.1)
        if lex == '.':
            self._add_error(lex, token.line, token.start_pos, "Ожидалась цифра перед десятичной точкой")
            self._next()
            # Читаем цифры после точки как обычное число
            token = self._get_token()
            if token and self._is_digit(token.lexeme):
                self._next()
                self._read_digits()
            return True  # Всё равно продолжаем разбор
        
        # Не число
        self._add_error(lex, token.line, token.start_pos, f"Ожидалось число, получено '{lex}'")
        self._next()
        return False
    
    def _skip_to_terminal(self):
        """Пропустить токены до запятой, скобки или точки с запятой"""
        while True:
            token = self._get_token()
            if token is None:
                return
            if token.lexeme in {',', ')', ';'}:
                return
            self._next()
    
    def _read_digits(self):
        while True:
            token = self._get_token()
            if token is None:
                return
            lex = token.lexeme
            
            if self._is_digit(lex):
                self._next()
            elif lex == '.':
                self._next()
                token = self._get_token()
                if token is None:
                    return
                if self._is_digit(token.lexeme):
                    self._next()
                else:
                    # После точки НЕ цифра — ошибка
                    self._add_error(token.lexeme, token.line, token.start_pos,
                                   f"Ожидалась цифра, получено '{token.lexeme}'")
                    # Пропускаем до терминального символа
                    while True:
                        token = self._get_token()
                        if token is None:
                            return
                        if token.lexeme in {',', ')', ';'}:
                            return
                        self._next()
            elif lex in {',', ')', ';'}:
                return
            else:
                self._add_error(lex, token.line, token.start_pos,
                               f"Ожидалась цифра, получено '{lex}'")
                self._next()
                return