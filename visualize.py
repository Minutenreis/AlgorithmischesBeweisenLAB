import matplotlib.pyplot as plt
import subprocess 

def saveFig(nValuesCDCL,CDCLBitPatterns, CDCLValues, nValuesDPLL, DPLLValues, GeneratorName, ylabel):
    for i, bitPattern in enumerate(CDCLBitPatterns):
        tempNValuesCDCL = nValuesCDCL
        if len(CDCLValues[i]) < len(nValuesCDCL):
            tempNValuesCDCL = nValuesCDCL[:len(CDCLValues[i])]
        plt.plot(tempNValuesCDCL, CDCLValues[i], label=f'CDCL-{bitPattern}')
    for i, bitPattern in enumerate(DPLLBitPatterns):
        plt.plot(nValuesDPLL, DPLLValues[i], label=f'DPLL-{bitPattern}')
    plt.xlabel('n')
    if GeneratorName != 'PHP':
        plt.xscale('log', base=2)
    plt.ylabel(ylabel)
    plt.yscale('log', base=10)
    plt.title(ylabel + ' ' + GeneratorName)
    plt.legend()
    plt.savefig("Plots/"+(ylabel + ' ' + GeneratorName).replace(' ', '_') + '.png')
    plt.clf()

def parseFile(fileName, UPArr, DecArr, TimeArr):
    with open(fileName, 'r') as file:
        for line in file:
            if line.startswith('Average unit propagations'):
                UPArr.append(float(line.split(":")[1]))
            elif line.startswith('Average decisions'):
                DecArr.append(float(line.split(":")[1]))
            elif line.startswith('Average time'):
                TimeArr.append(float(line.split(":")[1]))

# random with 4 ratio averaged over 100 instances
nValuesRandomCDCL = [16, 32, 64, 128]
#BitPattern: optRestarts, optVSIDS, optClauseLearning, optClauseDeletion, optClauseMinimization
CDCLBitPatterns = ['11111', '11110', '11100', '11000', '10000', '00000']
CDCLUnitPropagationsRandom = []
CDCLDecisionsRandom = []
CDCLTimeRandom = []
for i, bitPattern in enumerate(CDCLBitPatterns):
    CDCLUnitPropagationsRandom.append([])
    CDCLDecisionsRandom.append([])
    CDCLTimeRandom.append([])
    for n in nValuesRandomCDCL:
        # no data recorded because too slow
        if n > 100 and bitPattern[1] == '0':
            continue
        filename = f"temp/benchmark_cdcl-{bitPattern}_random_{n}.txt"
        parseFile(filename, CDCLUnitPropagationsRandom[i], CDCLDecisionsRandom[i], CDCLTimeRandom[i])

nValuesRandomDPLL = [16, 32, 64, 80, 96]
DPLLBitPatterns = ['0', '1']
DPLLUnitPropagationsRandom = []
DPLLDecisionsRandom = []
DPLLTimeRandom = []
for i, bitPattern in enumerate(DPLLBitPatterns):
    DPLLUnitPropagationsRandom.append([])
    DPLLDecisionsRandom.append([])
    DPLLTimeRandom.append([])
    for n in nValuesRandomDPLL:
        filename = f"temp/benchmark_dpll-{bitPattern}_random_{n}.txt"
        parseFile(filename, DPLLUnitPropagationsRandom[i], DPLLDecisionsRandom[i], DPLLTimeRandom[i])

nValuesPHPCDCL = [1,2,3,4,5,6,7]
CDCLUnitPropagationsPHP = []
CDCLDecisionsPHP = []
CDCLTimePHP = []
for i, bitPattern in enumerate(CDCLBitPatterns):
    CDCLUnitPropagationsPHP.append([])
    CDCLDecisionsPHP.append([])
    CDCLTimePHP.append([])
    for n in nValuesPHPCDCL:
        filename = f"temp/benchmark_cdcl-{bitPattern}_php_{n}.txt"
        parseFile(filename, CDCLUnitPropagationsPHP[i], CDCLDecisionsPHP[i], CDCLTimePHP[i])

