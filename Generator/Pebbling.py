import sys

if len(sys.argv) != 2:
    print("Usage: python PHP.py n [outputName]")
    print("n: number of source nodes")
    print("outputName: name of the output file (optional)")
    sys.exit(1)

n = int(sys.argv[1])
filenameInput = sys.argv[2] if len(sys.argv) == 3 else "Pebbling.cnf"
filename = filenameInput if filenameInput.endswith(".cnf") else filenameInput + ".cnf"

if n < 2:
    print("n must be at least 2")
    sys.exit(1)

numLiterals = n * (n + 1)//2

clauses = []

# nodes are numbered left to right, top to bottom; each node gets 2 literals (one for black, one for white)
# the first one being its index, the second one being its index + n*(n+1)/2

# all source nodes must be either black or white
for i in range(n):
    clauses.append([i+1, i+numLiterals+1])

# if both parent nodes have a color, the child must have a color
previousLineLength = n
currentLineSize = 0

for v in range(n,numLiterals):
    currentLineSize += 1
    # next line
    if currentLineSize == previousLineLength:
        previousLineLength = currentLineSize-1
        currentLineSize = 1
    for a in range(2):
        for b in range(2):
            # left parent, right parent, self, self in White
            clauses.append([-(v-previousLineLength+a*numLiterals+1), -(v-previousLineLength+1+b*numLiterals+1), v+1,v+numLiterals+1])

# final node may not have a stone
clauses.append([-numLiterals, -numLiterals*2])

# write to file
with open(filename, "w") as f:
    f.write("p cnf " + str(n*(n+1)) + " " + str(len(clauses)) + "\n")
    for clause in clauses:
        f.write(" ".join(map(str, clause)) + " 0\n")
            