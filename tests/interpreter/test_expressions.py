import pytest
from itertools import product
from tinyhi.interpreter.undefined import Undefined
from tinyhi.interpreter import ExecutionError
from tinyhi.interpreter.expressions import unary_expression, binary_expression


vals = [1, [1, 2], 'str', None, Undefined]
combinations = product(vals, vals)

def test_basic_algebra_typecheck():
    correct = [
        (1, 1), (1, [1, 2]), ([1, 2], 1), ([1, 2], [1, 2])
    ]
    incorrect = [x for x in combinations if x not in correct]
    for op in ['+', '-', '*', '/']:
        for left, right in correct:
            binary_expression(left, op, right)
        for left, right in incorrect:
            with pytest.raises(ExecutionError):
                binary_expression(left, op, right)

def test_blank_typecheck():
    correct = [
        (1, 1), (1, [1, 2]), ([1, 2], 1), ([1, 2], [1, 2]), 
        ('str', 'str')
    ]
    incorrect = [x for x in combinations if x not in correct]
    for left, right in correct:
        binary_expression(left, ' ', right)
    for left, right in incorrect:
        with pytest.raises(ExecutionError):
            binary_expression(left, ' ', right)

def test_negation():
    correct = [1]
    for val in correct:
        unary_expression('-', val)
    incorrect = [x for x in vals if x not in correct]
    for val in incorrect:
        with pytest.raises(ExecutionError):
            unary_expression('-', val)

def test_length():
    correct = [[1, 2], 'str']
    for val in correct:
        unary_expression('#', val)
    incorrect = [x for x in vals if x not in correct]
    for val in incorrect:
        with pytest.raises(ExecutionError):
            unary_expression('#', val)

def test_list_negation():
    correct = [[1, 2]]
    for val in correct:
        unary_expression('~', val)
    incorrect = [x for x in vals if x not in correct]
    for val in incorrect:
        with pytest.raises(ExecutionError):
            unary_expression('~', val)