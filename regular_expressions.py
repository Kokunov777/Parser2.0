"""
Модуль поиска подстрок с использованием регулярных выражений
Лабораторная работа №4

Варианты:
1. Годы между 2000 и 2010 — найти все вхождения годов от 2000 до 2010 включительно.
2. Номера карт Maestro Card — найти номера карт платежной системы Maestro.
3. IP-адрес (v4) с маской подсети — найти IPv4-адреса с указанием маски (например, 192.168.1.1/24).
"""

import re


class SearchResult:
    """Класс для хранения результата поиска"""
    def __init__(self, substring, line, start_pos, length):
        self.substring = substring          # Найденная подстрока
        self.line = line                    # Номер строки
        self.start_pos = start_pos          # Начальная позиция в строке
        self.length = length                # Длина подстроки


class RegularExpressionSearcher:
    """Класс для поиска подстрок с использованием регулярных выражений"""
    
    # Типы поиска
    SEARCH_YEARS = 0        # Годы 2000-2010
    SEARCH_MAESTRO = 1      # Номера карт Maestro
    SEARCH_IP_MASK = 2      # IPv4 с маской подсети
    
    SEARCH_NAMES = {
        0: "Годы 2000-2010",
        1: "Номера карт Maestro",
        2: "IPv4 адреса с маской подсети"
    }
    
    def __init__(self):
        self.results = []
        
        # Регулярные выражения для каждого типа поиска
        
        # 1. Годы между 2000 и 2010 включительно
        # Ищем числа от 2000 до 2010, которые не являются частью больших чисел
        self.pattern_years = re.compile(
            r'\b(200[0-9]|2010)\b'
        )
        
        # 2. Номера карт Maestro Card
        # Maestro: начинаются с 50, 56-58, 6xxxxx (длина 12-19 цифр)
        # Форматы: 50xxxx, 56xxxx-58xxxx, 6xxxxx
        self.pattern_maestro = re.compile(
            r'\b(?:5[0]|5[6-8]|6[0-9])\d{10,17}\b'
        )
        
        # 3. IPv4 адрес с маской подсети (например, 192.168.1.1/24)
        # Формат: xxx.xxx.xxx.xxx/xx
        self.pattern_ip_mask = re.compile(
            r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
            r'/(?:[0-9]|[12][0-9]|3[0-2])\b'
        )
    
    def search(self, text, search_type):
        """
        Поиск подстрок в тексте по заданному типу.
        
        Аргументы:
            text: исходный текст
            search_type: тип поиска (SEARCH_YEARS, SEARCH_MAESTRO, SEARCH_IP_MASK)
            
        Возвращает:
            список объектов SearchResult
        """
        self.results = []
        
        if not text:
            return self.results
        
        # Выбор шаблона в зависимости от типа поиска
        if search_type == self.SEARCH_YEARS:
            pattern = self.pattern_years
        elif search_type == self.SEARCH_MAESTRO:
            pattern = self.pattern_maestro
        elif search_type == self.SEARCH_IP_MASK:
            pattern = self.pattern_ip_mask
        else:
            return self.results
        
        # Разбиваем текст на строки
        lines = text.split('\n')
        
        # Поиск в каждой строке
        for line_num, line in enumerate(lines, 1):
            matches = pattern.finditer(line)
            
            for match in matches:
                substring = match.group()
                start_pos = match.start() + 1  # +1 для позиции с 1
                length = match.end() - match.start()
                
                result = SearchResult(substring, line_num, start_pos, length)
                self.results.append(result)
        
        return self.results
    
    def search_years(self, text):
        """
        Поиск годов от 2000 до 2010.
        
        Аргументы:
            text: исходный текст
            
        Возвращает:
            список объектов SearchResult
        """
        return self.search(text, self.SEARCH_YEARS)
    
    def search_maestro(self, text):
        """
        Поиск номеров карт Maestro.
        
        Аргументы:
            text: исходный текст
            
        Возвращает:
            список объектов SearchResult
        """
        return self.search(text, self.SEARCH_MAESTRO)
    
    def search_ip_mask(self, text):
        """
        Поиск IPv4 адресов с маской подсети.
        
        Аргументы:
            text: исходный текст
            
        Возвращает:
            список объектов SearchResult
        """
        return self.search(text, self.SEARCH_IP_MASK)
    
    def get_count(self):
        """Получить количество найденных совпадений"""
        return len(self.results)
    
    def get_results_as_dict(self):
        """
        Получить результаты в виде списка словарей.
        
        Возвращает:
            список словарей с ключами: substring, line, start_pos, length
        """
        return [
            {
                'substring': r.substring,
                'line': r.line,
                'start_pos': r.start_pos,
                'length': r.length
            }
            for r in self.results
        ]
    
    def highlight_text(self, text, search_type):
        """
        Подсветка найденных подстрок в тексте (HTML-форматирование).
        
        Аргументы:
            text: исходный текст
            search_type: тип поиска
            
        Возвращает:
            текст с HTML-подсветкой найденных фрагментов
        """
        if not text:
            return text
        
        if search_type == self.SEARCH_YEARS:
            pattern = self.pattern_years
        elif search_type == self.SEARCH_MAESTRO:
            pattern = self.pattern_maestro
        elif search_type == self.SEARCH_IP_MASK:
            pattern = self.pattern_ip_mask
        else:
            return text
        
        # Замена найденных подстрок на подсвеченные версии
        highlighted = pattern.sub(
            lambda m: f'<span style="background-color: #FFEB3B; font-weight: bold;">{m.group()}</span>',
            text
        )
        
        return highlighted
    
    def clear_results(self):
        """Очистить результаты поиска"""
        self.results = []


