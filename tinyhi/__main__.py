import argparse
import sys
from tinyhi import run
from tinyhi.parser import ParseError
from tinyhi.threader import ThreadError
from tinyhi.interpreter import ExecutionError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs programs written in TinyHI')
    parser.add_argument(
        'filename', metavar='F', type=str, 
        help='The path to the file contains the code for the program')
    args = parser.parse_args()
    filename = args.filename
    try:
        with open(filename, "r") as file:
            source = file.read()
    except OSError as e:
        print(f'Could not open file "{filename}" ({e})')
        exit(-1)
    exit(run(source))
