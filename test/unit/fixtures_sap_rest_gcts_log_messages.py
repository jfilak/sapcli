GCTS_LOG_MESSAGES_DATA = [
    {'rid': 'the_repo', 'process': 'CCC', 'processName': 'SWITCH_BRANCH', 'caller': 'DEVELOPER', 'time': 20260112134732, 'status': 'ERROR'},
    {'rid': 'the_repo', 'process': 'BBB', 'processName': 'PULL_BY_COMMIT', 'caller': 'DEVELOPER', 'time': 20251217133049, 'status': 'WARNING'},
    {'rid': 'the_repo', 'process': 'AAA', 'processName': 'CLONE', 'caller': 'DEVELOPER', 'time': 20260112104031, 'status': 'INFO'},
]

GCTS_LOG_MESSAGES_JSON_EXP = [
    {'rid': 'the_repo', 'processName': 'SWITCH_BRANCH', 'caller': 'DEVELOPER', 'time': 20260112134732, 'status': 'ERROR', 'processId': 'CCC'},
    {'rid': 'the_repo', 'processName': 'PULL_BY_COMMIT', 'caller': 'DEVELOPER', 'time': 20251217133049, 'status': 'WARNING', 'processId': 'BBB'},
    {'rid': 'the_repo', 'processName': 'CLONE', 'caller': 'DEVELOPER', 'time': 20260112104031, 'status': 'INFO', 'processId': 'AAA'},
]

GCTS_LOG_MESSAGES_PROCESS_CCC_DATA = [
    {'rid': 'the_repo', 'process': 'CCC', 'action': 'COMPARE_BRANCH', 'application': 'Client', 'applId': '20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08',
     'applInfo': '[{"type":"Parameters","protocol":["{\\"repodir\\":\\"/usr/sap/A4H/D00/gcts/the_repo/data/\\",\\"logfile\\":\\"/usr/sap/A4H/D00/gcts/the_repo/log/20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08.log\\",\\"loglevel\\":\\"INFORMATION\\",\\"remoteplatform\\":\\"GITHUB\\",\\"apploglevel\\":\\"INFORMATION\\",\\"command\\":\\"getdifferences\\",\\"tobranch\\":\\"foo\\"}"]},{"type":"Client Log","protocol":["client log line"]},'
         + '{"type":"Client Response","protocol":["'
         +    '{\\"log\\":['
         +        '{\\"code\\":\\"GCTS.CLIENT.500\\",\\"type\\":\\"INFO\\",\\"message\\":\\"Non Empty line 1\\",\\"step\\":\\"LOG.COMMIT.DATA\\"},'
         +        '{\\"code\\":\\"GCTS.CLIENT.500\\",\\"type\\":\\"INFO\\",\\"message\\":\\"\\",\\"step\\":\\"LOG.COMMIT.DATA\\"},'
         +        '{\\"code\\":\\"GCTS.CLIENT.500\\",\\"type\\":\\"INFO\\",\\"message\\":\\"Non Empty line 2\\",\\"step\\":\\"LOG.COMMIT.DATA\\"}'
         +   ']}'
         + '"]},'
         + '{"type":"Client Stack Log","protocol":["[]"]}]',
     'time': 20260112134733,
     'severity': 'ERROR'},

    {'rid': 'the_repo', 'process': 'CCC', 'action': 'COMPARE_BRANCH', 'application': 'Transport Tools',
     'applInfo': '{"returnCode":"0236","cmdLine":"SAPVCSCALL 6IT client100 pf=/usr/sap/trans/bin/TP_DOMAIN_A4H.PFL -DSYSTEM_PF=/usr/sap/A4H/SYS/profile/A4H_D00_saphost -DSAPINSTANCENAME=A4H_ddci SAPVCSPARAMS=-requestid 20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08 SAPVCSPARAMS=-responsedir /usr/sap/C5","stdout":[{"line":"This is tp version 381.724.83 (release 919) (Patch level:0)"},{},{"line":"standard output from tp and from tools called by tp:"},{},{},{"line":"ABAP to VCS (c) - SAP SE 2025 - Version 1.29.0-20251105155931_5a33982436600ed77b8f1c860670bfcb2cd503be from 2025-11-05 16:06:04"},{},{"line":"Error: \'The specified directory \'/usr/sap/A4H/D00/gcts/the_repo/data/\' is not a working directory of a version control"},{"line":" system\'"},{},{"line":"tp returncode summary:"},{},{"line":"TOOLS: Highest return code of single steps was: 12"},{"line":"ERRORS: Highest tp internal error was: 0236"},{"line":"tp call duration was: 0.352889 sec"}],"system":"6IT","alog":"ALOG2603.6IT","slog":"SLOG2603.6IT"}',
     'time': 20260112134733,
     'severity': 'ERROR'},

    {'rid': 'the_repo', 'process': 'CCC', 'action': 'LOG_LEVEL', 'application': 'gCTS',
     'applInfo': 'Log level is INFO',
     'time': 20260112134732,
     'severity': 'INFO'}
]

