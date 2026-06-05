from mock import Response
import json

GCTS_RESPONSE_REPO_NOT_EXISTS = Response.with_json(
    status_code=500,
    json={
        'exception': 'No relation between system and repository'
    }
)

GCTS_RESPONSE_REPO_PULL_OK = Response.with_json(
    status_code=200,
    json={
        'fromCommit': '123',
        'toCommit': '456',
        'history': {
            'fromCommit': '123',
            'toCommit': '456',
            'type': 'PULL'
        }
    }
)

CLONE_ERROR_PROCESS_MESSAGES_RAW = [
    {
        "rid": "empty",
        "process": "9617D6AFE539F5AF388E74AA8EE92196",
        "action": "FINISH_JOB",
        "application": "gCTS",
        "applInfo": "Job GCTS_CLONE_REPO finished but the action failed",
        "time": 20260604164323,
        "severity": "ERROR"
    },
    {
        "rid": "empty",
        "process": "9617D6AFE539F5AF388E74AA8EE92196",
        "action": "GET_SOURCE_FROM_REMOTE",
        "application": "Client",
        "applId": "20260604_164320_D6F0271C6C4FD654B12F582B73ACD049",
        "applInfo": json.dumps([
            {
                "type": "Parameters",
                "protocol": [
                    json.dumps({
                        "repouri": "https://github.com/example/empty",
                        "logfile": "/usr/sap/A4H/DVEBMGS00/gcts/empty/log/20260604_164320_D6F0271C6C4FD654B12F582B73ACD049.log",
                        "repodir": "/usr/sap/A4H/DVEBMGS00/gcts/empty/data/",
                        "remoteplatform": "GITHUB",
                        "loglevel": "INFORMATION",
                        "command": "clone"
                    })
                ]
            },
            {
                "type": "Client Log",
                "protocol": [
                    "4 ETW000 ",
                    "4 ETW000 ABAP to VCS - version 7.77.7 from 2026-04-22 14:53:52"
                ]
            },
            {
                "type": "Client Response",
                "protocol": [
                    json.dumps({
                        "log": [
                            {"code": "GCTS.CLIENT.1400", "type": "ERROR", "message": "Cloning a repository into a new working directory failed: https://github.com/example/empty: Authentication is required but no CredentialsProvider has been registered", "step": "CLONE"}
                        ]
                    })
                ]
            },
            {
                "type": "Client Stack Log",
                "protocol": [
                    "[]"
                ]
            }
        ]),
        "time": 20260604164322,
        "severity": "ERROR"
    },
    {
        "rid": "empty",
        "process": "9617D6AFE539F5AF388E74AA8EE92196",
        "action": "GET_SOURCE_FROM_REMOTE",
        "application": "Transport Tools",
        "applInfo": json.dumps({
            "returnCode": "0008",
            "cmdLine": "SAPVCSCALL 6IT client100 pf=/usr/sap/trans/bin/TP_DOMAIN_A4H.PFL",
            "stdout": [
                {"line": "This is tp version 381.742.08 (release 920) (Patch level:4)"},
                {},
                {"line": "standard output from tp and from tools called by tp:"},
                {},
                {},
                {"line": "ABAP to VCS (c) - SAP SE 2026 - Version 7.77.7 from 2026-04-22 14:53:52"},
                {},
                {"line": "Finished after 863 ms with RC 8"},
                {"line": "tp call duration was: 1.000840 sec"}
            ],
            "system": "6IT",
            "alog": "ALOG2623.6IT",
            "slog": "SLOG2623.6IT"
        }),
        "time": 20260604164322,
        "severity": "ERROR"
    },
    {
        "rid": "empty",
        "process": "9617D6AFE539F5AF388E74AA8EE92196",
        "action": "CLONE",
        "application": "gCTS",
        "applInfo": "Error when cloning repository.",
        "time": 20260604164322,
        "severity": "ERROR"
    },
    {
        "rid": "empty",
        "process": "9617D6AFE539F5AF388E74AA8EE92196",
        "action": "EXECUTE_JOB",
        "application": "gCTS",
        "applInfo": "Execution of job GCTS_CLONE_REPO started",
        "time": 20260604164320,
        "severity": "RUNNING"
    },
    {
        "rid": "empty",
        "process": "9617D6AFE539F5AF388E74AA8EE92196",
        "action": "LOG_LEVEL",
        "application": "gCTS",
        "applInfo": "Log level is INFO",
        "time": 20260604164319,
        "severity": "INFO"
    },
    {
        "rid": "empty",
        "process": "9617D6AFE539F5AF388E74AA8EE92196",
        "action": "SCHEDULE_JOB",
        "application": "gCTS",
        "applInfo": "Job GCTS_CLONE_REPO was scheduled for immediate execution",
        "time": 20260604164319,
        "severity": "SCHEDULED"
    }
]

