# Benchmark Results

## Preamble

To explain all the pictures a bit, the solvers are listed as "CDCL-XXXXX" and "DPLL-X".
The X bitpatterns each stand for the following:\
CDCL: \[restarts,VSIDS,ClauseLearning,ClauseDeletion,ClauseMinimization\]\
Each bit stands for whether the feature is set or not (where ClauseLearning means whether a 1UIP learning scheme is used or just the decided literals are learned).

DPLL: \[PureLiteralElimination\]\
This bit stands for whether the solver uses the pure literal elimination heuristic or not.

## Random CNF's

![RandomTime](/Plots/Time_Random.png)
![RandomUnitPropagations](/Plots/Unit_Propagations_Random.png)
![RandomDecisions](/Plots/Decisions_Random.png)

## PHP
![PHPTime](/Plots/Time_PHP.png)
![PHPUnitPropagations](/Plots/Unit_Propagations_PHP.png)
![PHPDecisions](/Plots/Decisions_PHP.png)

## Pebbling
![PebblingTime](/Plots/Time_Pebbling.png)
![PebblingUnitPropagations](/Plots/Unit_Propagations_Pebbling.png)
![PebblingDecisions](/Plots/Decisions_Pebbling.png)

// TODO: Erklärungen