GCTS_LOG_MESSAGES_PROCESS_CCC_JSON_EXP = [
    # Client application info (processed)
    {
        'rid': 'the_repo',
        'process': 'CCC',
        'action': 'COMPARE_BRANCH',
        'application': 'Client',
        'applId': '20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08',
        'applInfo': [
            {
                "type": "Parameters",
                "protocol": {
                    "repodir": "/usr/sap/A4H/D00/gcts/the_repo/data/",
                    "logfile": "/usr/sap/A4H/D00/gcts/the_repo/log/20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08.log",
                    "loglevel": "INFORMATION",
                    "remoteplatform": "GITHUB",
                    "apploglevel": "INFORMATION",
                    "command": "getdifferences",
                    "tobranch": "foo"
                }
            },
            {
                "type": "Client Log",
                "protocol": ["client log line"]
            },
            {
                "type": "Client Response",
                "protocol": {
                    "log": [
                        {"code": "GCTS.CLIENT.500", "type": "INFO", "message": "Non Empty line 1", "step": "LOG.COMMIT.DATA"},
                        {"code": "GCTS.CLIENT.500", "type": "INFO", "message": "", "step": "LOG.COMMIT.DATA"},
                        {"code": "GCTS.CLIENT.500", "type": "INFO", "message": "Non Empty line 2", "step": "LOG.COMMIT.DATA"}
                    ]
                }
            },
            {
                "type": "Client Stack Log",
                "protocol": []
            }
        ],
        "time": 20260112134733,
        "severity": "ERROR"
    },
    # Transport Tools application info (processed - stdout items replaced with line values)
    {
        'rid': 'the_repo',
        'process': 'CCC',
        'action': 'COMPARE_BRANCH',
        'application': 'Transport Tools',
        'applInfo': {
            "returnCode": "0236",
            "cmdLine": "SAPVCSCALL 6IT client100 pf=/usr/sap/trans/bin/TP_DOMAIN_A4H.PFL -DSYSTEM_PF=/usr/sap/A4H/SYS/profile/A4H_D00_saphost -DSAPINSTANCENAME=A4H_ddci SAPVCSPARAMS=-requestid 20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08 SAPVCSPARAMS=-responsedir /usr/sap/C5",
            "stdout":[
                "This is tp version 381.724.83 (release 919) (Patch level:0)",
                "",
                "standard output from tp and from tools called by tp:",
                "",
                "",
                "ABAP to VCS (c) - SAP SE 2025 - Version 1.29.0-20251105155931_5a33982436600ed77b8f1c860670bfcb2cd503be from 2025-11-05 16:06:04",
                "",
                "Error: 'The specified directory '/usr/sap/A4H/D00/gcts/the_repo/data/' is not a working directory of a version control",
                " system'",
                "",
                "tp returncode summary:",
                "",
                "TOOLS: Highest return code of single steps was: 12",
                "ERRORS: Highest tp internal error was: 0236",
                "tp call duration was: 0.352889 sec",
            ],
            "system":"6IT",
            "alog":"ALOG2603.6IT",
            "slog":"SLOG2603.6IT"
        },
        'time': 20260112134733,
        'severity': 'ERROR'
    },
    # gCTS info
    {
        'rid': 'the_repo',
        'process': 'CCC',
        'action': 'LOG_LEVEL',
        'application': 'gCTS',
        'applInfo': 'Log level is INFO',
        'time': 20260112134732,
        'severity': 'INFO'
    }
]
