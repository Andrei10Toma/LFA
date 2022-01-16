from typing import Dict, List, Set, Tuple
import enum

def string_escape(s, encoding='utf-8'):
    return s.encode('latin1').decode('unicode-escape')     

class State(enum.Enum):
    initial = 0
    accept = 1
    sink = 2

class DfaIntStates:
    _alphabet: Set[str]
    _initial_state: int
    _final_states: Set[int]
    _sink_states: Set[int]
    _delta: Dict[Tuple[int, str], int]
    _token: str
    _current_state: int
    _state: int
    _last_position_input_accepted: int

    def __str__(self) -> str:
        return str(self._alphabet) + '\n' + str(self._initial_state) + '\n' + str(self._final_states) + '\n' + str(self._delta) + '\n' + str(self._token)

    def __init__(self, lines: List[str]):
        self._alphabet = set()
        self._final_states = set()
        self._delta = dict()
        self._sink_states = set()
        alphabet = lines[0]
        token = lines[1]
        initial_state = lines[2]
        for character in string_escape(alphabet[0 : -1]):
            self._alphabet.add(character)
        self._token = token[0 : len(token) - 1]
        self._initial_state = int(initial_state[0 : len(initial_state) - 1])

        for line in lines[3 : -1]:
            transition = line.split(',')
            self._delta[(int(transition[0]), string_escape(transition[1][1 : -1]))] = int(transition[2])
        for final_state in lines[-1].split(' '):
            self._final_states.add(int(final_state))
        self._state = State.initial
        self._last_position_input_accepted = -1
        self._current_state = self._initial_state
        self.compute_sink_states()


    def step(self, word: str, position):
        if self._state != State.sink:
            next_state = self._delta.get((self._current_state, word[position]))
            if self.is_sink_state(next_state):
                self._state = State.sink
                return
            if next_state:
                if self._final_states.__contains__(next_state):
                    self._last_position_input_accepted = position
                    self._state = State.accept
                self._current_state = next_state
            else:
                self._state = State.sink


    def is_sink_state(self, state) -> bool:
        return state in self._sink_states


    def compute_sink_states(self) -> None:
        # compute the inverted DFA
        delta_aux: Dict[int, Set[int]] = dict()
        all_states: Set[int] = set()
        for tranzition in self._delta.items():
            if tranzition[1] not in delta_aux.keys():
                delta_aux[tranzition[1]] = set()
            delta_aux[tranzition[1]].add(tranzition[0][0])
            all_states.add(tranzition[1])
            all_states.add(tranzition[0][0])

        # bfs
        visited: Set[int] = set()
        bfs_queue: List[int] = []
        for state in self._final_states:
            bfs_queue.append(state)
            visited.add(state)
            while bfs_queue:
                extracted:int = bfs_queue.pop(0)
                if extracted in delta_aux.keys():
                    for value in delta_aux[extracted]:
                        if value not in visited:
                            bfs_queue.append(value)
                            visited.add(value)

        # compute the sink states
        for state in all_states:
            if state not in visited:
                self._sink_states.add(state)