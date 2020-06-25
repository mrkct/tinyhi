import pytest
from tinyhi.interpreter import run, ExecutionError


def test_main_return():
    source = r"""BEGIN main
        main <- 123
    END"""
    assert run(source) == 123
    source = r"""BEGIN main
        main <- 1 + 4 * 3
    END"""
    assert run(source) == 13

def test_assignment():
    source = r"""BEGIN main
        x <- 1
        main <- x
    END"""
    assert run(source) == 1
    source = r"""BEGIN main
        x <- 1
        x <- x + 1
        main <- x
    END"""
    assert run(source) == 2

def test_lists():
    source = r"""BEGIN main
        x <- 1 2 3
        y <- x 4
        main <- y
    END"""
    assert run(source) == [1, 2, 3, 4]
    source = r"""BEGIN main
        x <- 1 2
        y <- 3 4
        main <- 0 x y 5
    END"""
    assert run(source) == [0, 1, 2, 3, 4, 5]

def test_operations():
    source = r"""BEGIN main
        main <- 2 {} 1 2 3
    END"""
    expected = [
        ('+', [3, 4, 5]), 
        ('-', [1, 0, -1]), 
        ('*', [2, 4, 6]), 
        ('/', [2, 1, 0]), 
        (' ', [2, 1, 2, 3])
    ]
    for op, expect in expected:
        assert run(source.format(op)) == expect
    source = r"""BEGIN main
        main <- ~ 1 2 3
    END"""
    assert run(source) == [-1, -2, -3]
    source = r"""BEGIN main
        main <- # 1 2 3
    END"""
    assert run(source) == 3