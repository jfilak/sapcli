"""JSON serialization for Message Class objects (ABAP File Formats)"""


def to_json(message_class):
    """Convert a message class object to JSON-compatible dict.

    Args:
        message_class: object with .description, .master_language, .messages attributes

    Returns:
        dict matching ABAP File Formats for message classes
    """
    messages = []
    for msg in message_class.messages:
        messages.append({
            'number': msg.msgno,
            'text': msg.msgtext,
            'selfexplanatory': msg.selfexplainatory == 'true',
        })

    return {
        'formatVersion': '1',
        'header': {
            'description': message_class.description or '',
            'originalLanguage': (message_class.master_language or '').lower(),
        },
        'messages': messages,
    }


def from_json(data):
    """Parse JSON data and return list of message dicts.

    Args:
        data: dict with 'messages' key

    Returns:
        list of message dicts with 'number', 'text', 'selfexplanatory' keys
    """
    return data.get('messages', [])
