from copy import deepcopy
import sys
import cnf_utils
import time
import resource

type Literal = int
type Level = int
type Set = set[Literal]
type Clause = list[Literal]
type CNF = list[Clause]
type LevelList = list[Level]
type LiteralList = list[Literal]
type Conflict = list[Clause]
type V = tuple[LiteralList, LevelList, Set]

statTimeStart = time.time()
statUP = 0
statDecision = 0
statConflicts = 0
statLearnedClauses = 0
statMaxLengthLearnedClause = 0


def getNumLiterals(cnf: CNF) -> int:
    return len(set([abs(l) for c in cnf for l in c]))

def setLiteral(v: V,literal: Literal, decisionLevel: Level) -> V:
    v[0].append(literal)
    v[1].append(decisionLevel)
    v[2].add(literal)
    return v

# todo: optimize this method 
def decide(cnf: CNF, v: V, decisionLevel: Level) -> V:
    global statDecision
    statDecision += 1
    
    for clause in cnf:
        for literal in clause:
            if literal not in v[2] and -literal not in v[2]:
                return setLiteral(v, literal, decisionLevel)
    raise Exception("All literals are assigned")
        
            
def propagate(cnf: CNF, v: V, decisionLevel: Level) -> tuple[V,Conflict]:   
    global statUP
    global statConflicts
    i = 0
    
    decidedClauses = []
    while i < len(cnf):
        clause = cnf[i]
        
        if len(clause) > 1:
            # clause is satisfied
            if clause[0] in v[2] or clause[1] in v[2]:
                i += 1
                continue
            
            if -clause[0] in v[2]:
                for j in range(1, len(clause)):
                    if -clause[j] not in v[2]:
                        clause[0], clause[j] = clause[j], clause[0]
                        break
                # no non negative literal found -> conflict
                else: 
                    statConflicts += 1
                    return v, decidedClauses + [clause]
            # new literal is true -> invariant fulfilled
            if clause[0] in v[2]:
                i += 1
                continue
            if -clause[1] in v[2]:
                for j in range(2, len(clause)):
                    if -clause[j] not in v[2]:
                        clause[1], clause[j] = clause[j], clause[1]
                        break
                # only 1 non negative literal found -> unit propagation
                else: 
                    setLiteral(v, clause[0], decisionLevel)
                    decidedClauses.append(clause)
                    i = 0
                    statUP += 1
                    continue
        # clause only contains one literal -> conflict if false, unit propagation if not yet true
        else:
            if clause[0] in v[2]:
                i += 1
                continue
            elif -clause[0] in v[2]:
                statConflicts += 1
                return v, decidedClauses + [clause]
            else:
                setLiteral(v, clause[0], decisionLevel)
                decidedClauses.append(clause)
                i = 0
                statUP += 1
                continue
        i += 1
    return v, None

def analyzeConflict(v: V, c_conflict: Conflict, decisionLevel: Level) -> tuple[Clause, Level]:
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
def applyRestartPolicy(cnf: CNF, v: V, decisionLevel: Level, ogCnf: CNF) -> tuple[CNF, V, Level]:
    return cnf, v, decisionLevel

def backtrack(v : V, new_decision_level: Level) -> V:
    if new_decision_level == 0:
        return [],[], set()
    
    for i, level in enumerate(v[1]):
        # first found literal is decisionLiteral of that level
        if level >= new_decision_level:
            literalsToRemove = v[0][i+1:]
            v[2].difference_update(literalsToRemove)
            return v[0][:i+1], v[1][:i+1], v[2]
    else:
        raise Exception("No literal found to backtrack")

# if sat, return True and v, else return False and list of added clauses
def CDCL(cnf: CNF) -> tuple[True, list[int]] | tuple[False,  list[Clause]] :
    ogCnf = deepcopy(cnf)
    decisionLevel = 0
    numLiterals = getNumLiterals(cnf)
    v : tuple[list[int], list[int], set[int]] = ([],[],set())
    while len(v[0]) < numLiterals:
        decisionLevel += 1
        v = decide(cnf, v, decisionLevel)
        v, c_conflict = propagate(cnf, v, decisionLevel)
        while c_conflict is not None:
            if decisionLevel == 0:
                return False, cnf[len(ogCnf):]
            c_learned, decisionLevel = analyzeConflict(v, c_conflict, decisionLevel)
            cnf.append(c_learned)
            v = backtrack(v, decisionLevel)
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