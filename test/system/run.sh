#!/usr/bin/env bash

function phaseStart
{
    echo "Phase:: $@"
}

function phaseEnd
{
    echo "Phase:: End"
}

function setupStepStart
{
    echo "Test:: $@"
}

function setupStepEnd
{
    echo "Test:: End"
}

function testStart
{
    echo "Test:: $@"
}

function testEnd
{
    echo "Test:: End"
}

source ./config.sh

phaseStart "Setup"
    for setup_step in $( ls -A1 setup/ ); do
        setupStepStart ${setup_step}
            source setup/${setup_step}
        setupStepEnd
    done
phaseEnd

phaseStart "Testing"
    for test_case in $( ls -A1 test_cases/ ); do
        testStart ${test_case}
            source test_cases/${test_case}
        testEnd
    done
phaseEnd
