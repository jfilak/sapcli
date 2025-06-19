"""Feature Toggle ADT wrappers"""

import json
from enum import Enum
from typing import NamedTuple
from urllib.parse import quote_plus

from sap.errors import SAPCliError


# <?xml version="1.0" encoding="UTF-8"?>
# <blue:blueSource xmlns:blue="http://www.sap.com/wbobj/blue"
#   abapsource:fixPointArithmetic="false" abapsource:activeUnicodeCheck="false"
#   adtcore:responsible="DEVELOPER" adtcore:masterLanguage="EN" adtcore:masterSystem="C50"
#   adtcore:name="WFD_FT_SILM" adtcore:type="FTG2/FT" adtcore:changedAt="2025-04-29T19:53:28Z"
#   adtcore:version="active" adtcore:createdAt="2025-04-10T11:34:21Z" adtcore:changedBy="BHOSALESA"
#   adtcore:createdBy="TMS" adtcore:description="Simplified ILM Process feature toggle"
#   adtcore:descriptionTextLimit="60" adtcore:language="EN"
#   xmlns:abapsource="http://www.sap.com/adt/abapsource" xmlns:adtcore="http://www.sap.com/adt/core">
# <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./wfd_ft_silm/source/main/versions"
#   rel="http://www.sap.com/adt/relations/versions" title="Historic versions"/>
# <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./wfd_ft_silm/source/main"
#   rel="http://www.sap.com/adt/relations/source" type="application/vnd.sap.adt.toggle.content.v2+json"
#   title="Source Content" etag="..."/>
# <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="./wfd_ft_silm/source/main"
#   rel="http://www.sap.com/adt/relations/source" type="text/html" title="Source Content (HTML)" etag=""/>
# <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
#   href="/sap/bc/adt/vit/wb/object_type/ftg2ft/object_name/WFD_FT_SILM"
#   rel="self" type="application/vnd.sap.sapgui" title="Representation in SAP GUI"/>
# <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
#   href="/sap/bc/adt/sfw/featuretoggles/wfd_ft_silm/schema"
#   rel="http://www.sap.com/adt/relations/objecttypeschema"
#   type="application/vnd.sap.adt.serverdriven.schema.v1+json; framework=objectTypes.v1"
#   title="Server driven framework - Schema"/>
# <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
#   href="/sap/bc/adt/sfw/featuretoggles/wfd_ft_silm/configuration"
#   rel="http://www.sap.com/adt/relations/objecttypeconfiguration"
#   type="application/vnd.sap.adt.serverdriven.configuration.v1+json; framework=objectTypes.v1"
#   title="Server driven framework - Configuration"/>
# <atom:link xmlns:atom="http://www.w3.org/2005/Atom"
#   href="/sap/bc/adt/sfw/featuretoggles/wfd_ft_silm/configuration"
#   rel="http://www.sap.com/adt/relations/uiconfiguration"
#   type="application/vnd.sap.adt.serverdriven.configuration.v1+json; framework=objectTypes.v1"
#   title="JSON UI Configuration - Form Editor"/>
# <adtcore:packageRef
#   adtcore:uri="/sap/bc/adt/packages/wfd_int_rap_odata"
#   adtcore:type="DEVC/K"
#   adtcore:name="WFD_INT_RAP_ODATA" adtcore:description="RAP artifacts for ODATA Developments"/>
# </blue:blueSource>
# class FeatureToggleObject:
#   pass

# /sources/main
# {
#   "header": {
#    "description": "Simplified ILM Process feature toggle",
#    "originalLanguage": "en",
#    "abapLanguageVersion": "standard"
#  },
#  "rollout": {
#    "lifecycleStatus": "inValidation",
#    "validationStep": "internal",
#    "rolloutStep": "releaseToCustomer",
#    "strategy": "immediate",
#    "finalDate": "",
#    "event": "noRestriction",
#    "planning": {
#      "referenceProduct": "S4HANA OD",
#      "releaseToCustomer": {
#        "version": "2508",
#        "sp": "0000"
#      },
#      "generalAvailability": {
#        "version": "2508",
#        "sp": "0000"
#      },
#      "generalRollout": {
#        "version": "2508",
#        "sp": "0000"
#      }
#    },
#    "configurable": false,
#    "defaultEnabledFor": "none",
#    "reversible": false
#  },
#  "toggledPackages": [],
#  "relatedToggles": [],
#  "attributes": [
#    {
#      "key": "LC2_LIFECYCLE_STATUS",
#      "value": "V"
#    },
#    {
#      "key": "LC2_ROLLOUT_DATE",
#      "value": "00000000"
#    },
#    {
#      "key": "LC2_ROLLOUT_EVENT",
#      "value": ""
#    },
#    {
#      "key": "LC2_ROLLOUT_STRATEGY",
#      "value": "I"
#    }
#   ]
# }

class FeatureToggleState(Enum):
    """Feature Toggle State - ON or OFF"""

    ON = "on"
    OFF = "off"
    UNDEFINED = "undefined"

    @classmethod
    def from_string(cls, value: str) -> 'FeatureToggleState':
        """Convert a string to a FeatureToggleState"""

        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


