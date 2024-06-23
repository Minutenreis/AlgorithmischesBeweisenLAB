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
                clause.sort(key=abs)
            if clause not in clauses:
                break
        clauses.append(clause)
    clauses.sort() # for easier visual comparison
    return clauses

if len(sys.argv) < 2 and len(sys.argv) > 5:
    print("Usage: python randomCnf.py n [c] [k] [outputName]")
    print("n: number of variables")
    print("[c]: number of clauses (optional, default: 3.8*n)")
    print("[k]: number of literals per clause (optional, default: 3)")
    print("outputName: name of the output file (optional)")
    sys.exit(1)

n = int(sys.argv[1])
c = int(sys.argv[2]) if len(sys.argv) > 2 else round(3.8 * n)
k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
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