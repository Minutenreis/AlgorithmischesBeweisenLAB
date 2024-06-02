#include <iostream>
#include <chrono>
#include <vector>
#include <set>
#include <tuple>
#include <algorithm>
#include <sys/resource.h>
#include <fstream>
#include <string>

using Literal = int;
using Level = int;
using Set = std::set<Literal>;
using Clause = std::vector<Literal>;
using CNF = std::vector<Clause>;
using LevelList = std::vector<Level>;
using LiteralList = std::vector<Literal>;
using Conflict = std::vector<Clause>;
using V = std::tuple<LiteralList, LevelList, Set>;
using namespace std;

std::vector<Clause> NoConflict = std::vector<Clause>();

int statUP = 0;
int statDecisions = 0;
int statConflicts = 0;
int statLearnedClauses = 0;
int statMaxLengthLearnedClause = 0;

int getNumLiterals(CNF &cnf)
{
    Set literals = Set();
    for (Clause clause : cnf)
    {
        for (Literal literal : clause)
        {
            literals.insert(abs(literal));
        }
    }
    return literals.size();
}

V setLiteral(V &v, Literal literal, int decisionLevel)
{
    get<0>(v).push_back(literal);
    get<1>(v).push_back(decisionLevel);
    get<2>(v).insert(literal);
    return v;
}

V decide(CNF &cnf, V &v, int decisionLevel)
{
    statDecisions++;

    for (Clause clause : cnf)
        for (Literal literal : clause)
            if (!get<2>(v).contains(literal) &&
                !get<2>(v).contains(-literal))
            {
                return setLiteral(v, literal, decisionLevel);
            }
    throw "All literals are assigned";
}

std::tuple<V, Conflict> propagate(CNF &cnf, V &v, Level decisionLevel)
{
    int i = 0;

    Conflict decidedClauses = Conflict();

    while (i < cnf.size())
    {
        Clause clause = cnf[i];

        if (clause.size() > 1)
        {
            // clause is satisfied
            if (get<2>(v).contains(clause[0]) ||
                get<2>(v).contains(clause[1]))
            {
                i++;
                continue;
            }

            if (get<2>(v).contains(-clause[0]))
            {
                bool found = false;
                for (int j = 1; j < clause.size(); j++)
                {
                    if (!get<2>(v).contains(clause[j]))
                    {
                        swap(clause[0], clause[j]);
                        found = true;
                        break;
                    }
                }
                // no non negative literal found -> conflict
                if (!found) // ELSE
                {
                    statConflicts++;
                    decidedClauses.push_back(clause);
                    return {v, decidedClauses};
                }
            }
            // new literal is true -> invariant fulfilled
            if (get<2>(v).contains(clause[0]))
            {
                i++;
                continue;
            }
            if (get<2>(v).contains(-clause[1]))
            {
                for (int j = 2; j < clause.size(); j++)
                {
                    bool found = false;
                    if (!get<2>(v).contains(-clause[j]))
                    {
                        swap(clause[1], clause[j]);
                        found = true;
                        break;
                    }
                    // only 1 non negative literal found -> unit propagation
                    if (!found) // ELSE
                    {
                        setLiteral(v, clause[0], decisionLevel);
                        decidedClauses.push_back(clause);
                        i = 0;
                        statUP++;
                        continue;
                    }
                }
            }
        }
        // clause only contains one literal -> conflict if false, unit propagation if not yet true
        else
        {
            if (get<2>(v).contains(clause[0]))
            {
                i++;
                continue;
            }
            else if (get<2>(v).contains(-clause[0]))
            {
                statConflicts++;
                decidedClauses.push_back(clause);
                return {
                    v, decidedClauses};
            }
            else
            {
                setLiteral(v, clause[0], decisionLevel);
                decidedClauses.push_back(clause);
                i = 0;
                statUP++;
                continue;
            }
        }
        i++;
    }
    return {v, NoConflict};
}

int getLevel(V &v, Literal literal)
{
    for (int i = 0; i < get<0>(v).size(); i++)
    {
        if (get<0>(v)[i] == literal)
        {
            return get<1>(v)[i];
        }
    }
    return -1;
}

