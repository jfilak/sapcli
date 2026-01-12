"""gCTS log messages normalization utilities"""

import json


def _try_parse_json(value):
    """Try to parse a string as JSON, return original value if not JSON"""

    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped or (not stripped.startswith('{') and not stripped.startswith('[')):
        return value

    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value


def _normalize_protocol_item(item):
    """Normalize a protocol item which may be a nested JSON string"""

    return _try_parse_json(item)


def _normalize_client_section(section):
    """Normalize a client section (Parameters, Client Log, etc.)

    The section has 'type' and optionally 'protocol' keys.
    Protocol items may contain nested JSON strings.
    """

    normalized = {'type': section.get('type', '')}

    if 'protocol' in section:
        protocol = section['protocol']
        if isinstance(protocol, list):
            normalized['protocol'] = [_normalize_protocol_item(item) for item in protocol]
        else:
            normalized['protocol'] = _normalize_protocol_item(protocol)

    return normalized


def _normalize_appl_info_array(appl_info_list):
    """Normalize applInfo when it's parsed as a list (Client application format)"""

    return [_normalize_client_section(section) for section in appl_info_list]


def _normalize_appl_info_object(appl_info_obj):
    """Normalize applInfo when it's parsed as an object (Transport Tools format)"""

    # The object may contain stdout as array of line objects, etc.
    # Return as-is since it's already parsed
    return appl_info_obj


def normalize_appl_info(appl_info):
    """Normalize the applInfo field which can be:
    - A JSON array string (Client application log)
    - A JSON object string (Transport Tools log)
    - A plain string (simple info message)

    Returns the normalized data structure.
    """

    if appl_info is None:
        return None

    parsed = _try_parse_json(appl_info)

    if isinstance(parsed, list):
        return _normalize_appl_info_array(parsed)

    if isinstance(parsed, dict):
        return _normalize_appl_info_object(parsed)

    # Plain string, return as-is
    return parsed


def normalize_process_message(message):
    """Normalize a single process message entry

    Args:
        message: A dict containing process message data with potentially
                 nested JSON in the 'applInfo' field

    Returns:
        A new dict with normalized applInfo
    """

    if not isinstance(message, dict):
        return message

    result = dict(message)

    if 'applInfo' in result:
        result['applInfo'] = normalize_appl_info(result['applInfo'])

    return result


def normalize_process_messages(messages):
    """Normalize a list of process messages

    Args:
        messages: List of process message dictionaries

    Returns:
        List of normalized message dictionaries
    """

    if not isinstance(messages, list):
        return messages

    return [normalize_process_message(msg) for msg in messages]


def _is_empty_line(line):
    """Check if a line is considered empty"""

    if line is None:
        return True

    if isinstance(line, str):
        return not line.strip()

    if isinstance(line, dict):
        # Empty dict or dict with only empty 'line' value
        if not line:
            return True
        line_val = line.get('line', '')
        return not line_val or not str(line_val).strip()

    if isinstance(line, list):
        return len(line) == 0 or line == ['[]']

    return False


def _clean_line_text(text):
    """Clean up line text by removing surrounding quotes"""

    if not text:
        return text

    # Remove single quotes from the text
    return text.replace("'", "")


def _extract_line_text(line):
    """Extract text from a line object"""

    if isinstance(line, str):
        return _clean_line_text(line)

    if isinstance(line, dict):
        return _clean_line_text(line.get('line', ''))

    return _clean_line_text(str(line)) if line else ''


def extract_client_sections(appl_info):
    """Extract sections from Client application applInfo (array format)

    Args:
        appl_info: Normalized applInfo (list of section dicts)

    Returns:
        List of tuples (section_type, content_lines) where content_lines
        is a list of non-empty strings
    """

    if not isinstance(appl_info, list):
        return []

    sections = []
    for section in appl_info:
        section_type = section.get('type', '')
        protocol = section.get('protocol', [])

        content_lines = []
        if isinstance(protocol, list):
            for item in protocol:
                if isinstance(item, dict) and 'line' not in item:
                    # Nested JSON object (like Parameters) - extract key: value pairs
                    for key, value in item.items():
                        content_lines.append(f'{key}: {value}')
                elif not _is_empty_line(item):
                    text = _extract_line_text(item)
                    if text:
                        content_lines.append(text)
        elif protocol and not _is_empty_line(protocol):
            text = _extract_line_text(protocol)
            if text:
                content_lines.append(text)

        sections.append((section_type, content_lines))

    return sections


def extract_transport_tools_lines(appl_info):
    """Extract stdout lines from Transport Tools applInfo (object format)

    Args:
        appl_info: Normalized applInfo (dict with stdout key)

    Returns:
        List of non-empty stdout line strings
    """

    if not isinstance(appl_info, dict):
        return []

    stdout = appl_info.get('stdout', [])
    if not isinstance(stdout, list):
        return []

    lines = []
    for item in stdout:
        if not _is_empty_line(item):
            text = _extract_line_text(item)
            if text:
                lines.append(text)

    return lines
