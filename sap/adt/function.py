"""Function Group and Function Module object proxies"""

from copy import copy

# pylint: disable=unused-import
from sap.adt.objects import OrderedClassMembers
from sap.adt.objects import ADTObjectType, ADTObject, ADTObjectSourceEditorWithResponse, xmlns_adtcore_ancestor
from sap.adt.objects import find_mime_version
from sap.adt.annotations import xml_attribute, xml_element


class ADTContainer(metaclass=OrderedClassMembers):
    """ADT Container Reference"""

    def __init__(self, uri=None, object_type=None, object_name=None, package_name=None):
        # TODO add a helper for this brainless assignment
        self._uri = uri
        self._object_type = object_type
        self._object_name = object_name
        self._package_name = package_name

    @xml_attribute('adtcore:name')
    def object_name(self):
        """Returns ABAP Object name"""

        return self._object_name

    @object_name.setter
    def object_name(self, value):
        """Sets ABAP Object name"""

        self._object_name = value

    @xml_attribute('adtcore:type')
    def object_type(self):
        """Returns ABAP Object type"""

        return self._object_type

    @object_type.setter
    def object_type(self, value):
        """Begins ABAP Object type"""

        self._object_type = value

    @xml_attribute('adtcore:uri')
    def uri(self):
        """Returns URI of the reference"""

        return self._uri

    @uri.setter
    def uri(self, value):
        """Sets URI of the reference"""

        self._uri = value

    @xml_attribute('adtcore:packageName')
    def package_name(self):
        """Returns ABAP Package of the referenced object"""

        return self._package_name

    @package_name.setter
    def package_name(self, value):
        """Sets ABAP Package of the referenced object"""

        self._package_name = value


class FunctionGroup(ADTObject):
    """ABAP Function Group"""

    OBJTYPE = ADTObjectType(
        'FUGR/F',
        'functions/groups',
        xmlns_adtcore_ancestor('group', 'http://www.sap.com/adt/functions/groups'),
        ['application/vnd.sap.adt.functions.groups.v3+xml',
         'application/vnd.sap.adt.functions.groups.v2+xml'],
        {'text/plain': 'source/main'},
        'abapFunctionGroup',
        editor_factory=ADTObjectSourceEditorWithResponse
    )

    def __init__(self, connection, name, package=None, metadata=None, active_status=None):
        super().__init__(connection, name, metadata=metadata, active_status=active_status)

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

    @classmethod
    def create_reference(cls, connection, name, package_name):
        """Builds reference to Function Group"""

        return ADTContainer(
            uri=f'/{connection.uri}/{cls.OBJTYPE.basepath}/{name.lower()}',
            object_type=cls.OBJTYPE.code,
            object_name=name,
            package_name=package_name)


class FunctionModule(ADTObject):
    """ABAP Function Module"""

    OBJTYPE = ADTObjectType(
        'FUGR/FF',
        'functions/groups/{groupname}/fmodules',
        xmlns_adtcore_ancestor('fmodule', 'http://www.sap.com/adt/functions/fmodules'),
        ['application/vnd.sap.adt.functions.fmodules.v3+xml',
         'application/vnd.sap.adt.functions.fmodules.v2+xml'],
        {'text/plain': 'source/main'},
        'abapFunctionModule',
        editor_factory=ADTObjectSourceEditorWithResponse
    )

    def __init__(self, connection, name, function_group_name, metadata=None, active_status=None):
        super().__init__(connection, name, metadata=metadata, active_status=active_status)

        self._function_group_name = function_group_name

        self._objtype = copy(FunctionModule.OBJTYPE)
        self._objtype.basepath = FunctionModule.OBJTYPE.basepath.format(groupname=function_group_name.lower())

        self._processing_type = None
        self._reference = None
        self._release_state = None

    def _get_mime_and_version(self):
        # because the standard _get_mime_and_version() use basepath which
        # is modified in the __init__() method
        return find_mime_version(self.connection, FunctionModule.OBJTYPE)

    def language(self):
        """Not supported on Function Module level but Function Group level"""

        return None

    def master_language(self):
        """Not supported on Function Module level but Function Group level"""

        return None

    def master_system(self):
        """Not supported on Function Module level but Function Group level"""

        return None

    def responsible(self):
        """Not supported on Function Module level but Function Group level"""

        return None

    def reference(self):
        """Function Module has no Package reference but containerRef"""

        return None

    @property
    def objtype(self):
        """ADT type definition which is built for each instance
           and is not per class like othe ADT Objects.
        """

        return self._objtype

    @xml_attribute('fmodule:processingType')
    def processing_type(self):
        """Returns processing type : RFC or BAPI or Local"""

        return self._processing_type

    @processing_type.setter
    def processing_type(self, value):
        """Sets processing type : RFC or BAPI or Local"""

        self._processing_type = value

    @xml_attribute('fmodule:releaseState')
    def release_state(self):
        """"Attribute Release State"""

        return self._release_state

    @release_state.setter
    def release_state(self, value):
        """"Attribute Release State"""

        self._release_state = value

    @xml_element('adtcore:containerRef')
    def function_group_reference(self):
        """Returns parent Function Group reference"""

        if self._reference is None:
            self._reference = FunctionGroup.create_reference(self.connection, self._function_group_name, self.package)

        return self._reference


class FunctionInclude(ADTObject):
    """ABAP Function Group Include"""

    OBJTYPE = ADTObjectType(
        'FUGR/I',
        'functions/groups/{groupname}/includes',
        xmlns_adtcore_ancestor('finclude', 'http://www.sap.com/adt/functions/fincludes'),
        ['application/vnd.sap.adt.functions.fincludes.v2+xml',
         'application/vnd.sap.adt.functions.fincludes+xml'],
        {'text/plain': 'source/main'},
        'abapFunctionGroupInclude',
        editor_factory=ADTObjectSourceEditorWithResponse
    )

    def __init__(self, connection, name, function_group_name, metadata=None, active_status=None):
        super().__init__(connection, name, metadata=metadata, active_status=active_status)

        self._function_group_name = function_group_name

        self._objtype = copy(FunctionInclude.OBJTYPE)
        self._objtype.basepath = FunctionInclude.OBJTYPE.basepath.format(groupname=function_group_name.lower())

        self._reference = None

    def _get_mime_and_version(self):
        # because the standard _get_mime_and_version() use basepath which
        # is modified in the __init__() method
        return find_mime_version(self.connection, FunctionInclude.OBJTYPE)

    def language(self):
        """Not supported on Function Include level but Function Group level"""

        return None

    def master_language(self):
        """Not supported on Function Include level but Function Group level"""

        return None

    def master_system(self):
        """Not supported on Function Include level but Function Group level"""

        return None

    def responsible(self):
        """Not supported on Function Include level but Function Group level"""

        return None

    def reference(self):
        """Function Include has no Package reference but containerRef"""

        return None

    @property
    def objtype(self):
        """ADT type definition which is built for each instance
           and is not per class like other ADT Objects.
        """

        return self._objtype

    @xml_element('adtcore:containerRef')
    def function_group_reference(self):
        """Returns parent Function Group reference"""

        if self._reference is None:
            self._reference = FunctionGroup.create_reference(self.connection, self._function_group_name, self.package)

        return self._reference
