#!/usr/bin/env python

from SudokuConverter import SudokuConverter, pretty_print
import argparse

def main(args):
    if args.eval:
        arr = eval(args.sudoku)
    else:
        arr = list(args.sudoku.replace(args.fill_value, '0'))

    arr = [int(x) for x in arr]
    sudoku = SudokuConverter(args.n, arr)
    pretty_print(sudoku.convert_to_sat())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Sudoku to SAT.')
    #  parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument("sudoku",type=str)
    parser.add_argument("--eval", type=bool, default=False)
    parser.add_argument("--fill_value", type=str, default='.')
    parser.add_argument("-n", type=int, default=9)
    args = parser.parse_args()
    main(args)
