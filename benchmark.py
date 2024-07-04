import sys
import subprocess
import time
import os
import re

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
    print("Usage: python3.12 benchmark.py solver n generator")
    print("solver: cdcl or dpll")
    print("n: number of literals if randomGenerator is used, number of source nodes if Pebbling is used, number of holes in the PHP if PHP is used")
    print("generator: path to the generator (python3.12) or one of the following: PHP, Pebbling, Random  (optional)")
    sys.exit(1)

solver = sys.argv[1]
n = sys.argv[2]

generator = sys.argv[3]
generatorPath = generator
if (generator.upper() == "PHP"):
    generatorPath = "Generator/PHP.py"
    cnfFilename = "PHP.cnf"
elif (generator.upper() == "PEBBLING"):
    generatorPath = "Generator/Pebbling.py"
    cnfFilename = "Pebbling.cnf"
elif (generator.upper() == "RANDOM"):
    generatorPath = "Generator/randomCnf.py"
    cnfFilename = "randomCnf.cnf"
    
os.makedirs('temp', exist_ok=True)

if solver.upper() == "DPLL":
    solverOutputDPLL = 'temp/solverOutputDPLL.txt'
    # DPLLBitPatterns = ['0','1']
    DPLLBitPatterns = ["0"]
    DPLLFileNames = [f'temp/solverOutputDPLL{bitPattern}.txt' for bitPattern in DPLLBitPatterns]
    DPLLFiles = [open(name, 'w') for name in DPLLFileNames]
elif solver.upper() == "CDCL":
    CDCLBitPatterns = ['11111', '11110', '11100', '11000', '10000', '00000']
    if generator.upper() == "PEBBLING" and int(n)>8:
        CDCLBitPatterns = CDCLBitPatterns[:-2]
        if int(n)>16:
            CDCLBitPatterns = CDCLBitPatterns[:-1]
    elif generator.upper() == "RANDOM" and int(n)>100:
        CDCLBitPatterns = CDCLBitPatterns[:-2]
    CDCLFileNames = [f'temp/solverOutputCDCL{bitPattern}.txt' for bitPattern in CDCLBitPatterns]
    CDCLBitPatternFiles = [open(name, 'w') for name in CDCLFileNames]
    
if solver.upper() == "DPLL" and os.path.exists(f'temp/benchmark_{solver}_{generator}_{n}_0.txt') or\
    solver.upper() == "CDCL" and os.path.exists(f'temp/benchmark_{solver}-{CDCLBitPatterns[0]}_{generator}_{n}.txt'):
    print("Benchmark already exists")
    sys.exit(0)

tries = 100 if generator.upper() == "RANDOM" else 1
printProgressBar(0,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)
for i in range(tries):
    # Generate CNF
    subprocess.call(["python3.12", generatorPath, n])
    
    if solver.upper() == "CDCL":
        for j, bitPattern in enumerate(CDCLBitPatterns):
            subprocess.call(["python3.12", "CDCL/CDCL.py", cnfFilename, bitPattern], stdout=CDCLBitPatternFiles[j])
    elif solver.upper() == "DPLL":
        for j, bitPattern in enumerate(DPLLBitPatterns):
            subprocess.call(["python3.12", "DPLL/DPLL.py", cnfFilename, bitPattern], stdout=DPLLFiles[j])
    
    printProgressBar(i+1,tries, prefix = 'Progress:', suffix = 'Complete', length = 50)

if solver.upper() == "DPLL":
    for file in DPLLFiles:
        file.close()
elif solver.upper() == "CDCL":
    for file in CDCLBitPatternFiles:
        file.close()

if solver.upper() == "DPLL":
    outputs = DPLLFileNames
elif solver.upper() == "CDCL":
    outputs = CDCLFileNames

for i, solverOutput in enumerate(outputs):
    file = open(solverOutput, 'r')

    statsSolverSum = {}
    statsSolverNum = {}

    regex = re.compile(r"(c [a-zA-Z ]+:)")

    def getStat(file, statSum, statNum):
        for line in file:
            if regex.match(line):
                stat = " ".join(line.split(":")[0].split()[1:])
                statSum[stat] = statSum.get(stat,0) + float(line.split(":")[1].strip().split()[0])
                statNum[stat] = statNum.get(stat,0) + 1

    getStat(file, statsSolverSum, statsSolverNum)

    if solver.upper() == "DPLL":
        outputFile = f'temp/benchmark_{solver}-{DPLLBitPatterns[i]}_{generator}_{n}.txt'
    elif solver.upper() == "CDCL":
        outputFile = f'temp/benchmark_{solver}-{CDCLBitPatterns[i]}_{generator}_{n}.txt'
    with open(outputFile, 'w') as f:
        for stat in ["unit propagations", "decisions", "time"]:
            statSolver1 = statsSolverSum[stat] / statsSolverNum[stat]
            print(f"Average {stat} in {solver}: ", statSolver1, file=f)
    file.close()