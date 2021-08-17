#!/bin/sh

PARAMS=$@
if [ $# -eq 1 ]; then
    if [ -e $1 ]; then
        PARAMS=${1%.py}
    fi
fi

if [ ! -e README.md ]; then
    cd ../../
fi

PYTHONPATH=./:test/unit ${PYTHON_BIN:-python3} -m unittest ${PARAMS}
