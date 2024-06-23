type Literal = int
type Clause = list[Literal]

# Class that keeps track of the state of literals
class Assignment:
    def __init__(self, Literal: Literal):
        self.set = False # True, False (if the variable is assigned)
        self.polarity = -Literal # Literal, -Literal (last assignment)
        self.level: int = 0 # level in which the variable was assigned
        self.parents: list[Literal] = [] # list[Literal] (list of literals that implied this assignment)
        self.VSIDS: float = 0 # float 
        self.watchedWithLiteral: list[int] = [] # list[ClauseIndex]
        self.watchedWithNegLiteral: list[int] = [] # list[ClauseIndex]
    
    # outputs watched list of opposite polarity of literal
    def getWatchedReverse(self, literal: Literal) -> list[Clause]:
        if literal > 0:
            return self.watchedWithNegLiteral
        else:
            return self.watchedWithLiteral
    
    # removes clause with index clauseIndex from watched list, if maxClauseIndex is present, it gets replaced with clauseIndex
    def removeClause(self, clauseIndex: int, maxClauseIndex: int) -> None:
        self.watchedWithLiteral = [c for c in self.watchedWithLiteral if c != clauseIndex]
        self.watchedWithNegLiteral = [c for c in self.watchedWithNegLiteral if c != clauseIndex]
        if clauseIndex == maxClauseIndex:
            return
        self.watchedWithLiteral = [clauseIndex if c == maxClauseIndex else c for c in self.watchedWithLiteral]
        self.watchedWithNegLiteral = [clauseIndex if c == maxClauseIndex else c for c in self.watchedWithNegLiteral]
    
class Assignments:
    def __init__(self, numLiterals: int):
        self.assignments: list[Assignment] = [Assignment(i) for i in range(numLiterals + 1)]
    
    # returns the assignment of a literal
    def getAssignment(self, literal: Literal) -> Assignment:
        return self.assignments[abs(literal)]
    
    # literal in Assignment iff literal is assigned and polarity is the same
    def __contains__(self, literal: Literal) -> bool:
        return self.getAssignment(literal).set and self.getAssignment(literal).polarity == literal

    def setLiteral(self, literal: Literal, level: int, history: list[Literal], implyingClause: Clause) -> None:
        self.getAssignment(literal).set = True
        self.getAssignment(literal).polarity = literal
        self.getAssignment(literal).level = level
        history.append(literal)
        for lit in implyingClause:
            # own literal
            if lit == literal:
                continue
            # add -literal to parents -> x1 ∨ x2 ∨ x3 <=> -x1 ∧ -x2 -> x3
            self.getAssignment(literal).parents.append(-lit)