import sys
import cnf_utils
from Assignment import Assignment, Assignments
import time
import resource
import random
import math

optRestarts = True # if True, restarts are enabled, otherwise disabled
optVSIDS = True # if True, VSIDS are taken into account, otherwise not
optClauseLearning = True # if True, clause learning includes 1UIP, otherwise only decision literals
optClauseDeletion = True # if True, learned clauses are deleted, otherwise not
optClauseMinimization = False # if True, learned clauses are minimized, otherwise not

type Literal = int
type Clause = list[Literal]
type CNF = list[Clause]

# stats and constants
statTimeStart = time.time()
statUP = 0
statDecision = 0
statConflicts = 0
statLearnedClauses = 0
statDeletedClauses = 0
statMaxLengthLearnedClause = 0
statRestarts = 0
b = 2
c = 1.05
k = 200
c_luby = 100
numRandomDecision = 0
oldStatConflicts = 0
lbdLimit: float = 10
lbdFactor: float = 1.1

def getNumLiterals(cnf: CNF) -> int:
    return len(set([abs(l) for c in cnf for l in c]))

def decide(assignments: Assignments, decisionLevel: int) -> None:
    global statDecision
    statDecision += 1
    
    global optVSIDS
    if not optVSIDS:
        for assignment in assignments.assignments:
            if not assignment.set:
                assignments.setLiteral(assignment.polarity, decisionLevel, [])
                return
    
    global numRandomDecision
    global k
    if numRandomDecision * k < statConflicts:
        numRandomDecision += 1
        
        # choose random literal
        allUnsetAssignments = [assignment for assignment in assignments.assignments if not assignment.set]
        assignment = random.choice(allUnsetAssignments)
        assignments.setLiteral(assignment.polarity, decisionLevel, [])
        return

    max = 0
    maxAssignment = None
    for assignment in assignments.assignments:
        if not assignment.set and assignment.VSIDS >= max:
            max = assignment.VSIDS
            maxAssignment = assignment
    
    assignments.setLiteral(maxAssignment.polarity, decisionLevel, [])

def propagate(cnf: CNF, assignments: Assignments, decisionLevel: int) -> Clause:
    global statConflicts
    global statUP
    # newest literal has to be propagated (possibly violating the invariant)
    literalsToPropagate = [assignments.history[-1]]
    
    while len(literalsToPropagate) > 0:
        # all clauses with literal fulfill the invariant
        # all clauses with -literal possibly violate the invariant
        literal = -literalsToPropagate.pop()
        watchedClausesIndices = assignments.getAssignment(literal).getWatched(literal)
        for clauseIndex in watchedClausesIndices:
            clause = cnf[clauseIndex]
            
            if len(clause) >= 2:
                ownIndex = 0 if clause[0] == literal else 1
                otherLiteralInd = 1 - ownIndex
                otherLiteral = clause[otherLiteralInd]
                
                # check if other literal is satisfied
                if otherLiteral in assignments:
                    continue
                
                # check if other literal can be watched
                for i in range(2, len(clause)):
                    # literal can be watched if it is not falsified
                    if -clause[i] not in assignments:
                        # swap literals
                        clause[ownIndex], clause[i] = clause[i], clause[ownIndex]
                        assignments.getAssignment(literal).removeWatched(clauseIndex, literal)
                        assignments.getAssignment(clause[ownIndex]).addWatched(clauseIndex, clause[ownIndex])
                        # possible UP
                        if -otherLiteral in assignments and clause[ownIndex] not in assignments:
                            # look if otherLiteral can also be exchanged with watchable literal
                            for j in range(i+1, len(clause)):
                                if -clause[j] not in assignments:
                                    clause[otherLiteralInd], clause[j] = clause[j], clause[otherLiteralInd]
                                    assignments.getAssignment(otherLiteral).removeWatched(clauseIndex, otherLiteral)
                                    assignments.getAssignment(clause[otherLiteralInd]).addWatched(clauseIndex, clause[otherLiteralInd])
                                    break
                            else:
                                # no other watchable literal -> UP
                                statUP += 1
                                assignments.setLiteral(clause[ownIndex], decisionLevel, clause)
                                literalsToPropagate.append(clause[ownIndex])
                        break
                # if no literal can be watched clause is unit or conflict
                else:
                    # both literals are falsified -> conflict
                    if -otherLiteral in assignments:
                        statConflicts += 1
                        return clause
                    else:
                        statUP += 1
                        assignments.setLiteral(otherLiteral, decisionLevel, clause)
                        literalsToPropagate.append(otherLiteral)
            # only one literal -> conflict since literal is falsified
            else:
                statConflicts += 1
                return clause
    return None
            
