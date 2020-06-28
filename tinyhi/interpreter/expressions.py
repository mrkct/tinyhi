"""This file handles how to calculate expressions in the interpreter, 
including typechecking and broadcasting"""

from .errors import ExecutionError, strtype


def binary_expression(left, op, right):
    """Calculates a binary expression and returns its value
    Params:
        left: The left value of the expression
        op: A string representing the operation
        right: The right value of the expression
    Returns:
        The result of the operation, the type depends on the operands given
    Raises:
        ValueError if the operation is not a valid one
        ExecutionError on type mismatches
    """
    def handle_sum(left, right):
        # Simple sum of integers
        if type(left) == int and type(right) == int:
            return left + right
        # Sum of list and a single int
        # Note that lists of string are impossible to get in TinyHi so we 
        # don't check for those
        if type(left) == list and type(right) == int:
            left, right = right, left
        if type(left) == int and type(right) == list:
            return [left + x for x in right]
        if type(left) == list and type(right) == list:
            if len(left) != len(right):
                raise ExecutionError(
                    f'Type mismatch: cannot sum lists with different lengths'
                )
            return [left[i] + right[i] for i in range(0, len(left))]

    def handle_mul(left, right):
        # Simple mul of integers
        if type(left) == int and type(right) == int:
            return left * right
        # Sum of list and a single int
        if type(left) == list and type(right) == int:
            left, right = right, left
        if type(left) == int and type(right) == list:
            return [left * x for x in right]
        raise ExecutionError(
            f'Type mismatch: cannot multiply {strtype(left)} and {strtype(right)}'
        )

    def handle_sub(left, right):
        # Simple sub of integers
        if type(left) == int and type(right) == int:
            return left - right
        # Int - List is different than List - Int
        if type(left) == list and type(right) == int:
            return [x - right for x in left]
        if type(left) == int and type(right) == list:
            return [left - x for x in right]
        raise ExecutionError(
            f'Type mismatch: cannot subtract {strtype(left)} and {strtype(right)}'
        )

    def handle_div(left, right):
        try:
            # Simple divison of integers
            if type(left) == int and type(right) == int:
                return left // right
            # Int - List is different than List - Int
            if type(left) == list and type(right) == int:
                return [x // right for x in left]
            if type(left) == int and type(right) == list:
                return [left // x for x in right]
            raise ExecutionError(
                f'Type mismatch: cannot divide {strtype(left)} and {strtype(right)}'
            )
        except ZeroDivisionError:
            raise ExecutionError(
                f'Division by zero: {left} / {right}'
            )

    def handle_blank(left, right):
        if type(left) == str and type(right) == str:
            return left + right
        if type(left) == str or type(right) == str:
            raise ExecutionError(
                f'Type mismatch: vectors can only contain integers'
            )
        if type(left) != list:
            left = [left]
        if type(right) != list:
            right = [right]
        return left + right

    def handle_greater(left, right):
        if type(left) == int and type(right) == int:
            return left > right
        raise ExecutionError(
            f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
        )

    def handle_less(left, right):
        if type(left) == int and type(right) == int:
            return left < right
        raise ExecutionError(
            f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
        )

    def handle_equal(left, right):
        if type(left) == type(right):
            return left == right
        raise ExecutionError(
            f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
        )

    def handle_not_equal(left, right):
        if type(left) == type(right):
            return left != right
        raise ExecutionError(
            f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
        )

    def handle_greater_equal(left, right):
        return not handle_less(left, right)

    def handle_less_equal(left, right):
        return not handle_greater(left, right)

    OPERATIONS = {
        '+': handle_sum, 
        '-': handle_sub, 
        '*': handle_mul, 
        '/': handle_div, 
        ' ': handle_blank, 
        '>': handle_greater,
        '<': handle_less,
        '>=': handle_greater_equal,
        '<=': handle_less_equal,
        '=': handle_equal,
        '<>': handle_not_equal
    }
    if op not in OPERATIONS:
        raise ValueError(
            f'Operation "{op}" is not a valid binary operation'
        )
    return OPERATIONS[op](left, right)

def unary_expression(op, value):
    """Calculates an unary expression and returns its value
    Params:
        op: A string representing the unary operator
        value: The value to which to apply the operator
    Returns:
        The result of the operation, the type depends on the operand
    Raises:
        ValueError if the operator is not a valid one
        ExecutionError on type mismatches
    """
    def handle_length(value):
        if type(value) in [list, str]:
            return len(value)
        raise ExecutionError(
            f'Type mismatch: cannot get length of {strtype(value)}'
        )
        
    def handle_list_negation(expr):
        if type(expr) == list:
            return [-x for x in expr]
        raise ExecutionError(
            f'Type mismatch: cannot apply list negation to type {strtype(expr)}'
        )
    
    def handle_negation(expr):
        if type(expr) == int:
            return -expr
        raise ExecutionError(
            f'Type mismatch: cannot negate type {strtype(expr)}'
        )
    
    OPERATIONS = {
        '#': handle_length, 
        '~': handle_list_negation, 
        '-': handle_negation
    }
    if op not in OPERATIONS:
        raise ValueError(
            'Operation "{op}" is not a valid unary operation'
        )
    return OPERATIONS[op](value)

def array_index(array, index):
    """Returns the value indexed in an array or string
    Params:
        array: A list or string representing the value to index into
        index: An int or list of int each representing indexes. Note that 
        indexes start from 1 in TinyHi
    Returns:
        A string if `array` was a string, a list of ints of the index was also 
        a list or a single integer if there was a single index in an int list
    Raises:
        ExecutionError on type mismatches
    """
    if type(array) not in [list, str]:
        raise ExecutionError(
            f'Type mismatch: cannot index {strtype(array)}'
        )
    if type(index) not in [list, int]:
        raise ExecutionError(
            f'Type mismatch: cannot use {strtype(index)} as an index'
        )
    if type(index) == int: index = [index]

    result = []
    for i in index:
        if i < 1 or i > len(array):
            raise ExecutionError(
                f'Index out of bounds: {i} is not in [1, {len(array)}]'
            )
        result.append(array[i - 1])
    if type(array) == str:
        result = ''.join(result)
    elif len(result) == 1:
        result = result[0]
    return result