# Лабораторная работа 3: Разработка синтаксического анализатора (парсера)

## Цель работы
Изучить назначение и принципы работы синтаксического анализатора в структуре компилятора. Спроектировать грамматику, построить соответствующую схему метода анализа грамматики и выполнить программную реализацию парсера с нейтрализацией синтаксических ошибок методом Айронса. Интегрировать разработанный модуль в ранее созданный графический интерфейс языкового процессора.

## Сведения об авторе
- **ФИО**: kokunov Andrey 
- **Группа**: АВТ 313
- **Дата**: 2026 год

## Постановка задачи
Разработать синтаксический анализатор (парсер) в соответствии с индивидуальным вариантом курсовой (расчетно-графической) работы, интегрировать его в приложение из лабораторной работы №1 и обеспечить наглядный вывод результатов анализа.

## Вариант задания: 
5. Объявление комплексного числа с инициализацией на языке Rust
let complex_num2 = num::complex::Complex::new(3.1, -4.2);

## Пример верных строк 
## primer 1  let complex_num2 = num::complex::Complex::new(3.1, -4.2);
<img width="759" height="455" alt="image" src="https://github.com/user-attachments/assets/1eabf992-45ec-42c2-9427-fbd29951f288" />

## primer 2 let x = Complex::new(1, 2);
<img width="819" height="445" alt="image" src="https://github.com/user-attachments/assets/854c0d84-5a3e-4d83-8eda-94bc063bb911" />

## primer 3 let z = std::math::Complex::new(0.0, -1.5);
<img width="1108" height="630" alt="image" src="https://github.com/user-attachments/assets/e961b46a-049a-47b3-baa2-c7be42efefad" />


## разработка грамматики:

```
<START> -> 'let' <LET>
<LET> -> letter <ID>
<ID> -> letter <ID>| digit <ID>| '_' <ID>| '=' <EQUAL>
<EQUAL> -> 'num::comlex::Comlex::new' <OPEN>
<OPEN> -> '(' <NUM1>
<NUM1> -> digit <COMMA> -> '.' <COMMA1> -> digit <COMMA1> -> ',' <NUM2> 
<NUM2> -> '-' <COMMA2> -> digit <COMMA3> -> '.' <COMMA3> -> digit <NUM3> 
<NUM3>-> ')' <END>
<END> -> ';'

```
## Терминальный словарь 
V_T = {a....z, A....Z, 0....9, =, (, ), ., ,, -, ;}

## Нетерминальный словарь
V_N = <START>, <LET>, <ID>, <EQUAL>, <OPEN>, <NUM1>, <COMMA>, <COMMA1>, <NUM2>, <COMMA2>, <COMMA3>, <NUM3>, <END>

Грамматика G[Z] для объявления комплексного числа на языке Rust является автоматной (тип 3) и относится к подклассу праволинейных автоматных грамматик. Это означает, что для неё существует детерминированный конечный автомат, который может быть эффективно реализован в виде программы-распознавателя.


# Схема автоматов 
<img width="797" height="443" alt="image" src="https://github.com/user-attachments/assets/4e7fd78c-e2de-4480-a132-e65f303df8a5" />



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
