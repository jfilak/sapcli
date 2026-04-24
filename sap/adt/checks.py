"""Object Checks ADT wrappers"""

import base64
from fnmatch import fnmatch
from typing import Optional

from sap.errors import SAPCliError
from sap.adt.objects import ADTObjectType, XMLNamespace, xmlns_adtcore_ancestor
from sap.adt.marshalling import Marshal
from sap.adt.annotations import OrderedClassMembers, XmlNodeAttributeProperty, XmlListNodeProperty, XmlElementKind, \
    XmlContainer, XmlNodeProperty
from sap.adt.uri import format_check_location


XMLNS_CHKRUN = XMLNamespace('chkrun', 'http://www.sap.com/adt/checkrun')
XMLNS_CHKRUN_WITH_ADTCORE = xmlns_adtcore_ancestor('chkrun', 'http://www.sap.com/adt/checkrun')


# pylint: disable=too-few-public-methods
class Reporter(metaclass=OrderedClassMembers):
    """ADT Object Checks Run Reporter"""

    name = XmlNodeAttributeProperty('chkrun:name')
    supported_types = XmlListNodeProperty('chkrun:supportedType', kind=XmlElementKind.TEXT)

    def __init__(self, name=None):
        self.name = name

    def supports_type(self, obj_code):
        """Returns true if the give object code is supported"""

        return any((fnmatch(obj_code, styp) for styp in self.supported_types))

    def supports_object(self, adt_obj):
        """Returns true if the given object is supported"""

        return self.supports_type(adt_obj.objtype.code)


# pylint: disable=invalid-name
ReportersContainer = XmlContainer.define('chkrun:reporter', Reporter)
ReportersContainer.objtype = ADTObjectType(None,
                                           'checkruns/reporters',
                                           XMLNS_CHKRUN,
                                           'application/vnd.sap.adt.reporters+xml',
                                           None,
                                           'checkReporters')


class CheckArtifact(metaclass=OrderedClassMembers):
    """ADT Check Artifact - payload attached to a :class:`CheckObject`.

    Represents the source text being checked (Base64 encoded UTF-8) so
    that abapCheckRun inspects the candidate source instead of the
    currently stored one.
    """

    content_type = XmlNodeAttributeProperty('chkrun:contentType')
    uri = XmlNodeAttributeProperty('chkrun:uri')
    content = XmlNodeProperty('chkrun:content', kind=XmlElementKind.TEXT)

    def __init__(self, uri=None, content=None, content_type='text/plain; charset=utf-8'):
        self.uri = uri
        self.content = content
        self.content_type = content_type


# pylint: disable=invalid-name
CheckArtifactList = XmlContainer.define('chkrun:artifact', CheckArtifact)