def analyzeConflict(assignments: Assignments, conflict: Clause, decisionLevel: int) -> tuple[Clause, int]:
    previousLevelLiterals: set[tuple[Literal, int]] = set()
    currentLevelLiterals: set[Literal] = set()
    allLiterals: set[Literal] = set()
    
    # sort conflict into literals that are on the current decision level and literals that are on previous decision levels
    for literal in conflict:
        level = assignments.getAssignment(literal).level
        if level == decisionLevel:
            currentLevelLiterals.add(-literal)
        else:
            previousLevelLiterals.add((-literal, level))
        allLiterals.add(-literal)
    
    global optClauseLearning
    if optClauseLearning:
        # iterate over current level backwards according to history
        for literal in reversed(assignments.history):
            # currentLevelLiteral[0] is 1UIP
            if len(currentLevelLiterals) == 1:
                break
            
            # not in conflict
            if literal not in currentLevelLiterals:
                continue
            
            parents = assignments.getAssignment(literal).parents
            for parent in parents:
                level = assignments.getAssignment(parent).level
                if level == decisionLevel:
                    currentLevelLiterals.add(parent)
                else:
                    previousLevelLiterals.add((parent, level))
                allLiterals.add(literal)
                

            currentLevelLiterals.remove(literal)
    else:
        # iterate over current level backwards according to history
        for literal in reversed(assignments.history):
            # first previous level literal -> currentLevelLiteral[0] is decision literal
            if assignments.getAssignment(literal).level != decisionLevel:
                break
            
            # not in conflict
            if literal not in currentLevelLiterals:
                continue
            
            parents = assignments.getAssignment(literal).parents
            for parent in parents:
                level = assignments.getAssignment(parent).level
                if level == decisionLevel:
                    currentLevelLiterals.add(parent)
                else:
                    previousLevelLiterals.add((parent, level))
                allLiterals.add(literal)

            currentLevelLiterals.remove(literal)
        
    # 1UIP if optClauseLearning is True, otherwise decision literal 
    uip1 = currentLevelLiterals.pop()
    
    # create learned clause
    learnedClause = [-uip1] + [-literal for literal, _ in previousLevelLiterals]      
            
    # next decision level = highest level of previous decision levels
    newDecisionLevel = max([level for _, level in previousLevelLiterals], default=0)
    
    global optVSIDS
    if optVSIDS:
        # update VSIDS
        global b
        global c
        for literal in allLiterals:
            assignments.getAssignment(literal).VSIDS += b
        b *= c

        # scale all numbers if b is too large
        if b > 10**30:
            for assignment in assignments.assignments:
                assignment.VSIDS /= b
            b = 1
    
    global statMaxLengthLearnedClause
    global statLearnedClauses
    statLearnedClauses += 1
    statMaxLengthLearnedClause = max(statMaxLengthLearnedClause, len(learnedClause))
    return learnedClause, newDecisionLevel
    
def luby(i: int) -> int:
    k = math.floor(math.log(i,2)) + 1
    if i == 2**k-1:
        return 2**(k-1)
    return luby(i-2**(k-1)+1)

def deleteClause(cnf: CNF, assignments: Assignments, lbd: list[float], i: int) -> None:
    global statDeletedClauses
    statDeletedClauses += 1
    clauseToDelete = cnf[i]
    clauseToSwap = cnf[-1]
    # remove clause from watched list (swap with last clause, then delete)
    for literal in clauseToDelete[:2]:
        assignments.getAssignment(literal).removeWatched(i,literal)
    for literal in clauseToSwap[:2]:
        assignments.getAssignment(literal).changeClause(len(cnf) - 1, i, literal)
    cnf[i] = cnf[-1]
    cnf.pop()
    lbd[i] = lbd[-1]
    lbd.pop()

def applyRestartPolicy(assignments: Assignments, cnf: CNF, lbd: list[float], ogCnfLength: int, decisionLevel: int) -> int:
    if not optRestarts:
        return decisionLevel
    
    global statRestarts
    global statConflicts
    global oldStatConflicts
    global c_luby
    
    conflictsSinceLastRestart = statConflicts - oldStatConflicts
    
    if conflictsSinceLastRestart > c_luby * luby(statRestarts + 1):
        statRestarts += 1
        oldStatConflicts = statConflicts
        backtrack(assignments, 0)
        # delete learned clauses
        global optClauseDeletion
        if optClauseDeletion:
            global lbdLimit
            global lbdFactor
            for i in range(len(cnf) - 1, ogCnfLength - 1, -1):
                # delete clause by swapping it with last clause and then deleting the last clause
                if lbd[i] > lbdLimit:
                    deleteClause(cnf, assignments, lbd, i)
            lbdLimit *= lbdFactor
        return 0
            
    return decisionLevel  
                    
