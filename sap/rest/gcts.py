"""gCTS REST calls"""


def simple_fetch_repos(connection):
    return connection.get_json('repository')['result']


def simple_clone(connection, url, name, vsid='6IT', start_dir='src', vcs_token=None):
    repo_data = {
        'repository': name,
        'data': {
            'rid': name,
            'name': name,
            'role': 'SOURCE',
            'type': 'GITHUB',
            'vsid': vsid,
            'url': url,
            'connection': 'ssl'
        }
    }

    connection.post_obj_as_json('repository', repo_data)

    if start_dir:
        connection.post_obj_as_json(f'repository/{name}/config', {'key': 'VCS_TARGET_DIR', 'value': start_dir})

    if vcs_token:
        connection.post_obj_as_json(f'repository/{name}/config', {'key': 'CLIENT_VCS_AUTH_TOKEN', 'value': vcs_token})

    return connection.execute('POST', f'repository/{name}/clone')


def simple_checkout(connection, name, branch):
    response = connection.get_json(f'repository/{name}')
    repo = response['result']
    url = f'repository/{repo["rid"]}/branches/{repo["branch"]}/switch'
    return connection.execute('GET', url, params={'branch': branch})


def simple_delete(connection, name):
    return connection.execute('DELETE', f'repository/{name}')
