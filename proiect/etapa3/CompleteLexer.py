from typing import List, Tuple
from Lexer import runlexer
from dfa import Dfa, string_escape
from nfa import Nfa
from parse_prenex_regex import Expr, Symbol, Star, Plus, Concat, Union, create_expr
from string import ascii_lowercase
from ast import Expr, While, If, Assign, InstructionList , Node

def get_matching_bracket(s: str) -> int:
    brackets_stack:List[int] = []
    matching_position:int = -1
    for index, character in enumerate(s):
        if character == '(':
            brackets_stack.append(index)
        elif character == ')':
            brackets_stack.pop()
            matching_position = index
        if len(brackets_stack) == 0:
            return matching_position
    return matching_position

def parse_symbol(w: str, stack: List[Expr]) -> str:
    if len(w) == 0:
        return None

    if w[0] == '\'':
        stack.append(Symbol(w[1]))
        return w[3:]

    if w[0] == '[':
        if w[1:6] == 'a-z]+':
            expr: Union = Union(Symbol('a'), Symbol('b'))
            for character in ascii_lowercase[2:]:
                expr = Union(expr, Symbol(character))
            stack.append(expr)
            return w[6:]
        elif w[1:6] == '0-9]+':
            expr: Union = Union(Symbol('0'), Symbol('1'))
            for i in range(2, 10):
                expr = Union(expr, Symbol(str(i)))
            stack.append(expr)
            return w[6:]

    if w[0] != '|' and w[0] != '*' and w[0] != '(' and w[0] != ')' and w[0] != '+':
        stack.append(Symbol(w[0]))
        return w[1:]
    else:
        return None


def parse_plus(w: str, stack: List[Expr]) -> str:
    if len(w) == 0:
        return None
    
    if w[0] == '+':
        top: Expr = stack.pop()
        stack.append(Plus(top))
        return w[1:]
    else:
        return None


def parse_star(w: str, stack: List[Expr]) -> str:
    if len(w) == 0:
        return None
    
    if w[0] == '*':
        top: Expr = stack.pop()
        stack.append(Star(top))
        return w[1:]
    else:
        return None


def parse_union(w: str, stack: List[Expr]) -> str:
    if len(w) == 0:
        return None
    
    if w[0] == '|':
        top: Expr = stack.pop()
        stack.append(Union(top, None))
        return w[1:]
    else:
        return None


def parse_opened_bracket(w: str) -> str:
    if len(w) == 0:
        return None

    if w[0] == '(':
        return w[1:]
    else:
        return None


def parse_closed_bracket(w: str) -> str:
    if len(w) == 0:
        return None

    if w[0] == ')':
        return w[1:]
    else:
        return None


def parse_regex(regex: str, stack: List[Expr], parsed_regex_stack: List[Expr]):
    if regex == None or len(regex) == 0:
        return
    if regex != ';':
        regex_closed_bracket = parse_closed_bracket(regex)
        if regex_closed_bracket == None:
            regex_open_bracket = parse_opened_bracket(regex)
            if regex_open_bracket == None:
                # parse a symbol
                regex_symbol = parse_symbol(regex, stack)
                if regex_symbol != None:
                    # next to a symbol can be a star
                    regex_star = parse_star(regex_symbol, stack)
                    if regex_star == None:
                        # next to a symbol can be a plus
                        regex_plus = parse_plus(regex_symbol, stack)
                        if regex_plus == None:
                            # after a symbol can be an union
                            complete_union_expr(stack)
                            regex_union = parse_union(regex_symbol, stack)
                            if regex_union == None:
                                parse_regex(regex_symbol, stack, parsed_regex_stack)
                            else:
                                parse_regex(regex_union, stack, parsed_regex_stack)
                        else:
                            # after a symbol with plus can be an union
                            complete_union_expr(stack)
                            regex_union = parse_union(regex_plus, stack)
                            if regex_union == None:
                                parse_regex(regex_plus, stack, parsed_regex_stack)
                            else:
                                parse_regex(regex_union, stack, parsed_regex_stack)
                    else:
                        # after a symbol with star can be an union
                        complete_union_expr(stack)
                        regex_union = parse_union(regex_star, stack)
                        if regex_union == None:
                            parse_regex(regex_star, stack, parsed_regex_stack)
                        else:
                            parse_regex(regex_union, stack, parsed_regex_stack)
            else:
                # parse a new regex beacause a bracket is opened
                start_parse_regex(regex_open_bracket, parsed_regex_stack)
                # add the element to the stack of the regex with one depth lower
                stack.append(parsed_regex_stack.pop())
                regex_after_closed_bracket = regex_open_bracket[get_matching_bracket(regex):]
                regex_after_closed_bracket = regex_after_closed_bracket[1:] if regex_after_closed_bracket[0] == '*' or regex_after_closed_bracket[0] == '+' else regex_after_closed_bracket
                # parse the union if it is necessary
                complete_union_expr(stack)
                regex_union_2 = parse_union(regex_after_closed_bracket, stack)
                if regex_union_2 == None:    
                    parse_regex(regex_after_closed_bracket, stack, parsed_regex_stack)
                else:
                    parse_regex(regex_union_2, stack, parsed_regex_stack)
        else:
            # the regex between the bracket is parsed (the closed bracket is met)
            # concat the collected elements in the stack
            brackets_regex = concat_regex(stack)
            stack.append(brackets_regex)
            # add the star or the plus symbol if it is present
            regex_star_2 = parse_star(regex_closed_bracket, stack)
            if regex_star_2 == None:
                parse_plus(regex_closed_bracket, stack)
            parsed_regex_stack.append(stack.pop())
    else:
        brackets_regex = concat_regex(stack)
        parsed_regex_stack.append(brackets_regex)


