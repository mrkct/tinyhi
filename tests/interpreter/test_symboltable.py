import pytest
from tinyhi.interpreter.symboltable import SymbolTable
from tinyhi.interpreter import ExecutionError

def test_noparent():
    table = SymbolTable()
    table.put('x', 1)
    assert table.get('x') == 1
    table.put('y', 0)
    assert table.get('x') == 1 and table.get('y') == 0
    table.put('y', 1)
    assert table.get('x') == 1 and table.get('y') == 1
    table.put('z', 99, immutable=True)
    assert table.get('z') == 99
    with pytest.raises(ExecutionError):
        table.put('z', 100)

def test_withparent():
    parent = SymbolTable()
    parent.put('x', 100)
    parent.put('y', 200)
    child = SymbolTable(parent)
    assert child.get('x') == 100 and child.get('y') == 200
    child.put('x', 'hello')
    assert child.get('x') == 'hello' and child.get('y') == 200
    assert parent.get('x') == 'hello'