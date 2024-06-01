from copy import deepcopy
import sys
import cnf_utils
import time
import resource

statTimeStart = time.time()
statUP = 0
statDecision = 0
statConflicts = 0
statLearnedClauses = 0
statMaxLengthLearnedClause = 0


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
    global statConflicts
    i = 0
    
    decidedClauses = []
    while i < len(cnf):
        print(i)
        clause = cnf[i]
        
        if len(clause) > 1:
            # clause is satisfied
            if clause[0] in v[0] or clause[1] in v[0]:
                i += 1
                continue
            if -clause[0] in v[0]:
                for i in range(1, len(clause)):
                    if -clause[i] not in v[0]:
                        clause[0], clause[i] = clause[i], clause[0]
                        break
                # no non negative literal found -> conflict
                else: 
                    statConflicts += 1
                    return v, decidedClauses + [clause]
            # new literal is true -> invariant fulfilled
            if clause[0] in v[0]:
                i += 1
                continue
            if -clause[1] in v[0]:
                for i in range(2, len(clause)):
                    if -clause[i] not in v[0]:
                        clause[1], clause[i] = clause[i], clause[1]
                        break
                # only 1 non negative literal found -> unit propagation
                else: 
                    v[0].append(clause[0])
                    v[1].append(decisionLevel)
                    decidedClauses.append(clause)
                    i = 0
                    statUP += 1
                    continue
        # clause only contains one literal -> conflict if false, unit propagation if not yet true
        else:
            if -clause[0] in v[0]:
                statConflicts += 1
                return v, decidedClauses + [clause]
            elif clause[0] not in v[0]:
                v[0].append(clause[0])
                v[1].append(decisionLevel)
                decidedClauses.append(clause)
                i = 0
                statUP += 1
                continue
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
    
    global statMaxLengthLearnedClause
    global statLearnedClauses
    statLearnedClauses += 1
    statMaxLengthLearnedClause = max(statMaxLengthLearnedClause, len(learnedClause))
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
    ("learned clauses", str(statLearnedClauses)),
    ("max learned clause length", str(statMaxLengthLearnedClause)),
    ("peak memory", str(statPeakMemoryMB)+" MB (assumes Ubuntu)"),
    ("time", str(statTimeEnd - statTimeStart)+" s")
])