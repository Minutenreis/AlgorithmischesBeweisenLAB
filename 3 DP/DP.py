import sys
import time
import cnf_utils

statTimeStart = time.time()
statUP = 0
statAddedClauses = 0
statPureLiteralRemovedClauses = 0
statSubsumedClauses = 0

# remove all clauses that are strictly larger than another clause
def subsumption(cnf: list[list[int]]) -> list[list[int]]:
    global statSubsumedClauses
    
    i = 0
    while i < len(cnf):
        c = cnf[i]
        for j in range(i+1, len(cnf)):
            if all([l in cnf[j] for l in c]):
                cnf.pop(j)
                i = 0
                statSubsumedClauses += 1
                break
        i += 1
    return cnf

# remove tautologies and duplicates
def remove_tautologies_and_duplicates(cnf: list[list[int]]) -> list[list[int]]:
    # remove tautologies
    cnf = [c for c in cnf if not any([l == -l for l in c])]
    # remove duplicates
    cnf = [list(set(c)) for c in cnf]
    return cnf

# remove variable if it exists in only 1 polarity
def pure_literal_elimination(cnf: list[list[int]]) -> list[list[int]]:
    global statPureLiteralRemovedClauses
    
    # all literals in cnf
    literals = set([l for c in cnf for l in c]) 
    for l in literals:
        if -l not in literals:
            statClausesBefore = len(cnf)
            cnf = unit_propagation(cnf, l)
            statPureLiteralRemovedClauses += statClausesBefore - len(cnf)
    return cnf

# repeat unit propagation until no more unit clauses are found
def complete_unit_propagation(cnf: list[list[int]]) -> list[list[int]]:
    i = 0
    while i < len(cnf):
        if len(cnf[i]) == 1:
            literal = cnf[i][0]
            cnf = unit_propagation(cnf, literal)
            i = 0
            continue # skip increment
        i += 1
    return cnf

# unit_propagation: set variable (eg. 3 or -3) to true -> -3 = true implies 3 to be false for all clauses
def unit_propagation(cnf: list[list[int]], variable: int) -> list[list[int]]:
    global statUP
    statUP += 1
    
    # remove clauses with the variable
    cnf = [c for c in cnf if variable not in c]
    # remove negated literals from clauses
    cnf = [[l for l in c if l != -variable] for c in cnf]
    return cnf

# merge clauses without literal and its negation
def addResolvent(clause1: list[int], clause2: list[int], literal: int) -> list[list[int]]:
    global statAddedClauses
    statAddedClauses += 1
    return [l for l in clause1 + clause2 if l != literal and l != -literal]

def DP(cnf: list[list[int]]) -> bool:
    while True:
        last_cnf= cnf
        while last_cnf == cnf:
            cnf = complete_unit_propagation(cnf)
            cnf = remove_tautologies_and_duplicates(cnf)
            cnf = pure_literal_elimination(cnf)
            cnf = subsumption(cnf)
        if len(cnf) == 0:
            return True
        if [] in cnf:
            return False
        # choose a variable
        literal = cnf[0][0]
        new_cnf = cnf.copy()

        for i in range(len(cnf)):
            if literal in cnf[i]:
                for j in range(i+1, len(cnf)):
                    if -literal in cnf[j]:
                        new_cnf.append(addResolvent(cnf[i], cnf[j], literal))
            if -literal in cnf[i]:
                for j in range(i+1, len(cnf)):
                    if literal in cnf[j]:
                        new_cnf.append(addResolvent(cnf[i], cnf[j], literal))
        cnf = [c for c in new_cnf if literal not in c and -literal not in c]
    

if len(sys.argv) != 2:
    print("Usage: python DP.py filename")
    sys.exit(1)

filename = sys.argv[1]

cnf = cnf_utils.read_cnf(filename)
sat = DP(cnf)

statTimeEnd = time.time()

cnf_utils.fancy_output("DP Solver", sat, None, filename, [
    ("unit propagations", str(statUP)),
    ("added clauses", str(statAddedClauses)),
    ("pure literal removed clauses", str(statPureLiteralRemovedClauses)),
    ("subsumed clauses", str(statSubsumedClauses)),
    ("time", str(statTimeEnd - statTimeStart)+" s")
])