#!/usr/bin/env python

from SudokuConverter import SudokuConverter, pretty_print
import argparse

def main(args):
    if not args.sudoku and args.n:
        args.sudoku = '0' * args.n**2
        args.eval = False
    args.eval = str(args.eval).lower() in ('yes', 'true', 't', 'y', '1')
    if args.eval:
        arr = eval(args.sudoku)
    else:
        arr = list(args.sudoku.replace(args.fill_value, '0'))

    arr = [int(x) for x in arr]
    sudoku = SudokuConverter(arr)
    pretty_print(sudoku.convert_to_sat())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Sudoku to SAT.')
    #  parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument("--sudoku", type=str)
    parser.add_argument("-n", type=int, default=9, help="Create 0 filled sudoku if sudoku is not defined")
    parser.add_argument("--eval", type=str, default='0')
    parser.add_argument("--fill_value", type=str, default='.')
    args = parser.parse_args()
    main(args)
