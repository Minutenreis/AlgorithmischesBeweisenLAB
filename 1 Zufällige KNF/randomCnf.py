import sys
import random
import math

# n: number of variables
# c: number of clauses
# k: number of literals per clause
def random_cnf(n, c, k):
    clauses = []
    for _ in range(c):
        while True:
            clause = []
            possibleLiterals = list(range(1, n+1))
            for _ in range(k):
                literal = possibleLiterals.pop(random.randrange(len(possibleLiterals)))
                if random.random() < 0.5: # 50% chance to negate the literal
                    literal = -literal
                clause.append(literal)
            if clause not in clauses:
                break
        clauses.append(clause)
    return clauses

if len(sys.argv) != 4:
    print("Usage: python randomCnf.py n c k")
    print("n: number of variables")
    print("c: number of clauses")
    print("k: number of literals per clause")
    sys.exit(1)

n = int(sys.argv[1])
c = int(sys.argv[2])
k = int(sys.argv[3])

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

f = open("randomCnf.cnf", "w")
f.write("p cnf " + str(n) + " " + str(c) + "\n")
for clause in clauses:
    f.write(" ".join(map(str, clause)) + " 0\n")