from tinyhi import parse, ParseError
import os
import pytest


CORRECT_PROGRAMS_FOLDER = 'tests/programs/correct/'
INCORRECT_PROGRAMS_FOLDER = 'tests/programs/incorrect/'

def test_correct():
    for filename in os.listdir(CORRECT_PROGRAMS_FOLDER):
        with open(CORRECT_PROGRAMS_FOLDER + filename, 'r') as file:
            source = file.read()
        result = parse(source, throw_errors=True)
        print(filename, '...')
        assert result != None

def test_incorrect():
    for filename in os.listdir(INCORRECT_PROGRAMS_FOLDER):
        with open(INCORRECT_PROGRAMS_FOLDER + filename, 'r') as file:
            source = file.read()
        with pytest.raises(ParseError) as info:
            print(filename, '...')
            result = parse(source, throw_errors=True)
