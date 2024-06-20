from copy import deepcopy
import sys
import cnf_utils
import time
import resource
import random
import math

type Literal = int
type Level = int
# tuple[isSet,assignment,count, watched indices with literal, watched indices with -literal]
type Info = list[bool,int,float, list[int], list[int]]
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
c_luby = 100
numRandomDecision = 0
oldStatConflicts = 0

trivialLiterals = []

def isIn(literal: Literal, v: V) -> bool:
    info = v[2][abs(literal)-1]
    return info[0] and info[1] == literal

def getWatchedOfLiteral(v: V, literal: Literal ) -> list[int]:
    return v[2][abs(literal)-1][3 if literal > 0 else 4]

def getNumLiterals(cnf: CNF) -> int:
    return len(set([abs(l) for c in cnf for l in c]))

def setLiteral(v: V,literal: Literal, decisionLevel: Level) -> V:
    v[0].append(literal)
    v[1].append(decisionLevel)
    v[2][abs(literal)-1][0] = True
    v[2][abs(literal)-1][1] = literal
    return v

def decide(v: V, decisionLevel: Level) -> tuple[V, Literal]:
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
        return setLiteral(v,literal, decisionLevel), literal
    
    max = 0
    literal = 0
    for info in v[2]:
        if not info[0] and info[2]>=max:
            max = info[2]
            literal = info[1]
    
    return setLiteral(v, literal, decisionLevel), literal

def propagate(cnf: CNF, v: V, decisionLevel: Level, newLiteral: Literal) -> tuple[V,Conflict]:  
    global statUP
    global statConflicts
    i = 0
    
    decidedClauses = []
    global trivialLiterals
    possibleLiterals = ([newLiteral] if newLiteral != 0 else []) + trivialLiterals.copy()
    
    while len(possibleLiterals) > 0 :
        currentLiteral = possibleLiterals.pop()
        
        # get all clauses with -currentLiteral as watched literal
        watchedClauseIndices = getWatchedOfLiteral(v, -currentLiteral).copy()
        for clauseIndex in watchedClauseIndices:
            clause = cnf[clauseIndex]
            
            if len(clause) > 1:
                currLiteralIndex = 0 if clause[0] == -currentLiteral else 1
                otherWatchedLiteral = clause[1 - currLiteralIndex]
                
                # clause already satisfied
                if isIn(otherWatchedLiteral,v):
                    continue
                # seek if new literal can be watched
                for i in range(2,len(clause)):
                    if not isIn(-clause[i],v):
                        # add clause to other watched literal
                        getWatchedOfLiteral(v, clause[i]).append(clauseIndex)
                        # remove clause from current watched literal
                        getWatchedOfLiteral(v, clause[currLiteralIndex]).remove(clauseIndex)
                        clause[currLiteralIndex], clause[i] = clause[i], clause[currLiteralIndex]
                        break
                # no literal found: clause is unit or conflict
                else:
                    # potential unit propagation
                    if not isIn(-otherWatchedLiteral,v):
                        setLiteral(v, otherWatchedLiteral, decisionLevel)
                        possibleLiterals.append(currentLiteral) # later check remaining strands, depth first search
                        possibleLiterals.append(otherWatchedLiteral)
                        decidedClauses.append(clause)
                        statUP += 1
                        break # first check new variable
                    # conflict
                    else:
                        statConflicts += 1
                        return v, decidedClauses + [clause]
            # only one literal -> conflict
            else:
                statConflicts += 1
                return v, decidedClauses + [clause]
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

def applyRestartPolicy(cnf: CNF, v: V, decisionLevel: Level) -> tuple[CNF, V, Level]:
    global statRestarts
    global statConflicts
    global c_luby
    global oldStatConflicts
    
    newConflicts = statConflicts - oldStatConflicts
    
    if newConflicts > c_luby * luby(statRestarts+1):
        statRestarts += 1
        oldStatConflicts = statConflicts
        for info in v[2]:
            info[0] = False
        v = ([],[],v[2])
        decisionLevel = 0
    
    return cnf, v, decisionLevel

def backtrack(v : V, new_decision_level: Level) -> tuple[V, Literal]:
    global trivialLiterals
    if new_decision_level == 0:
        for lit in v[0]:
            v[2][abs(lit)-1][0] = lit in trivialLiterals
        return (trivialLiterals.copy(),[0] * len(trivialLiterals), v[2]), 0
    
    for i, level in enumerate(v[1]):
        # first found literal is decisionLiteral of that level
        if level >= new_decision_level:
            literalsToRemove = v[0][i+1:]
            for lit in literalsToRemove:
                v[2][abs(lit)-1][0] = False
            return (v[0][:i+1], v[1][:i+1], v[2]), v[0][i]
    # no literals set
    else:
        raise Exception("Backtrack failed")

def learn_clause(cnf: CNF, v: V, clause: Clause) -> tuple[CNF, V]:
    # sort clause by decision level
    clause.sort(key=lambda x: -v[1][v[0].index(-x)])
    
    # add clause to cnf
    cnf.append(clause)
    
    # add watched literals
    for i in range(2):
        if len(clause) > i:
            getWatchedOfLiteral(v,clause[i]).append(len(cnf)-1)
            
    # look if clause is trivial
    if len(clause) == 1:
        global trivialLiterals
        trivialLiterals.append(clause[0])
        setLiteral(v, clause[0], 0)
    
    return cnf, v

# if sat, return True and v, else return False and list of added clauses
def CDCL(cnf: CNF) -> tuple[True, list[int]] | tuple[False,  list[Clause]] :
    ogCnf = deepcopy(cnf)
    decisionLevel = 0
    numLiterals = getNumLiterals(cnf)
    # initialise all variables to negative
    v : V = ([],[],[[False,-i,0,[],[]] for i in range(1,numLiterals+1)])
    # get all watched literals
    for i, clause in enumerate(cnf):
        # add watched literals
        for j in range(2):
            if len(clause) > j:
                getWatchedOfLiteral(v,clause[j]).append(i)
    
    while len(v[0]) < numLiterals:
        decisionLevel += 1
        v, newLiteral = decide(v, decisionLevel)
        v, c_conflict = propagate(cnf, v, decisionLevel, newLiteral)
        while c_conflict is not None:
            if decisionLevel == 0:
                return False, cnf[len(ogCnf):]
            c_learned, decisionLevel = analyzeConflict(v, c_conflict, decisionLevel)
            cnf, v = learn_clause(cnf, v, c_learned)
            v, newLiteral  = backtrack(v, decisionLevel)
            v, c_conflict = propagate(cnf, v, decisionLevel, newLiteral)
        cnf,v,decisionLevel = applyRestartPolicy(cnf, v, decisionLevel)
    return True, v[0]

if len(sys.argv) == 2:
    filename = sys.argv[1]
elif len(sys.argv) == 1:
    from pathlib import Path
    filename = str(Path(__file__).parent.parent.joinpath("randomCnf.cnf"))
else:
    sys.exit("Usage: python CDCL.py filename")
    


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