def complete_union_expr(stack):
    if len(stack) >= 2:
        # the last element parsed from the regex
        top1 = stack.pop()
        # the possible union element
        top2 = stack.pop()
        if isinstance(top2, Union):
            if top2._expr2 == None:
                top2._expr2 = top1
                stack.append(top2)
            else:
                stack.append(top2)
                stack.append(top1)
        else:
            stack.append(top2)
            stack.append(top1)


def start_parse_regex(regex: str, parsed_regex_stack: List[Expr]):
    stack = []
    parse_regex(regex, stack, parsed_regex_stack)
    parsed_regex_stack = stack


def concat_regex(stack: List[Expr]) -> Expr:
    if len(stack) == 0:
        return None

    if len(stack) == 1:
        return stack.pop()

    top1: Expr = stack.pop(0)
    top2: Expr = stack.pop(0)
    concat_expr: Concat = Concat(top1, top2)
    
    if len(stack) > 0:
        while len(stack) != 0:
            top: Expr = stack.pop(0)
            new_concat_expr: Concat = Concat(concat_expr, top)
            concat_expr = new_concat_expr

    return concat_expr


def runcompletelexer(lexer, finput, foutput):
    dfas: List[Dfa] = []
    parsed_regex_stack: List[Expr] = []
    lexer_file = open(lexer, "r")
    lexer_lines = lexer_file.readlines()
    for lexer_line in lexer_lines:
        Nfa.number_of_states = 0
        space_index:int = lexer_line.index(' ')
        token: str = lexer_line[:space_index]
        regex: str = lexer_line[space_index + 1:]
        regex = regex[:-1]
        start_parse_regex(string_escape(regex), parsed_regex_stack)
        parsed_regex = concat_regex(parsed_regex_stack)
        expression:Expr = create_expr(parsed_regex.__str__())
        nfa: Nfa = expression.nfa
        nfa.compute_epsilon_enclosures()
        dfa, number_of_states = nfa.compute_dfa()
        dfa._token = token
        dfas.append(dfa)

    compute_lexemes(dfas, finput, foutput)
    lexer_file.close()


def get_matching_end(lines: List[List[Tuple[str, str]]]) -> int:
    stack = []
    if lines[0][0][0] == 'IF':
        for index, line in enumerate(lines):
            if line[0][0] == 'IF':
                stack.append(index)
            elif line[0][0] == 'FI':
                stack.pop()
            if len(stack) == 0:
                return index
    elif lines[0][0][0] == 'WHILE':
        for index, line in enumerate(lines):
            if line[0][0] == 'WHILE':
                stack.append(index)
            elif line[0][0] == 'OD':
                stack.pop()
            if len(stack) == 0:
                return index
    return -1


def get_matching_else(lines: List[List[Tuple[str, str]]]) -> int:
    stack = []
    if lines[0][0][0] == 'IF':
        for index, line in enumerate(lines):
            if line[0][0] == 'IF':
                stack.append(index)
            elif line[0][0] == 'ELSE':
                stack.pop()
            if len(stack) == 0:
                return index

