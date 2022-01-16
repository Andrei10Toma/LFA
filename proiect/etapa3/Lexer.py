from typing import List, Union
from dfa_int_states import DfaIntStates, State

class Lexer:
    dfas: List[DfaIntStates]
    word: str
    current_word_position: int
    start_word: int

    def __init__(self, dfas: List[DfaIntStates], word) -> None:
        self.dfas = dfas
        self.word = word
        self.current_word_position = 0
        self.start_word = 0


    def __str__(self) -> str:
        result: str = ''
        for dfa in self.dfas:
            result += dfa.__str__()
        result += '\n' + self.word
        return result


    def compute_lexemes(self) -> Union[List[List[str]], str]:
        lexemes: List[List[str]] = []
        while self.current_word_position < len(self.word):
            lexem_found: bool = True

            for dfa in self.dfas:
                dfa.step(self.word, self.current_word_position)

            dfa_filtered = filter(lambda dfa: dfa._state == State.sink and dfa._last_position_input_accepted == -1, self.dfas)
            if len(list(dfa_filtered)) == len(self.dfas):
                return str(self.current_word_position)
            
            if (self.current_word_position == len(self.word) - 1):
                dfa_filtered_last = filter(lambda dfa: (dfa._state == State.initial or dfa._state == State.sink) and dfa._last_position_input_accepted == -1, self.dfas)
                if (len(list(dfa_filtered_last)) == len(self.dfas)):
                    return 'EOF'
            for dfa in self.dfas:
                if (dfa._state == State.accept or dfa._state == State.initial) and self.current_word_position != len(self.word) - 1:
                    lexem_found = False
                    break
            if lexem_found:
                # maximal match
                maximal_dfa: DfaIntStates = self.dfas[0]
                for dfa in self.dfas:
                    if dfa._last_position_input_accepted > maximal_dfa._last_position_input_accepted:
                        maximal_dfa = dfa
                self.current_word_position = maximal_dfa._last_position_input_accepted + 1
                lexemes.append([maximal_dfa._token, self.word[self.start_word : maximal_dfa._last_position_input_accepted + 1]])
                self.start_word = maximal_dfa._last_position_input_accepted + 1

                for dfa in self.dfas:
                    dfa._current_state = dfa._initial_state
                    dfa._state = State.initial
                    dfa._last_position_input_accepted = -1
            else:
                self.current_word_position += 1
        return lexemes
            

def runlexer(lexer: str, finput: str, foutput: str) -> None:
    lexer_file = open(lexer)
    word_input_file = open(finput)
    lexemes_output_file = open(foutput, 'w')
    readLines = lexer_file.readlines()
    dfas: List[DfaIntStates] = []
    start = 0
    for i in range(0, len(readLines)):
        if readLines[i] == '\n':
            dfas.append(DfaIntStates(readLines[start : i]))
            start = i + 1

    dfas.append(DfaIntStates(readLines[start : len(readLines)]))

    lexer: Lexer = Lexer(dfas, word_input_file.read())
    lexemes: List[List[str]] = lexer.compute_lexemes()
    if isinstance(lexemes, list):
        for lexeme in lexemes:
            if (lexeme[1] != '\n'):
                write_lexeme = lexeme[0] + ' ' + lexeme[1] + '\n'
            else:
                write_lexeme = lexeme[0] + ' ' + '\\n' + '\n'
            lexemes_output_file.write(write_lexeme)
    else:
        lexemes_output_file.write(f'No viable alternative at character {lexemes}, line 0')