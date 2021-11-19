from mock import Response

GCTS_RESPONSE_REPO_NOT_EXISTS = Response.with_json(
    status_code=500,
    json={
        'exception': 'No relation between system and repository'
    }
)
