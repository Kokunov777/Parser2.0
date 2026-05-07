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

V_N = <START>, <LET>, <ID>, <EQUAL>, <OPEN>, <NUM1>, <COMMA>, <COMMA1>, <NUM2>, <COMMA2>, <COMMA3>, <NUM3>, <END>
letter = A | B | C | ... | Z | a | b | c | ... | z
digit = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
identifier — это идентификатор: имя типа или имя элемента перечисления.
```
Грамматика G[Z] для объявления комплексного числа на языке Rust является автоматной (тип 3) и относится к подклассу праволинейных автоматных грамматик. Это означает, что для неё существует детерминированный конечный автомат, который может быть эффективно реализован в виде программы-распознавателя.


# Схема автоматов 
[grammatic.drawio](https://github.com/user-attachments/files/27475948/grammatic.drawio)
<mxfile host="app.diagrams.net">
  <diagram name="Страница-1" id="z9eegi5GKCKqandDQPml">
    <mxGraphModel dx="2053" dy="997" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-12" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="160" y="100" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-1" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="START" vertex="1">
          <mxGeometry height="80" width="80" y="60" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-11" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="let" vertex="1">
          <mxGeometry height="30" width="60" x="90" y="60" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-14" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-13" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="320" y="100" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-13" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="LET" vertex="1">
          <mxGeometry height="80" width="80" x="160" y="60" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-15" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="letter" vertex="1">
          <mxGeometry height="30" width="60" x="240" y="60" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-22" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-16" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" target="AF-bvTOAn3FmN-8V7C8Z-21">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-16" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="ID" vertex="1">
          <mxGeometry height="80" width="80" x="320" y="60" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-17" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-16" style="curved=1;endArrow=classic;html=1;rounded=0;exitX=0;exitY=0;exitDx=0;exitDy=0;entryX=1;entryY=0;entryDx=0;entryDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-16" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <Array as="points">
              <mxPoint x="350" y="20" />
              <mxPoint x="390" y="30" />
            </Array>
            <mxPoint x="320" y="60" as="sourcePoint" />
            <mxPoint x="370" y="10" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-18" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="| &#39;_&#39;" vertex="1">
          <mxGeometry height="30" width="60" x="380" y="40" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-24" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-21" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="700" y="100" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-21" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="EQUAL" vertex="1">
          <mxGeometry height="80" width="80" x="450" y="60" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-23" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="=" vertex="1">
          <mxGeometry height="30" width="60" x="390" y="70" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-25" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="&#39;num::comlex::Comlex:::new&#39;" vertex="1">
          <mxGeometry height="30" width="60" x="580" y="70" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-27" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-26" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="740" y="220.0000000000001" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-26" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="OPEN" vertex="1">
          <mxGeometry height="80" width="80" x="700" y="60" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-28" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="(" vertex="1">
          <mxGeometry height="30" width="60" x="720" y="160" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-30" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-29" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="590" y="260" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-29" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="NUM1" vertex="1">
          <mxGeometry height="80" width="80" x="700" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-32" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="-" vertex="1">
          <mxGeometry height="30" width="60" x="620" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-36" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-33" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="430" y="260" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-33" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="NUM1" vertex="1">
          <mxGeometry height="80" width="80" x="510" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-35" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="450" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-39" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-38" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="280" y="260.0000000000001" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-58" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-38" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=1;exitDx=0;exitDy=0;entryX=1.001;entryY=0.602;entryDx=0;entryDy=0;entryPerimeter=0;" target="AF-bvTOAn3FmN-8V7C8Z-56">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="362" y="450" />
              <mxPoint x="250" y="450" />
              <mxPoint x="250" y="448" />
            </Array>
            <mxPoint x="150" y="450" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-38" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="INT1" vertex="1">
          <mxGeometry height="80" width="80" x="350" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-40" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="330" y="180" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-43" edge="1" parent="1" style="endArrow=classic;html=1;rounded=0;entryX=0.433;entryY=1.036;entryDx=0;entryDy=0;entryPerimeter=0;" target="AF-bvTOAn3FmN-8V7C8Z-38" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <mxPoint x="385" y="370" as="sourcePoint" />
            <mxPoint x="430" y="310" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-44" edge="1" parent="1" style="curved=1;endArrow=classic;html=1;rounded=0;exitX=1;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0;entryDx=0;entryDy=0;" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <Array as="points">
              <mxPoint x="430" y="190" />
              <mxPoint x="390" y="180" />
            </Array>
            <mxPoint x="418.2842712474619" y="231.7157287525382" as="sourcePoint" />
            <mxPoint x="361.7157287525381" y="231.7157287525381" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-45" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="." vertex="1">
          <mxGeometry height="30" width="60" x="290" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-46" edge="1" parent="1" style="endArrow=none;html=1;rounded=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-29" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <mxPoint x="740" y="380" as="sourcePoint" />
            <mxPoint x="750" y="310" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-47" edge="1" parent="1" style="endArrow=none;html=1;rounded=0;" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <mxPoint x="380" y="370" as="sourcePoint" />
            <mxPoint x="740" y="370" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-48" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="510" y="340" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-50" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-49" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="140" y="260" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-49" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="FLOAT" vertex="1">
          <mxGeometry height="80" width="80" x="200" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-51" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="140" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-53" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-52" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="100" y="400" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-52" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="REM1" vertex="1">
          <mxGeometry height="80" width="80" x="60" y="220" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-54" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-52" style="curved=1;endArrow=classic;html=1;rounded=0;exitX=1;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0;entryDx=0;entryDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-52" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <Array as="points">
              <mxPoint x="140" y="180" />
              <mxPoint x="100" y="180" />
            </Array>
            <mxPoint x="90" y="200" as="sourcePoint" />
            <mxPoint x="140" y="150" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-55" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="40" y="160" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-60" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-56" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="100" y="590" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-56" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="NUM2" vertex="1">
          <mxGeometry height="80" width="80" x="60" y="400" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-57" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="," vertex="1">
          <mxGeometry height="30" width="60" x="50" y="330" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-59" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="," vertex="1">
          <mxGeometry height="30" width="60" x="320" y="330" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-61" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="-" vertex="1">
          <mxGeometry height="30" width="60" x="50" y="510" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-63" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-62" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="100" y="780" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-62" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="NUM2" vertex="1">
          <mxGeometry height="80" width="80" x="60" y="590" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-64" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="50" y="700" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-71" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-65" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="210" y="820" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-80" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-65" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0;entryDx=0;entryDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-79">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="100" y="890" />
              <mxPoint x="212" y="890" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-65" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="INT2" vertex="1">
          <mxGeometry height="80" width="80" x="60" y="780" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-67" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;rotation=-84;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="-10" y="590" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-68" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-56" style="curved=1;endArrow=classic;html=1;rounded=0;exitX=0;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0;entryDx=0;entryDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-65" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <Array as="points">
              <mxPoint x="50" y="570" />
              <mxPoint x="20" y="550" />
            </Array>
            <mxPoint x="20" y="600" as="sourcePoint" />
            <mxPoint x="70" y="550" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-69" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-65" style="curved=1;endArrow=classic;html=1;rounded=0;entryX=0;entryY=1;entryDx=0;entryDy=0;exitX=0;exitY=0;exitDx=0;exitDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-65" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <Array as="points">
              <mxPoint x="30" y="800" />
              <mxPoint x="10" y="830" />
            </Array>
            <mxPoint x="10" y="880" as="sourcePoint" />
            <mxPoint x="60" y="830" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-70" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" y="770" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-72" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="." vertex="1">
          <mxGeometry height="30" width="60" x="150" y="780" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-74" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-73" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="350" y="820" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-73" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="FLOAT2" vertex="1">
          <mxGeometry height="80" width="80" x="210" y="780" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-75" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="290" y="780" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-81" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-76" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-79">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-76" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="REM2" vertex="1">
          <mxGeometry height="80" width="80" x="350" y="780" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-77" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-76" style="curved=1;endArrow=classic;html=1;rounded=0;exitX=0;exitY=0;exitDx=0;exitDy=0;entryX=1;entryY=0;entryDx=0;entryDy=0;" target="AF-bvTOAn3FmN-8V7C8Z-76" value="">
          <mxGeometry height="50" relative="1" width="50" as="geometry">
            <Array as="points">
              <mxPoint x="370" y="730" />
              <mxPoint x="410" y="740" />
            </Array>
            <mxPoint x="410" y="750" as="sourcePoint" />
            <mxPoint x="460" y="700" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-78" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="digit" vertex="1">
          <mxGeometry height="30" width="60" x="384" y="710" as="geometry" />
        </mxCell>
        <mxCell id="tysQLCYBixiTIMQvKPhE-3" edge="1" parent="1" source="AF-bvTOAn3FmN-8V7C8Z-79" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" target="tysQLCYBixiTIMQvKPhE-2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-79" parent="1" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" value="CLOSE" vertex="1">
          <mxGeometry height="80" width="80" x="205" y="910" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-82" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value="(" vertex="1">
          <mxGeometry height="30" width="60" x="120" y="890" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-83" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value=")" vertex="1">
          <mxGeometry height="30" width="60" x="300" y="910" as="geometry" />
        </mxCell>
        <mxCell id="AF-bvTOAn3FmN-8V7C8Z-85" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;" value=";" vertex="1">
          <mxGeometry height="30" width="60" x="240" y="1000" as="geometry" />
        </mxCell>
        <mxCell id="tysQLCYBixiTIMQvKPhE-2" parent="1" style="ellipse;shape=doubleEllipse;whiteSpace=wrap;html=1;aspect=fixed;" value="END" vertex="1">
          <mxGeometry height="80" width="80" x="210" y="1050" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>




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