std::tuple<Clause, Level> analyzeConflict(V &v, Conflict c_conflict, Level decisionLevel)
{
    std::set<std::tuple<Literal, Level>> previousLevelLiterals = std::set<std::tuple<Literal, Level>>();
    Set currentLevelLiterals = Set();

    int index = c_conflict.size() - 1;
    for (Literal literal : c_conflict[index])
    {
        int level = getLevel(v, -literal);
        if (level == decisionLevel)
            currentLevelLiterals.insert(-literal);
        else
            previousLevelLiterals.insert({-literal, level});
    }

    while (currentLevelLiterals.size() > 1)
    {
        index--;
        Clause clauseToResolve = c_conflict[index];
        // unrelated unit propagation
        bool unrelated = true;
        for (Literal literal : clauseToResolve)
        {
            if (currentLevelLiterals.contains(literal))
            {
                unrelated = false;
                break;
            }
        }
        if (unrelated)
        {
            continue;
        }

        // resolve over literal backwards
        for (Literal literal : clauseToResolve)
        {
            // implied literal, now not pointed to
            if (currentLevelLiterals.contains(literal))
            {
                currentLevelLiterals.erase(literal);
                continue;
            }
            int level = getLevel(v, -literal);
            if (level == decisionLevel)
            {
                currentLevelLiterals.insert(-literal);
            }
            else
            {
                previousLevelLiterals.insert({-literal, level});
            }
        }
    }

    Literal UIP1 = *currentLevelLiterals.begin();

    Level nextDecisionLevel = 0;
    for (auto [literal, level] : previousLevelLiterals)
    {
        if (level > nextDecisionLevel)
        {
            nextDecisionLevel = level;
        }
    }

    Clause learnedClause = Clause();
    learnedClause.push_back(UIP1);
    for (auto [literal, level] : previousLevelLiterals)
    {
        learnedClause.push_back(-literal);
    }

    statLearnedClauses++;
    statMaxLengthLearnedClause = max(statMaxLengthLearnedClause, (int)learnedClause.size());
    return {learnedClause, nextDecisionLevel};
}

std::tuple<CNF, V, Level> applyRestartPolicy(CNF &cnf, V &v, Level decisionLevel, CNF &ogCnf)
{
    return {cnf, v, decisionLevel};
}

V backtrack(V &v, Level new_decision_level)
{
    if (new_decision_level == 0)
        return {LiteralList(), LevelList(), Set()};

    for (int i = 0; i < get<0>(v).size(); i++)
    {
        Level level = get<1>(v)[i];
        if (level >= new_decision_level)
        {
            for (int j = i + 1; j < get<0>(v).size(); j++)
            {
                get<2>(v).erase(get<0>(v)[j]);
            }
            get<0>(v).erase(get<0>(v).begin() + i + 1, get<0>(v).end());
            get<1>(v).erase(get<1>(v).begin() + i + 1, get<1>(v).end());
            return v;
        }
    }
    throw "No literal found to backtrack";
}

std::tuple<bool, std::vector<Literal>, Conflict> CDCL(CNF &cnf)
{
    CNF ogCnf = CNF();
    for (Clause clause : cnf)
    {
        ogCnf.push_back(clause);
    }
    int decisionLevel = 0;
    int numLiterals = getNumLiterals(cnf);
    V v = {LiteralList(), LevelList(), Set()};
    while (get<0>(v).size() < numLiterals)
    {
        decisionLevel++;
        v = decide(cnf, v, decisionLevel);
        auto [v_, c_conflict] = propagate(cnf, v, decisionLevel);
        v = v_;
        while (c_conflict != NoConflict)
        {
            if (decisionLevel == 0)
            {
                Conflict newClauses = Conflict();
                for (int i = ogCnf.size(); i < cnf.size(); i++)
                {
                    newClauses.push_back(cnf[i]);
                }
                return {false, get<0>(v), newClauses};
            }
            auto [learnedClause, new_decision_level] = analyzeConflict(v, c_conflict, decisionLevel);
            decisionLevel = new_decision_level;
            cnf.push_back(learnedClause);
            v = backtrack(v, new_decision_level);
            auto [v_, c_conflict_] = propagate(cnf, v, decisionLevel);
            v = v_;
            c_conflict = c_conflict_;
        }
        auto [cnf2_, v2_, decisionLevel2_] = applyRestartPolicy(cnf, v, decisionLevel, ogCnf);
        cnf = cnf2_;
        v = v2_;
        decisionLevel = decisionLevel2_;
    }
    return {true, get<0>(v), Conflict()};
}

