#include <iostream>
#include <chrono>
#include <vector>
#include <set>
#include <tuple>
#include <algorithm>
#include <sys/resource.h>
#include <fstream>
#include <string>
#include <random>

using Literal = int;
using Level = int;
using Set = std::set<Literal>;
using Info = std::tuple<bool, Literal, double>;
using LiteralInfoArray = std::vector<Info>;
using Clause = std::vector<Literal>;
using CNF = std::vector<Clause>;
using LevelList = std::vector<Level>;
using LiteralList = std::vector<Literal>;
using Conflict = std::vector<Clause>;
using V = std::tuple<LiteralList, LevelList, LiteralInfoArray>;
using namespace std;

std::vector<Clause> NoConflict = std::vector<Clause>();

int statUP = 0;
int statDecisions = 0;
int statConflicts = 0;
int statLearnedClauses = 0;
int statMaxLengthLearnedClause = 0;
int statRestarts = 0;

double b = 2;
double c = 1.05;
double k = 200;
int c_luby = 100;
int numRandomDecision = 0;
int oldStatConflicts = 0;

bool isIn(Literal literal, V v)
{
    Info info = get<2>(v)[abs(literal) - 1];
    return get<0>(info) && get<1>(info) == literal;
}

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
    get<0>(get<2>(v)[abs(literal) - 1]) = true;
    get<1>(get<2>(v)[abs(literal) - 1]) = literal;
    return v;
}

size_t getRandomNumber(size_t start, size_t end)
{
    std::random_device dev;
    std::mt19937 rng(dev());
    std::uniform_int_distribution<std::mt19937::result_type> dist(start, end); // distribution in range [start, end]

    return dist(rng);
    // return start + rand() % (end - start + 1);
}

V decide(CNF &_cnf, V &v, int decisionLevel)
{
    statDecisions++;
    if (numRandomDecision * k < statConflicts)
    {
        numRandomDecision++;
        // get random unset literal
        LiteralList allUnsetLiterals = LiteralList();
        for (Info info : get<2>(v))
        {
            if (get<0>(info) == false)
            {
                allUnsetLiterals.push_back(get<1>(info));
            }
        }
        Literal literal = allUnsetLiterals[getRandomNumber(0, allUnsetLiterals.size() - 1)];
        return setLiteral(v, literal, decisionLevel);
    }
    double max = 0;
    int literal = 0;
    for (Info info : get<2>(v))
    {
        if (!get<0>(info) && get<2>(info) >= max)
        {
            max = get<2>(info);
            literal = get<1>(info);
        }
    }
    return setLiteral(v, literal, decisionLevel);
}

