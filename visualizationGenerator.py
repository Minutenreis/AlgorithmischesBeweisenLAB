import subprocess

nValuesRandomCDCL = [4,8,16, 32, 64, 128, 160]
nValuesRandomDPLL = [4,8,16, 32, 64, 80, 96]
nValuesPHPCDCL = [1,2,3,4,5,6,7]
nValuesPHPDPLL = [1,2,3,4,5,6,7,8]
nValuesPebblingCDCL = [2,4,8,9,10,15,20,25,30,35,40,45,50]
nValuesPebblingDPLL = [2,3,4,5]

print("CDCL Random")
for n in nValuesRandomCDCL:
    subprocess.call(["python3.12", "benchmark.py", "cdcl", str(n), "random"])
print("DPLL Random")
for n in nValuesRandomDPLL:
    subprocess.call(["python3.12", "benchmark.py", "dpll", str(n), "random"])
print("CDCL PHP")
for n in nValuesPHPCDCL:
    subprocess.call(["python3.12", "benchmark.py", "cdcl", str(n), "php"])
print("DPLL PHP")
for n in nValuesPHPDPLL:
    subprocess.call(["python3.12", "benchmark.py", "dpll", str(n), "php"])
print("CDCL Pebbling")
for n in nValuesPebblingCDCL:
    subprocess.call(["python3.12", "benchmark.py", "cdcl", str(n), "pebbling"])
print("DPLL Pebbling")
for n in nValuesPebblingDPLL:
    subprocess.call(["python3.12", "benchmark.py", "dpll", str(n), "pebbling"])