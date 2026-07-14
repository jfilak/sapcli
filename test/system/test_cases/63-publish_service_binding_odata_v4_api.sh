#!/usr/bin/bash

set -o nounset
set -o errexit
set -o pipefail

_tcn="63"
_round="0"

DDLS_NAME="ZAPCLI_ST${_tcn}_DDLS_O2UI_${_round}"
SRVD_NAME="ZAPCLI_ST${_tcn}_SRVD_O2UI_${_round}"
SRVB_NAME="ZAPCLI_ST${_tcn}_SRVB_O2UI_${_round}"

sapcli ddl create ${DDLS_NAME} "sapcli system test ${_tcn}" '$tmp'

sapcli ddl write -a ${DDLS_NAME} - <<_EOF
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'CDS View for T000'
define view entity ${DDLS_NAME}
  as select from t000
{
  key mandt,
      logsys,
      ort01,
      mtext
}
_EOF

sapcli srvd create ${SRVD_NAME} "sapcli system test ${_tcn}" '$TMP'

sapcli srvd write -a ${SRVD_NAME} - <<_EOF
@EndUserText.label: 'sapcli system test - service definition'
define service ${SRVD_NAME} {
  expose ${DDLS_NAME};
}
_EOF

sapcli srvb create ${SRVB_NAME} "sapcli system test ${_tcn}" '$TMP' --binding-type ODATAV4_API --service-definition ${SRVD_NAME}

sapcli srvb activate ${SRVB_NAME}

sapcli srvb publish ${SRVB_NAME}

sapcli srvb read ${SRVB_NAME}

sapcli srvb preview metadata ${SRVB_NAME}

sapcli srvb preview fetch ${SRVB_NAME} ${DDLS_NAME}

sapcli srvb unpublish -a ${SRVB_NAME}
