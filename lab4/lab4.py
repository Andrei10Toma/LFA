"""
Sfaturi de implementare:
- from lab2 import Dfa
- creati 3 obiecte Dfa pentru A3, A4 si A5, incepand de la string
- creati o clasa Lexer care primeste o lista de Dfa-uri si pentru fiecare un
nume
- creati metoda Lexer.longest_prefix care primeste un cuvant (string) si
gaseste cel mai lung prefix acceptat de 1 din Dfa-uri
- creati metoda Lexer.parse care tot apeleaza longest_prefix pana a consumat
tot cuvantul
"""

A3_text = """0
0 a 0
0 b 1
1 a 1
1 b 1
0"""
A4_text = """0
0 b 0
0 a 1
1 a 1
1 b 1
0"""
A5_text = """0
0 a 1
0 b 3
1 a 3
1 b 2
2 a 3
2 b 0
3 a 3
3 b 3
1"""

from typing import List
from lab1.Dfa import Dfa

class Lexer:
	dfa_list: List[Dfa] = []

	def __init__(self) -> None:
		self.dfa_list.append(Dfa(A3_text))
		self.dfa_list.append(Dfa(A4_text))
		self.dfa_list.append(Dfa(A5_text))
		pass

	def longest_prefix(word, self):
		pass

	def parse(word, self):
		pass