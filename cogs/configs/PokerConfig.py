'''
•	Список всех карт и эмоций к ним – как константа может храниться даже не в БД, а в коде в качестве переменной; # конфиг с азартными играми в общем
•	ID каналов для логов также хранятся в коде, а не БД; # конфиг с ID
•	Малый блайнд вычисляется как: малый блайнд = большой блайнд / 2; # конфиг с покером
•	Название всех раундов будет в виде списка [не начата, начало, пре-флоп, флоп, тёрн, ривер], чтобы изменять название актуального раунда в БД; # конфиг с покером
•	ЗП фиксированная записана в коде, а не в бд. Все коэффициенты тоже там; # конфиг с азартными играми в общем или работой
•	Возможно, какие-то комбинации карт для определения победителя (не помню, как делал в джуни); # конфиг с покером
'''