def compute_lexemes(dfas: List[Dfa], input_file_word: str, output_file: str):
    with open('input_file_dfa.in', 'w+') as input_file_dfa: 
        counter: int = 0
        for dfa in dfas:
            counter += 1
            # write the alphabet
            for character in dfa._alphabet:
                if character != '\n':
                    input_file_dfa.write(character)
                else:
                    input_file_dfa.write('\\n')
            input_file_dfa.write('\n')
            # write the token
            input_file_dfa.write(dfa._token)
            input_file_dfa.write('\n')
            # write the initial state
            input_file_dfa.write(str(dfa.map_from_set_states_to_normal_state[dfa._initial_state]))
            input_file_dfa.write('\n')
            # write tranzitions
            for key, value in dfa._delta.items():
                if key[1] != '\n':
                    input_file_dfa.write(f'{dfa.map_from_set_states_to_normal_state[key[0]]},\'{key[1]}\',{dfa.map_from_set_states_to_normal_state[value]}')
                else:
                    input_file_dfa.write(f'{dfa.map_from_set_states_to_normal_state[key[0]]},\'\\n\',{dfa.map_from_set_states_to_normal_state[value]}')
                input_file_dfa.write('\n')
            # write the final states
            counter_final_states: int = 0
            for final_state in dfa._final_states:
                counter_final_states += 1
                input_file_dfa.write(str(dfa.map_from_set_states_to_normal_state[final_state]))
                if counter_final_states != len(dfa._final_states):
                    input_file_dfa.write(' ')
            if counter != len(dfas):
                input_file_dfa.write('\n\n')
    runlexer('input_file_dfa.in', input_file_word, output_file)


def parse_expression(expression: List[Tuple[str, str]], level: int) -> Expr:
    if len(expression) == 1:
        return Expr(level, 'i' if expression[0][0] == 'INTEGER' or expression[0][0] == 'NEGATIVEINTEGER' else 'v', expression[0][1])
    # search for EQUAL token or for GREATER token
    for index, token_tuple in enumerate(expression):
        if token_tuple[0] == 'EQUAL' or token_tuple[0] == 'GREATER':
            return Expr(level, '==' if token_tuple[0] == 'EQUAL' else '>', parse_expression(expression[:index], level + 1), parse_expression(expression[index + 1:], level + 1))
    
    for index, token_tuple in enumerate(expression):
        if token_tuple[0] == 'PLUS' or token_tuple[0] == 'MINUS' or token_tuple[0] == 'MULTIPLY':
            return Expr(level, '+' if token_tuple[0] == 'PLUS' else '-' if token_tuple[0] == 'MINUS' else '*', parse_expression(expression[:index], level + 1), parse_expression(expression[index + 1:], level + 1))

    
def parse_lines(lines: List[List[Tuple[str, str]]], level: int) -> List[Node]:
    current_line: List[Tuple[str, str]] = lines[0]
    if current_line[0][0] == 'BEGIN':
        return InstructionList(level, parse_lines(lines[1:], level + 1))
    elif current_line[0][0] == 'END' or current_line[0][0] == 'ELSE' or current_line[0][0] == 'FI' or current_line[0][0] == 'OD':
        return []
    elif current_line[0][0] == 'VARIABLE':
        # if the first element of an instruction is a variable then an assignment will be done
        return [Assign(level, Expr(level + 1, 'v', current_line[0][1]), parse_expression(current_line[2:], level + 1))] + parse_lines(lines[1:], level)
    elif current_line[0][0] == 'IF':
        then_lines = parse_lines(lines[1:], level + 1)
        else_lines = parse_lines(lines[get_matching_else(lines) + 1:], level + 1)
        return [If(level, parse_expression(current_line[1:-1], level + 1), then_lines if isinstance(then_lines, InstructionList) else then_lines[0], else_lines if isinstance(else_lines, InstructionList) else else_lines[0])] + parse_lines(lines[get_matching_end(lines) + 1:], level)
    elif current_line[0][0] == 'WHILE':
        do_lines = parse_lines(lines[1:], level + 1)
        return [While(level, parse_expression(current_line[1:-1], level + 1), do_lines if isinstance(do_lines, InstructionList) else do_lines[0])] + parse_lines(lines[get_matching_end(lines) + 1:], level)


def runparser(finput, foutput):
    output_file = open(foutput, 'w')
    runcompletelexer('imperative.lex', finput, 'lexemes.out')
    lexemes_file = open('lexemes.out')
    lexemes = lexemes_file.readlines()
    lexemes_file.close()
    line: List[Tuple[str, str]] = []
    lines: List[List[Tuple[str, str]]] = []
    for lexeme in lexemes:
        token: str = lexeme[:lexeme.index(' ')]
        token_string: str = lexeme[lexeme.index(' ') + 1:]
        token_string = token_string[:-1]
        if token != 'SPACE' and token != 'NEWLINE' and token != 'OPENBRACKET' and token != 'CLOSEBRACKET':
            line.append((token, token_string))
        elif token == 'NEWLINE':
            lines.append(line)
            line = []
    lines.append([(token, token_string)])
    prog = parse_lines(lines, 0)
    output_file.write(str(prog))
    output_file.close()