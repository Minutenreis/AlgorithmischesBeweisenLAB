SCRIPT_DIR=$(dirname "$0")

mkdir -p $SCRIPT_DIR/bin

g++ $SCRIPT_DIR/CDCL.cpp -std=c++20 -O3 -o $SCRIPT_DIR/bin/CDCL.out
$SCRIPT_DIR/bin/CDCL.out $SCRIPT_DIR/../randomCnf.cnf