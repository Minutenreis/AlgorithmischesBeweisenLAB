from copy import deepcopy
import sys
import cnf_utils
import time
import resource

statTimeStart = time.time()
statUP = 0
statDecision = 0
statConflicts = 0


def getAllLiterals(cnf: list[list[int]]) -> set[int]:
    return set([abs(l) for c in cnf for l in c])

# todo: optimize this method 
def decide(cnf: list[list[int]], v: tuple[list[int], list[int]], decisionLevel: int, decidedLiterals: list[int]) -> set[int]:
    global statDecision
    statDecision += 1
    
    for clause in cnf:
        for literal in clause:
            if literal not in v[0] and -literal not in v[0]:
                v[0].append(literal)
                v[1].append(decisionLevel)
                decidedLiterals.append(literal)
                return v
    raise Exception("All literals are assigned")
        
            
def propagate(cnf: list[list[int]], v: tuple[list[int], list[int]], decisionLevel: int) -> tuple[tuple[list[int], list[int]], list[list[int]]]:   
    global statUP
    i = 0
    
    decidedClauses = []
    while i < len(cnf):
        clause = cnf[i]
        unassignedLiteral = 0
        numUnassigned = 0
        for literal in clause:
            # clause is satisfied
            if literal in v[0]:
                numUnassigned = -1
                break
            # variable is assigned
            if -literal in v[0]:
                continue
            
            unassignedLiteral = literal
            numUnassigned += 1
            
        # clause is a unit clause -> assign the unassigned literal
        if numUnassigned == 1:
            v[0].append(unassignedLiteral)
            v[1].append(decisionLevel)
            decidedClauses.append(clause)
            i = 0
            statUP += 1
            continue
        # clause is unsatisfied
        elif numUnassigned == 0:
            global statConflicts
            statConflicts += 1
            return v, decidedClauses + [clause]
        
        i += 1
    return v, None

def analyzeConflict(v: tuple[list[int], list[int]], c_conflict: list[list[int]], decisionLevel: int) -> tuple[list[int], int]:
    previousLevelLiterals = set()
    currentLevelLiterals = set()
    
    index = -1
    for literal in c_conflict[index]:
        level = v[1][v[0].index(-literal)]
        if level == decisionLevel:
            currentLevelLiterals.add(-literal)
        else:
            previousLevelLiterals.add((-literal, level))
    
    while len(currentLevelLiterals) > 1:
        index -= 1    
        clauseToResolve = c_conflict[index]
        # unrelated unit propagation
        if not any([literal in currentLevelLiterals for literal in clauseToResolve]):
            continue
        
        # resolve over literal backwards
        for literal in clauseToResolve:
            # implied literal, now not pointed to
            if literal in currentLevelLiterals:
                currentLevelLiterals.remove(literal)
                continue
            level = v[1][v[0].index(-literal)]
            if level == decisionLevel:
                currentLevelLiterals.add(-literal)
            else:
                previousLevelLiterals.add((-literal,level))
    
    UIP1 = currentLevelLiterals.pop()
    
    nextDecisionLevel = 0
    for literal in previousLevelLiterals:
        if literal[1] > nextDecisionLevel:
            nextDecisionLevel = literal[1]
    
    learnedClause = [-UIP1] + [-literal[0] for literal in previousLevelLiterals]
    return learnedClause, nextDecisionLevel
               
                
# todo implement
def applyRestartPolicy(cnf: list[list[int]], v: tuple[list[int], list[int]], decisionLevel: int, ogCnf: list[list[int]]):
    return cnf, v, decisionLevel

def backtrack(v : tuple[list[int], list[int]], new_decision_level: int, decidedLiterals: list[int]) -> tuple[tuple[list[int], list[int]],list[int]]:
    if new_decision_level == 0:
        return ([],[]), []
    
    decidedLiterals = decidedLiterals[:new_decision_level]
    for i, literal in enumerate(v[1]):
        if literal >= new_decision_level:
            return (v[0][:i]+[decidedLiterals[-1]], v[1][:i]+[new_decision_level]), decidedLiterals
    else:
        raise Exception("No literal found to backtrack")

# if sat, return True and v, else return False and list of added clauses
def CDCL(cnf: list[list[int]]) -> tuple[bool, list[int] | list[list[int]]] :
    ogCnf = deepcopy(cnf)
    decisionLevel = 0
    decidedLiterals = []
    allLiterals = getAllLiterals(cnf)
    v : tuple[list[int], list[int]] = ([],[])
    while len(v[0]) < len(allLiterals):
        decisionLevel += 1
        v = decide(cnf, v, decisionLevel, decidedLiterals)
        v, c_conflict = propagate(cnf, v, decisionLevel)
        while c_conflict is not None:
            if decisionLevel == 0:
                return False, cnf[len(ogCnf):]
            c_learned, decisionLevel = analyzeConflict(v, c_conflict, decisionLevel)
            cnf.append(c_learned)
            v, decidedLiterals = backtrack(v, decisionLevel, decidedLiterals)
            v, c_conflict = propagate(cnf, v, decisionLevel)
        cnf,v,decisionLevel = applyRestartPolicy(cnf, v, decisionLevel, ogCnf)
    return True, v[0]

# print(backtrack(([1,7,2,3,4], [1,1,2,2,2]), 1, [1,2]))
# sys.exit()     

if len(sys.argv) != 2:
    sys.exit("Usage: python CDCL.py filename")

filename = sys.argv[1]

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
    ("peak memory", str(statPeakMemoryMB)+" MB (assumes Ubuntu)"),
    ("time", str(statTimeEnd - statTimeStart)+" s")
])