# /sap/bc/adt/sfw/featuretoggles/{wfd_ft_silm}/states
# Accept    : application/vnd.sap.adt.states.v1+asjson
# {
#  "STATES": {
#    "NAME": "WFD_FT_SILM",
#    "CLIENT_STATE": "off",
#    "CLIENT_CHANGED_BY": "",
#    "CLIENT_CHANGED_ON": "",
#    "USER_STATE": "undefined",
#    "CLIENT_STATES": [
#      {
#        "CLIENT": "000",
#        "DESCRIPTION": "SAP SE",
#        "STATE": "off"
#      },
#      {
#        "CLIENT": "100",
#        "DESCRIPTION": "S/4HANA Cloud Edition",
#        "STATE": "off"
#      }
#    ],
#    "USER_STATES": []
#  }
# }
class FeatureToggleRuntimeStates(NamedTuple):
    """Feature Toggle States"""

    name: str
    client_state: FeatureToggleState
    user_state: FeatureToggleState

    @classmethod
    def from_json(cls, data: dict) -> 'FeatureToggleRuntimeStates':
        """Create FeatureToggleRuntimeStates from JSON data"""
        return cls(
            name=data['STATES']['NAME'],
            client_state=FeatureToggleState.from_string(data['STATES']['CLIENT_STATE']),
            user_state=FeatureToggleState.from_string(data['STATES']['USER_STATE']),
        )

    def is_on(self) -> bool:
        """Check if the feature toggle is ON"""
        return FeatureToggleState.ON in (self.client_state, self.user_state)

    def is_off(self) -> bool:
        """Check if the feature toggle is OFF"""
        return FeatureToggleState.OFF in (self.client_state, self.user_state)


# POST /sap/bc/adt/sfw/featuretoggles/{name}/check
# Accept      : application/vnd.sap.adt.toggle.check.result.v1+asjson
# Content-Type: application/vnd.sap.adt.toggle.check.parameters.v1+asjson
# {
#   "PARAMETERS": {
#     "IS_USER_SPECIFIC": false
#   }
# }
# ---
# Content-Type: application/vnd.sap.adt.toggle.check.result.v1+asjson; charset=utf-8
# {
#   "RESULT": {
#     "CURRENT_STATE": "off",
#     "TRANSPORT_PACKAGE": "WFD_INT_RAP_ODATA",
#     "TRANSPORT_URI": "/sap/bc/adt/vit/wb/object_type/sf01/object_name/wfd_ft_silm",
#     "CUSTOMIZING_TRANSPORT_ALLOWED": true
#   }
# }

# POST /sap/bc/adt/sfw/featuretoggles/{name}/toggle
# Content-Type: application/vnd.sap.adt.related.toggle.parameters.v1+asjson
# {
#   "TOGGLE_PARAMETERS": {
#     "IS_USER_SPECIFIC": false,
#     "TRANSPORT_REQUEST": "C50K000061",
#     "STATE": "on"
#   }
# }

# POST /sap/bc/adt/sfw/featuretoggles/{name}/validate
# Accept      : application/vnd.sap.adt.toggle.validation.result.v1+asjson
# Content-Type: application/vnd.sap.adt.toggle.validation.parameters.v1+asjson
# {
#   "PARAMETERS": {
#     "STATE": "on",
#     "IS_USER_SPECIFIC": false
#   }
# }

class FeatureToggleManager:
    """Feature Toggle Manager"""

    def __init__(self, connection):
        self._connection = connection

    def fetch_feature_toggle_state(self, feature_toggle_id: str) -> FeatureToggleRuntimeStates:
        """Fetch the states of the feature toggle"""
        # URL encode to replace /
        resp = self._connection.execute(
            'GET',
            f'sfw/featuretoggles/{quote_plus(feature_toggle_id)}/states',
            accept='application/vnd.sap.adt.states.v1+asjson'
        )

        states_json = resp.json()

        return FeatureToggleRuntimeStates.from_json(states_json)

    def _switch_feature_toggle(self,
                               feature_toggle_id: str,
                               user_specific=False,
                               corrnr=None,
                               state: FeatureToggleState = FeatureToggleState.OFF) -> None:
        """Switch the feature toggle to the specified state"""

        params = {
            'TOGGLE_PARAMETERS': {
                'IS_USER_SPECIFIC': user_specific,
                'STATE': state.value,
            }
        }

        if corrnr:
            params['TOGGLE_PARAMETERS']['TRANSPORT_REQUEST'] = corrnr

        resp = self._connection.execute(
            'POST',
            f'sfw/featuretoggles/{quote_plus(feature_toggle_id)}/toggle',
            body=json.dumps(params),
            content_type='application/vnd.sap.adt.related.toggle.parameters.v1+asjson',
        )

        if resp.status_code != 200:
            raise SAPCliError(f'Failed to switch feature toggle {feature_toggle_id} to {state.value}. Response: {resp.text}')

    def switch_feature_toggle_on(self, feature_toggle_id, user_specific=False, corrnr=None) -> None:
        """Toggle the feature toggle ON"""

        return self._switch_feature_toggle(feature_toggle_id, user_specific, corrnr, FeatureToggleState.ON)

    def switch_feature_toggle_off(self, feature_toggle_id, user_specific=False, corrnr=None) -> None:
        """Toggle the feature toggle OFF"""

        return self._switch_feature_toggle(feature_toggle_id, user_specific, corrnr, FeatureToggleState.OFF)
