"""CTS object proxies"""

import re
import xml.sax
from xml.sax.handler import ContentHandler
from xml.sax.saxutils import escape

from typing import NamedTuple, Any, List, Tuple

from sap import get_logger
from sap.errors import SAPCliError
from sap.adt.core import mod_log


class CTSReleaseError(SAPCliError):
    """CTS Release Error"""

    # pylint: disable=unnecessary-pass
    pass


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
        super().__init__()

        self._builder = builder

        self._transport = None
        self._task = None
        self.adt_task = None

    def startElement(self, name, attrs):
        if name == 'tm:request':
            self._transport = Element(attrs, [])
        elif name == 'tm:task':
            self._task = Element(attrs, [])
            if self._transport is not None:
                self._transport.children.append(self._task)
        elif name == 'tm:abap_object' and self._task is not None:
            self._task.children.append(Element(attrs, []))

    def endElement(self, name):
        if name == 'tm:request':
            self._builder.process_transport_xml(self._transport)
            self._transport = None
        elif name == 'tm:task' and self._transport is None:
            self.adt_task = self._builder.process_task_xml(self._task)


class ReleaseResponse:
    """Release response values"""

    def __init__(self, status: str, text: str):
        self._status = status
        self._text = text

    def __str__(self):
        return self._text

    @property
    def release_was_successful(self) -> bool:
        """True if the release action was successful"""

        return self._status == 'released'


class ReleaseResponseHandler(ContentHandler):
    """Python xml.sax.handler.ContentHandler converting ADT CTS Realase response XML
       data into corresponding Python objects.
    """

    def __init__(self):
        super().__init__()

        self.report = None

    def startElement(self, name, attrs):
        if name == 'chkrun:checkReport':
            self.report = ReleaseResponse(attrs['chkrun:status'], attrs['chkrun:statusText'])


def workbench_params(user: str):
    """Workbench URL pramaters"""

    return {
        'user': user,
        'target': 'true',
        'requestType': 'KWT',
        'requestStatus': 'DR'
    }


class WorkbenchRequestResponseCreate(NamedTuple):
    """Create response data"""

    number: str  # 6 digit number
    data: str  # full HTTP response


