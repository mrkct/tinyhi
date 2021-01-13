# TinyHI Interpreter
An interpreter for TinyHI, a programming language proposed in a 1976 article on Dr. Dobb's Journal (see `TinyHi.pdf`). This was a school project for a class on parsing, intepreting and translating code (Intepreti e Traduttori in italian). This does not follow exactly the PDFs rules, mostly because they are inconsistent and/or unspecified in some points.

## How to use it

First of all you need:

    python 3.7 or higher
    Antlr for generating the parser

Install the `antlr4-runtime` pip package and `pytest` (for running tests). Set the `ANTLR4_JAR` environment variable to point to your antlr4 jar and run `./antlr_gen.sh` to create the parser. If you don't want to set the variable just check inside `antlr_gen.sh`, it's only 2 lines of code anyway.

To run a program you can write `python -m tinyhi Filename.hi`. The interpreter is also a python module so it's easy to integrate with other applications, just import it and call `tinyhi.run(source_code)`

Here is a program that calculates the factorial and prints it:

    BEGIN TEST
        BEGIN DOIT(N)
            BEGIN FACT(N)
                IF N = 0
                    FACT <- 1
                ELSE
                    FACT <- N * FACT(N - 1)
                END
            END
            DOIT <- FACT(2 * N)
        END
        DOIT(3)
    END