def backtrack(assignments: Assignments, newDecisionLevel: int) -> None:
    
    literalsToKeep = 0
    for i, literal in reversed(list(enumerate(assignments.history))):
        level = assignments.getAssignment(literal).level
        # keep all literals on new Decision Level
        if level <= newDecisionLevel:
            literalsToKeep = i+1
            break
    
    # remove all literals larger than index
    for literal in assignments.history[literalsToKeep:]:
        assignments.getAssignment(literal).set = False
    assignments.history = assignments.history[:literalsToKeep]

def learnClause(cnf: CNF, assignments: Assignments, lbd: list[float], c_learned: Clause, decisionLevel: int, proofCnf: CNF, ogCnfSize: int) -> None:
    global statLearnedClauses
    statLearnedClauses += 1
    
    # add clause to cnf
    cnf.append(c_learned)
    proofCnf.append(c_learned)
    
    global statUP
    statUP += 1
        
    # find unset literal
    for i, literal in enumerate(c_learned):
        if not assignments.getAssignment(literal).set:
            # swap literals
            c_learned[0], c_learned[i] = c_learned[i], c_learned[0]
            break
    
    # sort other literals by index in history (so that backtracking will watch correct literals)
    c_learned[1:] = sorted(c_learned[1:], key=lambda x: assignments.history.index(-x), reverse=True)
    
    # set watched literals
    for literal in c_learned[:2]:
        assignments.getAssignment(literal).addWatched(len(cnf) - 1, literal)
        
    # calculate LBD
    lbd.append(len(set([assignments.getAssignment(literal).level for literal in c_learned])))
    
    # clause minimazation
    global optClauseMinimization
    if optClauseMinimization:
        # len(cnf) - 1 is the learned clause
        for i in range(len(cnf) - 2, ogCnfSize-1, -1):
            clause = cnf[i]
            # clause is redundant, if c_learned is a subset of clause
            if all([literal in clause for literal in c_learned]):
                deleteClause(cnf, assignments, lbd, i)
    # set literal
    assignments.setLiteral(c_learned[0], decisionLevel, c_learned)
      
def CDCL(cnf: CNF) -> tuple[bool, list[Literal] | CNF]:
    ogCnfSize = len(cnf)
    numLiterals = getNumLiterals(cnf)
    proofCnf = cnf.copy()
    
    # assignment of variables (0th index is not used)
    assignments = Assignments(numLiterals, cnf)
    # list of all LBD's of clauses
    lbd: list[float] = [0] * ogCnfSize
    decisionLevel = 0
    while len(assignments.history) < numLiterals:
        # decide
        decisionLevel += 1
        decide(assignments, decisionLevel)
        # propagate
        c_conflict = propagate(cnf, assignments, decisionLevel)
        # conflict
        while c_conflict is not None:
            # conflict on decision level means UNSAT
            if decisionLevel == 0:
                return False, proofCnf[ogCnfSize:]+[[]]
            c_learned, decisionLevel = analyzeConflict(assignments, c_conflict, decisionLevel)
            backtrack(assignments, decisionLevel)
            learnClause(cnf, assignments, lbd, c_learned, decisionLevel, proofCnf, ogCnfSize)
            c_conflict = propagate(cnf, assignments, decisionLevel)
        decisionLevel = applyRestartPolicy(assignments, cnf, lbd, ogCnfSize, decisionLevel)
    return True, assignments.history

if __name__ == "__main__":

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
    sat, res = CDCL(cnf)

    if not sat:
        with open("proof.drat", "w") as f:
            for clause in res:
                f.write(" ".join(map(str, clause)) + " 0"+ "\n")

    statTimeEnd = time.time()
    statPeakMemoryMB = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

    cnf_utils.fancy_output("CDCL Solver", sat, res, filename, [
    ("unit propagations", str(statUP)),
    ("decisions", str(statDecision)),
    ("conflicts", str(statConflicts)),
    ("learned clauses", str(statLearnedClauses)),
    ("deleted clauses", str(statDeletedClauses)),
    ("max learned clause length", str(statMaxLengthLearnedClause)),
    ("num Restarts", str(statRestarts)),
    ("peak memory", str(statPeakMemoryMB)+" MB (assumes Ubuntu)"),
    ("time", str(statTimeEnd - statTimeStart)+" s")
    ])