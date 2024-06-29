type Literal = int
type Clause = list[Literal]
type CNF = list[Clause]

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
    
    # outputs watched list of literal
    def getWatched(self, polarity: Literal) -> list[int]:
        if polarity > 0:
            return self.watchedWithLiteral
        else:
            return self.watchedWithNegLiteral
        
    # adds clauseIndex to watched list of literal
    def addWatched(self, clauseIndex: int, polarity: Literal) -> None:
        self.getWatched(polarity).append(clauseIndex)
    
    # remove clauseIndex from watched list of literal
    def removeWatched(self, clauseIndex: int, polarity: Literal) -> None:
        if polarity > 0:
            self.watchedWithLiteral = [c for c in self.watchedWithLiteral if c != clauseIndex]
        else:
            self.watchedWithNegLiteral = [c for c in self.watchedWithNegLiteral if c != clauseIndex]
    
    # changes clause index from oldIndex to newIndex
    def changeClause(self, oldIndex: int, newIndex: int, polarity: Literal) -> None:
        if polarity > 0:
            self.watchedWithLiteral = [newIndex if c == oldIndex else c for c in self.watchedWithLiteral]
        else:
            self.watchedWithNegLiteral = [newIndex if c == oldIndex else c for c in self.watchedWithNegLiteral]
    
class Assignments:
    def __init__(self, numLiterals: int, cnf: CNF):
        # order in which the variables are assigned
        self.history: list[Literal] = []
        # list of all assignments
        self.assignments: list[Assignment] = [Assignment(i+1) for i in range(numLiterals)]
        for i, clause in enumerate(cnf):
            for j in range(2):
                if len(clause) > j:
                    self.getAssignment(clause[j]).getWatched(clause[j]).append(i)  

    # returns the assignment of a literal
    def getAssignment(self, literal: Literal) -> Assignment:
        return self.assignments[abs(literal)-1]
    
    # literal in Assignment iff literal is assigned and polarity is the same
    def __contains__(self, literal: Literal) -> bool:
        return self.getAssignment(literal).set and self.getAssignment(literal).polarity == literal

    def setLiteral(self, literal: Literal, level: int, implyingClause: Clause) -> None:
        self.getAssignment(literal).set = True
        self.getAssignment(literal).polarity = literal
        self.getAssignment(literal).level = level
        self.history.append(literal)
        self.getAssignment(literal).parents = []
        for lit in implyingClause:
            # own literal
            if lit == literal:
                continue
            # add -literal to parents -> x1 ∨ x2 ∨ x3 <=> -x1 ∧ -x2 -> x3
            self.getAssignment(literal).parents.append(-lit)