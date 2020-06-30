import pytest
from tinyhi.interpreter import run, ExecutionError


def test_main_return():
    source = r"""BEGIN main
        main <- 123
    END"""
    assert run(source, throw_errors=True) == 123
    source = r"""BEGIN main
        main <- 1 + 4 * 3
    END"""
    assert run(source, throw_errors=True) == 13

def test_assignment():
    source = r"""BEGIN main
        x <- 1
        main <- x
    END"""
    assert run(source, throw_errors=True) == 1
    source = r"""BEGIN main
        x <- 1
        x <- x + 1
        main <- x
    END"""
    assert run(source, throw_errors=True) == 2

def test_lists():
    source = r"""BEGIN main
        x <- 1 2 3
        y <- x 4
        main <- y
    END"""
    assert run(source, throw_errors=True) == [1, 2, 3, 4]
    source = r"""BEGIN main
        x <- 1 2
        y <- 3 4
        main <- 0 x y 5
    END"""
    assert run(source, throw_errors=True) == [0, 1, 2, 3, 4, 5]

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
    assert run(source, throw_errors=True) == [-1, -2, -3]
    source = r"""BEGIN main
        main <- # 1 2 3
    END"""
    assert run(source, throw_errors=True) == 3

def test_functions():
    source = r"""BEGIN main
        BEGIN func()
            func <- 1
        END
        main <- func()
    END"""
    assert run(source, throw_errors=True) == 1

def test_param_immutability():
    source = r"""BEGIN main
        BEGIN MyFn(a)
            a <- 77
        END
        MyFn(7)
    END"""
    with pytest.raises(ExecutionError):
        run(source, throw_errors=True)

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
    assert run(source, throw_errors=True) == 55

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
    assert run(source, throw_errors=True) == 7

def test_var_scope():
    source = r"""BEGIN main
        BEGIN func()
            a <- 1
        END
        a <- 0
        func()
        main <- a
    END
    """
    assert run(source, throw_errors=True) == 0
    sources = [
        r"""BEGIN main
            a <- 0
            IF a = 0
                b <- 3
            END
            main <- b
        END""", 
        r"""BEGIN main
            a <- 1
            WHILE a <> 0
                b <- "Hello"
                a <- 0
            END
            main <- b
        END""",
        r"""BEGIN main
            UNTIL 0 = 0
                b <- "Hello"
            END
            main <- b
        END""" 
    ]
        
    for source in sources:
        with pytest.raises(ExecutionError):
            run(source, throw_errors=True)
    

def test_while():
    source = r"""BEGIN main
        x <- 0
        WHILE x < 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source, throw_errors=True) == 10
    source = r"""BEGIN main
        x <- 0
        WHILE x > 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source, throw_errors=True) == 0

def test_until(capsys):
    source = r"""BEGIN main
        x <- 0
        UNTIL x = 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source, throw_errors=True) == 10
    source = r"""BEGIN main
        x <- 0
        UNTIL x < 10
            x <- x + 1
        END
        main <- x
    END"""
    assert run(source, throw_errors=True) == 1

def test_print(capsys):
    source = r"""BEGIN main
        "Hello, world!"
        x <- 1
        x
        y <- 1 2 3
        y
    END"""
    run(source, throw_errors=True)
    stdout = capsys.readouterr().out
    assert stdout == "Hello, world!\n1\n1 2 3\n"

def test_globals():
    source = r"""BEGIN main
        BEGIN func
            .A <- 1
        END
        .A <- 0
        func()
        main <- .A
    END"""
    assert run(source, throw_errors=True) == 1
    source = r"""BEGIN main
        i <- 0
        WHILE i = 0
            .GLOBAL <- 1
            i <- 1
        END
        i <- 0
        main <- .GLOBAL
    END"""
    assert run(source, throw_errors=True) == 1

def test_clear_var():
    source = r"""BEGIN main
        a <- 0
        b <- 1
        a + b
        b <-
        a + b
    END"""
    with pytest.raises(ExecutionError):
        run(source, throw_errors=True)

def test_array_indexing(capsys):
    source = r"""BEGIN main
        X <- "ABCD"
        X[1 4]
        X <- 1 2 3 4
        X[2]
    END"""
    run(source, throw_errors=True)
    stdout = capsys.readouterr().out
    assert stdout == 'AD\n2\n'

def test_function_scope():
    source = r"""BEGIN main
        BEGIN func()
            BEGIN recurse(x)
                IF x <> 0
                    recurse(0)
                END
            END
            recurse(1)
        END
        func()
    END"""
    run(source, throw_errors=True)
    bad_scopes = [
        r"""BEGIN main
            BEGIN func()
                BEGIN recurse(x)
                    IF x <> 0
                        recurse(0)
                    END
                END
            END
            recurse(1)
        END""", 
        r"""BEGIN main
            IF 1 = 1
                BEGIN x
                END
            END
            x()
        END""", 
        r"""BEGIN main
            WHILE 0 = 1
                BEGIN x
                END
            END
            x()
        END""",
        r"""BEGIN main
            UNTIL 1 = 1
                BEGIN x
                END
            END
            x()
        END"""
    ]
    with pytest.raises(ExecutionError):
        for s in bad_scopes:
            run(s, throw_errors=True)