"""gCTS log messages normalization utilities"""

import json
from io import StringIO
from abc import (
    ABC,
    abstractmethod
)

from sap.errors import SAPCliError


type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]


class BaseApplicationInfo(ABC):
    """Base class for application info in gCTS log messages"""

    @property
    @abstractmethod
    def json_object(self) -> JsonValue:
        """Return the JSON representation of the application info"""
        raise NotImplementedError

    @property
    @abstractmethod
    def application(self) -> str:
        """Return the application name"""
        raise NotImplementedError

    @abstractmethod
    def formatted_str(self, indent: int = 0) -> str:
        """Return formatted string with essential output lines only"""
        raise NotImplementedError

    def __str__(self):
        """Return the full JSON representation of the application info """
        return json.dumps(self.json_object, indent=2)


class ClientApplicationInfo(BaseApplicationInfo):
    """Represents Transport Tools application info

       The minimum JSON schema:
            { "application": "Client",
              "applInfo": [
                    { "type": "Parameters",
                      "protocol": [
                            { "arbitrary-key": "value" },
                            { "arbitrary-key-2": "another value" }
                        ]
                    },
                    { "type": "Client Log",
                      "protocol": [
                            "line-0",
                            "line-n"
                        ]
                    },
                    { "type": "Client Response",
                      "protocol": [
                            { "log": [
                                    { "code": "...", "type": "...", "message": "...", "step: "..." },
                                    { "code": "...", "type": "...", "message": "...", "step: "..."}
                                ]
                            }
                        ]
                    },
                    { "type": "Client Stack Log",
                      "protocol": [
                            [
                                { "code": "...", "type": "...", "message": "...", "step: "..." },
                                { "code": "...", "type": "...", "message": "...", "step: "..."}
                            ]
                        ]
                    }
                ]
            }
    """

    Application_Name = "Client"

    Type_Parameters = "Parameters"
    Type_Client_Log = "Client Log"
    Type_Client_Response = "Client Response"
    Type_Client_Stack_Log = "Client Stack Log"

    def __init__(self, raw_application_info):
        # Raw application info is JSON object in String and need to be unquoted and the parsed
        self.application_info = json.loads(raw_application_info)
        self.client_response = None

        if not isinstance(self.application_info, list):
            raise SAPCliError("Invalid Client application info format")

        for section in self.application_info:
            section_type = section.get('type', '')
            raw_protocol = section.get('protocol', '')

            match section_type:
                case self.Type_Parameters:
                    if not isinstance(raw_protocol, list) or len(raw_protocol) != 1:
                        raise SAPCliError("Invalid Client Parameters section format")

                    protocol = json.loads(raw_protocol[0])

                case self.Type_Client_Log:
                    if not isinstance(raw_protocol, list):
                        raise SAPCliError("Invalid Client Log section format")

                    protocol = raw_protocol

                case self.Type_Client_Response:
                    if not isinstance(raw_protocol, list) or len(raw_protocol) != 1:
                        raise SAPCliError("Invalid Client Response section format")

                    protocol = json.loads(raw_protocol[0])
                    self.client_response = protocol

                case self.Type_Client_Stack_Log:
                    if not isinstance(raw_protocol, list) or len(raw_protocol) != 1:
                        raise SAPCliError("Invalid Client Response section format")

                    protocol = json.loads(raw_protocol[0])

                case _:
                    raise SAPCliError(f"Unknown Client application info section type: {section_type}")

            section['protocol'] = protocol

    @property
    def application(self) -> str:
        return self.Application_Name

    @property
    def json_object(self) -> JsonValue:
        return self.application_info

    def formatted_str(self, indent=0) -> str:
        """Return formatted string with essential output lines only.

            Only the 'Client Response' log messages are considered essential.
        """

        log = self.client_response.get('log', [])

        prefix = ' ' * indent

        # No joining list because I don't want to search
        # the log dict unnecessary many of times
        buffer = StringIO()
        for entry in log:
            msg = entry.get('message', None)
            if msg is None or _is_empty_line(msg):
                continue

            msg_type = entry.get('type', '?????')

            buffer.write(prefix + f'{msg_type}: {msg}\n')

        # Remove the last newline
        return buffer.getvalue()[:-1]


class GCTSApplicationInfo(BaseApplicationInfo):
    """Represents Transport Tools application info

       The minimum JSON schema:
            { "application: "gCTS",
              "applInfo": "... raw string ... "
            }
    """

    Application_Name = "gCTS"

    def __init__(self, raw_application_info):
        self.message = str(raw_application_info)

    @property
    def application(self) -> str:
        return self.Application_Name

    @property
    def json_object(self) -> JsonValue:
        return self.message

    def formatted_str(self, indent=0) -> str:
        """Return formatted string with essential output lines only"""

        return ' ' * indent + self.message


