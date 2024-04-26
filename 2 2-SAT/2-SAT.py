import sys
import time
import cnf_utils

statUP = 0
statDecisions = 0
statTimeStart = time.time()

# repeat unit propagation until no more unit clauses are found
def repeated_unit_propagation(cnf_v: tuple[list[list[int]], list[int]]) -> tuple[list[list[int]], list[int]]:
    cnf = cnf_v[0]
    v = cnf_v[1]
    
    
    i = 0
    while i < len(cnf):
        if len(cnf[i]) == 1:
            literal = cnf[i][0]
            (cnf, v) = unit_propagation((cnf, v), literal)
            i = 0
            continue # skip increment
        i += 1
    return (cnf, v)

# unit_propagation: set variable (eg. 3 or -3) to true -> -3 = true implies 3 to be false for all clauses
def unit_propagation(cnf_v: tuple[list[list[int]], list[int]], variable: int) -> tuple[list[list[int]], list[int]]:
    global statUP
    statUP += 1
    
    cnf = cnf_v[0]
    v = cnf_v[1]
    
    v = v + [variable]
    # remove clauses with the variable
    cnf = [c for c in cnf if variable not in c]
    # remove negated literals from clauses
    cnf = [[l for l in c if l != -variable] for c in cnf]
    return (cnf, v)

"""
2-SAT algorithm
cnf_v: tuple of cnf and v
cnf: list of clauses
v: list of variable assignments
"""
def SAT_2(cnf_v: tuple[list[list[int]], list[int]]) -> tuple[bool, list[int]]:
    # unit propagation
    cnf_v = repeated_unit_propagation(cnf_v)
    cnf = cnf_v[0]
    v = cnf_v[1]
    if len(cnf) == 0: # all clauses are satisfied
        return (True, v)
    if [] in cnf: # a clause is empty
        return (False, v)
    # choose a variable 
    literal = cnf[0][0]
    
    global statDecisions
    statDecisions += 1
    
    # try setting variable to False
    resultSetFalse = SAT_2(unit_propagation(cnf_v, -literal))
    if resultSetFalse[0]:
        return resultSetFalse
    # try setting variable to True
    return SAT_2(unit_propagation(cnf_v, literal))

if len(sys.argv) != 2:
    print("Usage: python 2-SAT.py filename")
    sys.exit(1)

filename = sys.argv[1]

cnf = cnf_utils.read_cnf(filename)
(sat, v) = SAT_2((cnf, []))

statTimeEnd = time.time()

# test result if true
if sat:
    for clause in cnf:
        if not any([literal in v for literal in clause]):
            sys.exit("c", "Error: clause not satisfied")

# output as required

# print("s","SATISFIABLE" if sat else "UNSATISFIABLE")
# print("v"," ".join(map(str, sorted(v, key=abs))))
# print("c", "Unit Propagation:", statUP)
# print("c", "Decisions:", statDecisions)

# fancy output

cnf_utils.fancy_output("2-SAT Solver", sat, v, filename, [
    ("unit propagation", str(statUP)), 
    ("decisions", str(statDecisions)), 
    ("time", str(statTimeEnd-statTimeStart)+" s")
    ])