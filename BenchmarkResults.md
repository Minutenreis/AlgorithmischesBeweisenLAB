# Benchmark Results

## Preamble

To explain all the pictures a bit, the solvers are listed as "CDCL-XXXXX" and "DPLL-X".
The X bitpatterns each stand for the following:\
CDCL: \[restarts,VSIDS,ClauseLearning,ClauseDeletion,ClauseMinimization\]\
Each bit stands for whether the feature is set or not (where ClauseLearning means whether a 1UIP learning scheme is used or just the decided literals are learned).

DPLL: \[PureLiteralElimination\]\
This bit stands for whether the solver uses the pure literal elimination heuristic or not.

## General Observations

Running Time, Unit Propagations and Decisions seemed all to exhibit a large correlation.
Because of that I will mostly focus on the running time, since it is the most intuitive measure of performance.

## Random CNF's

For the random CNF's each solver was run on 100 CNF's with n variables and 4n claues.

![RandomTime](/Plots/Time_Random.png)
![RandomUnitPropagations](/Plots/Unit_Propagations_Random.png)
![RandomDecisions](/Plots/Decisions_Random.png)

We see that DP is the slowest solver by far.
It was followed by DPLL and then with another smaller gap CDCL.
Also in CDCL the Restarts turned out to be a lot better for runtime over n=128 (the variation without has no datapoint since it was too slow to record it).
In the highest n value (n=160) it is evident that CDCL with local clause minimization is faster than without it.

The most surprising bit for me was that Pure Literal Elimination didn't make that much of a difference in DPLL.

## PHP
![PHPTime](/Plots/Time_PHP.png)
![PHPUnitPropagations](/Plots/Unit_Propagations_PHP.png)
![PHPDecisions](/Plots/Decisions_PHP.png)

In PHP we see again that DP is by far the slowest solver outside of trivial instances.
We also see that CDCL is generally slower than DPLL, because all the extra steps amount to nothing on PHP.
The only exception was CDCL with all optional features turned off, but that is likely explained by the more efficient watchedLiterals implementation than iterating over the Array in my DPLL variation, so an implementation problem not an algorithmic difference.

I was once again surprised that Pure Literal Elimination actually improved the runtime of DPLL quite a bit on PHP.

## Pebbling
![PebblingTime](/Plots/Time_Pebbling.png)
![PebblingUnitPropagations](/Plots/Unit_Propagations_Pebbling.png)
![PebblingDecisions](/Plots/Decisions_Pebbling.png)

In Pebbling tests the exponential divide between CDCL and DPLL is very visible.
The DPLL variations and CDCL with all features turned off all performed significantly worse than CDCL in general.
Once again DPLL with pure literal elimination was faster than without it and CDCL is even faster, likely again because of watched Literals.
Its also visible that in CDCL the improved learning scheme (green, orange, blue) cut down on runnning times significantly.
The red line was again cut out because it didn't finish in a reasonable time for instances larger than n=15. 