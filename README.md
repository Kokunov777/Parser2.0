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

G[Z] = { V_T, V_N, Z, P}

z = "let" let

let -> lettev id

id -> lettev id

digit id -> | '_' id '=' Eqaul

Equal -> 'num::complex::Complex::hew' OPEN

OPEN -> '(' NUMB

NUMB -> '3.1' digit

digit ->',' digit

digit ->  '-4.2' OPEN

OPEN -> ')' END

END -> ';'
## терминальные символы символ (V_T)
V_T = {let,  =,  num, ::, new, (, 3.1, -4.2, ), ;,)

## нетерминальный символ (V_N)
VN = {complex_num2, complex, Complex, }

# Классификация грамматики (по Хомскому)
Тип 2 — Контекстно-свободная грамматика (КС-грамматика)

Все правила имеют форму A → α, где:

A — один нетерминальный символ

α — цепочка из терминалов и нетерминалов (может быть пустой)

# метод анализа

## Алгоритм синтаксического анализа


# Диагностика и нейтрализация синтаксических ошибок.
Метод Айронса
Метод Айронса — это метод восстановления после синтаксических ошибок, который позволяет продолжить разбор после обнаружения ошибки, не прекращая анализ.

Принцип работы
При обнаружении ошибки:

Сохраняется информация об ошибке (фрагмент, позиция, описание)

Анализатор пропускает входные токены до нахождения "восстанавливающего" символа

После восстановления:

Разбор продолжается с найденной позиции

Это позволяет обнаружить несколько ошибок за один проход

#Пример диагностики 
1.`complex_num2 = num::complex::Complex::new(3.1, -4.2);`
<img width="674" height="289" alt="image" src="https://github.com/user-attachments/assets/4de41d0a-d28e-413a-a524-967f079ef5c5" />

2.`let x = Type::nw(1.0, 2.0);`
<img width="679" height="298" alt="image" src="https://github.com/user-attachments/assets/bb966cee-f556-4ebf-b92c-8393bdf081c4" />

3.`let x = Type::new(1.0, 2.0)`
<img width="748" height="278" alt="image" src="https://github.com/user-attachments/assets/79ae5fd5-bc15-4715-a19b-ddf322ac6842" />



# Тестовые примеры (скриншоты интерфейса программы, примеры анализа конкретных строк в программе).
# test 1 
<img width="819" height="336" alt="image" src="https://github.com/user-attachments/assets/7e3bac1c-3f59-48cd-8c61-7fa17b6abbec" />


# test 2
<img width="773" height="306" alt="image" src="https://github.com/user-attachments/assets/73495f47-9c22-47c2-b016-f480a54e2192" />


# test 3
<img width="759" height="348" alt="image" src="https://github.com/user-attachments/assets/5568a367-e445-432d-b10a-b6706cedccd4" />

# test 4
<img width="731" height="439" alt="image" src="https://github.com/user-attachments/assets/9bf20967-69dc-482d-8a37-56fa3be3bda7" />

# test 5
<img width="793" height="324" alt="image" src="https://github.com/user-attachments/assets/ce5706b6-90b6-4d36-a116-71e4a701d5ef" />

#test 6
<img width="698" height="300" alt="image" src="https://github.com/user-attachments/assets/d74dacb6-4011-4698-9f1a-59fcee2e9015" />

#test 7 
<img width="482" height="248" alt="image" src="https://github.com/user-attachments/assets/296e69e9-eeb1-404d-a1a1-83188fa35e24" />
