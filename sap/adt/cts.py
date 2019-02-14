"""CTS object proxies"""


class WorkbenchParser:
    """Prase ADT XML workbench description"""

    def __init__(self, connection, transport_factory, task_factory):
        self._connection = connection
        self._transport_factory = transport_factory
        self._task_factory = task_factory

    def process_workbench_xml(self, workbench_xml):
        """Converts Workbench XML into the list of Transport objects"""

        transports = []
        transport_elements = workbench_xml.elements('tm:request')
        for trelem in transport_elements:
            transport = self.process_transport_xml(trelem)

            task_elements = trelem.elements('tm:task')
            for taskelem in task_elements:
                task = self.process_taks_xml(transport, taskelem)
                transport.add_task(task)

            transports.append(transport)

        return transports

    def process_transport_xml(self, transport_xml):
        """Converts Transport XML into a python object"""

        transport = self._transport_factory(self._connection, transport_xml['number'], transport_xml['owner'])
        return transport

    def process_taks_xml(self, transport, task_xml):
        """Converts Task XML into a python object"""

        task = self._task_factory(transport, task_xml['number'])
        return task


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

    def __init__(self, connection, number: str, owner: str = None, description: str = None):
        self._connection = connection
        self._number = number
        self._owner = owner
        self._description = description

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

    def __init__(self, *params, **kwargs):
        super(WorkbenchTransport, self).__init__(*params, **kwargs)

        self._tasks = []

    def add_task(self, task):
        """Adds a new task to the list of tasks tracked under this transport"""

        self._tasks.append(task)

    def tasks(self):
        """Returns the list of tasks tracked under this transport"""

        return self._tasks


class WorkbenchTask(AbstractWorkbenchRequest):
    """Transport Manager Task"""

    def __init__(self, transport, *params, **kwargs):
        super(WorkbenchTask, self).__init__(*params, **kwargs)

        self._transport = transport
        self._objects = []

    @property
    def transport(self):
        """Parent transport"""

        return self._transport

    def objects(self):
        """Returns the list of objects registered in this task"""

        return self._objects


class Workbench:
    """Transport Manager Workbench"""

    def __init__(self, connection):
        self._connection = connection

    def get_transport_requests(self, user=None):
        """Returns the list of all transport requests"""

        if user is None:
            user = self._connection.user

        resp = self._connection.execute(
            'POST', 'cts/transportrequests',
            params=workbench_params(user),
            headers={'Accept': 'application/vnd.sap.adt.transportorganizer.v1+xml'}
        )

        parser = WorkbenchParser(self._connection, transport_factory=WorkbenchTransport, task_factory=WorkbenchTask)

        return parser.process_workbench_xml(resp.text)
