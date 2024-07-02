"""
its in the name
"""
def sign(n: int) -> int:
    if n < 0:
        return -1
    else:
        return 1

"""
parse DIMACS CNF files
filename: relative path to the DIMACS CNF file
returns: list of clauses
"""
def read_cnf(filename: str) -> list[list[int]]:
    cnf: list[list[int]] = []
    vars: set[int]= set()
    
    # read in cnf
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            # ignore comments and header
            if line.startswith("c") or line.startswith("p"):
                continue
            clause: list[int] = []
            literals = line.split()
            for literal in literals:
                literal = int(literal)
                if literal == 0:
                    break
                vars.add(abs(literal))
                clause.append(literal)
            clause.sort(key=abs)
            cnf.append(clause)
    
    # map all variables to continuous list 1,2,...,n
    existingVars = sorted(list(vars))
    
    for i, clause in enumerate(cnf):
        for j, lit in enumerate(clause):
            cnf[i][j] = sign(lit) * (existingVars.index(abs(lit))+1)
    
    return cnf

class bcolors:
    lightBlue = '\033[96m'
    purple = '\033[95m'
    darkBlue = '\033[94m'
    green = '\033[92m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'
    italic = '\033[3m'

"""
Fancy Cadical Style Output
name: name of the solver
sat: is the formula satisfiable
v: list of variable assignments (if not satisfiable, is ignored)
filename: name of the DIMACS CNF file
stats: list of statistics as tuple (name, value)
THIS CLOSES THE PROGRAM WITH THE CORRECT EXIT CODE (10 for SAT, 20 for UNSAT)
"""
def fancy_output(name: str, sat: bool, v: list[int],filename: str, stats: list[tuple[str,str]]) -> None:
    header = None 
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("p"):
                header = line.strip()
                break
    
    print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"banner"+bcolors.end+bcolors.lightBlue+" ] -------------------------------------------------------------" + bcolors.end)
    print("c")
    print("c", bcolors.purple+name+bcolors.end)
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

    if(sat and v):
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
    if stats and len(stats) > 0:
        print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"statistics"+bcolors.end+bcolors.lightBlue+" ] ---------------------------------------------------------" + bcolors.end)
        print("c")
        for stat in stats:
            print("c", (stat[0]+":").ljust(40), stat[1])
        print("c")
    print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"shutting down"+bcolors.end+bcolors.lightBlue+" ] ------------------------------------------------------" + bcolors.end)
    print("c")
    print("c", "exit", 10 if sat else 20)
    exit(10 if sat else 20)