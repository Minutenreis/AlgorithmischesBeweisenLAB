import sys
import time
from ... import cnf_utils

statUP = 0
statDecisions = 0
statTimeStart = time.time()

# parse cnf file to list of clauses
def read_cnf(filename: str) -> list[list[int]]:
    cnf: list[list[int]] = []
    header = None
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            # ignore comments and header
            if line.startswith("c"):
                continue
            if line.startswith("p"):
                header = line.strip()
                continue
            clause: list[int] = []
            literals = line.split()
            for literal in literals:
                literal = int(literal)
                if literal == 0:
                    break
                clause.append(literal)
            cnf.append(clause)
    return (cnf, header)

# unit propagation
def unit_propagation(cnf_v: tuple[list[list[int]], list[int]]) -> tuple[list[list[int]], list[int]]:
    cnf = cnf_v[0]
    v = cnf_v[1]
    
    global statUP
    statUP += 1
    i = 0
    while i < len(cnf):
        if len(cnf[i]) == 1:
            literal = cnf[i][0]
            (cnf, v) = setVariable((cnf, v), literal)
            i = 0
            continue # skip increment
        i += 1
    return (cnf, v)

# set variable (eg. 3 or -3) to true -> -3 = true implies 3 to be false
def setVariable(cnf_v: tuple[list[list[int]], list[int]], variable: int) -> tuple[list[list[int]], list[int]]:
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
    cnf_v = unit_propagation(cnf_v)
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
    resultSetFalse = SAT_2(setVariable(cnf_v, -literal))
    if resultSetFalse[0]:
        return resultSetFalse
    # try setting variable to True
    return SAT_2(setVariable(cnf_v, literal))

if len(sys.argv) != 2:
    print("Usage: python 2-SAT.py filename")
    sys.exit(1)

filename = sys.argv[1]

(cnf, header) = read_cnf(filename)
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

class bcolors:
    lightBlue = '\033[96m'
    purple = '\033[95m'
    darkBlue = '\033[94m'
    green = '\033[92m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'
    italic = '\033[3m'

print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"banner"+bcolors.end+bcolors.lightBlue+" ] -------------------------------------------------------------" + bcolors.end)
print("c")
print("c", bcolors.purple+"2-SAT Solver"+bcolors.end)
print("c", bcolors.purple+"Justus Dreßler"+bcolors.end)
print("c", bcolors.purple+"created for FMI-IN0159 Algorithmisches Beweisen LAB"+bcolors.end)
print("c")
print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"parsing input"+bcolors.end+bcolors.lightBlue+" ] ------------------------------------------------------" + bcolors.end)
print("c")
print("c", "reading DIMACS file from '" + bcolors.green+filename+bcolors.end + "'")
if header:
    print("c", "found '" + bcolors.green+header+bcolors.end + "' header")
print("c")
print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"result"+bcolors.end+bcolors.lightBlue+" ] -------------------------------------------------------------" + bcolors.end)
print("c")

print("s","SATISFIABLE" if sat else "UNSATISFIABLE")

if(sat):
    vPrint = map(str, sorted(v, key=abs))
    print("v", end=" ")
    currentLineLength = 2
    for vStr in vPrint:
        if currentLineLength + len(vStr) > 78:
            print()
            print("v", end=" ")
            currentLineLength = 2
        print(vStr, end=" ")
        currentLineLength += len(vStr) + 1
    print()
print("c")
print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"statistics"+bcolors.end+bcolors.lightBlue+" ] ---------------------------------------------------------" + bcolors.end)
print("c")
print("c", "unit propagation:", statUP)
print("c", "decisions:", statDecisions)
print("c", "time:", statTimeEnd - statTimeStart, "s")
print("c")