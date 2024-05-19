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

if len(sys.argv) != 5:
    print("Usage: python test.py <solver1> <solver2> <n> <tries>")
    print("<solver>: path to the solver executable")
    sys.exit(1)

def getPath(solver):
    if (solver.upper() == "CDCL"):
        return "CDCL/CDCL.py"
    elif (solver.upper() == "DPLL"):
        return "DPLL/DPLL.py"
    elif (solver.upper() == "DP"):
        return "DP/DP.py"
    else:
        return solver

solver1 = sys.argv[1]
solver1Path = getPath(solver1)
    
solver2 = sys.argv[2]
solver2Path = getPath(solver2)

n = sys.argv[3]
tries = int(sys.argv[4])

statTimeSolver1 = 0
statTimeSolver2 = 0
statTimeGen = 0

printProgressBar(0,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
for i in range(tries):
    timeGenStart = time.perf_counter()
    subprocess.call(["python3", "RandomCNF/randomCnf.py", n, str(round(3.8 * int(n))), "3"])
    timeGenEnd = time.perf_counter()
    
    timeSolver1Start = time.perf_counter()
    satSolver1 = subprocess.call(["python3",solver1Path, "randomCnf.cnf"],stdout=subprocess.DEVNULL)
    timeSolver1End = time.perf_counter()
    
    timeSolver2Start = time.perf_counter()
    satSolver2 = subprocess.call(["python3",solver2Path, "randomCnf.cnf"],stdout=subprocess.DEVNULL)
    timeSolver2End = time.perf_counter()
    
    if (satSolver1 != satSolver2):
        print("Different results")
        sys.exit(1)
    
    statTimeSolver1 += timeSolver1End - timeSolver1Start
    statTimeSolver2 += timeSolver2End - timeSolver2Start
    statTimeGen += timeGenEnd - timeGenStart
    
    
    printProgressBar(i+1,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)

print(f"Time spent in {solver1}: ", statTimeSolver1, "s")
print(f"Time spent in {solver2}: ", statTimeSolver2, "s")
print("Time spent generating CNFs: ", statTimeGen, "s")
if statTimeSolver1 < statTimeSolver2:
    print(f"{solver1} was {round((statTimeSolver2 / statTimeSolver1 - 1) * 100)}% faster than {solver2}")
else:
    print(f"{solver2} was {round((statTimeSolver1 / statTimeSolver2 - 1) * 100)}% faster than {solver1}")
    

