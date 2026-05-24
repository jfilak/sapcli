#!/usr/bin/env python3

import unittest

from sap.platform.abap.fileformats.messageclass import to_json, from_json


class TestMessageClassJSON(unittest.TestCase):

    def test_to_json(self):
        class MockMessage:
            def __init__(self, msgno, msgtext, selfexplainatory):
                self.msgno = msgno
                self.msgtext = msgtext
                self.selfexplainatory = selfexplainatory

        class MockMessageClass:
            def __init__(self):
                self.description = 'Example message class'
                self.master_language = 'EN'
                self.messages = [
                    MockMessage('001', 'My first message', 'true'),
                    MockMessage('002', 'My second message', 'false'),
                ]

        result = to_json(MockMessageClass())

        self.assertEqual(result['formatVersion'], '1')
        self.assertEqual(result['header']['description'], 'Example message class')
        self.assertEqual(result['header']['originalLanguage'], 'en')
        self.assertEqual(len(result['messages']), 2)
        self.assertEqual(result['messages'][0]['number'], '001')
        self.assertEqual(result['messages'][0]['text'], 'My first message')
        self.assertEqual(result['messages'][0]['selfexplanatory'], True)
        self.assertEqual(result['messages'][1]['selfexplanatory'], False)

    def test_to_json_special_characters(self):
        """XML entity decoded characters should appear as-is in JSON"""

        class MockMessage:
            def __init__(self, msgno, msgtext, selfexplainatory):
                self.msgno = msgno
                self.msgtext = msgtext
                self.selfexplainatory = selfexplainatory

        class MockMessageClass:
            def __init__(self):
                self.description = 'Test & messages'
                self.master_language = 'EN'
                self.messages = [
                    MockMessage('000', '&', 'true'),
                ]

        result = to_json(MockMessageClass())
        self.assertEqual(result['messages'][0]['text'], '&')

    def test_from_json(self):
        data = {
            'formatVersion': '1',
            'header': {
                'description': 'Example',
                'originalLanguage': 'en'
            },
            'messages': [
                {'number': '001', 'text': 'Hello', 'selfexplanatory': True},
                {'number': '002', 'text': 'World', 'selfexplanatory': False},
            ]
        }

        result = from_json(data)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['number'], '001')
        self.assertEqual(result[0]['text'], 'Hello')
        self.assertEqual(result[0]['selfexplanatory'], True)


if __name__ == '__main__':
    unittest.main()