nValuesPHPDPLL = [1,2,3,4,5,6,7,8]
DPLLUnitPropagationsPHP = []
DPLLDecisionsPHP = []
DPLLTimePHP = []
for i, bitPattern in enumerate(DPLLBitPatterns):
    DPLLUnitPropagationsPHP.append([])
    DPLLDecisionsPHP.append([])
    DPLLTimePHP.append([])
    for n in nValuesPHPDPLL:
        filename = f"temp/benchmark_dpll-{bitPattern}_php_{n}.txt"
        parseFile(filename, DPLLUnitPropagationsPHP[i], DPLLDecisionsPHP[i], DPLLTimePHP[i])

nValuesPebblingCDCL = [2,4,8,10,15,20,25,30,35,40,45,50]
CDCLUnitPropagationsPebbling = []
CDCLDecisionsPebbling = []
CDCLTimePebbling = []
for i, bitPattern in enumerate(CDCLBitPatterns):
    CDCLUnitPropagationsPebbling.append([])
    CDCLDecisionsPebbling.append([])
    CDCLTimePebbling.append([])
    for n in nValuesPebblingCDCL:
        # no data recorded because too slow
        if n > 8 and bitPattern[1] == '0':
            continue
        if n > 16 and bitPattern[2] == '0':
            continue
        filename = f"temp/benchmark_cdcl-{bitPattern}_pebbling_{n}.txt"
        parseFile(filename, CDCLUnitPropagationsPebbling[i], CDCLDecisionsPebbling[i], CDCLTimePebbling[i])

nValuesPebblingDPLL = [2,3,4,5,6]
DPLLUnitPropagationsPebbling = []
DPLLDecisionsPebbling = []
DPLLTimePebbling = []
for i, bitPattern in enumerate(DPLLBitPatterns):
    DPLLUnitPropagationsPebbling.append([])
    DPLLDecisionsPebbling.append([])
    DPLLTimePebbling.append([])
    for n in nValuesPebblingDPLL:
        filename = f"temp/benchmark_dpll-{i}_pebbling_{n}.txt"
        parseFile(filename, DPLLUnitPropagationsPebbling[i], DPLLDecisionsPebbling[i], DPLLTimePebbling[i])

# manuelle Nachträge aus Einzelmessungen
CDCLDecisionsPHP[5].append(3039)
CDCLUnitPropagationsPHP[5].append(64007)
CDCLTimePHP[5].append(1.5334668159484863)
CDCLDecisionsPHP[5].append(8405)
CDCLUnitPropagationsPHP[5].append(202217)
CDCLTimePHP[5].append(13.927376508712769)
nValuesPHPCDCL.append(8)
nValuesPHPCDCL.append(9)

saveFig(nValuesRandomCDCL, CDCLBitPatterns, CDCLUnitPropagationsRandom, nValuesRandomDPLL, DPLLUnitPropagationsRandom, 'Random', 'Unit Propagations')
saveFig(nValuesRandomCDCL, CDCLBitPatterns, CDCLDecisionsRandom, nValuesRandomDPLL, DPLLDecisionsRandom, 'Random', 'Decisions')
saveFig(nValuesRandomCDCL, CDCLBitPatterns, CDCLTimeRandom, nValuesRandomDPLL, DPLLTimeRandom, 'Random', 'Time')
saveFig(nValuesPHPCDCL, CDCLBitPatterns, CDCLUnitPropagationsPHP, nValuesPHPDPLL, DPLLUnitPropagationsPHP, 'PHP', 'Unit Propagations')
saveFig(nValuesPHPCDCL, CDCLBitPatterns, CDCLDecisionsPHP, nValuesPHPDPLL, DPLLDecisionsPHP, 'PHP', 'Decisions')
saveFig(nValuesPHPCDCL, CDCLBitPatterns, CDCLTimePHP, nValuesPHPDPLL, DPLLTimePHP, 'PHP', 'Time')
saveFig(nValuesPebblingCDCL, CDCLBitPatterns, CDCLUnitPropagationsPebbling, nValuesPebblingDPLL, DPLLUnitPropagationsPebbling, 'Pebbling', 'Unit Propagations')
saveFig(nValuesPebblingCDCL, CDCLBitPatterns, CDCLDecisionsPebbling, nValuesPebblingDPLL, DPLLDecisionsPebbling, 'Pebbling', 'Decisions')
saveFig(nValuesPebblingCDCL, CDCLBitPatterns, CDCLTimePebbling, nValuesPebblingDPLL, DPLLTimePebbling, 'Pebbling', 'Time')