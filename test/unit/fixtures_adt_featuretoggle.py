"""FeatureToggle ADT fixtures"""

import json
from mock import Response

JSON_FEATURE_TOGGLE_STATE_CLIENT_ON = json.loads('''{
  "STATES": {
    "NAME": "MY_LUCKY_TOGGLE",
    "CLIENT_STATE": "on",
    "CLIENT_CHANGED_BY": "",
    "CLIENT_CHANGED_ON": "",
    "USER_STATE": "undefined",
    "CLIENT_STATES": [
      {
        "CLIENT": "000",
        "DESCRIPTION": "SAP SE",
        "STATE": "off"
      },
      {
        "CLIENT": "100",
        "DESCRIPTION": "S/4HANA Cloud Edition",
        "STATE": "on"
      }
    ],
    "USER_STATES": []
  }
}''')

RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_ON = Response(status_code=200, json=JSON_FEATURE_TOGGLE_STATE_CLIENT_ON, headers={
    'Content-Type': 'application/vnd.sap.adt.states.v1+asjson; charset=utf-8'})

JSON_FEATURE_TOGGLE_STATE_CLIENT_OFF = json.loads('''{
  "STATES": {
    "NAME": "MY_LUCKY_TOGGLE",
    "CLIENT_STATE": "off",
    "CLIENT_CHANGED_BY": "",
    "CLIENT_CHANGED_ON": "",
    "USER_STATE": "undefined",
    "CLIENT_STATES": [
      {
        "CLIENT": "000",
        "DESCRIPTION": "SAP SE",
        "STATE": "off"
      },
      {
        "CLIENT": "100",
        "DESCRIPTION": "S/4HANA Cloud Edition",
        "STATE": "off"
      }
    ],
    "USER_STATES": []
  }
}''')

RESPONSE_FEATURE_TOGGLE_STATE_CLIENT_OFF = Response(status_code=200, json=JSON_FEATURE_TOGGLE_STATE_CLIENT_OFF, headers={
    'Content-Type': 'application/vnd.sap.adt.states.v1+asjson; charset=utf-8'})