class TransportToolsApplicationInfo(BaseApplicationInfo):
    """Represents Transport Tools application info

       The minimum JSON schema:
            { "application": "Transport Tools",
              "applInfo": {
                    "stdout": [
                        { "line": "..." },
                        { "line": "..." }
                    ]
                }
            }

        The 'applInfo.stdout' is transformed into a list of strings (the object
        is replaced by the item line) for easier processing
    """

    Application_Name = "Transport Tools"

    def __init__(self, raw_application_info):
        self.application_info = json.loads(raw_application_info)

        raw_stdout = self.application_info.get('stdout', [])
        if not isinstance(raw_stdout, list):
            raise SAPCliError("Invalid Transport Tools application info format")

        for i, item in enumerate(raw_stdout):
            self.application_info['stdout'][i] = item.get('line', '')

    @property
    def application(self) -> str:
        return self.Application_Name

    @property
    def json_object(self) -> JsonValue:
        return self.application_info

    def formatted_str(self, indent=0) -> str:
        """Return formatted string with essential output lines only.

           Only non-empty stdout lines are considered essential.
        """

        lines = self.application_info['stdout']

        prefix = ' ' * indent
        return '\n'.join((prefix + line for line in lines if not _is_empty_line(line)))


class ProcessMessage:
    """Represents a normalized process message with applInfo"""

    def __init__(self, raw_message):
        self.raw_message = raw_message
        self._application = None

    @property
    def time(self):
        """Return the time field"""
        return self.raw_message.get('time')

    @property
    def action(self):
        """Return the action field"""
        return self.raw_message.get('action')

    @property
    def application(self):
        """Return the application field"""
        return self.raw_message.get('application')

    @property
    def severity(self):
        """Return the severity field"""
        return self.raw_message.get('severity')

    @property
    def json_object(self) -> JsonValue:
        """Return the JSON representation of the process message"""

        raw_message = self.raw_message.copy()
        raw_message['applInfo'] = self.appl_info.json_object
        return raw_message

    @property
    def appl_info(self):
        """Get the application info object"""

        if self._application is None:
            application = self.raw_message['application']
            appl_info = self.raw_message['applInfo']

            match application:
                case ClientApplicationInfo.Application_Name:
                    self._application = ClientApplicationInfo(appl_info)
                case TransportToolsApplicationInfo.Application_Name:
                    self._application = TransportToolsApplicationInfo(appl_info)
                case GCTSApplicationInfo.Application_Name:
                    self._application = GCTSApplicationInfo(appl_info)
                case _:
                    raise SAPCliError(f"Unknown application type in process message: {application}")

        return self._application


class ActionMessage:
    """Represents a normalized action message with process messages"""

    _process_messages: list[ProcessMessage] | None

    def __init__(self, raw_message: dict[str, JsonValue] | None, raw_process_messages: list[JsonValue] | None = None):
        """Wrapper for gCTS Action message.

            Args:
                raw_message - gCTS JSON of a single /log item; can be None
                raw_process_messages - gCTS JSON list returned by /log/{process_ID}

            Notes: the raw_message key 'process' is renamed to 'processId'
        """

        if raw_message is not None:
            self.raw_message = raw_message

            if 'processId' in raw_message:
                raise SAPCliError("Invalid action message format: 'processId' key already exists")

            self.raw_message['processId'] = raw_message.pop('process', '')
        else:
            self.raw_message = {}

        self._raw_process_messages = raw_process_messages
        self._process_messages = None

    @property
    def time(self):
        """Return the time field"""
        return self.raw_message.get('time')

    @property
    def caller(self):
        """Return the caller field"""
        return self.raw_message.get('caller')

    @property
    def processName(self):
        """Return the processName field"""
        return self.raw_message.get('processName')

    @property
    def status(self):
        """Return the status field"""
        return self.raw_message.get('status')

    @property
    def processId(self):
        """Return the processId field"""
        return self.raw_message.get('processId')

    @property
    def json_object(self) -> JsonValue:
        """Return the JSON representation of the action message"""

        allpm = self.process_messages
        if allpm is not None:
            self.raw_message['process'] = [pm.json_object for pm in allpm]

        return self.raw_message

    @property
    def process_messages(self) -> list[ProcessMessage] | None:
        """Get the list of process messages corresponding for this action message"""

        if self._process_messages is None:
            if self._raw_process_messages is not None:
                self._process_messages = [ProcessMessage(rpm) for rpm in self._raw_process_messages]

        return self._process_messages


def _is_empty_line(line):
    """Check if a line is considered empty"""

    if line is None:
        return True

    if isinstance(line, str):
        return not line.strip()

    return False
