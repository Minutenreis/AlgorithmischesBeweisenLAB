import sys
import cnf_utils

if len(sys.argv) != 3:
    print("Usage: python checkTruthyness.py cnf output")
    print("file1: path to cnf file")
    print("file2: path to output file")
    sys.exit(1) 

cnfFile = sys.argv[1]
outputFile = sys.argv[2]

cnf = cnf_utils.read_cnf(cnfFile)

variables = set()
with open(outputFile) as f:
    for line in f:
        if line.startswith("v"):
            variables.update(map(int, line.split()[1:]))

for clause in cnf:
    if not any(lit in variables for lit in clause):
        print("Clause not satisfied: " + str(clause))
        sys.exit(1)

print("All clauses satisfied")
sys.exit(0)
