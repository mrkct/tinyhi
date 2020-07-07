from tinyhi import parse, ParseError
import os
import pytest


CORRECT_PROGRAMS_FOLDER = 'tests/programs/correct/'
INCORRECT_PROGRAMS_FOLDER = 'tests/programs/incorrect/'

CORRECT_PROGRAMS = os.listdir(CORRECT_PROGRAMS_FOLDER)
INCORRECT_PROGRAMS = os.listdir(INCORRECT_PROGRAMS_FOLDER)

@pytest.mark.parametrize('filename', CORRECT_PROGRAMS)
def test_correct(filename):
    with open(CORRECT_PROGRAMS_FOLDER + filename, 'r') as file:
        source = file.read()
    result = parse(source, throw_errors=True)
    assert result != None

@pytest.mark.parametrize('filename', INCORRECT_PROGRAMS)
def test_incorrect(filename):
    with open(INCORRECT_PROGRAMS_FOLDER + filename, 'r') as file:
        source = file.read()
    with pytest.raises(ParseError) as info:
        result = parse(source, throw_errors=True)
