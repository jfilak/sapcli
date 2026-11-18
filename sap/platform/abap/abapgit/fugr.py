"""Function groups in the abapGit serialization"""

import enum
from types import SimpleNamespace

from sap import get_logger

import sap.adt
import sap.adt.errors
import sap.adt.function
import sap.errors
import sap.adt.checks
import sap.platform.abap.abapgit
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult
from sap.platform.abap.abapgit.files import download_abap_source, dump_attributes_to_file, write_source
from sap.platform.abap.abapgit import AbapToAbapGitTranslator
from sap.platform.abap.ddic import PROGDIR, TPOOL, TPOOL_LINE, AREAT, INCLUDES, FUNCTIONS, FUNCTION_LINE, \
    IMPORT_TYPE, CHANGING_TYPE, EXPORT_TYPE, TABLE_TYPE, EXCEPTION_TYPE, DOCUMENTATION_TYPE, RSFDO


def mod_log():
    """Module logger"""

    return get_logger()


class SourceCodeFormat(enum.Enum):
    """Source code format of ADT objects"""

    ABAP = 'ABAP'
    ABAPGIT = 'ABAPGIT'


def download_abapgit_source(observer, object_name, source_object, typsfx, translate_fn, destdir=None):
    """Saves the source code of object in AbapGit format"""

    try:
        source_code = translate_fn(source_object)
    except sap.adt.errors.ADTError as err:
        observer.warning(f'Download of AbapGit source code failed: {err}')
    else:
        write_source(observer, source_code, object_name, typsfx, destdir)


def build_function_module_abap_attributes(func_module):
    """Returns populated FUNCTION_LINE ABAP structure with attributes"""

    func_line = FUNCTION_LINE()
    func_line.FUNCNAME = func_module.name
    func_line.REMOTE_CALL = 'R' if func_module.processing_type == 'rfc' else None
    func_line.SHORT_TEXT = func_module.description

    func_local_interface = func_module.get_local_interface()
    interface_helper = {
        'IMPORTING': (IMPORT_TYPE, 'IMPORT'),
        'CHANGING': (CHANGING_TYPE, 'CHANGING'),
        'EXPORTING': (EXPORT_TYPE, 'EXPORT'),
        'TABLES': (TABLE_TYPE, 'TABLES'),
        'EXCEPTIONS': (EXCEPTION_TYPE, 'EXCEPTION')
    }

    for param_type, params in func_local_interface.items():
        ddic_type, func_line_attr = interface_helper[param_type]
        ddic_type = ddic_type()
        for param in params:
            ddic_type.append(param)

        setattr(func_line, func_line_attr, ddic_type if ddic_type else None)

    documentation = DOCUMENTATION_TYPE()
    for param_type in func_module.DOCUMENTATION_ORDER:
        for param in func_local_interface[param_type]:
            if param_type == 'EXCEPTIONS':
                documentation.append(RSFDO(PARAMETER=param.EXCEPTION, KIND='X'))
            else:
                documentation.append(RSFDO(PARAMETER=param.PARAMETER, KIND='P'))

    func_line.DOCUMENTATION = documentation
    return func_line


def build_function_group_abap_attributes(adt_funcgrp, function_modules, funcgrp_includes):
    """Returns populated ABAP structure with attributes"""

    areat = AREAT(adt_funcgrp.description)
    includes = INCLUDES()
    for include in funcgrp_includes:
        includes.append(f'<SOBJ_NAME>{include.name}</SOBJ_NAME>')

    functions = FUNCTIONS()
    for func_module in function_modules:
        functions.append(build_function_module_abap_attributes(func_module))

    return areat, includes, functions


def build_user_fn_include_abap_attributes(include, funcgrp):
    """Returns populated PROGDIR ABAP structure with attributes for user-defined function include"""

    progdir = PROGDIR()
    progdir.NAME = include.name
    progdir.SUBC = 'I'
    progdir.APPL = 'S'
    progdir.RLOAD = 'E' if include.description else None
    progdir.UCCHECK = 'X' if funcgrp.active_unicode_check else None

    tpool = TPOOL()
    if include.description:
        tpool_line = TPOOL_LINE()
        tpool_line.ID = 'R'
        tpool_line.ENTRY = include.description
        tpool_line.LENGTH = len(include.description)
        tpool.append(tpool_line)

    return progdir, tpool


