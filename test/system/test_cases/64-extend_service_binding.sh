#!/usr/bin/bash

set -o nounset
set -o errexit
set -o pipefail

_tcn="64"
_code="SDEX"
_round="0"

DDLS_NAME="ZAPCLI_ST${_tcn}_DDLS_${_code}_${_round}"
DDLS_EXT_NAME="ZZ_APCLI_ST${_tcn}_DDLS_${_code}_E${_round}"
SRVD_NAME="ZAPCLI_ST${_tcn}_SRVD_${_code}_${_round}"
SRVD_EXT_NAME="ZZ_APCLI_ST${_tcn}_SRVD_${_code}_E${_round}"
SRVB_NAME="ZAPCLI_ST${_tcn}_SRVB_${_code}_${_round}"

# Create base CDS view

sapcli ddl create ${DDLS_NAME} "sapcli system test ${_tcn} CDS" '$tmp'

sapcli ddl write -a ${DDLS_NAME} - <<_EOF
@AccessControl.authorizationCheck: #NOT_REQUIRED
@AbapCatalog.extensibility.extensible: true
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

# Create base Service Definition

sapcli srvd create ${SRVD_NAME} "sapcli system test ${_tcn} SRVD" '$TMP'

sapcli srvd write -a ${SRVD_NAME} - <<_EOF
@EndUserText.label: 'sapcli system test - service definition'
@AbapCatalog.extensibility.extensible
define service ${SRVD_NAME}
  provider contracts odata_v2_ui, odata_v4_ui {
    expose ${DDLS_NAME};
}
_EOF

# Create base Service Binding 

sapcli srvb create ${SRVB_NAME} "sapcli system test ${_tcn}" '$TMP' --binding-type ODATAV4_UI --service-definition ${SRVD_NAME}
sapcli srvb activate ${SRVB_NAME}
sapcli srvb publish ${SRVB_NAME}

#
# Create CDS view for extension
#

sapcli ddl create ${DDLS_EXT_NAME} "sapcli system test ${_tcn} CDS Addition" '$tmp'

sapcli ddl write -a ${DDLS_EXT_NAME} - <<_EOF
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'CDS View for additional data from T000'
define view entity ${DDLS_EXT_NAME}
  as select from t000
{
  key mandt,
      mwaer
}
_EOF

#
# The real test starts here:
# Extension for the service definition - adding the new CDS view to the service definition
#

sapcli srvd create --type=extension ${SRVD_EXT_NAME} "sapcli system test ${_tcn} Service Extension" '$TMP'

sapcli srvd write -a ${SRVD_EXT_NAME} - <<_EOF
extend service ${SRVD_NAME} with {
    expose ${DDLS_EXT_NAME} as ZZ_TestExt;
}
_EOF

#
# Re-publish the service binding to include the new service definition extension
#
sapcli srvb unpublish -a ${SRVB_NAME}
sapcli srvb publish ${SRVB_NAME}

sapcli srvb preview metadata ${SRVB_NAME}

sapcli srvb preview fetch ${SRVB_NAME} ZZ_TestExt
