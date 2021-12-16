from os import EX_SOFTWARE, sep
import sys

from parse_prenex_regex import create_expr, Expr
from nfa import Nfa
from dfa import Dfa

if __name__ == '__main__':
    input_file_path: str = sys.argv[1]
    output_file_path: str = sys.argv[2]
    input_file = open(input_file_path, 'r')
    output_file = open(output_file_path, 'w')
    expression_string = input_file.read()
    expression: Expr = create_expr(expression_string)
    nfa: Nfa = expression.nfa
    # print(expression)
    # expression.nfa will have the final nfa created from the stack
    # convert the final nfa in the dfa
    nfa.compute_epsilon_enclosures()
    dfa, number_of_states = nfa.compute_dfa()
    for character in dfa._alphabet:
        output_file.write(character)
    output_file.write('\n')
    output_file.write(str(number_of_states))
    output_file.write('\n')
    output_file.write(str(dfa.map_from_set_states_to_normal_state[dfa._initial_state]))
    output_file.write('\n')
    for final_state in dfa._final_states:
        output_file.write(str(dfa.map_from_set_states_to_normal_state[final_state]))
        output_file.write(' ')
    output_file.write('\n')
    for key, value in dfa._delta.items():
        output_file.write(f'{dfa.map_from_set_states_to_normal_state[key[0]]},\'{key[1]}\',{dfa.map_from_set_states_to_normal_state[value]}')
        output_file.write('\n')
