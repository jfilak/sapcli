"""ADT operations shared by object handlers of all file formats"""

import sap.adt.checks
import sap.adt.errors


def write_source(source_code, adt_object, corrnr=None, source_label=None, check_before_save=False):
    """Write ``source_code`` to ``adt_object``.

    When ``check_before_save`` is ``True`` (because the user passed
    ``--check`` or set ``SAPCLI_CHECK_BEFORE_SAVE=true``), abapCheckRun
    runs first and a findings exception is raised if it reports errors.

    Independently of the flag, if the PUT to ``source/main`` raises
    :exc:`sap.adt.errors.ExceptionResourceSaveFailure`, abapCheckRun is
    run once on the source we tried to write so the user gets a
    readable diagnostic instead of the cryptic save error. If the
    check has nothing to say, the original failure carries the real
    reason (lock, missing inactive version, ...) and is re-raised.
    """

    if check_before_save:
        result = sap.adt.checks.run_object_check(adt_object, source_code)
        if result.has_errors:
            raise sap.adt.checks.ObjectCheckFindings(
                adt_object, result, source_label=source_label
            )

    try:
        with adt_object.open_editor(corrnr=corrnr) as editor:
            editor.write(source_code)
    except sap.adt.errors.ExceptionResourceSaveFailure as save_exc:
        result = sap.adt.checks.run_object_check(adt_object, source_code)
        if result.has_errors:
            raise sap.adt.checks.ObjectCheckFindings(
                adt_object, result, source_label=source_label
            ) from save_exc
        raise
