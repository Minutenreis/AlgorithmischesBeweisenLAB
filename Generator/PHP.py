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

cnf = []

# jede Taube muss in mind. einem Nest sein
# i = Taube column, j = Nest row, row major
for i in range(n+1):
    clause = []
    for j in range(n):
        clause.append(i+j*(n+1)+1)
    cnf.append(clause)

# keine 2 Tauben in einem Nest

for j in range(n):
    for i1 in range(n+1):
        for i2 in range(i1+1, n+1):
            cnf.append([-(i1+j*(n+1)+1), -(i2+j*(n+1)+1)])

# write to file
with open(filename, "w") as f:
    f.write("p cnf " + str(n*(n+1)) + " " + str(len(cnf)) + "\n")
    for clause in cnf:
        f.write(" ".join(map(str, clause)) + " 0\n")