CLONE_ERROR_PROCESS_MESSAGES_RESPONSE = {"list": CLONE_ERROR_PROCESS_MESSAGES_RAW}

CLONE_SUCCESS_PROCESS_MESSAGES_RAW = [
    {
        "rid":"empty",
        "process":"BAB8226D9C475D7EA930018B2BC956E2",
        "action":"FINISH_JOB",
        "application":"gCTS",
        "applInfo":"Job GCTS_CLONE_REPO finished",
        "time":20260605093707,
        "severity":"FINISHED"
    },
    {
        "rid":"empty",
        "process":"BAB8226D9C475D7EA930018B2BC956E2",
        "action":"GET_CURRENT_COMMIT",
        "application":"Client",
        "applId":"20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A",
        "applInfo":"[{\"type\":\"Parameters\",\"protocol\":[\"{\\\"repodir\\\":\\\"/usr/sap/A4H/DVEBMGS00/gcts/empty/data/\\\",\\\"logfile\\\":\\\"/usr/sap/A4H/DVEBMGS00/gcts/empty/log/20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A.log\\\",\\\"loglevel\\\":\\\"INFORMATION\\\",\\\"remoteplatform\\\":\\\"GITHUB\\\",\\\"apploglevel\\\":\\\"INFORMATION\\\",\\\"command\\\":\\\"getcurrentcommit\\\"}\"]},{\"type\":\"Client Log\",\"protocol\":[\"4 ETW000 \",\"4 ETW000 ABAP to VCS - version 7.77.7 from 2026-04-22 14:53:52\",\"4 ETW000 ==============================================================================================================================================\",\"4 ETW000 \",\"4 ETW000 Date & time: 05.06.2026 - 09:37:06\",\"4 ETW000 \",\"4 ETW000 The application was called with the following Attributes: \",\"4 ETW000 \",\"4 ETW000 - Command                                              : \",\"4 ETW000   - Mandatory                                          : yes\",\"4 ETW000   - Origin                                             : command line\",\"4 ETW000   - Value                                              : getcurrentcommit\",\"4 ETW000 - Append log                                           : \",\"4 ETW000   - ID/name                                            : appendlog\",\"4 ETW000   - Mandatory                                          : no\",\"4 ETW000   - Origin                                             : default value\",\"4 ETW000   - Value                                              : false\",\"4 ETW000 - Directory and file for storing the log               : \",\"4 ETW000   - ID/name                                            : logfile\",\"4 ETW000   - Mandatory                                          : no\",\"4 ETW000   - Origin                                             : request file\",\"4 ETW000   - Value                                              : /usr/sap/A4H/DVEBMGS00/gcts/empty/log/20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A.log\",\"4 ETW000 - Directory for storing the response                   : \",\"4 ETW000   - ID/name                                            : responsedir\",\"4 ETW000   - Mandatory                                          : yes\",\"4 ETW000   - Origin                                             : command line\",\"4 ETW000   - Value                                              : /usr/sap/A4H/DVEBMGS00/gcts/empty/response/\",\"4 ETW000 - Identifier for the 'request'-file (-> 'command'-file): \",\"4 ETW000   - ID/name                                            : requestid\",\"4 ETW000   - Mandatory                                          : yes\",\"4 ETW000   - Origin                                             : command line\",\"4 ETW000   - Value                                              : 20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A\",\"4 ETW000 - Log level 'application'                              : \",\"4 ETW000   - ID/name                                            : apploglevel\",\"4 ETW000   - Mandatory                                          : no\",\"4 ETW000   - Origin                                             : request file\",\"4 ETW000   - Value                                              : information\",\"4 ETW000 - Log level 'response'-file                            : \",\"4 ETW000   - ID/name                                            : loglevel\",\"4 ETW000   - Mandatory                                          : no\",\"4 ETW000   - Origin                                             : request file\",\"4 ETW000   - Value                                              : information\",\"4 ETW000 - Log to 'StdOut'                                      : \",\"4 ETW000   - ID/name                                            : stdoutlog\",\"4 ETW000   - Mandatory                                          : no\",\"4 ETW000   - Origin                                             : default value\",\"4 ETW000   - Value                                              : false\",\"4 ETW000 - Repository of the version control system             : \",\"4 ETW000   - ID/name                                            : repodir\",\"4 ETW000   - Mandatory                                          : yes\",\"4 ETW000   - Origin                                             : request file\",\"4 ETW000   - Value                                              : /usr/sap/A4H/DVEBMGS00/gcts/empty/data/\",\"4 ETW000 \",\"4 ETW000 Java-environment, operating system & working directory :\",\"4 ETW000 \",\"4 ETW000 - Java vendor                                          : SAP SE\",\"4 ETW000 - Java name                                            : OpenJDK 64-Bit Server VM\",\"4 ETW000 - Java version                                         : 17.0.9+0-LTS\",\"4 ETW000 - Java home                                            : /opt/sap/sapmachine-jdk-17.0.9\",\"4 ETW000 - Operating system name                                : Linux\",\"4 ETW000 - Operating system version                             : 6.4.0-150600.23.60-default\",\"4 ETW000 - Operating system patch level                         : unknown\",\"4 ETW000 - Operating system architecture                        : amd64\",\"4 ETW000 - Working directory (pwd)                              : /sapdata/usr/sap/A4H/DVEBMGS00/work/.\",\"4 ETW000 \",\"4 ETW000 Starting getting the current commit\",\"4 ETW000 \",\"4 ETW000 Repository of type 'git' instantiated\",\"4 ETW000 \",\"4 ETW000 Starting jgit specific getting current commit\",\"4 ETW000 \",\"4 ETW000 Getting the commit the 'HEAD' currently points to ...\",\"4 ETW000 \",\"4 ETW000 Performing 'log': showing commit logs ...\",\"4 ETW000 \",\"4 ETW000 - All                                                : false\",\"4 ETW000 - Limit the number of commits to output              : 1\",\"4 ETW000 \",\"4 ETW000 Showing commit logs took 7 ms\",\"4 ETW000 \",\"4 ETW000 Getting the commit the 'HEAD' currently points to took 8 ms\",\"4 ETW000 \",\"4WETW000 The commit the 'HEAD' currently points could not be found\",\"4 ETW000 \",\"4 ETW000 Overall process time: 71 ms\",\"4 ETW000 \",\"4 ETW000 Getting the current commit took 71 ms.\",\"4 ETW000 \",\"4 ETW000 End of transport: 0004\",\"4 ETW000 Date & time     : 05.06.2026 - 09:37:06\",\"4 ETW000 Creating the [requestID].response-file '20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A.response'\",\"4 ETW000 \",\"4 ETW000 The [requestID].response-file contains the following sections:\",\"4 ETW000 \",\"4 ETW000  - 'applicationAttributes'\",\"4 ETW000 \",\"4 ETW000    - 'name': 'ABAP to VCS (c) - SAP SE 2026'\",\"4 ETW000    - 'technicalName': 'abap2vcs.jar'\",\"4 ETW000    - 'description': 'Bring ABAP transportable objects to version control systems (VCS) like Git using the ABAP transport mechanism'\",\"4 ETW000    - ...\",\"4 ETW000 \",\"4 ETW000  - 'arguments'\",\"4 ETW000 \",\"4 ETW000    - 'optionId': 'command'\",\"4 ETW000    - 'optionValue': 'getcurrentcommit'\",\"4 ETW000    - 'optionOrigin': 'command line'\",\"4 ETW000    - ...\",\"4 ETW000 \",\"4 ETW000    - +8 further argument(s)\",\"4 ETW000 \",\"4 ETW000  - 'closeResult'\",\"4 ETW000 \",\"4 ETW000    - 'directory': '/sapdata/usr/sap/A4H/DVEBMGS00/gcts/empty/data/.git'\",\"4 ETW000    - 'isBare': 'false'\",\"4 ETW000    - 'hasDetachedHead': 'false'\",\"4 ETW000    - ...\",\"4 ETW000 \",\"4 ETW000  - 'log'\",\"4 ETW000 \",\"4 ETW000    - 'code': 'GCTS.CLIENT.927'\",\"4 ETW000    - 'type': 'WARNING'\",\"4 ETW000    - 'message': 'The commit the 'HEAD' currently points could not be found'\",\"4 ETW000    - ...\",\"4 ETW000 \",\"4 ETW000  - 'openResult'\",\"4 ETW000 \",\"4 ETW000    - 'directory': '/sapdata/usr/sap/A4H/DVEBMGS00/gcts/empty/data/.git'\",\"4 ETW000    - 'isBare': 'false'\",\"4 ETW000    - 'hasDetachedHead': 'false'\",\"4 ETW000    - ...\",\"4 ETW000 \",\"4 ETW000 The [requestID].response-file '20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A.response' has been created in the directory '/usr/sap/A4H/DVEBMGS00/gcts/empty/response/'\",\"4 ETW000 \"]},{\"type\":\"Client Response\",\"protocol\":[\"{\\\"applicationAttributes\\\":{\\\"name\\\":\\\"ABAP to VCS (c) - SAP SE 2026\\\",\\\"technicalName\\\":\\\"abap2vcs.jar\\\",\\\"description\\\":\\\"Bring ABAP transportable objects to version control systems (VCS) like Git using the ABAP transport mechanism\\\",\\\"version\\\":\\\"7.77.7 from 2026-04-22 14:53:52\\\",\\\"dateAndTime\\\":\\\"05.06.2026 - 09:37:06\\\"},\\\"arguments\\\":[{\\\"optionId\\\":\\\"command\\\",\\\"optionValue\\\":\\\"getcurrentcommit\\\",\\\"optionOrigin\\\":\\\"command line\\\"},{\\\"optionId\\\":\\\"apploglevel\\\",\\\"optionValue\\\":\\\"INFORMATION\\\",\\\"optionOrigin\\\":\\\"request file\\\"},{\\\"optionId\\\":\\\"logfile\\\",\\\"optionValue\\\":\\\"/usr/sap/A4H/DVEBMGS00/gcts/empty/log/20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A.log\\\",\\\"optionOrigin\\\":\\\"request file\\\"},{\\\"optionId\\\":\\\"loglevel\\\",\\\"optionValue\\\":\\\"INFORMATION\\\",\\\"optionOrigin\\\":\\\"request file\\\"},{\\\"optionId\\\":\\\"remoteplatform\\\",\\\"optionValue\\\":\\\"GITHUB\\\",\\\"optionOrigin\\\":\\\"request file\\\"},{\\\"optionId\\\":\\\"repodir\\\",\\\"optionValue\\\":\\\"/usr/sap/A4H/DVEBMGS00/gcts/empty/data/\\\",\\\"optionOrigin\\\":\\\"request file\\\"},{\\\"optionId\\\":\\\"requestid\\\",\\\"optionValue\\\":\\\"20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A\\\",\\\"optionOrigin\\\":\\\"command line\\\"},{\\\"optionId\\\":\\\"responsedir\\\",\\\"optionValue\\\":\\\"/usr/sap/A4H/DVEBMGS00/gcts/empty/response/\\\",\\\"optionOrigin\\\":\\\"command line\\\"},{\\\"optionId\\\":\\\"token\\\",\\\"optionOrigin\\\":\\\"standard input stream\\\"}],\\\"closeResult\\\":{\\\"directory\\\":\\\"/sapdata/usr/sap/A4H/DVEBMGS00/gcts/empty/data/.git\\\",\\\"isBare\\\":\\\"false\\\",\\\"hasDetachedHead\\\":\\\"false\\\",\\\"state\\\":{\\\"name\\\":\\\"SAFE\\\",\\\"description\\\":\\\"Normal\\\",\\\"canAmend\\\":\\\"true\\\",\\\"canCheckout\\\":\\\"true\\\",\\\"canCommit\\\":\\\"true\\\",\\\"canResetHead\\\":\\\"true\\\",\\\"isRebasing\\\":\\\"false\\\"},\\\"remoteNames\\\":[\\\"origin\\\"]},\\\"log\\\":[{\\\"code\\\":\\\"GCTS.CLIENT.927\\\",\\\"type\\\":\\\"WARNING\\\",\\\"message\\\":\\\"The commit the 'HEAD' currently points could not be found\\\",\\\"step\\\":\\\"GET.CURRENT.COMMIT\\\"}],\\\"openResult\\\":{\\\"directory\\\":\\\"/sapdata/usr/sap/A4H/DVEBMGS00/gcts/empty/data/.git\\\",\\\"isBare\\\":\\\"false\\\",\\\"hasDetachedHead\\\":\\\"false\\\",\\\"state\\\":{\\\"name\\\":\\\"SAFE\\\",\\\"description\\\":\\\"Normal\\\",\\\"canAmend\\\":\\\"true\\\",\\\"canCheckout\\\":\\\"true\\\",\\\"canCommit\\\":\\\"true\\\",\\\"canResetHead\\\":\\\"true\\\",\\\"isRebasing\\\":\\\"false\\\"},\\\"remoteNames\\\":[\\\"origin\\\"]}}\"]},{\"type\":\"Client Stack Log\",\"protocol\":[\"[{\\\"code\\\":\\\"GCTS.CLIENT.927\\\",\\\"type\\\":\\\"WARNING\\\",\\\"step\\\":\\\"GET.CURRENT.COMMIT\\\",\\\"message\\\":\\\"The commit the 'HEAD' currently points could not be found\\\"}]\"]}]",
        "time":20260605093706,
        "severity":"WARNING"
    },
    {
        "rid":"empty",
        "process":"BAB8226D9C475D7EA930018B2BC956E2",
        "action":"GET_CURRENT_COMMIT",
        "application":"Transport Tools",
        "applInfo":"{\"returnCode\":\"0004\",\"cmdLine\":\"SAPVCSCALL 6IT client100 pf=/usr/sap/trans/bin/TP_DOMAIN_A4H.PFL -DSYSTEM_PF=/usr/sap/A4H/SYS/profile/A4H_DVEBMGS00_myabap -DSAPINSTANCENAME=A4H_ddci SAPVCSPARAMS=-requestid 20260605_093706_9D19B3BFADEB71B07B06AF09E7730D7A SAPVCSPARAMS=-responsedir /usr/\",\"stdout\":[{\"line\":\"This is tp version 381.742.08 (release 920) (Patch level:4)\"},{},{\"line\":\"standard output from tp and from tools called by tp:\"},{},{},{\"line\":\"ABAP to VCS (c) - SAP SE 2026 - Version 7.77.7 from 2026-04-22 14:53:52\"},{},{\"line\":\"Finished after 494 ms with RC 4\"},{\"line\":\"tp call duration was: 0.634787 sec\"}],\"system\":\"6IT\",\"alog\":\"ALOG2623.6IT\",\"slog\":\"SLOG2623.6IT\"}","time":20260605093706,"severity":"WARNING"
    },
    {
        "rid":"empty",
        "process":"BAB8226D9C475D7EA930018B2BC956E2",
        "action":"EXECUTE_JOB",
        "application":"gCTS",
        "applInfo":"Execution of job GCTS_CLONE_REPO started",
        "time":20260605093704,
        "severity":"RUNNING"
    },
    {
        "rid":"empty",
        "process":"BAB8226D9C475D7EA930018B2BC956E2",
        "action":"LOG_LEVEL",
        "application":"gCTS",
        "applInfo":"Log level is INFO",
        "time":20260605093703,
        "severity":"INFO"
    },
    {
        "rid":"empty",
        "process":"BAB8226D9C475D7EA930018B2BC956E2",
        "action":"SCHEDULE_JOB",
        "application":"gCTS",
        "applInfo":"Job GCTS_CLONE_REPO was scheduled for immediate execution",
        "time":20260605093703,"severity":"SCHEDULED"
    }
]

CLONE_SUCCESS_PROCESS_MESSAGES_RESPONSE = {
    "list": CLONE_SUCCESS_PROCESS_MESSAGES_RAW
}
