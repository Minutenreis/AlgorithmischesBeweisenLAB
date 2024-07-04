import sys
import cnf_utils
import time
import resource


flagPureLiteralElimination = True
statTimeStart = time.time()
statUP = 0
statDecision = 0
statPureLiteralRemovedVars = 0

"""
removes all unit clauses, returns if it changed v
"""
def complete_unit_propagation(cnf: list[list[int]], v: set[int]):
    global statUP
    i = 0
    
    while i < len(cnf):
        clause = cnf[i]
        unassignedLiteral = 0
        numUnassigned = 0
        for literal in clause:
            # clause is satisfied
            if literal in v:
                numUnassigned = 0
                break
            # variable is assigned
            if -literal in v:
                continue
            
            unassignedLiteral = literal
            numUnassigned += 1
        # clause is a unit clause -> assign the unassigned literal
        if numUnassigned == 1:
            v.add(unassignedLiteral)
            i = 0
            statUP += 1
            continue
        i += 1
    return v
        
"""
removes all literals that only exist in one polarity
"""    
def pure_literal_elimination(cnf: list[list[int]], v: set[int]):
    if not flagPureLiteralElimination:
        return
    literals = set()
    for clause in cnf:
        # if clause isnt satisfied, note all literals
        if not any(literal in v for literal in clause):
            literals.update(clause)
    for literal in literals:
        # literal already set
        if -literal in v:
            continue
        if -literal not in literals:
            v.add(literal)
            global statPureLiteralRemovedVars
            statPureLiteralRemovedVars += 1

"""
returns the first literal that is not yet assigned as they come up in the cnf
"""
def get_decision_variable(cnf: list[list[int]], v: set[int]) -> int:
    global statDecision
    statDecision += 1
    # find the first literal that is not yet assigned
    for clause in cnf:
        for literal in clause:
            if not literal in v and not -literal in v:
                return literal

"""
returns 1 if the formula is satisfied, 0 if its not decided and -1 if the formula is unsatisfiable
"""
def is_finished(cnf: list[list[int]], v: set[int]) -> bool:
    satisfied = True
    for clause in cnf:
        allLiteralsFalse = True
        clauseSatisfied = False
        for literal in clause:
            if not -literal in v:
                allLiteralsFalse = False
            if literal in v:
                clauseSatisfied = True
                break
        # if all literals are false, the clause is unsatisfiable
        if allLiteralsFalse:
            return -1
        # if at least one clause is not satisfied, the formula is not satisfied
        if not clauseSatisfied:
            satisfied = False
    return 1 if satisfied else 0

"""
David-Putnam-Logemann-Loveland algorithm
@input a cnf and current assignment v
@output (True, v) if the formula is satisfiable, (False, None) if the formula is unsatisfiable
calls itself recursively
"""
def DPLL(cnf: list[list[int]], v: set[int] = set()) -> tuple[bool,set[int]]:
    oldLen = -1
    while oldLen != len(v):
        oldLen = len(v)
        pure_literal_elimination(cnf, v)
        complete_unit_propagation(cnf, v)
    
    finished = is_finished(cnf, v)
    if finished == 1:
        return True, v
    elif finished == -1:
        return False, None
    x = get_decision_variable(cnf, v)
    
    vCopy = v.copy()
    vCopy.add(-x)
    
    resNeg = DPLL(cnf, vCopy)
    if resNeg[0]:
        return resNeg
    
    v.add(x)
    return DPLL(cnf, v)
    
"""
parses argv for filename, reads it in with cnf_utils and runs CDCL
outputs the result and some statistics
"""
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print("Usage: python DPLL.py filename [PureLiteralBool]")
    print("filename: path to the cnf file")
    print("PureLiteralBool: 0 or 1, if 1 pure literal elimination is enabled")
    sys.exit(1)

filename = sys.argv[1]
if len(sys.argv) == 3:
    flagPureLiteralElimination = bool(int(sys.argv[2]))

cnf = cnf_utils.read_cnf(filename)
sat, v = DPLL(cnf)

statTimeEnd = time.time()
statPeakMemoryMB = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

cnf_utils.fancy_output("DP Solver", sat, v, filename, [
    ("unit propagations", str(statUP)),
    ("decisions", str(statDecision)),
    ("pure literal removed variables", str(statPureLiteralRemovedVars)),
    ("peak memory", str(statPeakMemoryMB)+" MB (assumes Ubuntu)"),
    ("time", str(statTimeEnd - statTimeStart)+" s")
])