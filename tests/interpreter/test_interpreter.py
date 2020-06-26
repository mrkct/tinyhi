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

def test_functions():
    source = r"""BEGIN main
        BEGIN func()
            func <- 1
        END
        main <- func()
    END"""
    assert run(source) == 1

def test_param_immutability():
    source = r"""BEGIN main
        BEGIN MyFn(a)
            a <- 77
        END
        MyFn(7)
    END"""
    with pytest.raises(ExecutionError):
        run(source)

def test_deep_recursion():
    source = r"""BEGIN main
        BEGIN fib(x)
            IF x = 0
                fib <- 0
            ELSE
                IF x = 1
                    fib <- 1
                ELSE
                    fib <- fib(x - 1) + fib(x - 2)
                END
            END
        END
        main <- fib(10)
    END"""
    assert run(source) == 55

def test_if():
    source = r"""BEGIN main
        a <- 1
        IF a = 0
            a <- 3
        ELSE
            a <- 7
        END
        main <- a
    END"""
    assert run(source) == 7

def test_var_scope():
    source = r"""BEGIN main
        a <- 0
        BEGIN func()
            a <- 1
        END
        func()
        main <- a
    END
    """
    assert run(source) == 0
    return
    source = r"""BEGIN main
        a <- 0
        IF a = 0
            b <- 3
        END
        main <- b
    END"""
    with pytest.raises(ExecutionError):
        run(source)

def test_while():
    source = r"""BEGIN main
        x <- 0
        WHILE x < 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source) == 10
    source = r"""BEGIN main
        x <- 0
        WHILE x > 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source) == 0

def test_until(capsys):
    source = r"""BEGIN main
        x <- 0
        UNTIL x = 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source) == 10
    source = r"""BEGIN main
        x <- 0
        UNTIL x < 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source) == 1