# Algorithmisches Beweisen LAB

[Justus Dreßler](mailto:justus.dressler@uni-jena.de)

## Allgemeines

Alle Algorithmen wurden mit `Python 3.12` geschrieben, die C++ Codes sind nicht gedacht für die Abgabe!

CaDiCaL Style refers to the following output format:
```
c comments (divided into header, parsed input, statistics and shutting down)
s SATISFIABLE | UNSATISFIABLE
v variable assignments (if SATISFIABLE)
```
and that the program should exit with status code 10 for SATISFIABLE and 20 for UNSATISFIABLE

## Generating Random CNF's

To generate random CNF's, run the following command:

```
python3.12 RandomCNF/RandomCNF.py n c k [outputfile]
n - number of variables
c - number of clauses
k - number of literals per clause
outputfile - optional output file (default: randomCnf.cnf)
```

## DP

To run the Davis-Putnam algorithm, run the following command:

```
python3.12 DP/DP.py inputfile
inputfile - the input CNF file
```

it outputs to stdout in CaDiCaL style
No proof is generated for UNSAT instances

## DPLL

To run the DPLL algorithm, run the following command:

```
python3.12 DPLL/DPLL.py inputfile
inputfile - the input CNF file
```

it outputs to stdout in CaDiCaL style
No proof is generated for UNSAT instances

## CDCL

To run the CDCL algorithm, run the following command:

```
python3.12 CDCL/CDCL.py inputfile
inputfile - the input CNF file
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
python3.12 test.py solver n tries
solver - CDCL, DPLL, DP or path to Solver
n - number of literals in generated CNF
tries - number of tries to run the solver
```

or run my comparitive benchmark with
```
python3.12 benchmark.py solver1 solver2 n tries
solver1 - CDCL, DPLL, DP or path to Solver
solver2 - CDCL, DPLL, DP or path to Solver
n - number of literals in generated CNF
tries - number of tries to run the solver
```