from mock import Response

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
