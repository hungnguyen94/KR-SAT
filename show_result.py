#!/usr/bin/env python
from SudokuConverter import SudokuConverter
import argparse
import sys

def main(args):
    if args.pycosat:
        import pycosat
        cnf = sudoku.convert_to_sat()[1:]
        solution = pycosat.solve(cnf, verbose=True)
    else:
        sol_str = "".join(args.solution.readlines())
        solution = [int(x) for x in sol_str.split()[:-1]]

    if args.sudoku == '':
        args.sudoku = '0' * round(len(solution)**(1/3))**2

    if args.eval:
        arr = eval(args.sudoku)
    else:
        arr = list(args.sudoku.replace(args.fill_value, '0'))
    arr = [int(x) for x in arr]

    sudoku = SudokuConverter(arr)
    sudoku.enter_solution(solution)
    sudoku.print_board()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a SAT assignment to Sudoku.')
    parser.add_argument('solution', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument("--sudoku", type=str, default='')
    parser.add_argument("--eval", type=bool, default=False)
    #  parser.add_argument("--solution", type=str)
    parser.add_argument("--fill_value", type=str, default='.')
    parser.add_argument("--pycosat", type=bool, default=False)
    args = parser.parse_args()
    main(args)

