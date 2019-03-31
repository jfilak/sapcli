"""SAP Programs in ADT functionality module"""

# pylint: disable=unused-import
from sap.adt.objects import OrderedClassMembers
from sap.adt.objects import ADTObjectType, ADTObject, ADTCoreData
from sap.adt.objects import modify_object_params, mod_log
from sap.adt.annotations import xml_attribute, xml_element


class BaseProgram(ADTObject):
    """Base class for object ins the Program ADT namespace"""

    def __init__(self, connection, name, package=None, metadata=None):
        super(BaseProgram, self).__init__(connection, name, metadata, active_status='active')

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

    def change_text(self, content, corrnr=None):
        """Changes the source code"""

        text_uri = self.objtype.get_uri_for_type('text/plain')

        resp = self._connection.execute(
            'PUT', self.uri + text_uri,
            params=modify_object_params(self._lock, corrnr),
            headers={
                'Content-Type': 'text/plain; charset=utf-8'},
            body=content)

        mod_log().debug("Change text response status: %i", resp.status_code)


class Program(BaseProgram):
    """ABAP Report/Program
    """

    OBJTYPE = ADTObjectType(
        'PROG/P',
        'programs/programs',
        ('program', 'http://www.sap.com/adt/programs/programs'),
        'application/vnd.sap.adt.programs.programs.v2+xml',
        {'text/plain': 'source/main'},
        'abapProgram'
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
        super(Program, self).__init__(connection, name, package=package, metadata=metadata)

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

    # pylint: disable=no-self-use
    @property
    def case_sensitive(self):
        """True if the program is case sensitive"""

        return True

    # pylint: disable=no-self-use
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
        ('include', 'http://www.sap.com/adt/programs/includes'),
        # application/vnd.sap.adt.programs.includes+xml, application/vnd.sap.adt.programs.includes.v2+xml
        'application/vnd.sap.adt.programs.includes.v2+xml',
        {'text/plain': 'source/main'},
        'abapInclude'
    )
