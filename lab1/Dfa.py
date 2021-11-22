from typing import Dict, Set, Tuple


class Dfa:
    _alphabet: Set[str] = set()
    _initial_state: int
    _final_states: Set[int] = set()
    _delta: Dict[Tuple[int, str], int] = dict()

    def __str__(self) -> str:
        return str(self._alphabet) + '\n' + str(self._initial_state) + '\n' + str(self._final_states) + '\n' + str(self._delta)


    def __init__(self, text: str):
        lines = text.split('\n')
        self._initial_state = int(lines[0])
        for i in range(1, len(lines) - 1):
            line_content = lines[i].split(' ')
            self._alphabet.add(line_content[1])
            self._delta[(int(line_content[0]), line_content[1])] = int(line_content[2])

        final_states = lines[len(lines) - 1].split(' ')
        for final_state in final_states:
            self._final_states.add(int(final_state))

    def next_config(self, config: Tuple[int, str]):
        if len(config[1]) == 0:
            return None
        return (self._delta[(config[0], config[1][0])], config[1][1:])

    def accept(self, word: str) -> bool:
        current_state:int = self._initial_state
        current_word: str = word
        while (self.next_config((current_state, current_word)) is not None):
            current_config = self.next_config((current_state, current_word))
            print (str(current_config))
            current_word = current_word[1:]
            current_state = current_config[0]
        return self._final_states.__contains__(current_state)

with open('lab1.in', 'r') as txt_file:
    dfa = Dfa(txt_file.read())
    print(dfa)
    print(dfa.accept('1100001'))