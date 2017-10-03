import numpy as np
from typing import List
import itertools
import sys


class SudokuConverter(object):

    def __init__(self, sudoku_arr: List[int]):
        self.n = int(len(sudoku_arr)**0.5)
        rows = cols = self.n
        board = [[0 for j in range(cols)] for i in range(rows)]
        for i, cell in enumerate(sudoku_arr):
            entry: int = cell
            row_idx: int = int(i / rows)
            col_idx: int = int(i % cols)
            board[col_idx][row_idx] = entry
        self.board = np.array(board)
        self.possible_entries = list(range(1, self.n + 1))

    def col(self, col_idx: int):
        return self.board[:, col_idx]

    def row(self, row_idx: int):
        return self.board[row_idx]

    def foreach_col(self):
        for i in range(self.n):
            yield i, self.col(i)

    def foreach_row(self):
        for i in range(self.n):
            yield i, self.board[i]

    def foreach_cell(self):
        for i, j in itertools.product(range(self.n), range(self.n)):
            yield i, j, self.board[i, j]

    def cell_d(self):
        """
        Cell definedness contraint. Every cell must have at least
        one number from 1 to n.
        """
        clauses = []
        # Loop through all cell indices
        for r, c in itertools.product(range(self.n), range(self.n)):
            clause = [(r, c, v, True) for v in self.possible_entries]
            clauses.append(clause)
        return clauses

    def cell_u(self):
        """
        Cell uniqueness contraint. Every cell must have at most
        one number from 1 to n.
        """
        clauses = []
        # Loop through all cell indices
        for r, c in itertools.product(range(self.n), range(self.n)):
            for v_i in range(1, self.n):
                for v_j in range(v_i + 1, self.n + 1):
                    clause = [(r, c, v_i, False), (r, c, v_j, False)]
                    clauses.append(clause)
        return clauses

    def row_d(self):
        """
        Row definedness constraint.
        """
        clauses = []
        for r in range(self.n):
            for v in self.possible_entries:
                clause = [(r, c, v, True) for c in range(self.n)]
                clauses.append(clause)
        return clauses

    def row_u(self):
        """
        Row uniqueness contraint.
        """
        clauses = []
        for r in range(self.n):
            for v in self.possible_entries:
                for c_i in range(self.n - 1):
                    for c_j in range(c_i + 1, self.n):
                        clause = [(r, c_i, v, False), (r, c_j, v, False)]
                        clauses.append(clause)
        return clauses

    def col_d(self):
        """
        Column definedness constraint.
        """
        clauses = []
        for c in range(self.n):
            for v in self.possible_entries:
                clause = [(r, c, v, True) for r in range(self.n)]
                clauses.append(clause)
        return clauses

    def col_u(self):
        """
        Column uniqueness contraint.
        """
        clauses = []
        for c in range(self.n):
            for v in self.possible_entries:
                for r_i in range(self.n - 1):
                    for r_j in range(r_i + 1, self.n):
                        clause = [(r_i, c, v, False), (r_j, c, v, False)]
                        clauses.append(clause)
        return clauses

    def block_d(self):
        """
        Block definedness constraint.
        """
        clauses = []
        block_n = int(self.n**0.5)
        for r_offs in range(block_n):
            for c_offs in range(block_n):
                for v in self.possible_entries:
                    clause = [(r_offs * block_n + r, c_offs * block_n + c, v, True)
                              for r, c in itertools.product(range(block_n), range(block_n))]
                    clauses.append(clause)
        return clauses

    def block_u(self):
        """
        Block uniqueness constraint.
        """
        clauses = []
        block_n = int(self.n**0.5)
        for v in self.possible_entries:
            for g in range(self.n):
                r = int(g / block_n)
                c = int(g % block_n)
                for r_i, c_j in itertools.product(range(block_n * r, block_n * r + block_n), range(block_n * c, block_n * c + block_n)):
                    for r_i2, c_j2 in itertools.product(range(block_n * r, block_n * r + block_n), range(block_n * c, block_n * c + block_n)):
                        if r_i != r_i2 or c_j != c_j2:
                            if r_i >= r_i2 and c_j >= c_j2:
                                continue
                            clause = [(r_i, c_j, v, False),
                                      (r_i2, c_j2, v, False)]
                            clauses.append(clause)
        return clauses

    def assigned(self):
        """
        Constraint for the fixed cells, aka the givens.
        """
        clauses = []
        for r, c, v in self.foreach_cell():
            if v != 0:
                clause = [(r, c, v, True)]
                clauses.append(clause)
        return clauses

    def _eliminate_clauses(self, clauses, implied):
        clauses = clauses()
        #  result = []
        #  for clause in clauses:
        #  if all(atom not in implied for atom in clause):
        #  result.append(clause)
        #  return result
        return lambda: [clause for clause in clauses if all(atom not in implied for atom in clause)]

    def _eliminate_literals(self, clauses, implied):
        clauses = clauses()
        #  result = []
        #  for clause in clauses:
        #  result_clause = []
        #  for r, c, v, b in clause:
        #  if (r, c, v, not(b)) not in implied:
        #  result_clause.append([r, c, v, b])
        #  result.append(result_clause)
        #  return result
        return lambda: [[(r, c, v, b) for r, c, v, b in clause if (r, c, v, not(b)) not in implied] for clause in clauses]

    def _implied_constraints(self):
        """
        Implied constraint for the fixed cells, aka the givens.
        These should be removed from the other clauses
        """
        clauses = set()
        for r, c, v in self.foreach_cell():
            if v != 0:
                clause1 = {(r, c, v_j, False)
                           for v_j in self.possible_entries if v_j != v}
                # Add row and column constraints
                # This value should not occur in the same row and column again
                clause2 = {(r, c_j, v, False)
                           for c_j in range(self.n) if c_j != c}
                clause3 = {(r_j, c, v, False)
                           for r_j in range(self.n) if r_j != r}

                clauses = clauses | clause1 | clause2 | clause3

                block_n = int(self.n**0.5)
                r2 = int(r / block_n)
                c2 = int(c / block_n)

                # Block contraints
                # This value should not occur in the same block again
                for r_i, c_i in itertools.product(range(block_n * r2, block_n * r2 + block_n), range(block_n * c2, block_n * c2 + block_n)):
                    if r_i == r and c_i == c:
                        continue
                    clause4 = (r_i, c_i, v, False)
                    clauses.add(clause4)
        return clauses

    def convert_to_sat(self, encoding="minimal"):
        implied = self._implied_constraints()
        switcher = {
            "minimal": [
                self.cell_d,
                self.row_u,
                self.col_u,
                self.block_u,
                self.assigned
            ],
            "efficient": [
                self.cell_d,
                self.cell_u,
                self.row_u,
                self.col_u,
                self.block_u,
                self.assigned
            ],
            "extended": [
                self.cell_d,
                self.cell_u,
                self.row_d,
                self.row_u,
                self.col_d,
                self.col_u,
                self.block_d,
                self.block_u,
                self.assigned
            ],
            "optimized_minimal": [
                self._eliminate_literals(self.cell_d, implied),
                self._eliminate_clauses(self.row_u, implied),
                self._eliminate_clauses(self.col_u, implied),
                self._eliminate_clauses(self.block_u, implied),
            ],
            "optimized_efficient": [
                self._eliminate_literals(self.cell_d, implied),
                self._eliminate_clauses(self.cell_u, implied),
                self._eliminate_clauses(self.row_u, implied),
                self._eliminate_clauses(self.col_u, implied),
                self._eliminate_clauses(self.block_u, implied),
            ],
            "optimized_extended": [
                self._eliminate_literals(self.cell_d, implied),
                self._eliminate_clauses(self.cell_u, implied),
                self._eliminate_literals(self.row_d, implied),
                self._eliminate_clauses(self.row_u, implied),
                self._eliminate_literals(self.col_d, implied),
                self._eliminate_clauses(self.col_u, implied),
                self._eliminate_literals(self.block_d, implied),
                self._eliminate_clauses(self.block_u, implied),
            ]
        }
        clauses_encodings = switcher.get(encoding)  # , switcher["minimal"])

        clauses = []
        for enc in clauses_encodings:
            clauses.extend(enc())

        dimacs = [[self.atom_to_dimacs(atom) for atom in disjunction]
                  for disjunction in clauses]

        info = ['p', "cnf", self.n**3, len(clauses)]
        dimacs.insert(0, info)
        return dimacs

    def atom_to_dimacs(self, atom):
        n = self.n
        r, c, v, b = atom
        index = r * (n**2) + c * n + v
        return int(index if b else -index)

    def dimacs_to_atom(self, atom: int):
        b = atom > 0
        atom = abs(atom)
        row = int(atom / (self.n**2))
        col = int((atom - (row * self.n**2)) / self.n)
        val = atom - (row * (self.n**2) + col * self.n)

        # Cover this edge case, because values cannot be 0
        # If value == 0, its actually 9 and in the previous column
        if val == 0:
            if col == 0:
                row -= 1
                col = self.n - 1
                val = self.n
            else:
                col -= 1
                val = self.n
        return row, col, val, b

    def enter_solution(self, solution):
        s = [self.dimacs_to_atom(atom) for atom in solution]
        for row, col, val, b in s:
            if b:
                self.board[row, col] = val

    def print_board(self):
        output = ""
        block_n = int(self.n**0.5)
        for i, row in self.foreach_row():
            if i % block_n == 0 and i != 0:
                for i in range(block_n):
                    output += '-' * (self.n)
                    output += '\t'
                output += "\n"
            for j, val in enumerate(row):
                if j % block_n == 0 and j != 0:
                    output += '\t | '
                output += f" {val} "
            output += "\n"
        output += "\n\n"
        print(output)


def pretty_print(clauses):
    output = ""
    output += " ".join(str(x) for x in clauses[0])
    output += "\n"
    for clause in clauses[1:]:
        dnj = " ".join(str(x) for x in clause)
        dnj += " 0\n"
        output += dnj
    print(output)