std::tuple<CNF, V, Conflict> propagate(CNF &cnf, V &v, Level decisionLevel)
{
    int i = 0;

    Conflict decidedClauses = Conflict();

    while (i < cnf.size())
    {
        Clause clause = cnf[i];

        if (clause.size() > 1)
        {
            // clause is satisfied
            if (isIn(clause[0], v) ||
                isIn(clause[1], v))
            {

                i++;
                continue;
            }

            if (isIn(-clause[0], v))
            {
                bool found = false;
                for (int j = 1; j < clause.size(); j++)
                {
                    if (!isIn(-clause[j], v))
                    {
                        swap(clause[0], clause[j]);
                        cnf[i] = clause;
                        found = true;
                        break;
                    }
                }
                // no non negative literal found -> conflict
                if (!found) // ELSE
                {
                    statConflicts++;
                    decidedClauses.push_back(clause);
                    return {cnf, v, decidedClauses};
                }
            }
            // new literal is true -> invariant fulfilled
            if (isIn(clause[0], v))
            {
                i++;
                continue;
            }
            if (isIn(-clause[1], v))
            {
                bool found = false;
                for (int j = 2; j < clause.size(); j++)
                {
                    if (!isIn(-clause[j], v))
                    {
                        swap(clause[1], clause[j]);
                        cnf[i] = clause;
                        found = true;
                        break;
                    }
                }
                // only 1 non negative literal found -> unit propagation
                if (!found) // ELSE
                {
                    v = setLiteral(v, clause[0], decisionLevel);
                    decidedClauses.push_back(clause);
                    i = 0;
                    statUP++;
                    continue;
                }
            }
        }
        // clause only contains one literal -> conflict if false, unit propagation if not yet true
        else
        {
            if (isIn(clause[0], v))
            {
                i++;
                continue;
            }
            else if (isIn(-clause[0], v))
            {
                statConflicts++;
                decidedClauses.push_back(clause);
                return {cnf, v, decidedClauses};
            }
            else
            {
                v = setLiteral(v, clause[0], decisionLevel);
                decidedClauses.push_back(clause);
                i = 0;
                statUP++;
                continue;
            }
        }
        i++;
    }
    return {cnf, v, NoConflict};
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
    Set allLiteralsInConflict = Set();

    int index = c_conflict.size() - 1;
    for (Literal literal : c_conflict[index])
    {
        int level = getLevel(v, -literal);
        if (level == decisionLevel)
        {
            currentLevelLiterals.insert(-literal);
            allLiteralsInConflict.insert(-literal);
        }
        else
        {
            previousLevelLiterals.insert({-literal, level});
            allLiteralsInConflict.insert(-literal);
        }
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
                allLiteralsInConflict.insert(-literal);
            }
            else
            {
                previousLevelLiterals.insert({-literal, level});
                allLiteralsInConflict.insert(-literal);
            }
        }
    }

    Literal UIP1 = *currentLevelLiterals.begin();

    // find next decision level
    Level nextDecisionLevel = 0;
    for (auto [literal, level] : previousLevelLiterals)
    {
        if (level > nextDecisionLevel)
        {
            nextDecisionLevel = level;
        }
    }

    // update VSIDS
    for (Literal literal : allLiteralsInConflict)
    {
        get<2>(get<2>(v)[abs(literal) - 1]) += b;
    }
    b *= c;

    // scale all numbers if b is too large
    if (b > pow(10, 30))
    {
        for (Info info : get<2>(v))
        {
            get<2>(info) /= b;
        }
        b = 1;
    }

    Clause learnedClause = Clause();
    learnedClause.push_back(-UIP1);
    for (auto [literal, level] : previousLevelLiterals)
    {
        learnedClause.push_back(-literal);
    }

    statLearnedClauses++;
    statMaxLengthLearnedClause = max(statMaxLengthLearnedClause, (int)learnedClause.size());
    return {learnedClause, nextDecisionLevel};
}

// https://stackoverflow.com/a/59420788
template <typename T>
static constexpr inline T pown(T x, unsigned p)
{
    T result = 1;

    while (p)
    {
        if (p & 0x1)
        {
            result *= x;
        }
        x *= x;
        p >>= 1;
    }

    return result;
}

int luby(int i)
{
    int k = log2(i) + 1;
    if (i == pown(2, k) - 1)
    {
        return pown(2, k - 1);
    }
    return luby(i - pown(2, k - 1) + 1);
}

std::tuple<CNF, V, Level> applyRestartPolicy(CNF &cnf, V &v, Level decisionLevel)
{
    int newConflicts = statConflicts - oldStatConflicts;

    if (newConflicts > c_luby * luby(statRestarts + 1))
    {
        statRestarts++;
        oldStatConflicts = statConflicts;
        for (Info &info : get<2>(v))
        {
            get<0>(info) = false;
        }
        v = {LiteralList(), LevelList(), get<2>(v)};
        decisionLevel = 0;
    }

    return {cnf, v, decisionLevel};
}

