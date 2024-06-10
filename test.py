import sys
import subprocess
import time

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '_' * (length - filledLength)
    print(f'\r{prefix} {bar} {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

if len(sys.argv) != 4:
    print("Usage: python test.py <solver> <n> <tries>")
    print("<solver>: path to the solver executable")
    sys.exit(1)

solver = sys.argv[1]
proof = False
python = True
if (solver.upper() == "CDCL"):
    solver = "CDCL/CDCL.py"
    proof = True
elif (solver.upper() == "CDCL-CPP"):
    solver = "CDCL/CDCL.cpp"
    subprocess.call(["mkdir", "-p", "CDCL/bin"])
    subprocess.call(["g++", "CDCL/CDCL.cpp","-std=c++20","-O3", "-o", "CDCL/bin/CDCL"])
    proof = True
    python = False
elif (solver.upper() == "DPLL"):
    solver = "DPLL/DPLL.py"
elif (solver.upper() == "DP"):
    solver = "DP/DP.py"

n = sys.argv[2]
tries = int(sys.argv[3])

statTimeCadical = 0
statTimeSolver = 0
statTimeGen = 0
statTimeDrat = 0

solver1Output = 'temp/solverOutput.txt'
file = open(solver1Output, 'w')

printProgressBar(0,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
for i in range(tries):
    timeGenStart = time.perf_counter()
    subprocess.call(["python3.12", "RandomCNF/randomCnf.py", n, str(round(3.8 * int(n))), "3"])
    timeGenEnd = time.perf_counter()
    
    timeSolverStart = time.perf_counter()
    if (python):
        satSolver = subprocess.call(["python3.12",solver, "randomCnf.cnf"],stdout=file)
    else:
        satSolver = subprocess.call(["CDCL/bin/CDCL", "randomCnf.cnf"],stdout=file)
    timeSolverEnd = time.perf_counter()
    
    if (proof and satSolver == 20):
        timeDratStart = time.perf_counter()
        correctDrat = subprocess.call(["./Submodules/drat-trim/drat-trim", "randomCnf.cnf", "proof.drat"],stdout=subprocess.DEVNULL)
        timeDratEnd = time.perf_counter()
        if (correctDrat != 0):
            print()
            print(f"Error: {solver} did not produce a correct proof")
            sys.exit(1)
        statTimeDrat += timeDratEnd - timeDratStart
    else:
        timeCadicalStart = time.perf_counter()
        satCadical = subprocess.call(["./Submodules/cadical/build/cadical", "randomCnf.cnf"], stdout=subprocess.DEVNULL)
        timeCadicalEnd = time.perf_counter()
        statTimeCadical += timeCadicalEnd - timeCadicalStart
        if (satSolver != satCadical):
            print()
            print("Error: Solver output does not match Cadical output")
            print("Cadical: ", satCadical)
            print("Solver: ", satSolver)
            sys.exit(1)

    statTimeSolver += timeSolverEnd - timeSolverStart
    statTimeGen += timeGenEnd - timeGenStart
    printProgressBar(i+1,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
print("All tests passed")
print("Time spent in drat-trim: ", statTimeDrat, "s")
print("Time spent in Cadical: ", statTimeCadical, "s")
print(f"Time spent in {solver}: ", statTimeSolver, "s")
print("Time spent generating CNFs: ", statTimeGen, "s")
    

