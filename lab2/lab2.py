from typing import List

class Expr:
    pass

class Symbol(Expr):
    _char: str

    def __init__(self, c:str) -> None:
        self._char = c

    def __str__(self) -> str:
        return self._char


class Star(Expr):
    _expr: Expr

    def __init__(self, expr: Expr) -> None:
        self._expr = expr

    def __str__(self) -> str:
        return '(' + self._expr.__str__() + ')*'

class Concat(Expr):
    _expr1: Expr
    _expr2: Expr

    def __init__(self, expr1, expr2) -> None:
        self._expr1 = expr1
        self._expr2 = expr2

    def __str__(self) -> str:
        return '(' + self._expr1.__str__() + self._expr2.__str__() + ')'

class Union(Expr):
    _expr1: Expr
    _expr2: Expr

    def __init__(self, expr1, expr2) -> None:
        self._expr1 = expr1
        self._expr2 = expr2

    def __str__(self) -> str:
        return '(' + self._expr1.__str__() + 'U' + self._expr2.__str__() + ')'

class Plus(Expr):
    _expr: Expr

    def __init__(self, expr) -> None:
        self._expr = expr


def create_expr(s: str) -> Expr:
    stack = []
    for split_s in s.split(' '):
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
    if len(stack) == 0 or len(stack) == 1:
        return False
    top = stack.pop()
    if isinstance(top, Symbol):
        stack.append(top)
        return True
    if isinstance(top, Concat) or isinstance(top, Union):
        if top._expr2 != None and top._expr1 != None:
            stack.append(top)
            return True
    if isinstance(top, Star) or isinstance(top, Plus):
        if top._expr != None:
            stack.append(top)
            return True
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
        
    if isinstance(top2, Star):
        if top2._expr == None:
            top2._expr = top
    
    if isinstance(top2, Plus):
        if top2._expr == None:
            expanded_plus: Expr = Concat(top, Star(top))
            stack.append(expanded_plus)
            return

    stack.append(top2)


expression = create_expr("PLUS UNION STAR UNION CONCAT d e f STAR c")
print(expression)