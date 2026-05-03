"""
Лексический анализатор для объявления комплексного числа на языке Rust
Вариант 5: Объявление комплексного числа с инициализацией
"""


class Token:
    """Класс для хранения информации о лексеме"""
    def __init__(self, code, token_type, lexeme, line, start_pos, end_pos):
        self.code = code          # Условный код
        self.token_type = token_type  # Тип лексемы
        self.lexeme = lexeme      # Лексема
        self.line = line          # Номер строки
        self.start_pos = start_pos    # Начальная позиция в строке
        self.end_pos = end_pos        # Конечная позиция в строке
        self.is_error = False     # Флаг ошибки


class LexicalAnalyzer:
    """Лексический анализатор (сканер) для Rust-подобного синтаксиса"""
    
    # Словарь кодов лексем
    TOKEN_CODES = {
        'KEYWORD_LET': 1,        # Ключевое слово let
        'IDENTIFIER': 2,         # Идентификатор
        'ASSIGN': 10,            # Оператор присваивания =
        'DOUBLE_COLON': 4,       # Разделитель ::
        'KEYWORD_NEW': 3,        # Ключевое слово new (можно заменить на другой код)
        'OPEN_PAREN': 8,         # Открывающая скобка (
        'CLOSE_PAREN': 9,        # Закрывающая скобка )
        'FLOAT_LITERAL': 1,      # Число с плавающей точкой (условный код 1 для чисел)
        'INTEGER_LITERAL': 1,    # Целое число (условный код 1 как в примере)
        'COMMA': 12,             # Разделитель запятая
        'MINUS': 13,             # Оператор минус
        'DOT': 4,                # Точка как разделитель пути
        'SEMICOLON': 14,         # Конец оператора ;
        'WHITESPACE': 11,        # Разделитель (пробел)
        'ERROR': 99              # Ошибка
    }
    
    # Ключевые слова языка
    KEYWORDS = {
        'let', 'use', 'new', 'as', 'mut', 'fn', 
        'pub', 'struct', 'enum', 'impl', 'trait'
    }
    
    # Известные модули
    MODULES = {'num', 'complex', 'Complex', 'std', 'core', 'alloc'}
    
    def __init__(self):
        self.tokens = []
        self.errors = []
    
    def is_letter(self, char):
        """Проверка: буква или подчеркивание"""
        return char.isalpha() or char == '_'
    
    def is_digit(self, char):
        """Проверка: цифра"""
        return char.isdigit()
    
    def is_alphanumeric(self, char):
        """Проверка: буква, цифра или подчеркивание"""
        return self.is_letter(char) or self.is_digit(char)
    
    def analyze(self, text):
        """
        Анализ входного текста и выделение лексем.
        
        Аргументы:
            text: строка с исходным кодом
            
        Возвращает:
            кортеж (tokens, errors)
        """
        self.tokens = []
        self.errors = []
        
        if not text:
            return self.tokens, self.errors
        
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            col = 0
            while col < len(line):
                char = line[col]
                
                # Пропуск пробелов и табуляций
                if char in ' \t':
                    whitespace_start = col
                    while col < len(line) and line[col] in ' \t':
                        col += 1
                    lexeme = line[whitespace_start:col]
                    display_lexeme = '(пробел)' if lexeme == ' ' else lexeme
                    self.tokens.append(Token(
                        self.TOKEN_CODES['WHITESPACE'],
                        'разделитель (пробел)',
                        display_lexeme,
                        line_num,
                        whitespace_start + 1,
                        col
                    ))
                    continue
                
                # Идентификаторы и ключевые слова
                if self.is_letter(char):
                    start = col
                    while col < len(line) and self.is_alphanumeric(line[col]):
                        col += 1
                    lexeme = line[start:col]
                    
                    # Определение типа лексемы
                    if lexeme == 'let':
                        token_code = self.TOKEN_CODES['KEYWORD_LET']
                        token_type = 'ключевое слово'
                    elif lexeme == 'new' or lexeme == 'use':
                        token_code = self.TOKEN_CODES['KEYWORD_NEW'] if lexeme == 'new' else self.TOKEN_CODES['KEYWORD_LET']
                        token_type = 'ключевое слово'
                    elif lexeme in self.MODULES:
                        token_code = self.TOKEN_CODES['IDENTIFIER']
                        token_type = 'идентификатор'
                    else:
                        token_code = self.TOKEN_CODES['IDENTIFIER']
                        token_type = 'идентификатор'
                    
                    self.tokens.append(Token(
                        token_code,
                        token_type,
                        lexeme,
                        line_num,
                        start + 1,
                        col
                    ))
                    continue
                
                # Числа (целые и с плавающей точкой)
                if self.is_digit(char) or (char == '-' and col + 1 < len(line) and self.is_digit(line[col + 1])):
                    start = col
                    has_dot = False
                    
                    # Обработка знака минус
                    if char == '-':
                        col += 1
                    
                    # Сбор цифр и точки
                    while col < len(line) and (self.is_digit(line[col]) or line[col] == '.'):
                        if line[col] == '.':
                            if has_dot:
                                break  # Вторая точка - ошибка
                            has_dot = True
                        col += 1
                    
                    lexeme = line[start:col]
                    
                    # Определение типа числа
                    if has_dot:
                        token_code = self.TOKEN_CODES['FLOAT_LITERAL']
                        token_type = 'целое без знака' if not lexeme.startswith('-') else 'число с плавающей точкой'
                    else:
                        token_code = self.TOKEN_CODES['INTEGER_LITERAL']
                        token_type = 'целое без знака' if not lexeme.startswith('-') else 'целое число'
                    
                    self.tokens.append(Token(
                        token_code,
                        token_type,
                        lexeme,
                        line_num,
                        start + 1,
                        col
                    ))
                    continue
                
                # Оператор присваивания =
                if char == '=':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['ASSIGN'],
                        'оператор присваивания',
                        '=',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Двойное двоеточие ::
                if char == ':':
                    if col + 1 < len(line) and line[col + 1] == ':':
                        self.tokens.append(Token(
                            self.TOKEN_CODES['DOUBLE_COLON'],
                            'разделитель',
                            '::',
                            line_num,
                            col + 1,
                            col + 2
                        ))
                        col += 2
                    else:
                        self._add_error(line_num, col + 1, char)
                        col += 1
                    continue
                
                # Точка (разделитель пути)
                if char == '.':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['DOT'],
                        'разделитель',
                        '.',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Запятая
                if char == ',':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['COMMA'],
                        'разделитель',
                        ',',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Точка с запятой
                if char == ';':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['SEMICOLON'],
                        'конец оператора',
                        ';',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Открывающая скобка
                if char == '(':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['OPEN_PAREN'],
                        'разделитель',
                        '(',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Закрывающая скобка
                if char == ')':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['CLOSE_PAREN'],
                        'разделитель',
                        ')',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Оператор минус
                if char == '-':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['MINUS'],
                        'оператор',
                        '-',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Недопустимый символ
                self._add_error(line_num, col + 1, char)
                col += 1
        
        return self.tokens, self.errors
    
    def _add_error(self, line, pos, char):
        """Добавление информации об ошибке"""
        error_token = Token(
            self.TOKEN_CODES['ERROR'],
            'ОШИБКА',
            char,
            line,
            pos,
            pos
        )
        error_token.is_error = True
        self.tokens.append(error_token)
        self.errors.append({
            'line': line,
            'position': pos,
            'char': char,
            'message': f'Недопустимый символ: "{char}"'
        })
    
    def get_token_code_name(self, code):
        """Получение названия типа лексемы по коду"""
        code_names = {
            1: 'константа',
            2: 'идентификатор',
            3: 'ключевое слово new',
            4: 'разделитель',
            8: 'разделитель',
            9: 'разделитель',
            10: 'оператор присваивания',
            11: 'разделитель (пробел)',
            12: 'разделитель',
            13: 'оператор',
            14: 'конец оператора',
            99: 'ОШИБКА'
        }
        return code_names.get(code, 'неизвестный тип')