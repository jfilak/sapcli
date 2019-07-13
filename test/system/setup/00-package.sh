#!/usr/bin/bash

export SAPCLI_TEST_PACKAGE_ROOT='$sapcli_test_root'
export SAPCLI_TEST_PACKAGE_CHILD='$sapcli_test_child'

sapcli package create --no-error-existing "${SAPCLI_TEST_PACKAGE_ROOT}" "sapcli test's root package"
sapcli package create --no-error-existing "${SAPCLI_TEST_PACKAGE_CHILD}" "sapcli test's root child"
