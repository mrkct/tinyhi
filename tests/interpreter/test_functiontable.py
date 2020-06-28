import pytest
from tinyhi.interpreter.functiontable import FunctionTable
from tinyhi.interpreter import ExecutionError


def test_noparent():
    table = FunctionTable()
    table.declare("F", [])
    assert table.isVisible("F")
    assert not table.isVisible("P")
    table.declare("P", [])
    assert table.isVisible("F")
    assert table.isVisible("P")

def test_parent():
    parent = FunctionTable()
    table = FunctionTable(parent=parent)
    parent.declare("F", [])
    assert table.isVisible("F")
    table.declare("P", [])
    assert not parent.isVisible("P")