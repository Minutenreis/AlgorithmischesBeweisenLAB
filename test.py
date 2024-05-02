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
n = sys.argv[2]
tries = int(sys.argv[3])

statTimeCadical = 0
statTimeSolver = 0
statTimeGen = 0

printProgressBar(0,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
for i in range(tries):
    timeGenStart = time.time()
    subprocess.call(["python3", "RandomCNF/randomCnf.py", n, str(round(3.8 * int(n))), "3"])
    timeCadicalStart = time.time()
    satCadical = subprocess.call(["./Submodules/cadical/build/cadical", "randomCnf.cnf"], stdout=subprocess.DEVNULL)
    timeSolverStart = time.time()
    satSolver = subprocess.call(["python3",solver, "randomCnf.cnf"],stdout=subprocess.DEVNULL)
    timeSolverEnd = time.time()
    
    statTimeCadical += timeSolverStart - timeCadicalStart
    statTimeSolver += timeSolverEnd - timeSolverStart
    statTimeGen += timeCadicalStart - timeGenStart
    
    if (satSolver != satCadical):
        print()
        print("Error: Solver output does not match Cadical output")
        print("Cadical: ", satCadical)
        print("Solver: ", satSolver)
        sys.exit(1)
    printProgressBar(i+1,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
print("All tests passed")
print("Time spent in Cadical: ", statTimeCadical, "s")
print("Time spent in Solver: ", statTimeSolver, "s")
print("Time spent generating CNFs: ", statTimeGen, "s")
    

