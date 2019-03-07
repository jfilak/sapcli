"""ABAP Package (DEV/C) ADT functionality module"""

# pylint: disable=unused-import
from sap.adt.objects import OrderedClassMembers
from sap.adt.objects import ADTObjectType, ADTObject
from sap.adt.annotations import xml_attribute, xml_element


class Package(ADTObject):
    """ABAP Package - Development class - DEVC"""

    OBJTYPE = ADTObjectType(
        'DEVC/K',
        'packages',
        ('pak', 'http://www.sap.com/adt/packages'),
        'application/vnd.sap.adt.packages.v1+xml',
        {},
        'package'
    )

    class SuperPackage(metaclass=OrderedClassMembers):
        """Super Package
        """

        def __init__(self, name=None):
            self._name = name

        @xml_attribute('adtcore:name')
        def name(self):
            """super package name
            """

            return self._name

        @name.setter
        def name(self, value):
            """super package name
            """

            self._name = value

    class SoftwareComponent(metaclass=OrderedClassMembers):
        """SAP Software component.
        """

        def __init__(self, name=None):
            self._name = name

        @xml_attribute('pak:name')
        def name(self):
            """Software component name
            """

            return self._name

    class ApplicationComponent(metaclass=OrderedClassMembers):
        """Application component.
        """

        def __init__(self, name=None):
            self._name = name

        @xml_attribute('pak:name')
        def name(self):
            """Application component name
            """

            return self._name

    class Attributes(metaclass=OrderedClassMembers):
        """SAP Package attributes.
        """

        def __init__(self, name=None):
            self._package_type = name

        @xml_attribute('pak:packageType')
        def package_type(self):
            """The Package's type
            """

            return self._package_type

        @package_type.setter
        def package_type(self, value):
            """The Package's type setter
            """

            self._package_type = value

    class Transport(metaclass=OrderedClassMembers):
        """SAP Package transport details.
        """

        class Layer(metaclass=OrderedClassMembers):
            """SAP Software component.
            """

            def __init__(self, name=None):
                self._name = name

            @xml_attribute('pak:name')
            def name(self):
                """Software component name
                """

                return self._name

        def __init__(self):
            self._software_component = Package.SoftwareComponent()
            self._layer = Package.Transport.Layer()

        @xml_element('pak:softwareComponent')
        def software_component(self):
            """The Package's software component
            """

            return self._software_component

        @software_component.setter
        def software_component(self, value):
            """The Package's software component setter
            """

            self._software_component = value

        @xml_element('pak:transportLayer')
        def transport_layer(self):
            """The Package's transport layer
            """

            return self._layer

        @transport_layer.setter
        def transport_layer(self, value):
            """Set's the transport layer"""

            self._layer = value

    def __init__(self, connection, name, metadata=None):
        super(Package, self).__init__(connection, name, metadata)

        self._superpkg = Package.SuperPackage()
        self._transport = Package.Transport()
        self._attributes = Package.Attributes()
        self._metadata.package_reference.name = name
        self._appcomp = None

    # pylint: disable=no-self-use
    @xml_attribute('adtcore:version')
    def active(self):
        """Version in regards of activation"""

        return "active"

    @xml_element('pak:attributes')
    def attributes(self):
        """The package's attributes.
        """
        return self._attributes

    @xml_element('pak:superPackage')
    def super_package(self):
        """The package's super package.
        """

        return self._superpkg

    @xml_element('pak:applicationComponent')
    # pylint: disable=no-self-use
    def app_component(self):
        """The package's application component
        """

        return self._appcomp

    @xml_element('pak:transport')
    def transport(self):
        """The package's transport configuration.
        """

        return self._transport

    @xml_element('pak:translation')
    # pylint: disable=no-self-use
    def translation(self):
        """The package's translation flag
        """

        return None

    @xml_element('pak:useAccesses')
    # pylint: disable=no-self-use
    def use_accesses(self):
        """The package's Use Accesses
        """

        return None

    @xml_element('pak:packageInterfaces')
    # pylint: disable=no-self-use
    def package_interfaces(self):
        """The package's Interfaces
        """

        return None

    @xml_element('pak:subPackages')
    # pylint: disable=no-self-use
    def sub_packages(self):
        """The package's sub-packages
        """

        return None

    def set_package_type(self, package_type):
        """Changes the Package's type
        """

        self._attributes.package_type = package_type

    def set_software_component(self, name):
        """Changes the Package's software component
        """

        self._transport.software_component = Package.SoftwareComponent(name)

    def set_transport_layer(self, name):
        """Changes the Package's transport layer
        """

        self._transport.transport_layer = Package.Transport.Layer(name)

    def set_app_component(self, name):
        """Changes the Package's software component
        """

        self._appcomp = Package.ApplicationComponent(name)
