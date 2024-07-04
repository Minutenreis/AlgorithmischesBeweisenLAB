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
statClauseMinimalization = 0
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

"""
returns the number of unique literals in the CNF (+literal, -literal is counted as 1)
"""
def getNumLiterals(cnf: CNF) -> int:
    return len(set([abs(l) for c in cnf for l in c]))

"""
decides the next literal by choosing the literal with the highest VSIDS score
every k decisions a random literal is chosen instead
if optVSIDS is False, the first unset literal is chosen (by traversing the list front to back)
"""
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
"""
applies unit propagation to the latest literal in the history and then recursively for all found literals
returns None if no conflict is found, otherwise the conflicting clause
"""
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

"""
analyses the conflict and implication graph and generates a learned clause
the learned clause is either 1UIP if optClauseLearning is True, otherwise the decision literal
also increments the VSIDS if optVSIDS is True
"""         
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
            # first previous level literal -> previous is decision literal
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
            previous = literal
        currentLevelLiterals.add(previous)
        
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

"""
returns the luby number of i
1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8, 1,...
"""
def luby(i: int) -> int:
    k = math.floor(math.log(i,2)) + 1
    if i == 2**k-1:
        return 2**(k-1)
    return luby(i-2**(k-1)+1)

"""
deletes the ith clause from the CNF by swapping it with the last clause and then deleting the last clause
updates the watched literals and lbd list accordingly
"""
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

"""
if optRestart is true this method checks if a restart is necessary (more new conflicts than c_luby * luby(restarts+1)))
if so, it backtracks to level 0
if optClauseDeletion is true, it deletes learned clauses with LBD > lbdLimit and multiplies the lbd limit by lbdFactor
outputs the new decision level (currentLevel if no restart, otherwise 0)
"""
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

"""
backtracks to new Decision Level
unsets all literals with level > newDecisionLevel
removes unset literals from history
"""               
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

"""
Sorts the clause by history index (and puts the UIP at the beginning)
"""
def sortClause(c_learned: Clause, assignments: Assignments) -> None:
    # find unset literal
    for i, literal in enumerate(c_learned):
        if not assignments.getAssignment(literal).set:
            # swap literals
            c_learned[0], c_learned[i] = c_learned[i], c_learned[0]
            break
        
    # sort other literals by index in history (so that backtracking will watch correct literals)
    c_learned[1:] = sorted(c_learned[1:], key=lambda x: assignments.history.index(-x), reverse=True)

"""
minimizes the the learned clause with local minimization if optClauseMinimization is True otherwise does nothing
expects clause[0] to be the UIP
"""
def minimizeClause(c_learned: Clause, assignments: Assignments) -> None:
    global optClauseMinimization
    if not optClauseMinimization:
        return
    
    global statClauseMinimalization
    statClauseMinimalization += 1
    # only local minimization is implemented, read Sörensoson and Biere, Minimizing Learned Clauses 2009
    # https://cca.informatik.uni-freiburg.de/papers/SoerenssonBiere-SAT09.pdf
    c_learned_set = set(c_learned)
    for lit in c_learned[1:]:
        parents = assignments.getAssignment(lit).parents
        # if all parents are in the learned clause, the literal is redundant
        if len(parents) > 0 and all([-parent in c_learned_set for parent in parents]):
            c_learned.remove(lit)

"""
learns the clause and adds it to the CNF
sorts the clause by its decision order (in history)
watches the first two literals (one of which is sorted to be the UIP)
also calculates the LBD for the new clause and sets the UIP (since the clauses are asserting)
also locally minimizes the clause if optClauseMinimization is True
"""
def learnClause(cnf: CNF, assignments: Assignments, lbd: list[float], c_learned: Clause, decisionLevel: int, proofCnf: CNF) -> None:
    global statLearnedClauses
    statLearnedClauses += 1
    
    sortClause(c_learned, assignments)
    minimizeClause(c_learned, assignments)
    
    # add clause to cnf
    cnf.append(c_learned)
    proofCnf.append(c_learned)
    
    global statUP
    statUP += 1
        
    # set watched literals
    for literal in c_learned[:2]:
        assignments.getAssignment(literal).addWatched(len(cnf) - 1, literal)
        
    # calculate LBD
    lbd.append(len(set([assignments.getAssignment(literal).level for literal in c_learned])))
    
    # set literal
    assignments.setLiteral(c_learned[0], decisionLevel, c_learned)

"""
Conflict Driven Clause Learning (CDCL) algorithm
gets a cnf as input and returns either:
    - True and the assignment history if the cnf is satisfiable
    - False and the proof cnf if the cnf is unsatisfiable
the proof is saved in an extra proofCnf, if one ever runs into memory problems this can instead be written to file instantly
iterates until either all literals are validly set or a conflict on level 0 is found (which means the cnf is unsatisfiable)
""" 
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
            learnClause(cnf, assignments, lbd, c_learned, decisionLevel, proofCnf)
            c_conflict = propagate(cnf, assignments, decisionLevel)
        decisionLevel = applyRestartPolicy(assignments, cnf, lbd, ogCnfSize, decisionLevel)
    return True, assignments.history

"""
parses argv for filename, reads it in with cnf_utils and runs CDCL
outputs the result, dratProof if UNSAT and some statistics
"""
if __name__ == "__main__":

    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    elif len(sys.argv) == 1:
        from pathlib import Path
        filename = str(Path(__file__).parent.parent.joinpath("randomCnf.cnf"))
    elif len(sys.argv) > 3:
        print("Usage: python CDCL.py filename [options]")
        print("filename: path to the cnf file")
        print("options: 5 bit pattern for opts (default: 11111)")
        sys.exit(1)
    
    if len(sys.argv) == 3:
        opts = sys.argv[2]
        if len(opts) != 5:
            print("Options must be a 5 bit pattern")
            sys.exit(1)
        optRestarts = opts[0] == "1"
        optVSIDS = opts[1] == "1"
        optClauseLearning = opts[2] == "1"
        optClauseDeletion = opts[3] == "1"
        optClauseMinimization = opts[4] == "1"


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
    ("clause minimizations", str(statClauseMinimalization)),
    ("max learned clause length", str(statMaxLengthLearnedClause)),
    ("num Restarts", str(statRestarts)),
    ("peak memory", str(statPeakMemoryMB)+" MB (assumes Ubuntu)"),
    ("time", str(statTimeEnd - statTimeStart)+" s")
    ])