V backtrack(V &v, Level new_decision_level)
{
    if (new_decision_level == 0)
    {
        for (Literal lit : get<0>(v))
        {
            get<0>(get<2>(v)[abs(lit) - 1]) = false;
        }
        return {LiteralList(), LevelList(), get<2>(v)};
    }

    for (int i = 0; i < get<1>(v).size(); i++)
    {
        Level level = get<1>(v)[i];
        // first found literal is decisionLiteral on that level
        if (level >= new_decision_level)
        {
            for (int j = i + 1; j < get<0>(v).size(); j++)
            {
                Literal lit = get<0>(v)[j];
                get<0>(get<2>(v)[abs(lit) - 1]) = false;
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
    Conflict c_conflict = NoConflict;

    LiteralInfoArray infoArr = LiteralInfoArray();
    for (int i = 1; i < numLiterals + 1; i++)
    {
        infoArr.push_back({false, -i, 0});
    }

    V v = {LiteralList(), LevelList(), infoArr};
    while (get<0>(v).size() < numLiterals)
    {
        decisionLevel++;
        v = decide(cnf, v, decisionLevel);
        tie(cnf, v, c_conflict) = propagate(cnf, v, decisionLevel);

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
            v = backtrack(v, decisionLevel);
            tie(cnf, v, c_conflict) = propagate(cnf, v, decisionLevel);
        }
        tie(cnf, v, decisionLevel) = applyRestartPolicy(cnf, v, decisionLevel);
    }
    return {true, get<0>(v), NoConflict};
}

// https://stackoverflow.com/a/4609795
template <typename T>
int sign(T val)
{
    return (T(0) < val) - (val < T(0));
}

// https://www.geeksforgeeks.org/binary-search/
// An iterative binary search function.
int binarySearch(LiteralList arr, int low, int high, Literal lit)
{
    while (low <= high)
    {
        int mid = low + (high - low) / 2;

        // Check if x is present at mid
        if (arr[mid] == lit)
            return mid;

        // If x greater, ignore left half
        if (arr[mid] < lit)
            low = mid + 1;

        // If x is smaller, ignore right half
        else
            high = mid - 1;
    }

    // If we reach here, then element was not present
    return -1;
}

int indexOf(Literal lit, LiteralList arr)
{
    int result = binarySearch(arr, 0, arr.size() - 1, lit);
    if (result == -1)
    {
        throw "Element not found";
    }
    return result;
}

std::tuple<CNF, string> readCnf(string filename)
{
    string header = "";
    CNF cnf = CNF();
    Set vars = Set();

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
                vars.insert(abs(lit));
                literal = "";
            }
            else
            {
                literal += line[i];
            }
        }
        sort(clause.begin(), clause.end(), [](int a, int b)
             { return abs(a) < abs(b); });
        cnf.push_back(clause);
    }

    // map all variables to continuous list 1,2,...,n
    LiteralList existingVars(vars.begin(), vars.end());
    sort(existingVars.begin(), existingVars.end());

    for (int i = 0; i < cnf.size(); i++)
    {
        Clause clause = cnf[i];
        for (int j = 0; j < clause.size(); j++)
        {
            Literal lit = clause[j];
            cnf[i][j] = sign(lit) * (indexOf(abs(lit), existingVars) + 1);
        }
    }

    return {cnf, header};
}

int main(int argc, char const *argv[])
{
    srand(5);

    auto startTime = std::chrono::high_resolution_clock::now();

    string filename = "../randomCnf.cnf";

    if (argc == 2)
    {
        filename = argv[1];
    }

    auto [cnf, header] = readCnf(filename);
    auto [satisfiable, assignment, conflict] = CDCL(cnf);

    if (!satisfiable)
    {
        ofstream drat;
        drat.open("proof.drat");
        for (Clause clause : conflict)
        {
            for (Literal literal : clause)
            {
                drat << literal << " ";
            }
            drat << "0" << endl;
        }
        drat.close();
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
        {"numRestarts", to_string(statRestarts)},
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
