import sys
import cnf_utils
from Assignment import Assignment, Assignments
import time
import resource
import random
import math

# Make Optional: Restarts, VSIDS, Clause Learning (1UIP vs Entscheidungsliterale), Klausellöschen

type Literal = int
type Clause = list[Literal]
type CNF = list[Clause]

# stats and constants
statTimeStart = time.time()
statUP = 0
statDecision = 0
statConflicts = 0
statLearnedClauses = 0
statMaxLengthLearnedClause = 0
statRestarts = 0
b = 2
c = 1.05
k = 200
c_luby = 100
numRandomDecision = 0
oldStatConflicts = 0

def getNumLiterals(cnf: CNF) -> int:
    return len(set([abs(l) for c in cnf for l in c]))

def decide():
    pass

def propagate():
    pass

def analyzeConflict():
    pass

def luby(i: int) -> int:
    k = math.floor(math.log(i,2)) + 1
    if i == 2**k-1:
        return 2**(k-1)
    return luby(i-2**(k-1)+1)

def applyRestartPolicy():
    pass

def backtrack():
    pass

def learnClause():
    pass

def CDCL(cnf: CNF) -> tuple[bool, list[Literal]]:
    ogCnfSize = len(cnf)
    numLiterals = getNumLiterals(cnf)
    # order in which the variables are assigned
    history: list[Literal] = []
    # assignment of variables (0th index is not used)
    assignments = Assignments(numLiterals, cnf)
    # list of all LBD's of clauses
    lbd: list[int] = [0] * ogCnfSize
    decisionLevel = 0
    while len(history) < numLiterals:
        # decide
        decisionLevel += 1
        decide()
        # propagate
        c_conflict = propagate()
        # conflict
        while c_conflict is not None:
            # conflict on decision level means UNSAT
            if decisionLevel == 0:
                return False, cnf[ogCnfSize:]
            c_learned, newDecisionLevel = analyzeConflict(c_conflict, decisionLevel)
            learnClause(c_learned)
            backtrack(newDecisionLevel)
            decisionLevel = newDecisionLevel
            c_conflict = propagate()
        applyRestartPolicy()
    return True, history

if len(sys.argv) == 2:
    filename = sys.argv[1]
elif len(sys.argv) == 1:
    from pathlib import Path
    filename = str(Path(__file__).parent.parent.joinpath("randomCnf.cnf"))
else:
    print("Usage: python CDCL.py filename")
    print("filename: path to the cnf file")
    sys.exit(1)
    


cnf = cnf_utils.read_cnf(filename)
sat, v = CDCL(cnf)

if not sat:
    with open("proof.drat", "w") as f:
        for clause in v:
            f.write(" ".join(map(str, clause)) + " 0"+ "\n")

statTimeEnd = time.time()
statPeakMemoryMB = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

cnf_utils.fancy_output("CDCL Solver", sat, v, filename, [
    ("unit propagations", str(statUP)),
    ("decisions", str(statDecision)),
    ("conflicts", str(statConflicts)),
    ("learned clauses", str(statLearnedClauses)),
    ("max learned clause length", str(statMaxLengthLearnedClause)),
    ("num Restarts", str(statRestarts)),
    ("peak memory", str(statPeakMemoryMB)+" MB (assumes Ubuntu)"),
    ("time", str(statTimeEnd - statTimeStart)+" s")
])