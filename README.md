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
формальные определение грамматики 

Z      → "let" ID "=" PATH "::" "new" "(" ARGS ")" ";"

PATH   → ID ("::" ID)*

ARGS   → NUM "," NUM

NUM    → ["-"] DIGITS ["." DIGITS]

ID     → LETTER (LETTER | DIGIT | "_")*

DIGITS → DIGIT+

LETTER → "a".."z" | "A".."Z" | "_"

DIGIT  → "0".."9"


## Терминалы (VT)
<img width="580" height="458" alt="image" src="https://github.com/user-attachments/assets/d95295ed-e5a5-44d0-a0bf-f274ffe8e4f0" />

## Нетерминалы (VN)
<img width="566" height="380" alt="image" src="https://github.com/user-attachments/assets/ad129ef2-d134-4382-bc8a-3142ce9d7b48" />


# Классификация грамматики (по Хомскому)
Тип 2 — Контекстно-свободная грамматика (КС-грамматика)

Все правила имеют форму A → α, где:

A — один нетерминальный символ

α — цепочка из терминалов и нетерминалов (может быть пустой)

# метод анализа
## Схема рекурсивного спуска (РС)
<img width="478" height="1199" alt="hLJ1RX9H5DsJy0ytpmrO5sfqmuHO8xHXeGjRDuYBKHxjXEaRCZF4n5N1M6jeqeJ4fHhz0h2W26Nw2_VzWb_YUM_QIhKrCG4ItdltdNlFENVki1h5RXYtT_ni9cfwgkM6xWuzTryqjyAWhUeF0Zy8wTfQsNmN8NNPSDj-l1QeUCDx9UdMxSLR5THb95jqz-PYD7HLqqJl89hDn5xiI-BF-Ws" src="https://github.com/user-attachments/assets/6707b0e0-759b-476e-b7c5-995754f8701d" />

## Алгоритм синтаксического анализа
<img width="164" height="1121" alt="Диаграмма без названия drawio (5)" src="https://github.com/user-attachments/assets/39341fa7-136a-4d17-8cc0-02c9511cd556" />

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