def build_system_fn_include_abap_attributes(include, funcgrp):
    """Returns populated PROGDIR ABAP structure with attributes for system function include"""

    progdir, _ = build_user_fn_include_abap_attributes(include, funcgrp)
    progdir.DBAPL = 'S'
    progdir.DBNA = 'D$'
    progdir.FIXPT = 'X' if funcgrp.fix_point_arithmetic else None
    progdir.LDBNAME = 'D$S'

    return (progdir,)


def checkout_function_include(observer, include_name, funcgrp, destdir=None):
    """Checkout Function Group Include"""

    include = sap.adt.FunctionInclude(funcgrp.connection, include_name, funcgrp.name)
    if include_name.endswith('TOP'):
        include_attrs = build_system_fn_include_abap_attributes(include, funcgrp)
    else:
        include_attrs = build_user_fn_include_abap_attributes(include, funcgrp)

    dump_attributes_to_file(observer, funcgrp.name, include_attrs, f'.fugr.{include.name}', '', destdir=destdir)

    return include


def checkout_function_group(connection, name, observer, destdir=None, source_format=SourceCodeFormat.ABAPGIT):
    """Download function group sources"""

    observer.checking_out(name)
    funcgrp = sap.adt.FunctionGroup(connection, name)
    function_modules = []
    includes = []

    walk_step = funcgrp.walk()[0]  # Function group always has only a single step
    objects = walk_step[2]
    for obj in objects:
        if obj.typ == sap.adt.FunctionInclude.OBJTYPE.code and obj.name.endswith('UXX'):
            observer.warning(f'Skipping system generated "UXX" function group include: {obj.name}.')
            continue

        if obj.typ == sap.adt.FunctionModule.OBJTYPE.code:
            adt_obj = sap.adt.FunctionModule(funcgrp.connection, obj.name, funcgrp.name)
            function_modules.append(adt_obj)
            if source_format == SourceCodeFormat.ABAPGIT:
                download_abapgit_source(observer, funcgrp.name, adt_obj, f'.fugr.{adt_obj.name}',
                                        AbapToAbapGitTranslator.translate_function_module, destdir=destdir)
            else:
                download_abap_source(observer, funcgrp.name, adt_obj, f'.fugr.{adt_obj.name}', destdir=destdir)

        elif obj.typ in (sap.adt.FunctionInclude.OBJTYPE.code, 'FUGR/PX'):
            adt_obj = checkout_function_include(observer, obj.name, funcgrp, destdir=destdir)
            includes.append(adt_obj)
            download_abap_source(observer, funcgrp.name, adt_obj, f'.fugr.{adt_obj.name}', destdir=destdir)
        else:
            raise sap.errors.SAPCliError(f'Unsupported function group object: {obj.typ} {obj.name}')

    funcgrp_attrs = build_function_group_abap_attributes(funcgrp, function_modules, includes)
    dump_attributes_to_file(observer, funcgrp.name, funcgrp_attrs, '.fugr', 'LCL_OBJECT_FUGR', destdir=destdir)


def _check_fugr_source_files(repo_obj, functions, includes):
    """Check that all functions and includes have source files"""

    for func in functions:
        function_name = func.FUNCNAME.lower()
        function_file_path = repo_obj.path[:-4] + f'.{function_name}' + '.abap'
        if function_file_path not in repo_obj.files:
            raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for function {function_name}')

    for include in includes:
        include_name = include.lower()
        include_file_path = repo_obj.path[:-4] + f'.{include_name}' + '.abap'
        if include_file_path not in repo_obj.files:
            raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for include {include_name}')


def _format_function(source_code):
    """Format parameters of function

    Original source code:
    ```
        FUNCTION ztest_function.
        *"----------------------------------------------------------------------
        *"*"Local Interface:
        *"  IMPORTING
        *"     VALUE(IV_PARAM1) TYPE  STRING
        *"  EXPORTING
        *"     VALUE(EV_PARAM2) TYPE  STRING
        *"----------------------------------------------------------------------
        ...
        ENDFUNCTION.
    ```
    Formatted source code:
    ```
        FUNCTION ztest_function
        IMPORTING
        VALUE(IV_PARAM1) TYPE STRING
        EXPORTING
        VALUE(EV_PARAM2) TYPE STRING
        .
        ...
        ENDFUNCTION.
    ```
    """

    source_lines = source_code.split('\n')
    start_block, end_block = sap.adt.function.FunctionModule.get_parameters_block(source_lines)
    if end_block == 0:
        # Source code is in ADT format
        return '\n'.join(source_lines)

    source_lines[0] = source_lines[0].replace('.', '')  # Remove dot at the end of first line
    parameters = sap.adt.function.FunctionModule.parse_function_parameters(source_lines[start_block:end_block])
    adt_parameters_block = []
    for param_type, params in parameters.items():
        if not params:
            continue

        adt_parameters_block.append(f'{param_type}')
        adt_parameters_block += params

    adt_parameters_block.append('.')  # Add dot at the end of the parameters block
    source_lines[start_block:end_block + 1] = adt_parameters_block
    return '\n'.join(source_lines)


