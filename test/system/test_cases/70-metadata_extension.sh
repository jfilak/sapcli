#!/usr/bin/bash

set -o nounset
set -o errexit
set -o pipefail

_tcn="70"
_code="CDSMD"
_round="0"

DDLS_NAME="ZAPCLI_ST${_tcn}_DDLS_${_code}_${_round}"
DDLX_NAME="ZAPCLI_ST${_tcn}_DDLX_${_code}_${_round}"
SRVD_NAME="ZAPCLI_ST${_tcn}_SRVD_${_code}_${_round}"
SRVB_NAME="ZAPCLI_ST${_tcn}_SRVB_${_code}_${_round}"

# Create base CDS view

sapcli ddl create ${DDLS_NAME} "sapcli system test ${_tcn} CDS" '$tmp'
sapcli ddl write -a ${DDLS_NAME} - <<_EOF
@AbapCatalog.extensibility.extensible: true
@Metadata.allowExtensions: true
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

# Create Metadata Extension for the CDS view

sapcli ddlx create ${DDLX_NAME} "sapcli system test ${_tcn} MD ext" '$tmp'
sapcli ddlx write -a ${DDLX_NAME} - <<_EOF
@Metadata.layer: #CUSTOMER
annotate entity ${DDLS_NAME}
  with {

  @EndUserText.label: 'TEST CASE sapcli Client Description'
  mtext;
}
_EOF

# Create base Service Definition

sapcli srvd create ${SRVD_NAME} "sapcli system test ${_tcn} SRVD" '$TMP'
sapcli srvd write -a ${SRVD_NAME} - <<_EOF
@EndUserText.label: 'sapcli system test - service definition'
define service ${SRVD_NAME} {
    expose ${DDLS_NAME};
}
_EOF

# Create base Service Binding

sapcli srvb create ${SRVB_NAME} "sapcli system test ${_tcn}" '$TMP' --binding-type ODATAV4_UI --service-definition ${SRVD_NAME}
sapcli srvb activate ${SRVB_NAME}
sapcli srvb publish ${SRVB_NAME}
sapcli srvb preview metadata ${SRVB_NAME}
