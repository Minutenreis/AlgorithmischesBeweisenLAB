# Description: Initialize and update submodules 
# and generate their binaries
# Usage: ./Submodules.sh

git submodule update --init --recursive
cd submodules/cadical
./configure && make
cd ../drat-trim
make
cd ../..