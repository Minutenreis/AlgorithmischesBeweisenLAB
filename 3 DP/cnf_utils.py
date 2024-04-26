"""
parse DIMACS CNF files
filename: relative path to the DIMACS CNF file
returns: list of clauses
"""
def read_cnf(filename: str) -> list[list[int]]:
    cnf: list[list[int]] = []
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
                clause.append(literal)
            cnf.append(clause)
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
    if stats and len(stats) > 0:
        print("c", bcolors.lightBlue+"--- [ "+bcolors.end+bcolors.darkBlue+bcolors.bold+"statistics"+bcolors.end+bcolors.lightBlue+" ] ---------------------------------------------------------" + bcolors.end)
        print("c")
        for stat in stats:
            print("c", (stat[0]+":").ljust(20), stat[1])
        print("c")