# Пример использования
if __name__ == "__main__":
    # Тестовый текст
    test_text = """
    Важные годы: 2000, 2005, 2010, а также 1999 и 2011.
    
    Номера карт Maestro:
    5012345678901234
    5612345678901234567
    6012345678901234
    
    IP-адреса с маской:
    192.168.1.1/24
    10.0.0.1/8
    172.16.0.1/16
    255.255.255.0/32
    """
    
    searcher = RegularExpressionSearcher()
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ПОИСКА ПО РЕГУЛЯРНЫМ ВЫРАЖЕНИЯМ")
    print("=" * 60)
    
    # Тест поиска годов
    print("\n1. ПОИСК ГОДОВ (2000-2010):")
    print("-" * 40)
    results = searcher.search_years(test_text)
    for result in results:
        print(f"  Найдено: '{result.substring}' - строка {result.line}, позиция {result.start_pos}, длина {result.length}")
    print(f"  Всего найдено: {searcher.get_count()}")
    
    # Тест поиска карт Maestro
    print("\n2. ПОИСК НОМЕРОВ КАРТ MAESTRO:")
    print("-" * 40)
    results = searcher.search_maestro(test_text)
    for result in results:
        print(f"  Найдено: '{result.substring}' - строка {result.line}, позиция {result.start_pos}, длина {result.length}")
    print(f"  Всего найдено: {searcher.get_count()}")
    
    # Тест поиска IP-адресов
    print("\n3. ПОИСК IP-АДРЕСОВ С МАСКОЙ:")
    print("-" * 40)
    results = searcher.search_ip_mask(test_text)
    for result in results:
        print(f"  Найдено: '{result.substring}' - строка {result.line}, позиция {result.start_pos}, длина {result.length}")
    print(f"  Всего найдено: {searcher.get_count()}")
    
    # Тест подсветки
    print("\n4. ПОДСВЕТКА ТЕКСТА (HTML):")
    print("-" * 40)
    highlighted = searcher.highlight_text(test_text, RegularExpressionSearcher.SEARCH_YEARS)
    print("HTML-разметка сгенерирована (длина текста: {} символов)".format(len(highlighted)))
    
    print("\n" + "=" * 60)
    print("Тестирование завершено успешно!")