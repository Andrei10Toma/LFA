from typing import List

from nfa import Nfa

class Expr:
    nfa: Nfa

    def __init__(self) -> None:
        self.nfa = Nfa()
    
    def __str__(self) -> str:
        return self.nfa.__str__()


class Symbol(Expr):
    _char: str

    def __init__(self, c:str) -> None:
        super().__init__()
        self._char = c

    def __str__(self) -> str:
        return self._char


class Star(Expr):
    _expr: Expr

    def __init__(self, expr: Expr) -> None:
        super().__init__()
        self._expr = expr

    def __str__(self) -> str:
        return '(' + self._expr.__str__() + ')*'

class Concat(Expr):
    _expr1: Expr
    _expr2: Expr

    def __init__(self, expr1, expr2) -> None:
        super().__init__()
        self._expr1 = expr1
        self._expr2 = expr2

    def __str__(self) -> str:
        return '(' + self._expr1.__str__() + self._expr2.__str__() + ')'

class Union(Expr):
    _expr1: Expr
    _expr2: Expr

    def __init__(self, expr1, expr2) -> None:
        super().__init__()
        self._expr1 = expr1
        self._expr2 = expr2

    def __str__(self) -> str:
        return '(' + self._expr1.__str__() + 'U' + self._expr2.__str__() + ')'

class Plus(Expr):
    _expr: Expr

    def __init__(self, expr) -> None:
        super().__init__()
        self._expr = expr

    def __str__(self) -> str:
        return '(' + self._expr.__str__() + '(' + self._expr.__str__() + ')*' + ')'


def create_expr(s: str) -> Expr:
    stack = []
    split_expr:List[str] = s.split(' ')
    for split_s in split_expr:
        if (split_s == 'CONCAT'):
            stack.append(Concat(None, None))
        elif (split_s == 'STAR'):
            stack.append(Star(None))
        elif (split_s == 'UNION'):
            stack.append(Union(None, None))
        elif (split_s == 'PLUS'):
            stack.append(Plus(None))
        else:
            stack.append(Symbol(split_s))

        reduce_stack(stack)
    return stack[0]


def is_stack_reduceable(stack: List) -> bool:
    if len(stack) == 0:
        return False
    top = stack.pop()

    if isinstance(top, Symbol):
        stack.append(top)
        top.nfa.initial_state = Nfa.number_of_states
        top.nfa.final_state = Nfa.number_of_states + 1
        top.nfa.delta.append([top.nfa.initial_state, top.__str__(), top.nfa.final_state])
        Nfa.number_of_states += 2
        return True and len(stack) != 1

    if isinstance(top, Concat):
        if top._expr2 != None and top._expr1 != None:
            stack.append(top)
            top.nfa.initial_state = top._expr1.nfa.initial_state
            top.nfa.final_state = top._expr2.nfa.final_state
            for tranzition in top._expr1.nfa.delta:
                top.nfa.delta.append(tranzition)
            for tranzition in top._expr2.nfa.delta:
                top.nfa.delta.append(tranzition)
            top.nfa.delta.append([top._expr1.nfa.final_state, None, top._expr2.nfa.initial_state])
            return True and len(stack) != 1

    if isinstance(top, Union):
        if top._expr2 != None and top._expr1 != None:
            stack.append(top)
            top.nfa.initial_state = Nfa.number_of_states
            top.nfa.final_state = Nfa.number_of_states + 1
            for tranzition in top._expr1.nfa.delta:
                top.nfa.delta.append(tranzition)
            for tranzition in top._expr2.nfa.delta:
                top.nfa.delta.append(tranzition)
            top.nfa.delta.append([top.nfa.initial_state, None, top._expr1.nfa.initial_state])
            top.nfa.delta.append([top.nfa.initial_state, None, top._expr2.nfa.initial_state])
            top.nfa.delta.append([top._expr1.nfa.final_state, None, top.nfa.final_state])
            top.nfa.delta.append([top._expr2.nfa.final_state, None, top.nfa.final_state])
            Nfa.number_of_states += 2
            return True and len(stack) != 1

    if isinstance(top, Star):
        if top._expr != None:
            stack.append(top)
            top.nfa.initial_state = Nfa.number_of_states
            top.nfa.final_state = Nfa.number_of_states + 1
            for tranzition in top._expr.nfa.delta:
                top.nfa.delta.append(tranzition)
            top.nfa.delta.append([top.nfa.initial_state, None, top._expr.nfa.initial_state])
            top.nfa.delta.append([top.nfa.initial_state, None, top.nfa.final_state])
            top.nfa.delta.append([top._expr.nfa.final_state, None, top.nfa.final_state])
            top.nfa.delta.append([top._expr.nfa.final_state, None, top.nfa.initial_state])
            Nfa.number_of_states += 2
            return True and len(stack) != 1

    if isinstance(top, Plus):
        if top._expr != None:
            stack.append(top)
            top.nfa.initial_state = top._expr.nfa.initial_state
            
            previous_number_of_states: int = Nfa.number_of_states
            for tranzition in top._expr.nfa.delta:
                top.nfa.delta.append(tranzition)
                Nfa.number_of_states += 2
            
            star_initial_state: int = top._expr.nfa.initial_state + Nfa.number_of_states - previous_number_of_states
            star_final_state: int = top._expr.nfa.final_state + Nfa.number_of_states - previous_number_of_states
            
            for tranzition in top._expr.nfa.delta:
                top.nfa.delta.append([tranzition[0] + Nfa.number_of_states - previous_number_of_states, tranzition[1], tranzition[2] + Nfa.number_of_states - previous_number_of_states])
            top.nfa.delta.append([Nfa.number_of_states, None, star_initial_state])
            top.nfa.delta.append([Nfa.number_of_states, None, Nfa.number_of_states + 1])
            top.nfa.delta.append([star_final_state, None, Nfa.number_of_states])
            top.nfa.delta.append([star_final_state, None, Nfa.number_of_states + 1])
            top.nfa.delta.append([top._expr.nfa.final_state, None, Nfa.number_of_states])
            top.nfa.final_state = Nfa.number_of_states + 1
            Nfa.number_of_states += 2
            return True and len(stack) != 1

    stack.append(top)
    return False


def reduce_stack(stack: List):
    if not is_stack_reduceable(stack):
        return
    top = stack.pop()

    if isinstance(top, Concat):
        if top._expr1 == None or top._expr2 == None:
            stack.append(top)
            return

    if isinstance(top, Union):
        if top._expr1 == None or top._expr2 == None:
            stack.append(top)
            return

    if isinstance(top, Star) or isinstance(top, Plus):
        if top._expr == None:
            stack.append(top)
            return

    reduce_peek_of_stack(stack, top)
    reduce_stack(stack)


def reduce_peek_of_stack(stack, top):
    top2 = stack.pop()
    if isinstance(top2, Concat) or isinstance(top2, Union):
        if top2._expr1 == None:
            top2._expr1 = top
        else:
            top2._expr2 = top
        
    if isinstance(top2, Star) or isinstance(top2, Plus):
        if top2._expr == None:
            top2._expr = top

    stack.append(top2)