import sys
import random
import math

# n: number of variables
# c: number of clauses
# k: number of literals per clause
def random_cnf(n, c, k):
    clauses = []
    for _ in range(c):
        # repeat clause generation until a new clause is found
        while True:
            clause = []
            # all possible literals (excluding negations)
            possibleLiterals = list(range(1, n+1))
            for _ in range(k):
                # get and remove a random literal from the list
                literal = possibleLiterals.pop(random.randrange(len(possibleLiterals)))
                # randomly negate the literal
                if random.random() < 0.5: 
                    literal = -literal
                clause.append(literal)
            if clause not in clauses:
                break
        clauses.append(clause)
    return clauses

if len(sys.argv) != 4 and len(sys.argv) != 5:
    print("Usage: python randomCnf.py n c k [outputName]")
    print("n: number of variables")
    print("c: number of clauses")
    print("k: number of literals per clause")
    print("outputName: name of the output file (optional)")
    sys.exit(1)

n = int(sys.argv[1])
c = int(sys.argv[2])
k = int(sys.argv[3])
filenameInput = sys.argv[4] if len(sys.argv) == 5 else "randomCnf.cnf"
filename = filenameInput if filenameInput.endswith(".cnf") else filenameInput + ".cnf"

if n <= 1 or c <= 1 or k <= 1:
    print("n, c and k must be greater than 1")
    sys.exit(1)
if k > n:
    print("k must be smaller or equal to n")
    sys.exit(1)
if c > math.comb(n, k) * 2**k:
    print("c must be smaller or equal to n choose k * 2^k = " + str(math.comb(n, k) * 2**k))
    sys.exit(1)
    
clauses = random_cnf(n, c, k)

f = open(filename, "w")
f.write("p cnf " + str(n) + " " + str(c) + "\n")
for clause in clauses:
    f.write(" ".join(map(str, clause)) + " 0\n")