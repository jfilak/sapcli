#!/usr/bin/bash

set -o nounset
set -o errexit
set -o pipefail

ABAP_NAME='ztest_inc'

SAPCLI_OBJECT='include'


echo "+++ create +++"
sapcli ${SAPCLI_OBJECT} create ${ABAP_NAME} 'sapcli test' ${SAPCLI_TEST_PACKAGE_ROOT}

echo "+++ write +++"
echo "* empty source by sapcli" | sapcli ${SAPCLI_OBJECT} write ${ABAP_NAME} -

echo "+++ activate +++"
sapcli ${SAPCLI_OBJECT} activate ${ABAP_NAME}

echo "+++ read +++"
sapcli ${SAPCLI_OBJECT} read ${ABAP_NAME}
