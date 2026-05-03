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
LETTER → "a".."z" | "A".."Z" | "_"
DIGIT → "0".."9"

Метод анализа: нисходящий разбор (LL(1)) с нейтрализацией ошибок методом Айронса
"""

from lexical_analyzer import LexicalAnalyzer, Token


class SyntaxError:
    """Класс для хранения информации о синтаксической ошибке"""
    def __init__(self, fragment, line, position, description):
        self.fragment = fragment        # Неверный фрагмент
        self.line = line                # Номер строки
        self.position = position        # Позиция в строке
        self.description = description  # Описание ошибки


class SyntaxAnalyzer:
    """Синтаксический анализатор с методом нейтрализации ошибок Айронса"""
    
    def __init__(self):
        self.tokens = []
        self.current_pos = 0
        self.errors = []
        self.lexical_analyzer = LexicalAnalyzer()
        
        # Множества восстанавливающих символов для каждого нетерминала
        self.recovery_symbols = {
            'Z': {';'},           # После объявления - конец оператора
            'PATH': {'::', '(', ';'},  # Путь может продолжаться :: или закончиться
            'ARGS': {',', ')', ';'},   # Аргументы разделены запятой
            'NUM': {',', ')', ';'},    # Число заканчивается запятой или скобкой
        }
        
        # Ожидаемые символы для каждого нетерминала
        self.expected_symbols = {
            'Z': ['ключевое слово let'],
            'PATH': ['идентификатор'],
            'ARGS': ['число'],
            'NUM': ['число'],
        }
    
    def skip_non_essential(self):
        """Пропуск незначащих токенов (пробелы, переводы строк)"""
        while (self.current_pos < len(self.tokens) and 
               self.tokens[self.current_pos].token_type in ['разделитель (пробел)', 
                                                            'разделитель (новая строка)']):
            self.current_pos += 1
    
    def get_current_token(self):
        """Получение текущего токена с пропуском пробелов"""
        self.skip_non_essential()
        if self.current_pos < len(self.tokens):
            return self.tokens[self.current_pos]
        return None
    
    def get_token_value(self, token):
        """Получение значения токена для сравнения"""
        if token is None:
            return None
        return token.lexeme
    
    def get_token_type(self, token):
        """Получение типа токена"""
        if token is None:
            return None
        return token.token_type
    
    def match(self, expected_type=None, expected_value=None):
        """
        Проверка соответствия текущего токена ожидаемому.
        При успехе - переход к следующему токену.
        """
        self.skip_non_essential()
        
        if self.current_pos >= len(self.tokens):
            return None
        
        token = self.tokens[self.current_pos]
        
        # Пропускаем токены ошибок лексического анализатора
        if token.is_error:
            self.current_pos += 1
            return self.match(expected_type, expected_value)
        
        if expected_type and token.token_type != expected_type:
            return None
        
        if expected_value and token.lexeme != expected_value:
            return None
        
        self.current_pos += 1
        return token
    
    def add_error(self, fragment, line, position, description):
        """Добавление синтаксической ошибки"""
        error = SyntaxError(fragment, line, position, description)
        self.errors.append(error)
    
    def recover_to_symbols(self, recovery_set):
        """
        Метод Айронса: восстановление после ошибки.
        Пропускает токены до нахождения восстанавливающего символа.
        """
        while self.current_pos < len(self.tokens):
            token = self.tokens[self.current_pos]
            
            # Проверяем, является ли токен восстанавливающим символом
            if token.lexeme in recovery_set or token.token_type in recovery_set:
                return True
            
            self.current_pos += 1
        
        return False
    
    def parse_Z(self):
        """
        Разбор правила Z → "let" ID "=" PATH "::" "new" "(" ARGS ")" ";"
        """
        self.skip_non_essential()
        
        # Проверка ключевого слова "let"
        token = self.get_current_token()
        if token is None:
            self.add_error("", 0, 0, "Ожидалось ключевое слово 'let', но строка пуста")
            return False
        
        if token.lexeme != 'let':
            self.add_error(
                token.lexeme,
                token.line,
                token.start_pos,
                f"Ожидалось ключевое слово 'let', получено '{token.lexeme}'"
            )
            # Восстановление: ищем ';'
            self.recover_to_symbols(self.recovery_symbols['Z'])
            return False
        
        self.current_pos += 1  # Пропускаем 'let'
        
        # Проверка идентификатора
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.token_type != 'идентификатор':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидался идентификатор после 'let', получено '{token.lexeme}'"
                )
                self.recover_to_symbols(self.recovery_symbols['Z'])
            else:
                self.add_error("", 0, 0, "Ожидался идентификатор, но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем идентификатор
        
        # Проверка '='
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.lexeme != '=':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидался оператор '=', получено '{token.lexeme}'"
                )
                self.recover_to_symbols(self.recovery_symbols['Z'])
            else:
                self.add_error("", 0, 0, "Ожидался оператор '=', но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем '='
        
        # Разбор PATH
        if not self.parse_PATH():
            return False
        
        # Проверка '::'
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.lexeme != '::':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидался разделитель '::', получено '{token.lexeme}'"
                )
                self.recover_to_symbols(self.recovery_symbols['Z'])
            else:
                self.add_error("", 0, 0, "Ожидался разделитель '::', но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем '::'
        
        # Проверка 'new'
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.lexeme != 'new':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидалось ключевое слово 'new', получено '{token.lexeme}'"
                )
                self.recover_to_symbols(self.recovery_symbols['Z'])
            else:
                self.add_error("", 0, 0, "Ожидалось ключевое слово 'new', но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем 'new'
        
        # Проверка '('
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.lexeme != '(':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидалась открывающая скобка '(', получено '{token.lexeme}'"
                )
                self.recover_to_symbols({')', ';'})
            else:
                self.add_error("", 0, 0, "Ожидалась '(', но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем '('
        
        # Разбор ARGS
        if not self.parse_ARGS():
            return False
        
        # Проверка ')'
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.lexeme != ')':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидалась закрывающая скобка ')', получено '{token.lexeme}'"
                )
                # Пробуем восстановиться до ';'
                self.recover_to_symbols({';'})
            else:
                self.add_error("", 0, 0, "Ожидалась ')', но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем ')'
        
        # Проверка ';'
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.lexeme != ';':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидался конец оператора ';', получено '{token.lexeme}'"
                )
            else:
                self.add_error("", 0, 0, "Ожидался ';' в конце объявления")
            return False
        
        self.current_pos += 1  # Пропускаем ';'
        
        return True
    
    def parse_PATH(self):
        """Разбор правила PATH → ID ("::" ID)*"""
        self.skip_non_essential()
        
        # Первый идентификатор обязателен
        token = self.get_current_token()
        if token is None or token.token_type != 'идентификатор':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидался идентификатор в пути, получено '{token.lexeme}'"
                )
                self.recover_to_symbols(self.recovery_symbols['PATH'])
            else:
                self.add_error("", 0, 0, "Ожидался идентификатор в пути, но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем идентификатор
        
        # Цикл обработки "::" ID
        while True:
            self.skip_non_essential()
            
            if self.current_pos >= len(self.tokens):
                break
            
            token = self.tokens[self.current_pos]
            
            # Проверяем, продолжается ли путь
            if token.lexeme == '::':
                self.current_pos += 1  # Пропускаем '::'
                
                self.skip_non_essential()
                next_token = self.get_current_token()
                
                if next_token is None or next_token.token_type != 'идентификатор':
                    if next_token:
                        self.add_error(
                            next_token.lexeme,
                            next_token.line,
                            next_token.start_pos,
                            f"Ожидался идентификатор после '::', получено '{next_token.lexeme}'"
                        )
                        self.recover_to_symbols(self.recovery_symbols['PATH'])
                    else:
                        self.add_error("", 0, 0, "Ожидался идентификатор после '::', но строка закончилась")
                    return False
                
                self.current_pos += 1  # Пропускаем идентификатор
            else:
                break
        
        return True
    
    def parse_ARGS(self):
        """Разбор правила ARGS → NUM "," NUM"""
        # Первое число
        if not self.parse_NUM():
            return False
        
        # Запятая
        self.skip_non_essential()
        token = self.get_current_token()
        if token is None or token.lexeme != ',':
            if token:
                self.add_error(
                    token.lexeme,
                    token.line,
                    token.start_pos,
                    f"Ожидалась запятая ',' между аргументами, получено '{token.lexeme}'"
                )
                self.recover_to_symbols({')', ';'})
            else:
                self.add_error("", 0, 0, "Ожидалась ',' между аргументами, но строка закончилась")
            return False
        
        self.current_pos += 1  # Пропускаем ','
        
        # Второе число
        if not self.parse_NUM():
            return False
        
        return True
    
    def parse_NUM(self):
        """Разбор правила NUM → ["-"] DIGITS ["." DIGITS]"""
        self.skip_non_essential()
        
        token = self.get_current_token()
        if token is None:
            self.add_error("", 0, 0, "Ожидалось число, но строка закончилась")
            return False
        
        # Проверка, что токен - число
        if 'число' not in token.token_type and 'константа' not in token.token_type:
            self.add_error(
                token.lexeme,
                token.line,
                token.start_pos,
                f"Ожидалось число, получено '{token.lexeme}'"
            )
            self.recover_to_symbols(self.recovery_symbols['NUM'])
            return False
        
        # Дополнительная проверка чисел с плавающей точкой
        lexeme = token.lexeme
        
        # Проверка на точку без цифр перед ней
        if lexeme.startswith('.'):
            self.add_error(
                lexeme,
                token.line,
                token.start_pos,
                f"Ожидалась цифра перед десятичной точкой в '{lexeme}'"
            )
            self.current_pos += 1
            return False
        
        # Проверка на точку без цифр после неё
        if lexeme.endswith('.'):
            self.add_error(
                lexeme,
                token.line,
                token.start_pos,
                f"Ожидалась цифра после десятичной точки в '{lexeme}'"
            )
            self.current_pos += 1
            return False
        
        # Проверка на множественные точки
        if lexeme.count('.') > 1:
            self.add_error(
                lexeme,
                token.line,
                token.start_pos,
                f"Некорректное число: множественные десятичные точки в '{lexeme}'"
            )
            self.current_pos += 1
            return False
        
        # Проверка на отрицательный ноль (допустимо)
        if lexeme == '-0' or lexeme == '-0.0':
            # Спорный случай, считаем допустимым
            pass
        
        self.current_pos += 1  # Пропускаем число
        return True
    
    def analyze(self, text):
        """
        Главный метод анализа.
        Возвращает (success, errors) - флаг успеха и список ошибок.
        """
        self.errors = []
        
        if not text or not text.strip():
            self.add_error("", 0, 0, "Пустая строка для анализа")
            return False, self.errors
        
        # Сначала выполняем лексический анализ
        self.tokens, lexical_errors = self.lexical_analyzer.analyze(text)
        self.current_pos = 0
        
        # Добавляем лексические ошибки
        for err in lexical_errors:
            self.add_error(
                err['char'],
                err['line'],
                err['position'],
                f"Лексическая ошибка: {err['message']}"
            )
        
        # Запускаем синтаксический разбор
        success = self.parse_Z()
        
        # Проверяем, остались ли неразобранные токены
        self.skip_non_essential()
        if self.current_pos < len(self.tokens):
            remaining = self.tokens[self.current_pos]
            if not remaining.is_error:
                self.add_error(
                    remaining.lexeme,
                    remaining.line,
                    remaining.start_pos,
                    f"Неожиданный токен '{remaining.lexeme}' после конца объявления"
                )
                success = False
        
        return success and len(self.errors) == 0, self.errors