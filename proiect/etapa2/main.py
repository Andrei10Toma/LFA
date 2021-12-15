from os import EX_SOFTWARE
import sys

from parse_prenex_regex import create_expr, Expr
from nfa import Nfa

if __name__ == '__main__':
    input_file_path: str = sys.argv[1]
    output_file_path: str = sys.argv[2]
    input_file = open(input_file_path)
    output_file = open(output_file_path)
    expression_string = input_file.read()
    expression: Expr = create_expr(expression_string)
    nfa: Nfa = expression.nfa
    print(expression)
    print(expression.nfa)
    # expression.nfa will have the final nfa created from the stack
    # convert the final nfa in the dfa
    nfa.compute_epsilon_enclosures()