class AbstractWorkbenchRequest:
    """Workbench request"""

    def __init__(self, connection, number: str, owner: str = None,
                 description: str = None, status: str = None, target: str = None):
        """
        Parameters:
          - status: single character from the set R,D,?
        """

        self._connection = connection
        self._number = number
        self._owner = owner
        self._description = description
        self._status = '?' if status is None else status
        self._target = target

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
    def target(self):
        """Request target"""

        return self._target

    @property
    def status(self):
        """Status -> [D,R,?]"""

        return self._status

    @property
    def is_released(self):
        """True if the request is already released"""

        return self._status == 'R'

    @property
    def uri(self):
        """CTS Request part of ADT URI"""

        return f'cts/transportrequests/{self._number}'

    def _create_request(self) -> Tuple[str, str]:
        """Returns a tuple (CTS URI request, XML content)"""

        raise NotImplementedError

    def create(self):
        """Create the request"""

        uri, body = self._create_request()
        resp = self._connection.execute(
            'POST',
            uri,
            headers={'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml',
                     'Content-Type': 'text/plain'},
            body=body
        )

        self._number = re.search('.*tm:number="([^"]+)".*', resp.text).group(1)
        return WorkbenchRequestResponseCreate(self._number, resp.text)

    def release(self, recursive=False):
        """Release the request"""

        if recursive:
            self._release_children()

        resp = self._connection.execute(
            'POST',
            f'{self.uri}/newreleasejobs',
            headers={'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml'}
        )

        xml_handler = ReleaseResponseHandler()
        xml.sax.parseString(resp.text, xml_handler)

        report = xml_handler.report

        if not report.release_was_successful:
            raise CTSReleaseError(f'Failed to release {self.__class__.__name__} {self._number}: {str(report)}')

        return report

    def reassign(self, newowner, recursive=False):
        """Changes the request's owner"""

        if recursive:
            self._reassign_children(newowner)

        get_logger().info('Reassigning CTS request: %s', self.number)

        self._connection.execute('PUT', self.uri, body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm"
 tm:number="{self._number}"
 tm:targetuser="{newowner}"
 tm:useraction="changeowner"/>''')

    def delete(self, recursive=False):
        """Deletes Request"""

        if recursive:
            self._delete_children()

        get_logger().info('Deleting CTS request: %s', self.number)
        self._connection.execute('DELETE', self.uri)

    def fetch(self):
        """Fetch the request information"""

        resp = self._connection.execute('GET', self.uri)

        self._deserialize(resp.text)

    def get_type(self):
        """Return type of Request"""

        raise NotImplementedError

    def _deserialize(self, xml_data):
        """Deserialize ADT request information"""

        raise NotImplementedError

    def _release_children(self):
        """Release child objects"""

        raise NotImplementedError

    def _reassign_children(self, newowner):
        """Changes owner of child objects"""

        raise NotImplementedError

    def _delete_children(self):
        """Delete children or this request"""

        raise NotImplementedError

    def _copy(self, another):
        if not isinstance(another, self.__class__):
            raise ValueError

        # pylint: disable=protected-access
        self._owner = another._owner
        self._description = another._description
        self._status = another._status
        self._target = another._target


class WorkbenchTransport(AbstractWorkbenchRequest):
    """Transport Manager Request"""

    def __init__(self, tasks, *params, **kwargs):
        super().__init__(*params, **kwargs)

        self._tasks = tasks

    def get_type(self):
        """Return type of Request"""

        return 'K'

    @property
    def tasks(self):
        """Returns the list of tasks tracked under this transport"""

        return self._tasks or []

    def _create_request(self):
        """Create the request"""

        return ('cts/transportrequests', f'''<?xml version="1.0" encoding="UTF-8"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:useraction="newrequest">
  <tm:request tm:desc="{self.description}" tm:type="{self.get_type()}" tm:target="{self.target}" tm:cts_project="">
    <tm:task tm:owner="{self.owner}"/>
  </tm:request>
</tm:root>
''')

    def _deserialize(self, xml_data):
        """Deserialize ADT request information"""

        builder = WorkbenchBuilder(self._connection)
        xml_handler = WorkbenchResponseHandler(builder)
        xml.sax.parseString(xml_data, xml_handler)

        self._copy(builder.transports[0])
        self._tasks = builder.transports[0].tasks

    def _release_children(self):
        for task in self.tasks:
            if task.is_released:
                continue

            task.release()

    def _reassign_children(self, newowner):
        """Changes owner of child objects"""

        get_logger().info('Reassigning tasks of transport: %s', self.number)
        for task in self.tasks:
            if task.is_released:
                continue

            task.reassign(newowner, recursive=True)

    def _delete_children(self):
        """Deletes tasks of transport"""

        get_logger().info('Deleting tasks of transport: %s', self.number)
        for task in self.tasks:
            if task.is_released:
                continue

            task.delete(recursive=True)


class WorkbenchABAPObject(NamedTuple):
    """ABAP Object tracked in a Transport Manager Request Task"""

    pgmid: str  # 4 letters type from TADIR -> e.g. LIMU, R3TR
    type: str  # 4 letters object type from  TADIR -> e.g. TABD, CLAS, SUSH
    name: str  # up to 30 letters object name without padding
    wbtype: str  # type/kind where the kind is 2 letters code
    description: str  # up to 30 letters randomt string with any characters
    locked: bool  # lock status
    position: str  # 6 digit, zero padded string -> 000001


WorkbenchABAPObjectList = List[WorkbenchABAPObject]


class WorkbenchTask(AbstractWorkbenchRequest):
    """Transport Manager Task"""

    def __init__(self, transport: str, objects: WorkbenchABAPObjectList, *params, **kwargs):
        super().__init__(*params, **kwargs)

        self._transport = transport
        self._objects = objects

    @property
    def transport(self) -> str:
        """Parent transport"""

        return self._transport

    @property
    def objects(self) -> WorkbenchABAPObjectList:
        """Returns the list of objects registered in this task"""

        return self._objects

    def get_type(self):
        """Return type of Request"""

        return 'T'

    def _create_request(self):
        """Create the request"""

        return (f'cts/transportrequests/{self.transport}/tasks', f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:number="{self.transport}" tm:targetuser="{self.owner}" tm:useraction="newtask"/>
''')

    def _deserialize(self, xml_data):
        """Deserialize ADT request information"""

        builder = WorkbenchBuilder(self._connection)
        xml_handler = WorkbenchResponseHandler(builder)
        xml.sax.parseString(xml_data, xml_handler)

        self._copy(xml_handler.adt_task)
        # pylint: disable=protected-access
        self._objects = xml_handler.adt_task._objects
        self._transport = builder.transports[0].number

    def _release_children(self):
        # pylint: disable=unnecessary-pass
        pass  # No children to reassign

    def _reassign_children(self, newowner):
        """Changes owner of child objects"""

        # pylint: disable=unnecessary-pass
        pass  # No children to reassign

    def _delete_object(self, obj):
        """Remove the selected object from the task"""

        get_logger().info('Deleting object: %s %s %s', obj.pgmid, obj.type, obj.name)
        self._connection.execute(
            'PUT',
            self.uri,
            body=f'''<?xml version="1.0" encoding="ASCII"?>
<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm" tm:number="{self._number}" tm:useraction="removeobject">
  <tm:request>
    <tm:abap_object tm:name="{obj.name}" tm:obj_desc="{escape(obj.description)}" tm:pgmid="{obj.pgmid}" tm:type="{obj.type}" tm:position="{obj.position}"/>
  </tm:request>
</tm:root>''')

    def _delete_children(self):
        """Deletes objects of task"""

        get_logger().info('Deleting objects of task: %s', self.number)
        for obj in self.objects:
            self._delete_object(obj)


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
            status=transport_elem.attributes['tm:status'],
            target=transport_elem.attributes.get('tm:target', None)
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

        description = attributes.get('tm:obj_desc', attributes.get('tm:obj_info', None))
        if description is None:
            description = '(PGMID={},TYPE={},NAME={})'.format(attributes.get('tm:pgmid', '*'),
                                                              attributes.get('tm:type', '*'),
                                                              attributes.get('tm:name', '*'))

        mod_log().debug('Processing CTS ABAP Object(PGMID=%s,TYPE=%s,NAME=%s)',
                        attributes.get('tm:pgmid', '*'),
                        attributes.get('tm:type', '*'),
                        attributes.get('tm:name', '*'))

        abap_object = WorkbenchABAPObject(
            attributes['tm:pgmid'],
            attributes['tm:type'],
            attributes['tm:name'],
            attributes.get('tm:wbtype', ''),
            description,
            attributes.get('tm:lock_status', ' ') == 'X',
            attributes.get('tm:position', '000000')
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
            headers={'Accept': ', '.join(['application/vnd.sap.adt.transportorganizertree.v1+xml',
                                          'application/vnd.sap.adt.transportorganizer.v1+xml'])}
        )

        builder = WorkbenchBuilder(self._connection)
        xml_handler = WorkbenchResponseHandler(builder)
        xml.sax.parseString(resp.text, xml_handler)

        return builder.transports

    def fetch_transport_request(self, number, user=None):
        """Returns the transport request"""

        # TODO: user is None, use GET /sap/bc/adt/cts/transporrequests/{number}
        transports = self.get_transport_requests(user=user)

        for trns in transports:
            if trns.number == number:
                return trns

        return None
