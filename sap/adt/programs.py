"""SAP Programs in ADT functionality module"""

import urllib

# pylint: disable=unused-import
import sap.errors
from sap.adt.objects import OrderedClassMembers
from sap.adt.objects import (
    ADTObjectType,
    ADTObject,
    ADTObjectReference,
    ADTCoreData,
    ADTObjectSourceEditor,
    xmlns_adtcore_ancestor
)
from sap.adt.annotations import xml_attribute, xml_element


class BaseProgram(ADTObject):
    """Base class for object ins the Program ADT namespace"""

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata, active_status='active')

        self._metadata.package_reference.name = package
        self._fixpntar = None

    @xml_attribute('abapsource:fixPointArithmetic')
    def fix_point_arithmetic(self):
        """Fixed point arithmetic flag"""

        return self._fixpntar

    @fix_point_arithmetic.setter
    def fix_point_arithmetic(self, value):
        """Fixed point arithmetic flag"""

        self._fixpntar = value == 'true'


class Program(BaseProgram):
    """ABAP Report/Program
    """

    OBJTYPE = ADTObjectType(
        'PROG/P',
        'programs/programs',
        xmlns_adtcore_ancestor('program', 'http://www.sap.com/adt/programs/programs'),
        'application/vnd.sap.adt.programs.programs.v2+xml',
        {'text/plain': 'source/main'},
        'abapProgram',
        editor_factory=ADTObjectSourceEditor
    )

    class LogicalDatabase(metaclass=OrderedClassMembers):
        """Logical database ADT element"""

        def __init__(self):
            self._ref = ADTCoreData.Reference()

        @xml_element('program:ref')
        def reference(self):
            """Returns reference"""

            return self._ref

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, package=package, metadata=metadata)

        self._program_type = None
        self._logical_dabase = Program.LogicalDatabase()

    @xml_attribute('program:programType')
    def program_type(self):
        """Returns program type"""

        return self._program_type

    @program_type.setter
    def program_type(self, value):
        """Sets value of Program Type"""

        types = {
            'executableProgram': '1'
        }

        self._program_type = types[value]

    @property
    def case_sensitive(self):
        """True if the program is case sensitive"""

        return True

    @property
    def application_database(self):
        """Application database"""

        return 'S'

    @xml_element('program:logicalDatabase')
    def logical_database(self):
        """Logical database configuration"""

        return self._logical_dabase


class Include(BaseProgram):
    """ABAP Program Include"""

    OBJTYPE = ADTObjectType(
        'PROG/I',
        'programs/includes',
        xmlns_adtcore_ancestor('include', 'http://www.sap.com/adt/programs/includes'),
        # application/vnd.sap.adt.programs.includes+xml, application/vnd.sap.adt.programs.includes.v2+xml
        'application/vnd.sap.adt.programs.includes.v2+xml',
        {'text/plain': 'source/main'},
        'abapInclude',
        editor_factory=ADTObjectSourceEditor
    )

    def __init__(self, connection, name, package=None, metadata=None, master=None):
        super().__init__(connection, name, package=package, metadata=metadata)

        if master is not None:
            self._context = ADTObjectReference(name=master)
        else:
            self._context = None

    @property
    def uri(self):
        """Own version of URI which adds context with the master program"""

        uri = super().uri

        if self.master is not None:
            master_uri = Program(self.connection, self.master).full_adt_uri
            master_uri = urllib.parse.quote(master_uri, safe='')
            uri = f'{uri}?context={master_uri}'

        return uri

    @property
    def master(self):
        """Returns name of the master program of this include"""

        if self._context is not None:
            return self._context.name

        return None

    @master.setter
    def master(self, value):
        """Sets name of the master program of this include"""

        if self._context is None:
            self._context = ADTObjectReference()

        self._context.name = value

    @xml_element('include:contextRef', factory=ADTObjectReference, ignore_empty=True)
    def context(self):
        """Returns the object holding the inforation about reference to the corresponding
           main program.
        """

        return self._context

    @context.setter
    def context(self, value):
        """Sets the object holding the inforation about reference to the corresponding
           main program.
        """

        self._context = value


def make_program_include_object(connection, name):
    """Either splits include name into main\\include
       or fetches the include's data from the remote system
    """

    name_parts = name.split('\\')

    if len(name_parts) == 1:
        theobject = Include(connection, name)
        theobject.fetch()
        return theobject

    if len(name_parts) == 2:
        return Include(connection, name_parts[1], master=name_parts[0])

    raise sap.errors.SAPCliError('Program include name can be: INCLUDE or MAIN\\INCLUDE')