class CheckObject(metaclass=OrderedClassMembers):
    """ADT Check Object item for the run request"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    chkrun_version = XmlNodeAttributeProperty('chkrun:version', value='active')
    artifacts = XmlNodeProperty('chkrun:artifacts', ignore_empty=True)

    def __init__(self, uri):
        self.uri = uri

    def add_artifact(self, artifact):
        """Appends a :class:`CheckArtifact` to this object, creating the
           container lazily."""

        # pylint: disable=no-value-for-parameter
        if self.artifacts is None:
            self.artifacts = CheckArtifactList()

        self.artifacts.append(artifact)


class CheckObjectList(metaclass=OrderedClassMembers):
    """ADT run request items"""

    objtype = ADTObjectType(None,
                            'checkruns',
                            XMLNS_CHKRUN_WITH_ADTCORE,
                            'application/vnd.sap.adt.checkobjects+xml',
                            None,
                            'checkObjectList')

    objects = XmlListNodeProperty('chkrun:checkObject')

    def __iter__(self):
        return iter(self.objects)

    def add_uri(self, uri):
        """Adds the give URI to the list"""

        self.objects = CheckObject(uri)

    def add_object(self, adt_object):
        """Adds the give object to the list"""

        self.add_uri(adt_object.full_adt_uri)

    def add_object_with_source(self, adt_object, source, *, version='active'):
        """Adds an object along with a candidate source payload.

        The artifact URI is derived from the object's ``full_adt_uri``
        and the ``text/plain`` typeuri (e.g. ``source/main``).
        ``source`` is expected to be a text string; the trailing newline
        is stripped to mirror :class:`ADTObjectSourceEditor.write` before
        the payload is Base64 encoded.
        """

        check_object = CheckObject(adt_object.full_adt_uri)
        check_object.chkrun_version = version

        if source and source[-1] == '\n':
            source = source[:-1]

        artifact_uri = adt_object.full_adt_uri + adt_object.objtype.get_uri_for_type('text/plain')
        encoded = base64.b64encode(source.encode('utf-8')).decode('ascii')
        check_object.add_artifact(CheckArtifact(uri=artifact_uri, content=encoded))

        self.objects = check_object
        return check_object


class CheckMessage(metaclass=OrderedClassMembers):
    """Run Check result message"""

    uri = XmlNodeAttributeProperty('chkrun:uri')
    typ = XmlNodeAttributeProperty('chkrun:type')
    short_text = XmlNodeAttributeProperty('chkrun:shortText')
    category = XmlNodeAttributeProperty('chkrun:category')
    code = XmlNodeAttributeProperty('chkrun:code')


# pylint: disable=invalid-name
CheckMessageList = XmlContainer.define('chkrun:checkMessage', CheckMessage)


class CheckReport(metaclass=OrderedClassMembers):
    """Group of messages for a single reporter"""

    reporter = XmlNodeAttributeProperty('chkrun:reporter')
    triggering_uri = XmlNodeAttributeProperty('chkrun:triggeringUri')
    status = XmlNodeAttributeProperty('chkrun:status')
    status_text = XmlNodeAttributeProperty('chkrun:statusText')
    messages = XmlNodeProperty('chkrun:checkMessageList')

    # pylint: disable=no-value-for-parameter
    def __init__(self):
        self.messages = CheckMessageList()


# pylint: disable=invalid-name
CheckReportList = XmlContainer.define('chkrun:checkReport', CheckReport)
CheckReportList.objtype = ADTObjectType(None,
                                        'checkruns',
                                        XMLNS_CHKRUN,
                                        'application/vnd.sap.adt.checkmessages+xml',
                                        None,
                                        'checkRunReports')


def fetch_reporters(connection):
    """Returns the list of supported ADT reporters"""

    # pylint: disable=no-value-for-parameter
    reporters = ReportersContainer()

    resp = connection.execute('GET', reporters.objtype.basepath, accept=reporters.objtype.mimetype)

    Marshal.deserialize(resp.text, reporters)

    return reporters.items


def run(connection, reporter, object_list):
    """Run the reporter :class Reporter: for the give object list :class CheckObjectList:"""

    xml = Marshal().serialize(object_list)

    resp = connection.execute('POST', object_list.objtype.basepath,
                              accept=CheckReportList.objtype.mimetype,
                              content_type=object_list.objtype.mimetype,
                              params={'reporters': reporter.name},
                              body=xml)

    # pylint: disable=no-value-for-parameter
    report_list = CheckReportList()
    Marshal.deserialize(resp.text, report_list)

    return report_list.items


def run_for_supported_objects(connection, reporter, adt_objects):
    """Runs the give checks for all supported adt objects"""

    object_list = CheckObjectList()

    for obj in adt_objects:
        if reporter.supports_object(obj):
            object_list.add_object(obj)

    return run(connection, reporter, object_list)


class CheckResult:
    """Aggregated outcome of a single-object checkrun.

    Wraps the list of raw :class:`CheckReport` instances so callers can
    ask the usual "is it safe to write?" question without walking the
    nested XML structure themselves. ``reports`` remains available for
    code that still needs the raw per-reporter detail.
    """

    def __init__(self, reports):
        self.reports = list(reports)

    @property
    def messages(self):
        """Flat iterable of messages across all reports."""

        for report in self.reports:
            if report.messages is None:
                continue
            yield from report.messages

    @property
    def has_errors(self):
        """True iff at least one message carries type ``E``."""

        return any(msg.typ == 'E' for msg in self.messages)

    @property
    def has_warnings(self):
        """True iff at least one message carries type ``W``."""

        return any(msg.typ == 'W' for msg in self.messages)


def format_check_message(message, source_label: Optional[str] = None) -> str:
    """One-line rendering of a :class:`CheckMessage` for CLI / exception output.

    Format: ``<label>:<line>:<col>: <type> <code>: <short_text>``.
    """

    location = format_check_location(message.uri or '', source_label=source_label)
    code = message.code or ''
    code_part = f' {code}' if code else ''
    return f'{location}: {message.typ}{code_part}: {message.short_text}'


class ObjectCheckFindings(SAPCliError):
    """Raised when abapCheckRun reports error messages for a candidate source.

    Carries the :class:`CheckResult` unchanged so callers can re-render
    the location (for instance, map the ADT URI back to a filesystem
    path when the code came from an abapgit repository).
    """

    def __init__(self, adt_object, result, *, source_label: Optional[str] = None):
        super().__init__()
        self.adt_object = adt_object
        self.result = result
        self.source_label = source_label

    def __str__(self):
        lines = [f'Object check failed for {self.adt_object.name}:']
        for msg in self.result.messages:
            lines.append('  ' + format_check_message(msg, self.source_label))
        return '\n'.join(lines)


def run_object_check(adt_object, source, *, version='active', reporter='abapCheckRun'):
    """Runs ``abapCheckRun`` against a candidate source for an ADT object.

    Builds the check request from ``adt_object`` + ``source``, posts it
    to ``/sap/bc/adt/checkruns?reporters=<reporter>`` and returns a
    :class:`CheckResult`.
    """

    object_list = CheckObjectList()
    object_list.add_object_with_source(adt_object, source, version=version)

    reports = run(adt_object.connection, Reporter(reporter), object_list)
    return CheckResult(reports)
