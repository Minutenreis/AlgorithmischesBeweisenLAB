# Algorithmisches Beweisen LAB

[Justus Dreßler](mailto:justus.dressler@uni-jena.de)

## Allgemeines

Alle Algorithmen wurden mit `Python 3.12` geschrieben.

CaDiCaL Style refers to the following output format:
```
c comments (divided into header, parsed input, statistics and shutting down)
s SATISFIABLE | UNSATISFIABLE
v variable assignments (if SATISFIABLE)
```
and that the program should exit with status code 10 for SATISFIABLE and 20 for UNSATISFIABLE

## Generating CNF's

To generate a random CNF file, run the following command:

```
python3.12 Generator/RandomCNF.py n [c] [k] [outputName]
n: number of variables
[c]: number of clauses (optional, default: 3.8*n)
[k]: number of literals per clause (optional, default: 3)
outputName: name of the output file (optional)
```

To generate a PHP CNF file, run the following command:

```
python3.12 Generator/PHP.py n [outputfile]
n: number of holes in the PHP
outputName: name of the output file (optional)
```

To generate a Pebbling CNF file, run the following command:

```
python3.12 Generator/Pebbling.py n [outputfile]
n: number of source nodes
outputName: name of the output file (optional)
```

## 2-SAT

To run the 2-SAT algorithm, run the following command:

```
python3.12 2SAT/2SAT.py inputfile
inputfile - the input CNF file
```

it outputs to stdout in CaDiCaL style
No proof is generated for UNSAT instances

## DP

To run the Davis-Putnam algorithm, run the following command:

```
python3.12 DP/DP.py filename
filename: path to the cnf file
```

it outputs to stdout in CaDiCaL style
No proof is generated for UNSAT instances

## DPLL

To run the DPLL algorithm, run the following command:

```
python3.12 DPLL/DPLL.py filename
filename: path to the cnf file
```

it outputs to stdout in CaDiCaL style
No proof is generated for UNSAT instances

## CDCL

To run the CDCL algorithm, run the following command:

```
python3.12 CDCL/CDCL.py filename
filename: path to the cnf file
```

it outputs to stdout in CaDiCaL style
A proof is generated in the file `proof.drat`

## Other

There are some convenience methods included.

You may checkout `CaDiCaL` and `drat-trim` with `./Submodules.sh`

You may call each inidividually with 
```
./Submodules/drat-trim/drat-trim randomCnf.cnf proof.drat
``` 
or 
```
./Submodules/CaDiCaL/build/cadical randomCnf.cnf
```

You may also run my tests with 
```
python3.12 test.py solver n tries [generator]
solver: path to the solver (python3.12) or one of the following: CDCL, DPLL, DP
n: number of literals if randomGenerator is used, number of sourcenodes if Pebbling is used, number of holes in the PHP if PHP is used
tries: number of CNFs to generate and test
[generator]: path to the generator (python3.12) or one of thefollowing: PHP, Pebbling, Random  (optional)
```

or run my comparitive benchmark with
```
python3.12 benchmark.py solver1 solver2 n tries [generator]
solver1: path to the solver1 (python3.12) or one of the following: CDCL, DPLL, DP
solver2: path to the solver2 (python3.12) or one of the following: CDCL, DPLL, DP
n: number of literals if randomGenerator is used, number of source nodes if Pebbling is used, number of holes in the PHP if PHP is used
tries: number of CNFs to generate and test
[generator]: path to the generator (python3.12) or one of the following: PHP, Pebbling, Random  (optional)
```