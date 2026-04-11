"""Formatting utilities for Domain objects"""


def format_domain_human(console, domain_obj, indent=''):
    """Format domain information in human-readable format

    Args:
        console: Console object for output
        domain_obj: sap.adt.Domain instance with fetched content
        indent: String prefix for indentation (e.g., '    ' or '  ')
    """
    # Type Information
    console.printout(f'{indent}Type Information:')
    console.printout(f'{indent}    Datatype: {domain_obj.content.type_information.datatype}')
    length = int(domain_obj.content.type_information.length) if domain_obj.content.type_information.length else 0
    console.printout(f'{indent}    Length: {length}')

    # Output Information
    console.printout(f'{indent}Output Information:')
    out_length = int(domain_obj.content.output_information.length) if domain_obj.content.output_information.length else 0
    console.printout(f'{indent}    Length: {out_length}')

    # Value Information
    console.printout(f'{indent}Value Information:')
    if domain_obj.content.value_information.value_table_ref and domain_obj.content.value_information.value_table_ref.name:
        console.printout(f'{indent}    Table Reference: {domain_obj.content.value_information.value_table_ref.name}')

    if domain_obj.content.value_information.fix_values:
        console.printout(f'{indent}    Fix Values:')
        for fix_value in domain_obj.content.value_information.fix_values:
            console.printout(f'{indent}        - {fix_value.low}: {fix_value.text}')


def format_domain_abap(domain_obj):
    """Format domain information in ABAP-compatible JSON structure

    Args:
        domain_obj: sap.adt.Domain instance with fetched content

    Returns:
        dict: Formatted domain data ready for json.dumps()
    """
    output = {
        'formatVersion': '1',
        'header': {
            'description': domain_obj.description or '',
            'originalLanguage': domain_obj.coredata.master_language.lower() if domain_obj.coredata.master_language else ''
        },
        'format': {
            'dataType': domain_obj.content.type_information.datatype or '',
            'length': int(domain_obj.content.type_information.length) if domain_obj.content.type_information.length else 0
        },
        'outputCharacteristics': {
            'length': int(domain_obj.content.output_information.length) if domain_obj.content.output_information.length else 0
        }
    }

    # Add fixed values if they exist
    if domain_obj.content.value_information.fix_values:
        output['fixedValues'] = []
        for fix_value in domain_obj.content.value_information.fix_values:
            output['fixedValues'].append({
                'fixedValue': fix_value.low or '',
                'description': fix_value.text or ''
            })

    return output
