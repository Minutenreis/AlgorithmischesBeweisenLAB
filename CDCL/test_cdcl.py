import unittest
import CDCL
import Assignment

def gen_assignments():
    cnf = [[1, 2, 3], [-1, 2, 3], [1, -2, 3]]
    return Assignment.Assignments(3, cnf)

class TestCDCL(unittest.TestCase):
    
    def test_getNumLiterals(self):
        cnf = [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]
        self.assertEqual(CDCL.getNumLiterals(cnf), 3)

    def test_getNumLiterals2(self):
        cnf = [[1,2,3,4],[5,6,7,8]]
        self.assertEqual(CDCL.getNumLiterals(cnf), 8)
    
    def test_decide(self):
        assignments = gen_assignments()
        CDCL.statConflicts = 0
        assignments.getAssignment(1).VSIDS = 2
        assignments.getAssignment(2).VSIDS = 1
        assignments.getAssignment(3).VSIDS = 0
        CDCL.decide(assignments,1)
        self.assertEqual(assignments.getAssignment(1).level, 1)
        self.assertTrue(assignments.getAssignment(1).set)
    
    def test_decideRandom(self):
        assignments = gen_assignments()
        assignments.setLiteral(1, 0, [1])
        CDCL.statConflicts = 1000
        CDCL.numRandomDecision = 1
        CDCL.decide(assignments, 1)
        self.assertTrue(assignments.getAssignment(2).set or assignments.getAssignment(3).set)
        self.assertTrue(not (assignments.getAssignment(2).set and assignments.getAssignment(3).set))
        
    def test_propagate(self):
        pass
    
    def test_analyzeConflict(self):
        pass
    
    def test_backtrack(self):
        pass
    
    def test_luby(self):
        self.assertEqual(CDCL.luby(1), 1)
        self.assertEqual(CDCL.luby(2), 1)
        self.assertEqual(CDCL.luby(3), 2)
    
    def test_restart(self):
        pass
    
    def test_learnAndPropagate(self):
        pass

class TestAssignment(unittest.TestCase):
    def test_init(self):
        assignments = gen_assignments()
        self.assertEqual(assignments.getAssignment(1).getWatched(1), [0, 2])
        self.assertEqual(assignments.getAssignment(2).getWatched(2), [0, 1])
        self.assertEqual(assignments.getAssignment(3).getWatched(3), [])
        self.assertEqual(assignments.getAssignment(1).getWatchedReverse(1), [1])
        self.assertEqual(assignments.getAssignment(2).getWatchedReverse(2), [2])
        self.assertEqual(assignments.getAssignment(3).getWatchedReverse(3), [])
        self.assertEqual(assignments.getAssignment(1).set, False)
        self.assertEqual(assignments.getAssignment(2).set, False)
        self.assertEqual(assignments.getAssignment(3).set, False)  
        self.assertEqual(assignments.getAssignment(1).polarity, -1)
        self.assertEqual(assignments.getAssignment(2).polarity, -2)
        self.assertEqual(assignments.getAssignment(3).polarity, -3)
    
    def test_addWatched(self):
        assignments = gen_assignments()
        assignments.getAssignment(1).addWatched(1, 1)
        self.assertEqual(assignments.getAssignment(1).getWatched(1), [0, 2, 1])
        assignments.getAssignment(3).addWatched(1, 3)
        self.assertEqual(assignments.getAssignment(3).getWatched(3), [1])

    def test_removeWatched(self):
        assignments = gen_assignments()
        assignments.getAssignment(1).removeWatched(0, 1)
        self.assertEqual(assignments.getAssignment(1).getWatched(1), [2])
        assignments.getAssignment(1).removeWatched(1, -1)
        self.assertEqual(assignments.getAssignment(1).getWatchedReverse(1), [])
    
    def test_changeClause(self):
        assignments = gen_assignments()
        assignments.getAssignment(1).changeClause(0, 1)
        self.assertEqual(assignments.getAssignment(1).getWatched(1), [1, 2])
    
    def test_contains(self):
        assignment = gen_assignments()
        self.assertTrue(1 not in assignment)
        self.assertTrue(-1 not in assignment)
        assignment.setLiteral(1,0,[1])
        self.assertTrue(1 in assignment)
        self.assertTrue(-1 not in assignment)
    
    def test_setLiteral(self):
        assignment = gen_assignments()
        assignment.setLiteral(1, 0, [1])
        assignment.setLiteral(2, 1, [1,2,-3])
        self.assertTrue(assignment.getAssignment(1).set)
        self.assertTrue(assignment.getAssignment(2).set)
        self.assertTrue(not assignment.getAssignment(3).set)
        self.assertTrue(1 in assignment)
        self.assertTrue(2 in assignment)
        self.assertEqual(assignment.getAssignment(1).level, 0)
        self.assertEqual(assignment.getAssignment(2).level, 1)
        self.assertEqual(assignment.getAssignment(1).parents, [])
        self.assertEqual(assignment.getAssignment(2).parents, [-1,3])
        self.assertEqual(assignment.history, [1,2])
    
if __name__ == '__main__':
    unittest.main()