std::tuple<CNF, string> readCnf(string filename)
{
    string header = "";
    CNF cnf = CNF();

    fstream cnfFile(filename);
    string line;
    while (getline(cnfFile, line))
    {
        if (line[0] == 'c')
            continue;
        if (line[0] == 'p')
        {
            header = line;
            header.erase(header.find_last_not_of(" \n\r\t") + 1);
            continue;
        }
        Clause clause = Clause();
        string literal;
        for (int i = 0; i < line.size(); i++)
        {
            if (line[i] == ' ')
            {
                int lit = stoi(literal);
                if (lit == 0)
                    break;
                clause.push_back(lit);
                literal = "";
            }
            else
            {
                literal += line[i];
            }
        }
        cnf.push_back(clause);
    }
    return {cnf, header};
}

int main(int argc, char const *argv[])
{
    auto startTime = std::chrono::high_resolution_clock::now();

    if (argc != 2)
    {
        cout << "Usage ./CDCL <filename>" << endl;
        return 1;
    }

    string filename = argv[1];

    auto [cnf, header] = readCnf(filename);
    auto [satisfiable, assignment, conflict] = CDCL(cnf);

    if (!satisfiable)
    {
        fstream drat("proof.drat");
        for (Clause clause : conflict)
        {
            for (Literal literal : clause)
            {
                drat << literal << " ";
            }
            drat << "0" << endl;
        }
    }

    auto endTime = std::chrono::high_resolution_clock::now();
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    auto statPeakMemoryMB = usage.ru_maxrss / 1024;

    vector<tuple<string, string>> stats = {
        {"decisions", to_string(statDecisions)},
        {"conflicts", to_string(statConflicts)},
        {"unit propagations", to_string(statUP)},
        {"learned clauses", to_string(statLearnedClauses)},
        {"max length learned clause", to_string(statMaxLengthLearnedClause)},
        {"peak memory usage (MB)", to_string(statPeakMemoryMB)},
        {"runtime (ms)", to_string(std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count())}};

    for (tuple<string, string> stat : stats)
    {
        get<0>(stat) = get<0>(stat) + string(40 - get<0>(stat).length(), ' ');
    }

    string lightBlue = "\033[96m";
    string purple = "\033[95m";
    string darkBlue = "\033[94m";
    string green = "\033[92m";
    string end = "\033[0m";
    string bold = "\033[1m";
    string underline = "\033[4m";
    string italic = "\033[3m";

    cout << "c " << lightBlue << "--- [ " << end << darkBlue << bold << "banner" << end << lightBlue << " ] -------------------------------------------------------------" << end << endl;
    cout << "c " << endl;
    cout << "c " << purple << "CDCL C++ Implementation" << end << endl;
    cout << "c " << purple << "Justus Dreßler" << end << endl;
    cout << "c " << purple << "created for FMI-IN0159 Algorithmisches Beweisen LAB" << end << endl;
    cout << "c " << endl;
    cout << "c " << lightBlue << "--- [ " << end << darkBlue << bold << "parsing input" << end << lightBlue << " ] ------------------------------------------------------" << end << endl;
    cout << "c " << endl;
    cout << "c " << "reading DIMACS file from '" << green << filename << end << "'" << endl;
    if (header != "")
        cout << "c " << "found '" << green << header << end << "' header" << endl;
    cout << "c " << endl;
    cout << "c " << lightBlue << "--- [ " << end << darkBlue << bold << "result" << end << lightBlue << " ] -------------------------------------------------------------" << end << endl;
    cout << "c " << endl;

    cout << "s " << (satisfiable ? "SATISFIABLE" : "UNSATISFIABLE") << endl;

    if (satisfiable and assignment.size() > 0)
    {
        sort(assignment.begin(), assignment.end(), [](int a, int b)
             { return abs(a) < abs(b); });
        cout << "v ";
        int currentLineLength = 2;
        for (int literal : assignment)
        {
            if (currentLineLength + to_string(literal).length() > 78)
            {
                cout << endl;
                cout << "v ";
                currentLineLength = 2;
            }
            cout << literal << " ";
            currentLineLength += to_string(literal).length() + 1;
        }
        cout << endl;
    }
    cout << "c " << endl;
    cout << "c " << lightBlue << "--- [ " << end << darkBlue << bold << "statistics" << end << lightBlue << " ] ---------------------------------------------------------" << end << endl;
    cout << "c " << endl;
    for (tuple<string, string> stat : stats)
        cout << "c " << get<0>(stat) << ":" << get<1>(stat) << endl;
    cout << "c " << endl;
    cout << "c " << lightBlue << "--- [ " << end << darkBlue << bold << "shutting down" << end << lightBlue << " ] ------------------------------------------------------" << end << endl;
    cout << "c " << endl;
    cout << "c exit " << (satisfiable ? 10 : 20) << endl;
    return (satisfiable ? 10 : 20);
}
