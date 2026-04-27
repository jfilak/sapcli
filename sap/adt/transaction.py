"""ABAP Transaction ADT functionality module"""

import json
from base64 import b64encode
from collections import namedtuple
from dataclasses import dataclass, fields
from typing import Optional

from sap.adt.objects import ADTObject, ADTObjectType, ADTCoreData, xmlns_adtcore_ancestor, ADTObjectSourceEditor, create_params


CREATION_CONTENT_TYPE = 'application/vnd.sap.adt.serverdriven.content.v1+json'


# Maps Python field names to JSON key names for the flat creation JSON.
_JSON_KEY_MAP = {
    'transaction_type': 'transactionType',
    'abap_language_version_text': 'abapLanguVersionText',
    'update_mode': 'updateMode',
    'report_name': 'reportName',
    'report_dynnr': 'reportDynnr',
    'report_variant_name': 'reportVariantName',
    'par_parent_transaction_code': 'parParentTransactionCode',
    'program_name': 'programName',
    'program_dynnr': 'programDynnr',
    'local_in_program': 'localInProgramIndi',
    'class_program_name': 'classProgramName',
    'class_name': 'className',
    'method_name': 'methodName',
    'oo_transaction_model': 'ooTransactionModelIndi',
    'var_parent_transaction_code': 'varParentTransactionCode',
    'transaction_variant_cross_client': 'transactionVariantCiIndi',
    'transaction_variant_name': 'transactionCiVariantName',
}


@dataclass
class ReportTransactionDefinition:
    """Report transaction type-specific fields."""

    report_name: Optional[str] = None
    report_dynnr: Optional[str] = None
    report_variant_name: Optional[str] = None


@dataclass
class ParameterTransactionDefinition:
    """Parameter transaction type-specific fields."""

    par_parent_transaction_code: Optional[str] = None


@dataclass
class DialogTransactionDefinition:
    """Dialog transaction type-specific fields."""

    program_name: Optional[str] = None
    program_dynnr: Optional[str] = None


@dataclass
class OOTransactionDefinition:
    """OO transaction type-specific fields."""

    class_name: Optional[str] = None
    method_name: Optional[str] = None
    class_program_name: Optional[str] = None
    local_in_program: Optional[bool] = None
    oo_transaction_model: Optional[bool] = None


@dataclass
class VariantTransactionDefinition:
    """Variant transaction type-specific fields."""

    var_parent_transaction_code: Optional[str] = None
    transaction_variant_cross_client: Optional[bool] = None
    transaction_variant_name: Optional[str] = None


_TypeInfo = namedtuple('_TypeInfo', ['attr', 'cls'])

# Maps transaction type string to its attribute name on TransactionDefinition
# and the corresponding sub-dataclass constructor.
_TYPE_MAP = {
    'reportTransaction': _TypeInfo('report_transaction', ReportTransactionDefinition),
    'parameterTransaction': _TypeInfo('parameter_transaction', ParameterTransactionDefinition),
    'dialogTransaction': _TypeInfo('dialog_transaction', DialogTransactionDefinition),
    'ooTransaction': _TypeInfo('oo_transaction', OOTransactionDefinition),
    'variantTransaction': _TypeInfo('variant_transaction', VariantTransactionDefinition),
}


@dataclass
class TransactionDefinition:  # pylint: disable=too-many-instance-attributes
    """Transaction creation definition.

       Holds the common fields and a type-specific sub-dataclass.
       Fields are plain Python - not coupled to ADT XML marshalling.
    """

    transaction_type: Optional[str] = None
    abap_language_version_text: str = 'Standard ABAP'
    update_mode: str = 'notSet'

    report_transaction: Optional[ReportTransactionDefinition] = None
    parameter_transaction: Optional[ParameterTransactionDefinition] = None
    dialog_transaction: Optional[DialogTransactionDefinition] = None
    oo_transaction: Optional[OOTransactionDefinition] = None
    variant_transaction: Optional[VariantTransactionDefinition] = None

    def _type_specific_definition(self):
        """Returns the active type-specific sub-dataclass or None."""

        if self.transaction_type is None:
            return None

        info = _TYPE_MAP.get(self.transaction_type)
        if info is None:
            return None

        return getattr(self, info.attr)

    def to_create_json(self, name, description, package):
        """Builds the flat creation JSON string.

           The creation JSON is a flat structure with all fields at the
           root level - type-specific fields are flattened from the
           nested sub-dataclass.

           The parameters name, description, and package come from the
           Transaction ADT object metadata and are duplicated into the
           JSON metadata section as required by the ADT API.
        """

        content = {}

        # Emit common fields in order: abap_language_version_text, transaction_type
        for field_name in ('abap_language_version_text', 'transaction_type'):
            value = getattr(self, field_name)
            if value is not None:
                content[_JSON_KEY_MAP[field_name]] = value

        # Emit type-specific fields from sub-dataclass
        type_def = self._type_specific_definition()
        if type_def is not None:
            for fld in fields(type_def):
                value = getattr(type_def, fld.name)
                if value is not None:
                    content[_JSON_KEY_MAP[fld.name]] = value

        # Emit update_mode last (before metadata)
        content[_JSON_KEY_MAP['update_mode']] = self.update_mode

        content['metadata'] = {
            'name': name,
            'description': description,
            'package': package,
        }

        return json.dumps(content, separators=(',', ':'))


