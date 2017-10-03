import subprocess
import re
import csv
import sys
import os

header_pattern = re.compile("^=+\[\s*(?P<header>\w+) Statistics\s*\]=+$")
problem_stats_pattern = re.compile("^\|\s*(.+):\s*(\w+)(?:\w|\s)*\|$")
statis_pattern = re.compile(
    "^\|?\s*(?P<attribute>.+?)\s*:\s*(?P<value>.+?)\s*(?P<extra>\(.+\))?\s*\|?$")
search_stats_pattern = re.compile(
    "^\|\s*(?P<conflicts>\w+)\s*\|\s*(?P<vars>\w+)\s*(?P<clauses>\w+)\s*(?P<literals>\w+)\s*\|\s*(?P<limit>\w+)\s*(?P<learntclauses>\w+)\s*(?P<litcl>\w+)\s*\|\s*(?P<progress>.+)\s%\s*\|$")
footer_pattern = re.compile("^=+$")


def parse_minisat_output(lines: str) -> dict:
    result: dict = {}
    index = 0
    # iter to the header
    while index < len(lines):
        line = lines[index]
        index += 1
        # Reached the problem statistics header
        if header_pattern.match(line):
            break
    index += 1
    while index < len(lines):
        line = lines[index]
        index += 1
        m = statis_pattern.match(line)
        if m:
            attribute = m.group("attribute")
            value = m.group("value")
            result[attribute] = value
        else:
            # Reached search statistics header
            if header_pattern.match(line):
                # Skip to the data
                index += 3
                break
    while index < len(lines):
        line = lines[index]
        index += 1
        # We only care about the last one,
        # so keep overwriting the result with
        # the last search stats
        m = search_stats_pattern.match(line)
        if m:
            result["Conflicts"] = m.group("conflicts")
            result["ORIGINAL Vars"] = m.group("vars")
            result["ORIGINAL Clauses"] = m.group("clauses")
            result["ORIGINAL Literals"] = m.group("literals")
            result["LEARNT Limit"] = m.group("limit")
            result["LEARNT Clauses"] = m.group("learntclauses")
            result["LEARNT Lit/Cl"] = m.group("litcl")
            result["Progress"] = m.group("progress")
        else:
            if footer_pattern.match(line):
                break
    while index < len(lines):
        line = lines[index]
        index += 1
        m = statis_pattern.match(line)
        if m:
            attribute = m.group("attribute")
            value = m.group("value")
            result[attribute] = value
    return result


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Specify a filename", file=sys.stderr)
        exit(1)
    else:
        sudoku_file = sys.argv[1]
        if len(sys.argv) > 2:
            offset = int(sys.argv[2])
        else:
            offset = 0

        with open(f"results/{os.path.basename(sudoku_file)}.csv", 'a') as csvfile:

            fieldnames = ["Sudoku", "Number of variables", "Number of clauses", "Parse time", "Eliminated clauses", "Simplification time", "Conflicts", "ORIGINAL Vars", "ORIGINAL Clauses", "ORIGINAL Literals", "LEARNT Limit",
                          "LEARNT Clauses", "LEARNT Lit/Cl", "Progress", "restarts", "conflicts", "decisions", "propagations", "conflict literals", "Memory used", "CPU time", "Encoding", "parsed_text", "solution"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            with open(sudoku_file, mode='r') as f:
                for i, line in enumerate(f):
                    if i < offset:
                        continue
                    for encoding in ["minimal", "efficient", "extended", "optimized_minimal", "optimized_efficient", "optimized_extended"]:
                        sudoku = line.strip()
                        print(f"index: {i}")
                        print(f"Sudoku: {sudoku}")
                        print(f"Encoding: {encoding}")
                        minisat = subprocess.Popen(f"python print_dimacs.py --sudoku={sudoku} --encoding={encoding} | docker exec -i minisat minisat",
                                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        try:
                            out, err = minisat.communicate(timeout=60)
                            row = parse_minisat_output(
                                err.decode().splitlines())
                            row["Sudoku"] = str(sudoku)
                            row["Encoding"] = encoding
                            row["parsed_text"] = err
                            row["solution"] = out
                            print(err.decode())
                            writer.writerow(row)
                        except subprocess.TimeoutExpired:
                            minisat.kill()
                            print("Killed")
