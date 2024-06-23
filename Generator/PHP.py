import sys

if len(sys.argv) != 2:
    print("Usage: python PHP.py n [outputName]")
    print("n: number of holes in the PHP")
    print("outputName: name of the output file (optional)")
    sys.exit(1)

n = int(sys.argv[1])
filenameInput = sys.argv[2] if len(sys.argv) == 3 else "PHP.cnf"
filename = filenameInput if filenameInput.endswith(".cnf") else filenameInput + ".cnf"

if n < 1:
    print("n must be at least 1")
    sys.exit(1)

clauses = []

# jede Taube muss in mind. einem Nest sein

for i in range(1, n+2):
    clause = []
    for j in range(1, n+1):
        clause.append(i*n+j)
    clauses.append(clause)

# keine 2 Tauben in einem Nest

for i1 in range(1, n+2):
    for i2 in range(i1+1, n+2):
        for j in range(1, n+1):
            clauses.append([-(i1*n+j), -(i2*n+j)])

# write to file
with open(filename, "w") as f:
    f.write("p cnf " + str(n*(n+1)) + " " + str(len(clauses)) + "\n")
    for clause in clauses:
        f.write(" ".join(map(str, clause)) + " 0\n")