class Transaction(ADTObject):
    """ABAP Transaction"""

    OBJTYPE = ADTObjectType(
        'TRAN/T',
        'aps/iam/tran',
        xmlns_adtcore_ancestor('blue', 'http://www.sap.com/wbobj/blue'),
        ['application/vnd.sap.adt.blues.v2+xml', 'application/vnd.sap.adt.blues.v1+xml'],
        {'application/json': 'source/main'},
        'blueSource',
        editor_factory=ADTObjectSourceEditor.json,
        source_mimetype='application/json',
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        if package is not None:
            self._metadata.package_reference.name = package

        self.definition = TransactionDefinition()

    @staticmethod
    def _make_metadata(description, metadata):
        """Creates or updates ADTCoreData for factory methods."""

        if metadata is None:
            return ADTCoreData(description=description, language='EN', master_language='EN')

        metadata.description = description
        return metadata

    @classmethod
    def report(cls, connection, name, *, description, package, metadata=None,
               report_name=None, report_dynnr=None, report_variant_name=None,
               abap_language_version_text='Standard ABAP', update_mode='notSet'):
        """Create a report transaction instance."""

        instance = cls(connection, name, package=package,
                       metadata=cls._make_metadata(description, metadata))
        instance.definition = TransactionDefinition(
            transaction_type='reportTransaction',
            abap_language_version_text=abap_language_version_text,
            update_mode=update_mode,
            report_transaction=ReportTransactionDefinition(
                report_name=report_name,
                report_dynnr=report_dynnr,
                report_variant_name=report_variant_name,
            ),
        )
        return instance

    @classmethod
    def parameter(cls, connection, name, *, description, package, metadata=None,
                  par_parent_transaction_code=None,
                  abap_language_version_text='Standard ABAP', update_mode='notSet'):
        """Create a parameter transaction instance."""

        instance = cls(connection, name, package=package,
                       metadata=cls._make_metadata(description, metadata))
        instance.definition = TransactionDefinition(
            transaction_type='parameterTransaction',
            abap_language_version_text=abap_language_version_text,
            update_mode=update_mode,
            parameter_transaction=ParameterTransactionDefinition(
                par_parent_transaction_code=par_parent_transaction_code,
            ),
        )
        return instance

    @classmethod
    def dialog(cls, connection, name, *, description, package, metadata=None,
               program_name=None, program_dynnr=None,
               abap_language_version_text='Standard ABAP', update_mode='notSet'):
        """Create a dialog transaction instance."""

        instance = cls(connection, name, package=package,
                       metadata=cls._make_metadata(description, metadata))
        instance.definition = TransactionDefinition(
            transaction_type='dialogTransaction',
            abap_language_version_text=abap_language_version_text,
            update_mode=update_mode,
            dialog_transaction=DialogTransactionDefinition(
                program_name=program_name,
                program_dynnr=program_dynnr,
            ),
        )
        return instance

    @classmethod
    def oo(cls, connection, name, *, description, package, metadata=None,  # pylint: disable=invalid-name
           class_name=None, method_name=None, class_program_name=None,
           local_in_program=None, oo_transaction_model=None,
           abap_language_version_text='Standard ABAP', update_mode='notSet'):
        """Create an OO transaction instance."""

        instance = cls(connection, name, package=package,
                       metadata=cls._make_metadata(description, metadata))
        instance.definition = TransactionDefinition(
            transaction_type='ooTransaction',
            abap_language_version_text=abap_language_version_text,
            update_mode=update_mode,
            oo_transaction=OOTransactionDefinition(
                class_name=class_name,
                method_name=method_name,
                class_program_name=class_program_name,
                local_in_program=local_in_program,
                oo_transaction_model=oo_transaction_model,
            ),
        )
        return instance

    @classmethod
    def variant(cls, connection, name, *, description, package, metadata=None,
                var_parent_transaction_code=None,
                transaction_variant_cross_client=None,
                transaction_variant_name=None,
                abap_language_version_text='Standard ABAP', update_mode='notSet'):
        """Create a variant transaction instance."""

        instance = cls(connection, name, package=package,
                       metadata=cls._make_metadata(description, metadata))
        instance.definition = TransactionDefinition(
            transaction_type='variantTransaction',
            abap_language_version_text=abap_language_version_text,
            update_mode=update_mode,
            variant_transaction=VariantTransactionDefinition(
                var_parent_transaction_code=var_parent_transaction_code,
                transaction_variant_cross_client=transaction_variant_cross_client,
                transaction_variant_name=transaction_variant_name,
            ),
        )
        return instance

    def create(self, corrnr=None):
        """Creates Transaction object

           If transaction_type is set on the definition, the creation
           content is built automatically and base64 encoded into the
           XML payload.
        """

        xml, seri_mime = self.serialize()

        if self.definition.transaction_type is not None:
            creation_content = self.definition.to_create_json(
                self.name, self.description, self._metadata.package_reference.name
            )
            encoded = b64encode(creation_content.encode('utf-8')).decode('ascii')
            closing_tag = '</blue:blueSource>'
            xml = xml.replace(
                closing_tag,
                f'<blue:additionalCreationProperties>\n'
                f'<adtcore:content adtcore:encoding="base64"'
                f' adtcore:type="{CREATION_CONTENT_TYPE}"'
                f'>{encoded}</adtcore:content>\n'
                f'</blue:additionalCreationProperties>\n'
                f'{closing_tag}'
            )

        return self.connection.execute(
            'POST',
            self.objtype.basepath,
            headers={'Content-Type': seri_mime},
            params=create_params(corrnr),
            body=bytes(xml, 'utf-8'))
