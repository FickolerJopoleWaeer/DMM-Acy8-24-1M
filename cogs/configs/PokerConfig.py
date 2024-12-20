# PokerConfig.py


'''
•	Список всех карт и эмоций к ним – как константа может храниться даже не в БД, а в коде в качестве переменной; # конфиг с азартными играми в общем
•	ID каналов для логов также хранятся в коде, а не БД; # конфиг с ID
•	# Малый блайнд вычисляется как: малый блайнд = большой блайнд / 2; # конфиг с покером
•	Название всех раундов будет в виде списка [не начата, начало, пре-флоп, флоп, тёрн, ривер], чтобы изменять название актуального раунда в БД; # конфиг с покером
•	ЗП фиксированная записана в коде, а не в бд. Все коэффициенты тоже там; # конфиг с азартными играми в общем или работой
•	Возможно, какие-то комбинации карт для определения победителя; # конфиг с покером
'''

# Список всех карт и эмоций к ним – как константа может храниться даже не в БД, а в коде в качестве переменной; # конфиг с азартными играми в общем
Колода = [
    ['2♠', 'p', 2], ['2♥', 'c', 2], ['2♣', 'k', 2], ['2♦', 'b', 2],
    ['3♠', 'p', 3], ['3♥', 'c', 3], ['3♣', 'k', 3], ['3♦', 'b', 3],
    ['4♠', 'p', 4], ['4♥', 'c', 4], ['4♣', 'k', 4], ['4♦', 'b', 4],
    ['5♠', 'p', 5], ['5♥', 'c', 5], ['5♣', 'k', 5], ['5♦', 'b', 5],
    ['6♠', 'p', 6], ['6♥', 'c', 6], ['6♣', 'k', 6], ['6♦', 'b', 6],
    ['7♠', 'p', 7], ['7♥', 'c', 7], ['7♣', 'k', 7], ['7♦', 'b', 7],
    ['8♠', 'p', 8], ['8♥', 'c', 8], ['8♣', 'k', 8], ['8♦', 'b', 8],
    ['9♠', 'p', 9], ['9♥', 'c', 9], ['9♣', 'k', 9], ['9♦', 'b', 9],
    ['10♠','p',10], ['10♥','c',10], ['10♣','k',10], ['10♦','b',10],
    ['J♠', 'p',11], ['J♥', 'c',11], ['J♣', 'k',11], ['J♦', 'b',11],
    ['Q♠', 'p',12], ['Q♥', 'c',12], ['Q♣', 'k',12], ['Q♦', 'b',12],
    ['К♠', 'p',13], ['К♥', 'c',13], ['К♣', 'k',13], ['К♦', 'b',13],
    ['A♠', 'p',14], ['A♥', 'c',14], ['A♣', 'k',14], ['A♦', 'b',14]
]

# Название всех раундов в виде списка
Раунды: list[str] = ['не начата', 'начало', 'пре-флоп', 'флоп', 'тёрн', 'ривер']

# Названия всех комбинаций для каждой силы
названия_комбинаций = {
    0: "Старшая карта",
    1: "Пара",
    2: "Две пары",
    3: "Сет",
    4: "Стрит",
    5: "Флеш",
    6: "Фулл Хаус",
    7: "Каре",
    8: "Стрит Флеш",
    9: "Флеш Рояль"
}