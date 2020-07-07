from tinyhi import run, ExecutionError
import os
import pytest


PROGRAMS = {
    'find_str': (r"""BEGIN MyProgram
        BEGIN IniziaCon(haystack, needle, start)
            i <- start
            j <- 1
            IniziaCon <- 1
            continua <- 1
            WHILE continua = 1
                IF haystack[i] <> needle[j]
                    continua <- 0
                    IniziaCon <- 0
                END
                i <- i + 1
                j <- j + 1
                IF j > #needle
                    continua <- 0
                END
            END
        END
        s <- "asdkfasddCIAOdasdasd"
        da_trovare <- "CIAO"
        i <- 1
        trovata <- 0
        WHILE i <= #s - #da_trovare + 1
            IF IniziaCon(s, da_trovare, i) = 1
                trovata <- 1
                MyProgram <- i
            END
            i <- i + 1
        END
        IF trovata = 0
            MyProgram <- -1
        END
    END""", 10), 
    'sum_all': (r"""BEGIN main()
        a <- 1 2 3 4 5 6 7 8 9 10
        main <- 0
        i <- 1
        UNTIL i > #a
            main <- main + a[i]
            i <- i + 1
        END
    END""", 55), 
    'recursive_sum_all': (r"""BEGIN main
        BEGIN sum(array, i)
            IF i > #array
                sum <- 0
            ELSE
                sum <- array[i] + sum(array, i+1)
            END
        END
        main <- sum(1 2 3 4 5 6 7 8 9 10, 1)
    END""", 55), 
    'use_before_decl': (r"""BEGIN MAIN
        BEGIN F(X)
            F <- G(X)
        END
        BEGIN G(X)
            G <- X
        END
        MAIN <- F(1)
    END""", 1), 
    'use_after_decl': (r"""BEGIN MAIN
        BEGIN G(X)
            G <- X
        END
        BEGIN F(X)
            F <- G(X)
        END
        MAIN <- F(1)
    END""", 1)
}

@pytest.mark.parametrize('program', PROGRAMS)
def test_correct(program):
    source, expected = PROGRAMS[program]
    assert expected == run(source, throw_errors=True)
