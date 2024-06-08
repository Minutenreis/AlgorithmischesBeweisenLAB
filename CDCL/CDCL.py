from copy import deepcopy
import sys
import cnf_utils
import time
import resource
import random
import math

type Literal = int
type Level = int
# tuple[isSet,assignment,count]
type Info = list[bool,int,float]
type LiteralInfoArray = list[Info]
type Clause = list[Literal]
type CNF = list[Clause]
type LevelList = list[Level]
type LiteralList = list[Literal]
type Conflict = list[Clause]
type V = tuple[LiteralList, LevelList, LiteralInfoArray]

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
numRandomDecision = 0
oldStatConflicts = 0

def isIn(literal: Literal, v: V) -> bool:
    info = v[2][abs(literal)-1]
    return info[0] and info[1] == literal

def getNumLiterals(cnf: CNF) -> int:
    return len(set([abs(l) for c in cnf for l in c]))

def setLiteral(v: V,literal: Literal, decisionLevel: Level) -> V:
    v[0].append(literal)
    v[1].append(decisionLevel)
    v[2][abs(literal)-1][0] = True
    v[2][abs(literal)-1][1] = literal
    return v

def decide(cnf: CNF, v: V, decisionLevel: Level) -> V:
    global statDecision
    statDecision += 1
    
    global statConflicts
    global numRandomDecision
    global k
    if numRandomDecision * k < statConflicts:
        numRandomDecision += 1
        # get random unset literal
        allUnsetLiterals = [info[1] for info in v[2] if info[0] == False]
        literal = random.choice(allUnsetLiterals)
        return setLiteral(v,literal, decisionLevel)
    
    max = 0
    literal = 0
    for info in v[2]:
        if not info[0] and info[2]>=max:
            max = info[2]
            literal = info[1]
            
    return setLiteral(v, literal, decisionLevel)
            
def propagate(cnf: CNF, v: V, decisionLevel: Level) -> tuple[V,Conflict]:   
    global statUP
    global statConflicts
    i = 0
    
    decidedClauses = []
    while i < len(cnf):
        clause = cnf[i]
        
        if len(clause) > 1:
            # clause is satisfied
            if isIn(clause[0],v) or isIn(clause[1],v):
                i += 1
                continue
            
            if isIn(-clause[0],v):
                for j in range(1, len(clause)):
                    if not isIn(-clause[j],v):
                        clause[0], clause[j] = clause[j], clause[0]
                        break
                # no non negative literal found -> conflict
                else: 
                    statConflicts += 1
                    return v, decidedClauses + [clause]
            # new literal is true -> invariant fulfilled
            if isIn(clause[0],v):
                i += 1
                continue
            if isIn(-clause[1],v):
                for j in range(2, len(clause)):
                    if not isIn(-clause[j],v):
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
            if isIn(clause[0],v):
                i += 1
                continue
            elif isIn(-clause[0],v):
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
    allLiteralsInConflict = set()
    
    index = -1
    for literal in c_conflict[index]:
        level = v[1][v[0].index(-literal)]
        if level == decisionLevel:
            currentLevelLiterals.add(-literal)
            allLiteralsInConflict.add(-literal)
        else:
            previousLevelLiterals.add((-literal, level))
            allLiteralsInConflict.add(-literal)
    
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
                allLiteralsInConflict.add(-literal)
            else:
                previousLevelLiterals.add((-literal,level))
                allLiteralsInConflict.add(-literal)
    
    UIP1 = currentLevelLiterals.pop()
    
    # find next decision level
    nextDecisionLevel = 0
    for literal in previousLevelLiterals:
        if literal[1] > nextDecisionLevel:
            nextDecisionLevel = literal[1]
            
    # update VSIDS
    global b
    global c
    for literal in allLiteralsInConflict:
        v[2][abs(literal)-1][2] += b
    b *= c
    
    # scale all numbers if b is too large
    if b > 10**30:
        for info in v[2]:
            info[2] /= b
        b = 1
    
    learnedClause = [-UIP1] + [-literal[0] for literal in previousLevelLiterals]
    
    global statMaxLengthLearnedClause
    global statLearnedClauses
    statLearnedClauses += 1
    statMaxLengthLearnedClause = max(statMaxLengthLearnedClause, len(learnedClause))
    return learnedClause, nextDecisionLevel
               
def luby(i: int) -> int:
    k = math.floor(math.log(i,2)) + 1
    if i == 2**k-1:
        return 2**(k-1)
    return luby(i-2**(k-1)+1)

# todo: wie ist nach i-ter neustart nach c*ti konflikten zu interpretieren? c*ti weiteren?
def applyRestartPolicy(cnf: CNF, v: V, decisionLevel: Level) -> tuple[CNF, V, Level]:
    global statRestarts
    global statConflicts
    global c
    global oldStatConflicts
    
    newConflicts = statConflicts - oldStatConflicts
    
    if newConflicts > c * luby(statRestarts+1):
        statRestarts += 1
        oldStatConflicts = statConflicts
        for info in v[2]:
            info[0] = False
        v = ([],[],v[2])
        decisionLevel = 0
    
    return cnf, v, decisionLevel

def backtrack(v : V, new_decision_level: Level) -> V:
    if new_decision_level == 0:
        for lit in v[0]:
            v[2][abs(lit)-1][0] = False
        return [],[], v[2]
    
    for i, level in enumerate(v[1]):
        # first found literal is decisionLiteral of that level
        if level >= new_decision_level:
            literalsToRemove = v[0][i+1:]
            for lit in literalsToRemove:
                v[2][abs(lit)-1][0] = False
            return v[0][:i+1], v[1][:i+1], v[2]
    else:
        raise Exception("No literal found to backtrack")

# if sat, return True and v, else return False and list of added clauses
def CDCL(cnf: CNF) -> tuple[True, list[int]] | tuple[False,  list[Clause]] :
    ogCnf = deepcopy(cnf)
    decisionLevel = 0
    numLiterals = getNumLiterals(cnf)
    # initialise all variables to negative
    v : V = ([],[],[[False,-i,0] for i in range(1,numLiterals+1)])
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
        cnf,v,decisionLevel = applyRestartPolicy(cnf, v, decisionLevel)
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
    ("num Restarts", str(statRestarts)),
    ("peak memory", str(statPeakMemoryMB)+" MB (assumes Ubuntu)"),
    ("time", str(statTimeEnd - statTimeStart)+" s")
])