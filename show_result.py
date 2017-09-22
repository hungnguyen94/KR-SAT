#!/usr/bin/env python
from SudokuConverter import SudokuConverter
import pycosat
import argparse
from ptpython.repl import embed

def main(args):
    if args.eval:
        arr = eval(args.sudoku)
    else:
        arr = list(args.sudoku.replace(args.fill_value, '0'))
    arr = [int(x) for x in arr]
    #  solution = [int(x) for x in args.solution.split()[:-1]]

    sudoku = SudokuConverter(args.n, arr)
    cnf = sudoku.convert_to_sat()[1:]
    solution = pycosat.solve(cnf, verbose=True)
    print(solution)
    sudoku.print_board()
    sudoku.enter_solution(solution)
    sudoku.print_board()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a SAT assignment to Sudoku.')
    #  parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument("sudoku", type=str)
    parser.add_argument("--eval", type=bool, default=False)
    parser.add_argument("--solution", type=str)
    parser.add_argument("--fill_value", type=str, default='.')
    parser.add_argument("-n", type=int, default=9)
    args = parser.parse_args()
    main(args)

