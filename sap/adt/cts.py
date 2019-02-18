"""CTS object proxies"""

import xml.sax
from xml.sax.handler import ContentHandler

from typing import NamedTuple, Any, List


# pylint: disable=too-few-public-methods
class Element(NamedTuple):
    """Intermediate XML element representation"""

    attributes: Any
    children: List


class WorkbenchResponseHandler(ContentHandler):
    """Python xml.sax.handler.ContentHandler converting ADT CTS Workbench XML
       data into corresponding Python objects.
    """

    def __init__(self, builder):
        super(WorkbenchResponseHandler, self).__init__()

        self._builder = builder

        self._transport = None
        self._task = None

    def startElement(self, name, attrs):
        if name == 'tm:request':
            self._transport = Element(attrs, [])
        elif name == 'tm:task':
            self._task = Element(attrs, [])
            self._transport.children.append(self._task)
        elif name == 'tm:abap_object' and self._task is not None:
            self._task.children.append(Element(attrs, []))

    def endElement(self, name):
        if name == 'tm:request':
            self._builder.process_transport_xml(self._transport)


def workbench_params(user: str):
    """Workbench URL pramaters"""

    return {
        'user': user,
        'target': 'true',
        'requestType': 'KWT',
        'requestStatus': 'DR'
    }


class AbstractWorkbenchRequest:
    """Workbench request"""

    def __init__(self, connection, number: str, owner: str = None,
                 description: str = None, status: str = None):
        self._connection = connection
        self._number = number
        self._owner = owner
        self._description = description
        self._status = '?' if status is None else status

    @property
    def number(self):
        """Request ID"""

        return self._number

    @property
    def owner(self):
        """Request owner"""

        # TODO: raise an error if None
        return self._owner

    @property
    def description(self):
        """Request description"""

        return self._description

    @property
    def status(self):
        """Status -> [D,R,?]"""

        return self._status

    def release(self):
        """Release the request"""

        resp = self._connection.execute(
            'POST',
            f'cts/transportrequests/{self._number}/newreleasejobs',
            headers={'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml'}
        )

        return resp.text


class WorkbenchTransport(AbstractWorkbenchRequest):
    """Transport Manager Request"""

    def __init__(self, tasks, *params, **kwargs):
        super(WorkbenchTransport, self).__init__(*params, **kwargs)

        self._tasks = tasks

    def add_task(self, task):
        """Adds a new task to the list of tasks tracked under this transport"""

        self._tasks.append(task)

    @property
    def tasks(self):
        """Returns the list of tasks tracked under this transport"""

        return self._tasks


class WorkbenchABAPObject(NamedTuple):
    """ABAP Object tracked in a Transport Manager Request Task"""

    pgmid: str
    type: str
    name: str
    wbtype: str
    description: str
    locked: bool


class WorkbenchTask(AbstractWorkbenchRequest):
    """Transport Manager Task"""

    def __init__(self, transport, objects, *params, **kwargs):
        super(WorkbenchTask, self).__init__(*params, **kwargs)

        self._transport = transport
        self._objects = objects

    @property
    def transport(self):
        """Parent transport"""

        return self._transport

    @property
    def objects(self):
        """Returns the list of objects registered in this task"""

        return self._objects


class WorkbenchBuilder:
    """Prase ADT XML workbench description"""

    def __init__(self, connection):
        self._connection = connection

        self.transports = []

    def process_transport_xml(self, transport_elem):
        """Converts Transport XML into a python object"""

        transport_tasks = []

        for task_elem in transport_elem.children:
            if 'tm:parent' not in task_elem.attributes:
                attrs = dict(task_elem.attributes)
                attrs['tm:parent'] = transport_elem.attributes['tm:number']
                task_elem = Element(attrs, task_elem.children)

            task = self.process_task_xml(task_elem)
            transport_tasks.append(task)

        transport = WorkbenchTransport(
            transport_tasks,
            self._connection,
            transport_elem.attributes['tm:number'],
            owner=transport_elem.attributes['tm:owner'],
            description=transport_elem.attributes['tm:desc'],
            status=transport_elem.attributes['tm:status']
        )

        self.transports.append(transport)

        return transport

    def process_task_xml(self, task_elem):
        """Converts Task XML into a python object"""

        task_objects = []

        for object_elem in task_elem.children:
            abap_object = self.process_abap_object_xml(object_elem)
            task_objects.append(abap_object)

        task = WorkbenchTask(
            task_elem.attributes['tm:parent'],
            task_objects,
            self._connection,
            task_elem.attributes['tm:number'],
            task_elem.attributes['tm:owner'],
            task_elem.attributes['tm:desc'],
            task_elem.attributes['tm:status']
        )

        return task

    # pylint: disable=no-self-use
    def process_abap_object_xml(self, object_elem):
        """Converts Object XML into a python object"""

        attributes = object_elem.attributes
        abap_object = WorkbenchABAPObject(
            attributes['tm:pgmid'],
            attributes['tm:type'],
            attributes['tm:name'],
            attributes.get('tm:wbtype', ''),
            attributes.get('tm:obj_desc', attributes['tm:obj_info']),
            attributes.get('tm:lock_status', ' ') == 'X'
        )

        return abap_object


class Workbench:
    """Transport Manager Workbench"""

    def __init__(self, connection):
        self._connection = connection

    def get_transport_requests(self, user=None):
        """Returns the list of all transport requests"""

        if user is None:
            user = self._connection.user

        resp = self._connection.execute(
            'GET', 'cts/transportrequests',
            params=workbench_params(user),
            headers={'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml'}
        )

        builder = WorkbenchBuilder(self._connection)
        xml_handler = WorkbenchResponseHandler(builder)
        xml.sax.parseString(resp.text, xml_handler)

        return builder.transports