def create_function_module(context, func, function_group, metadata):
    """Create Function Module"""

    function_module = sap.adt.FunctionModule(context.connection, func.FUNCNAME, function_group.name, metadata=metadata)
    function_module.description = func.SHORT_TEXT

    context.observer.creating('Function Module', function_module.name)
    try:
        function_module.create(context.corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    if func.REMOTE_CALL == 'R':
        function_module.processing_type = 'rfc'
        lock_handle = function_module.lock()
        with function_module.open_editor(lock_handle, context.corrnr) as fn_editor:
            fn_editor.push()

    return function_module


def create_function_include(context, include, function_group, metadata):
    """Create Function Group Include"""

    include_obj = sap.adt.FunctionInclude(context.connection, include, function_group.name, metadata=metadata)

    context.observer.creating('Function Group Include', include_obj.name)
    try:
        include_obj.create(context.corrnr)
    except sap.adt.errors.ExceptionResourceCreationFailure as err:
        if not str(err).endswith('already exists'):
            raise

        mod_log().info(err.message)

    return include_obj


def _read_fugr_source_file(repo_obj, name):
    """Returns the path and the contents of the source file of the function
       group include or function module of the given name
    """

    source_file = repo_obj.path[:-4] + f'.{name.lower()}' + '.abap'
    with open(source_file, 'r', encoding='utf-8') as source:
        return (source_file, source.read())


class FunctionGroupHandler(ObjectHandler):
    """Function group: <name>.fugr.xml, <name>.fugr.<include>.abap with
       <name>.fugr.<include>.xml for every include and
       <name>.fugr.<function module>.abap for every function module
    """

    FILE_TYPE = 'fugr'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('FUGR/F',)

    def checkout(self, connection, adt_type, name, destdir, observer):
        checkout_function_group(connection, name, observer, destdir=destdir)

    def prepare(self, repo_obj, observer):
        with open(repo_obj.path, encoding='utf-8') as abap_data_file:
            results = sap.platform.abap.abapgit.from_xml([AREAT, INCLUDES, FUNCTIONS], abap_data_file.read())

        includes = results['INCLUDES']
        functions = results['FUNCTIONS']

        _check_fugr_source_files(repo_obj, functions, includes)

        include_sources = [(include,) + _read_fugr_source_file(repo_obj, include) for include in includes]

        function_sources = []
        for func in functions:
            source_file, source_code = _read_fugr_source_file(repo_obj, func.FUNCNAME)
            # If the function is in abapGit format, change it to ADT format
            function_sources.append((func, source_file, _format_function(source_code)))

        return SimpleNamespace(description=results['AREAT'], includes=include_sources, functions=function_sources)

    def checkin(self, context, repo_obj, prepared):
        context.observer.creating('Function Group', repo_obj.name)

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper())
        function_group = sap.adt.FunctionGroup(context.connection, repo_obj.name.upper(), package=context.package_name,
                                               metadata=metadata)
        function_group.description = prepared.description

        try:
            function_group.create(context.corrnr)
        except sap.adt.errors.ExceptionResourceAlreadyExists as err:
            mod_log().info(err.message)

        abap_objs_inactive = [function_group]
        used_files = []

        for include, source_file, source_code in prepared.includes:
            include_obj = create_function_include(context, include, function_group, metadata)
            abap_objs_inactive.append(include_obj)

            context.observer.writing('Function Group Include', include_obj.name)
            sap.adt.checks.write_source(source_code, include_obj, context.corrnr, source_label=source_file,
                                        check_before_save=context.check_before_save)
            used_files.append(source_file)

        for func, source_file, source_code in prepared.functions:
            function_module = create_function_module(context, func, function_group, metadata)
            abap_objs_inactive.append(function_module)

            context.observer.writing('Function Module', function_module.name)
            sap.adt.checks.write_source(source_code, function_module, context.corrnr, source_label=source_file,
                                        check_before_save=context.check_before_save)
            used_files.append(source_file)

        return ObjectCheckinResult(abap_objs_inactive, used_files)

    def locate(self, repo_obj, part, line):
        # Source code positions of function groups are not mapped to files yet
        return None
