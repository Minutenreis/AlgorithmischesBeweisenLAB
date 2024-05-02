import sys
import subprocess

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

if len(sys.argv) != 6:
    print("Usage: python test.py <solver> <n> <c> <k> <tries>")
    print("<solver>: path to the solver executable")
    sys.exit(1)

solver = sys.argv[1]
n = sys.argv[2]
c = sys.argv[3]
k = sys.argv[4]
tries = int(sys.argv[5])

printProgressBar(0,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
for i in range(tries):
    subprocess.call(["python3", "RandomCNF/randomCnf.py", n, c, k])
    satCadical = subprocess.call(["./Submodules/cadical/build/cadical", "randomCnf.cnf"], stdout=subprocess.DEVNULL)
    satSolver = subprocess.call(["python3",solver, "randomCnf.cnf"],stdout=subprocess.DEVNULL)
    if (satSolver != satCadical):
        print()
        print("Error: Solver output does not match Cadical output")
        print("Cadical: ", satCadical)
        print("Solver: ", satSolver)
        sys.exit(1)
    printProgressBar(i+1,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
print("All tests passed")
    

