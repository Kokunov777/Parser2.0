"""
Модуль анализа арифметических выражений.
Реализует:
- Лексический анализ
- Синтаксический анализ методом рекурсивного спуска
- Генерацию тетрад (op, arg1, arg2, result)
- Преобразование в ПОЛИЗ и вычисление значения
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional, Union
from enum import Enum, auto


class TokenType(Enum):
    """Типы токенов для арифметических выражений"""
    NUMBER = auto()      # num
    IDENTIFIER = auto()  # id
    PLUS = auto()        # +
    MINUS = auto()       # -
    MUL = auto()         # *
    DIV = auto()         # /
    MOD = auto()         # %
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    EOF = auto()         # конец строки
    ERROR = auto()       # ошибочный токен


@dataclass
class Token:
    """Токен лексического анализатора"""
    type: TokenType
    value: str
    line: int = 1
    position: int = 0
    
    def __str__(self):
        return f"Token({self.type.name}, '{self.value}', pos={self.position})"
    
    @property
    def is_error(self) -> bool:
        return self.type == TokenType.ERROR


class LexicalError(Exception):
    """Ошибка лексического анализа"""
    def __init__(self, message: str, line: int = 1, position: int = 0):
        self.message = message
        self.line = line
        self.position = position
        super().__init__(self.message)


class SyntaxErrorExpr(Exception):
    """Ошибка синтаксического анализа"""
    def __init__(self, message: str, position: int = 0):
        self.message = message
        self.position = position
        super().__init__(self.message)


@dataclass
class Tetrad:
    """Тетрада (op, arg1, arg2, result)"""
    op: str
    arg1: str
    arg2: str
    result: str
    
    def __str__(self):
        return f"({self.op}, {self.arg1}, {self.arg2}, {self.result})"


class ExpressionAnalyzer:
    """
    Анализатор арифметических выражений.
    Грамматика:
        E → TA
        A → ε | + TA | - TA
        T → FB
        B → ε | * FB | / FB | % FB
        F → num | id | (E)
        id → letter {letter | digit | _}
        num → digit {digit}
    """
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.temp_counter: int = 0
        self.tetrads: List[Tetrad] = []
        self.errors: List[SyntaxErrorExpr] = []
        self.has_identifiers: bool = False  # флаг наличия идентификаторов
        self.current_token: Optional[Token] = None
        
    def get_temp_name(self) -> str:
        """Генерирует имя временной переменной"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def reset(self):
        """Сброс состояния анализатора"""
        self.pos = 0
        self.temp_counter = 0
        self.tetrads = []
        self.errors = []
        self.has_identifiers = False
    
    # ==================== Лексический анализ ====================
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Лексический анализ: разбивает входную строку на токены
        """
        tokens = []
        i = 0
        line = 1
        pos_in_line = 1
        
        while i < len(text):
            char = text[i]
            
            # Пропуск пробелов
            if char.isspace():
                if char == '\n':
                    line += 1
                    pos_in_line = 1
                else:
                    pos_in_line += 1
                i += 1
                continue
            
            # Идентификаторы (буква + буквы/цифры/_)
            if char.isalpha():
                start_pos = pos_in_line
                start = i
                while i < len(text) and (text[i].isalnum() or text[i] == '_'):
                    i += 1
                    pos_in_line += 1
                value = text[start:i]
                tokens.append(Token(TokenType.IDENTIFIER, value, line, start_pos))
                continue
            
            # Числа (только целые)
            if char.isdigit():
                start_pos = pos_in_line
                start = i
                while i < len(text) and text[i].isdigit():
                    i += 1
                    pos_in_line += 1
                value = text[start:i]
                tokens.append(Token(TokenType.NUMBER, value, line, start_pos))
                continue
            
            # Операторы и скобки
            if char == '+':
                tokens.append(Token(TokenType.PLUS, '+', line, pos_in_line))
                i += 1
                pos_in_line += 1
            elif char == '-':
                tokens.append(Token(TokenType.MINUS, '-', line, pos_in_line))
                i += 1
                pos_in_line += 1
            elif char == '*':
                tokens.append(Token(TokenType.MUL, '*', line, pos_in_line))
                i += 1
                pos_in_line += 1
            elif char == '/':
                tokens.append(Token(TokenType.DIV, '/', line, pos_in_line))
                i += 1
                pos_in_line += 1
            elif char == '%':
                tokens.append(Token(TokenType.MOD, '%', line, pos_in_line))
                i += 1
                pos_in_line += 1
            elif char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', line, pos_in_line))
                i += 1
                pos_in_line += 1
            elif char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', line, pos_in_line))
                i += 1
                pos_in_line += 1
            else:
                # Неверный символ
                tokens.append(Token(TokenType.ERROR, char, line, pos_in_line))
                i += 1
                pos_in_line += 1
        
        tokens.append(Token(TokenType.EOF, '', line, pos_in_line))
        return tokens
    
    # ==================== Синтаксический анализ (рекурсивный спуск) ====================
    
    def peek(self) -> Token:
        """Возвращает текущий токен без продвижения"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, '')
    
    def advance(self) -> Token:
        """Возвращает текущий токен и продвигается к следующему"""
        token = self.peek()
        if self.pos < len(self.tokens):
            self.pos += 1
        self.current_token = token
        return token
    
    def expect(self, expected_type: TokenType, error_msg: str = "") -> Token:
        """Ожидает токен определённого типа, иначе ошибка"""
        token = self.peek()
        if token.type == expected_type:
            return self.advance()
        
        if not error_msg:
            error_msg = f"Ожидался {expected_type.name}, получен {token.type.name} '{token.value}'"
        
        self.errors.append(SyntaxErrorExpr(
            error_msg,
            token.position if token else 0
        ))
        raise SyntaxErrorExpr(error_msg, token.position if token else 0)
    
    def parse(self, text: str) -> Tuple[bool, List[Tetrad], List[str], Optional[float]]:
        """
        Главный метод анализа.
        Возвращает: (успех, тетрады, список ошибок, результат вычисления или None)
        """
        self.reset()
        
        # Этап 1: Лексический анализ
        self.tokens = self.tokenize(text)
        
        # Проверяем на лексические ошибки
        lexical_errors = [t for t in self.tokens if t.is_error]
        if lexical_errors:
            for err in lexical_errors:
                self.errors.append(SyntaxErrorExpr(
                    f"Лексическая ошибка: неверный символ '{err.value}'",
                    err.position
                ))
            return False, [], [str(e) for e in self.errors], None
        
        # Проверяем, есть ли идентификаторы (для определения возможности вычисления)
        self.has_identifiers = any(t.type == TokenType.IDENTIFIER for t in self.tokens)
        
        # Этап 2: Синтаксический анализ
        try:
            result_var = self.parse_E()
            
            # Проверяем, что дошли до конца
            if self.peek().type != TokenType.EOF:
                token = self.peek()
                self.errors.append(SyntaxErrorExpr(
                    f"Лишние символы после выражения: '{token.value}'",
                    token.position
                ))
                return False, self.tetrads, [str(e) for e in self.errors], None
            
            # Этап 3: Генерация ПОЛИЗ и вычисление
            poliz = self.generate_poliz()
            
            result = None
            if not self.has_identifiers:
                result = self.evaluate_poliz(poliz)
            
            return True, self.tetrads, [], result
            
        except SyntaxErrorExpr as e:
            # Добавляем ошибку, если ещё не добавлена
            if not self.errors or self.errors[-1].message != e.message:
                self.errors.append(e)
            return False, [], [str(err) for err in self.errors], None
        except Exception as e:
            self.errors.append(SyntaxErrorExpr(f"Неожиданная ошибка: {str(e)}", 0))
            return False, [], [str(err) for err in self.errors], None
    
    # -------------------- Правила грамматики --------------------
    
    def parse_E(self) -> str:
        """E → TA"""
        result = self.parse_T()
        return self.parse_A(result)
    
    def parse_A(self, inherited: str) -> str:
        """A → ε | + TA | - TA"""
        token = self.peek()
        
        if token.type == TokenType.PLUS:
            self.advance()  # consume '+'
            right = self.parse_T()
            temp = self.get_temp_name()
            self.tetrads.append(Tetrad('+', inherited, right, temp))
            return self.parse_A(temp)
        
        elif token.type == TokenType.MINUS:
            self.advance()  # consume '-'
            right = self.parse_T()
            temp = self.get_temp_name()
            self.tetrads.append(Tetrad('-', inherited, right, temp))
            return self.parse_A(temp)
        
        else:
            # ε - пустая строка
            return inherited
    
    def parse_T(self) -> str:
        """T → FB"""
        result = self.parse_F()
        return self.parse_B(result)
    
    def parse_B(self, inherited: str) -> str:
        """B → ε | * FB | / FB | % FB"""
        token = self.peek()
        
        if token.type == TokenType.MUL:
            self.advance()  # consume '*'
            right = self.parse_F()
            temp = self.get_temp_name()
            self.tetrads.append(Tetrad('*', inherited, right, temp))
            return self.parse_B(temp)
        
        elif token.type == TokenType.DIV:
            self.advance()  # consume '/'
            right = self.parse_F()
            temp = self.get_temp_name()
            self.tetrads.append(Tetrad('/', inherited, right, temp))
            return self.parse_B(temp)
        
        elif token.type == TokenType.MOD:
            self.advance()  # consume '%'
            right = self.parse_F()
            temp = self.get_temp_name()
            self.tetrads.append(Tetrad('%', inherited, right, temp))
            return self.parse_B(temp)
        
        else:
            # ε - пустая строка
            return inherited
    
    def parse_F(self) -> str:
        """F → num | id | (E)"""
        token = self.peek()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            # Для чисел не создаём тетраду, возвращаем само значение
            return token.value
        
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            # Для идентификаторов не создаём тетраду, возвращаем имя
            return token.value
        
        elif token.type == TokenType.LPAREN:
            self.advance()  # consume '('
            result = self.parse_E()
            self.expect(TokenType.RPAREN, f"Ожидалась закрывающая скобка ')', позиция {self.peek().position}")
            return result
        
        elif token.type == TokenType.EOF:
            self.errors.append(SyntaxErrorExpr(
                "Неожиданный конец выражения: пропущен операнд",
                0
            ))
            raise SyntaxErrorExpr("Пропущен операнд", 0)
        
        else:
            self.errors.append(SyntaxErrorExpr(
                f"Неожиданный токен '{token.value}' (тип: {token.type.name}), ожидался операнд",
                token.position
            ))
            raise SyntaxErrorExpr(
                f"Неожиданный токен '{token.value}'",
                token.position
            )
    
    # ==================== Генерация ПОЛИЗ ====================
    
    def generate_poliz(self) -> List[str]:
        """
        Генерация ПОЛИЗ из тетрад.
        Используется алгоритм: обход тетрад в обратном порядке,
        замена временных переменных на соответствующие операции.
        """
        if not self.tetrads:
            # Если нет тетрад (только число или идентификатор), возвращаем его
            for token in self.tokens:
                if token.type in (TokenType.NUMBER, TokenType.IDENTIFIER):
                    return [token.value]
            return []
        
        # Строим отображение: временная переменная -> тетрада
        temp_to_tetrad = {}
        for t in self.tetrads:
            temp_to_tetrad[t.result] = t
        
        # Находим последнюю тетраду (корень дерева)
        last_temp = self.tetrads[-1].result
        
        # Рекурсивно разворачиваем в ПОЛИЗ
        return self._unfold_poliz(last_temp, temp_to_tetrad)
    
    def _unfold_poliz(self, var: str, temp_map: dict) -> List[str]:
        """Рекурсивное разворачивание временной переменной в ПОЛИЗ"""
        if var in temp_map:
            tetrad = temp_map[var]
            result = []
            
            # Разворачиваем левый операнд
            if tetrad.arg1 in temp_map:
                result.extend(self._unfold_poliz(tetrad.arg1, temp_map))
            else:
                result.append(tetrad.arg1)
            
            # Разворачиваем правый операнд
            if tetrad.arg2 in temp_map:
                result.extend(self._unfold_poliz(tetrad.arg2, temp_map))
            else:
                result.append(tetrad.arg2)
            
            # Добавляем операцию
            result.append(tetrad.op)
            
            return result
        else:
            return [var]
    
    # ==================== Вычисление значения ====================
    
    def evaluate_poliz(self, poliz: List[str]) -> float:
        """
        Вычисление значения выражения по ПОЛИЗ.
        Работает только для целых чисел.
        """
        stack = []
        
        for token in poliz:
            if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
                # Число (целое)
                stack.append(int(token))
            elif token in ('+', '-', '*', '/', '%'):
                if len(stack) < 2:
                    raise ValueError(f"Недостаточно операндов для операции '{token}'")
                
                b = stack.pop()
                a = stack.pop()
                
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        raise ZeroDivisionError("Деление на ноль")
                    stack.append(a // b)  # целочисленное деление
                elif token == '%':
                    if b == 0:
                        raise ZeroDivisionError("Деление на ноль при вычислении остатка")
                    stack.append(a % b)
            else:
                # Идентификатор - нельзя вычислить
                raise ValueError(f"Невозможно вычислить: идентификатор '{token}'")
        
        if len(stack) != 1:
            raise ValueError("Некорректное выражение в ПОЛИЗ")
        
        return stack[0]
    
    # ==================== Вспомогательные методы ====================
    
    def get_poliz_string(self, poliz: List[str]) -> str:
        """Возвращает строковое представление ПОЛИЗ"""
        return ' '.join(poliz)
    
    def get_tetrads_string(self) -> str:
        """Возвращает строковое представление тетрад"""
        return '\n'.join(str(t) for t in self.tetrads)
    
    def analyze_with_details(self, text: str) -> dict:
        """
        Полный анализ с подробными результатами.
        Возвращает словарь с результатами анализа.
        """
        success, tetrads, errors, result = self.parse(text)
        
        poliz = []
        poliz_str = ""
        eval_result = None
        
        if success:
            poliz = self.generate_poliz()
            poliz_str = self.get_poliz_string(poliz)
            
            if not self.has_identifiers:
                try:
                    eval_result = self.evaluate_poliz(poliz)
                except Exception as e:
                    eval_result = f"Ошибка вычисления: {str(e)}"
        
        return {
            'success': success,
            'tokens': self.tokens,
            'tetrads': self.tetrads,
            'tetrads_str': self.get_tetrads_string(),
            'poliz': poliz,
            'poliz_str': poliz_str,
            'errors': errors,
            'eval_result': eval_result,
            'has_identifiers': self.has_identifiers
        }


# ==================== Демонстрация ====================

def demo():
    """Демонстрация работы анализатора выражений"""
    analyzer = ExpressionAnalyzer()
    
    test_expressions = [
        "3 + 5 * 2",
        "(3 + 5) * 2",
        "10 - 4 / 2",
        "a + b * 3",
        "7 % 3 + 2",
        "3 + * 5",  # ошибка
        "(1 + 2",    # ошибка
        "x * (y + 5)",
    ]
    
    for expr in test_expressions:
        print(f"\n{'='*50}")
        print(f"Выражение: {expr}")
        print('='*50)
        
        result = analyzer.analyze_with_details(expr)
        
        if result['success']:
            print("✅ Анализ успешен")
            print(f"\nТетрады:")
            print(result['tetrads_str'])
            print(f"\nПОЛИЗ: {result['poliz_str']}")
            if result['eval_result'] is not None:
                print(f"Результат: {result['eval_result']}")
        else:
            print("❌ Анализ завершился с ошибками:")
            for err in result['errors']:
                print(f"  • {err}")


if __name__ == "__main__":
    demo()