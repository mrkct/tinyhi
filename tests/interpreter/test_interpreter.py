import pytest
from tinyhi.interpreter import run, ExecutionError


def test_return():
    source = r"""BEGIN main
        main <- 123
    END"""
    assert run(source) == 123
    source = r"""BEGIN main
        main <- 1 + 4 * 3
    END"""
    assert run(source) == 13
    