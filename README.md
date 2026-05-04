# Лабораторная работа 3: Разработка синтаксического анализатора (парсера)

## Цель работы
Изучить назначение и принципы работы синтаксического анализатора в структуре компилятора. Спроектировать грамматику, построить соответствующую схему метода анализа грамматики и выполнить программную реализацию парсера с нейтрализацией синтаксических ошибок методом Айронса. Интегрировать разработанный модуль в ранее созданный графический интерфейс языкового процессора.

## Сведения об авторе
- **ФИО**: kokunov Andrey 
- **Группа**: АВТ 313
- **Дата**: 2026 год

## Постановка задачи
Разработать синтаксический анализатор (парсер) в соответствии с индивидуальным вариантом курсовой (расчетно-графической) работы, интегрировать его в приложение из лабораторной работы №1 и обеспечить наглядный вывод результатов анализа.

## Вариант задания: Номер варианта,
**Вариант 5**: Объявление комплексного числа с инициализацией на языке Rust

## Текстовое описание
Разработать синтаксический анализатор для конструкции объявления комплексного числа в языке Rust.

Синтаксис конструкции:
`let complex_num2 = num::complex::Complex::new(3.1, -4.2);`

 <img width="815" height="808" alt="image" src="https://github.com/user-attachments/assets/41ea0615-954c-4885-8455-7c9316214da8" />
               
## его текстовое описание 2–3 примера корректных входных строк для данного варианта и перечень допустимых лексем.
`let x = 123;`
<img width="511" height="441" alt="image" src="https://github.com/user-attachments/assets/e7ac4397-a654-423e-91cc-458577dea517" />

`let c = std::complex::Complex::new(0.0, 1.0);`
<img width="655" height="806" alt="image" src="https://github.com/user-attachments/assets/5b2b8259-4dd3-48e0-837f-e61db6eddbd3" />


# таблица лексемы 
<img width="725" height="566" alt="image" src="https://github.com/user-attachments/assets/824e97b3-1968-40c0-91a4-0de98c2a188e" />
<img width="738" height="331" alt="image" src="https://github.com/user-attachments/assets/363fabbf-cb25-436d-8600-2fa2074c8e75" />


## Разработка грамматики
`G[Z] = (VT, VN, Z, P)`

Терминалы (VT)
`V_T = { let, =, ;, ::, ,, (, ), -, num, complex, Complex, new, INTEGER, FLOAT }`

Нетерминалы (V<sub>N</sub>)
`V_N = { <program>, <statement>, <let_statement>, <var_ident>, 
        <complex_creation>, <path_expr>, <path_segment>, 
        <call_expr>, <arg_list>, <arg>, <float_literal> }`
        
Начальный символ (Z)
`Z = <program>`

1.  <program>        → <statement> | <statement> <program>
2.  <statement>      → <let_statement> ';'
3.  <let_statement>  → 'let' <var_ident> '=' <complex_creation>
4.  <var_ident>      → IDENT
5.  <complex_creation> → <path_expr> <call_expr>
6.  <path_expr>      → <path_segment> { '::' <path_segment> }
7.  <path_segment>   → 'num' | 'complex' | 'Complex' | 'new'
8.  <call_expr>      → '(' <arg_list> ')'
9.  <arg_list>       → <arg> { ',' <arg> }
10. <arg>            → <float_literal>
11. <float_literal>  → [ '-' ] FLOAT_LIT

# Классификация грамматики (по Хомскому)
Грамматика G[Z] является контекстно-свободной (КС, тип 2 по Хомскому).

Обоснование:
Все правила имеют вид A → α, где A ∈ VN, α ∈ V*

Нет правил вида αAβ → αγβ (характерных для КЗ-грамматик)

Есть рекурсивные правила для обработки списков

Грамматика не является регулярной (тип 3) из-за наличия вложенных скобок

Подкласс: LL(1)
Нет левой рекурсии

FIRST-множества альтернатив не пересекаются

# Возможно построение анализатора методом рекурсивного спуска
 parse_program() → while lookahead != EOF: parse_statement()
                       │
                       ▼
parse_statement() → parse_let_statement(); match(SEMICOLON)
                       │
                       ▼
parse_let_statement() → match(KW_LET); parse_var_ident(); 
                        match(ASSIGN); parse_complex_creation()
                       │
                       ▼
parse_complex_creation() → parse_path_expr(); parse_call_expr()
                       │
                       ▼
parse_path_expr() → parse_path_segment(); while PATH_SEP: 
                    match(PATH_SEP); parse_path_segment()
                       │
                       ▼
parse_call_expr() → match(LPAREN); parse_arg_list(); match(RPAREN)
                       │
                       ▼
parse_arg_list() → parse_arg(); while COMMA: 
                   match(COMMA); parse_arg()

# Диагностика и нейтрализация синтаксических ошибок.
Типы диагностируемых ошибок
| № | Тип ошибки                    | Сообщение                                  |
|----|-------------------------------|--------------------------------------------|
| 1  | Отсутствует let               | "Ожидается 'let'"                          |
| 2  | Отсутствует идентификатор     | "Ожидается идентификатор переменной"       |
| 3  | Отсутствует =                 | "Ожидается '='"                            |
| 4  | Неверный разделитель пути     | "Ожидается '::'"                           |
| 5  | Неверный сегмент пути         | "Ожидается 'num', 'complex', 'Complex' или 'new'" |
| 6  | Отсутствует (                 | "Ожидается '('"                            |
| 7  | Отсутствует )                 | "Ожидается ')'"                            |
| 8  | Неверный формат аргумента     | "Ожидается вещественное число"             |
| 9  | Отсутствует ,                 | "Ожидается ','"                            |
| 10 | Отсутствует ;                 | "Ожидается ';'"                            |
| 11 | Неизвестный символ            | "Недопустимый символ"                      |

# Тестовые примеры (скриншоты интерфейса программы, примеры анализа конкретных строк в программе).
# test 1 
<img width="435" height="193" alt="image" src="https://github.com/user-attachments/assets/5086fad4-0840-4814-b03d-8a484ef428de" />

# test 2
<img width="624" height="247" alt="image" src="https://github.com/user-attachments/assets/8e8f8e57-0d57-4f72-bb5c-56aaa3e344d7" />

# test 3
<img width="662" height="653" alt="image" src="https://github.com/user-attachments/assets/cf17e55a-eabe-4238-8cd5-d5e9919bf24e" />
#
