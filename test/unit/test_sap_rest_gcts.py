#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, call, patch, PropertyMock

from sap.rest.errors import HTTPRequestError, UnauthorizedError

import sap.rest.gcts
import sap.rest.gcts.remote_repo
import sap.rest.gcts.simple

from mock import Request, Response, RESTConnection, make_gcts_log_error
from mock import GCTSLogBuilder as LogBuilder


class TestgCTSUtils(unittest.TestCase):

    def test_parse_url_https_git(self):
        package = sap.rest.gcts.package_name_from_url('https://example.org/foo/community.sap.git')
        self.assertEqual(package, 'community.sap')

    def test_parse_url_https(self):
        package = sap.rest.gcts.package_name_from_url('https://example.org/foo/git.no.suffix')
        self.assertEqual(package, 'git.no.suffix')


class TestGCSTRequestError(unittest.TestCase):

    def test_str_and_repr(self):
        log_builder = LogBuilder()
        messages = log_builder.log_error(make_gcts_log_error('Exists')).log_exception('Message', 'EEXIST').get_contents()
        ex = sap.rest.gcts.errors.GCTSRequestError(messages)

        self.assertEqual(str(ex), 'gCTS exception: Message')
        self.assertEqual(repr(ex), 'gCTS exception: Message')


class TestGCTSExceptionFactory(unittest.TestCase):

    def test_not_json_response(self):
        req = Request(method='GET', adt_uri='/epic/success', headers=None, body=None, params=None)
        res = Response(status_code=401, text='Not JSON')

        orig_error = UnauthorizedError(req, res, 'foo')
        new_error = sap.rest.gcts.errors.exception_from_http_error(orig_error)

        self.assertEqual(new_error, orig_error)

    def test_repository_does_not_exist(self):
        messages = {'exception': 'No relation between system and repository'}
        req = Request(method='GET', adt_uri='/epic/success', headers=None, body=None, params=None)
        res = Response.with_json(status_code=500, json=messages)

        orig_error = HTTPRequestError(req, res)
        new_error = sap.rest.gcts.errors.exception_from_http_error(orig_error)

        expected_error = sap.rest.gcts.errors.GCTSRepoNotExistsError(messages)

        self.assertEqual(str(new_error), str(expected_error))


class GCTSTestSetUp:

    def setUp(self):
        self.repo_url = 'https://example.com/git/repo'
        self.repo_name = 'repo'
        self.repo_vsid = '6IT'
        self.repo_data = {
            'rid': self.repo_name,
            'name': self.repo_name,
            'role': 'SOURCE',
            'type': 'GITHUB',
            'vsid': '6IT',
            'url': self.repo_url,
            'connection': 'ssl',
        }

        self.repo_request ={
            'repository': self.repo_name,
            'data': {
                'rid': self.repo_name,
                'name': self.repo_name,
                'role': 'SOURCE',
                'type': 'GITHUB',
                'vsid': '6IT',
                'url': self.repo_url,
                'connection': 'ssl',
            }
        }

        self.repo_server_data = dict(self.repo_data)
        self.repo_server_data['branch'] = 'the_branch'
        self.repo_server_data['currentCommit'] = 'FEDCBA9876543210'
        self.repo_server_data['status'] = 'READY'
        self.repo_server_data['config'] = [
            {'key': 'VCS_CONNECTION', 'value': 'SSL', 'category': 'Connection'},
            {'key': 'CLIENT_VCS_URI', 'category': 'Repository'}
        ]

        self.conn = RESTConnection()


class TestGCTSRepostiroy(GCTSTestSetUp, unittest.TestCase):

    def test_wipe_data(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data={})
        repo.wipe_data()
        self.assertIsNone(repo._data)

    def test_ctor_no_data(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)
        self.assertEqual(repo._http.connection, self.conn)
        self.assertEqual(repo.name, self.repo_name)
        self.assertIsNone(repo._data)

    def test_ctor_with_data(self):
        data = {}

        repo = sap.rest.gcts.remote_repo.Repository(None, self.repo_name, data=data)

        self.assertIsNone(repo._http.connection)
        self.assertEqual(repo.name, self.repo_name)
        self.assertIsNotNone(repo._data)

    def test_properties_cached(self):
        repo = sap.rest.gcts.remote_repo.Repository(None, self.repo_name, data=self.repo_server_data)

        self.assertEqual(repo.status, self.repo_server_data['status'])
        self.assertEqual(repo.rid, self.repo_server_data['rid'])
        self.assertEqual(repo.url, self.repo_server_data['url'])
        self.assertEqual(repo.branch, self.repo_server_data['branch'])
        self.assertEqual(repo.configuration, {'VCS_CONNECTION': 'SSL', 'CLIENT_VCS_URI': ''})

    def test_properties_fetch(self):
        response = {'result': self.repo_server_data}

        self.conn.set_responses([Response.with_json(json=response, status_code=200)])

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)

        self.assertEqual(repo.status, self.repo_server_data['status'])
        self.assertEqual(repo.rid, self.repo_server_data['rid'])
        self.assertEqual(repo.url, self.repo_server_data['url'])
        self.assertEqual(repo.branch, self.repo_server_data['branch'])

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_name}'), self)

    def test_properties_fetch_error(self):
        messages = LogBuilder(exception='Get Repo Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            unused = repo.rid

        self.assertEqual(str(caught.exception), 'gCTS exception: Get Repo Error')

    def test_create_no_self_data_no_config(self):
        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': self.repo_server_data})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)
        repo.create(self.repo_url, self.repo_vsid)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository', body=self.repo_request, accept='application/json'),
                                       self, json_body=True)

    def test_create_with_config_instance_none(self):
        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': self.repo_server_data})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)
        repo.create(self.repo_url, self.repo_vsid, config={'THE_KEY': 'THE_VALUE'})

        repo_request = dict(self.repo_request)
        repo_request['data']['config'] = [{
            'key': 'THE_KEY', 'value': 'THE_VALUE'
        }]

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository', body=repo_request, accept='application/json'),
                                       self, json_body=True)

    def test_create_with_config_update_instance(self):
        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': self.repo_server_data})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data={
            'config': [
                {'key': 'first_key', 'value': 'first_value'},
                {'key': 'third_key', 'value': 'third_value'}
            ]
        })

        repo.create(self.repo_url, self.repo_vsid, config={'second_key': 'second_value', 'third_key': 'fourth_value'})

        repo_request = dict(self.repo_request)
        repo_request['data']['config'] = [
            {'key': 'first_key', 'value': 'first_value'},
            {'key': 'third_key', 'value': 'fourth_value'},
            {'key': 'second_key', 'value': 'second_value'},
        ]

        self.maxDiff = None
        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository', body=repo_request, accept='application/json'),
                                       self, json_body=True)

    def test_create_with_role_and_type(self):
        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': self.repo_server_data})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)

        repo.create(self.repo_url, self.repo_vsid, role='TARGET', typ='GIT')

        repo_request = dict(self.repo_request)
        repo_request['data']['role'] = 'TARGET'
        repo_request['data']['type'] = 'GIT'

        self.maxDiff = None
        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository', body=repo_request, accept='application/json'),
                                       self, json_body=True)

    # Covered by TestgCTSSimpleClone
    #def test_create_generic_error(self):
    #    pass

    # Covered by TestgCTSSimpleClone
    #def test_create_already_exists_error(self):
    #    pass

    def test_set_config_success(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)
        repo.set_config('THE_KEY', 'the value')
        self.assertEqual(repo.get_config('THE_KEY'), 'the value')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository/{self.repo_name}/config', body={'key': 'THE_KEY', 'value': 'the value'}), self, json_body=True)

    def test_set_config_success_overwrite(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        repo.set_config('VCS_CONNECTION', 'git')
        self.assertEqual(repo.get_config('VCS_CONNECTION'), 'git')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository/{self.repo_name}/config', body={'key': 'VCS_CONNECTION', 'value': 'git'}), self, json_body=True)

    def test_set_config_error(self):
        messages = LogBuilder(exception='Set Config Error').get_contents()

        self.conn.set_responses(Response.with_json(status_code=500, json=messages))
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.set_config('THE_KEY', 'the value')

        self.assertEqual(str(caught.exception), 'gCTS exception: Set Config Error')

    def test_get_config_cached_ok(self):
        repo = sap.rest.gcts.remote_repo.Repository(None, self.repo_name, data={
            'config': [
                {'key': 'THE_KEY', 'value': 'the value', 'category': 'connection'}
            ]
        })

        value = repo.get_config('THE_KEY')
        self.assertEqual(value, 'the value')

    def test_get_config_no_config_ok(self):
        self.conn.set_responses(Response.with_json(status_code=200, json={'result':self.repo_server_data}))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name)

        # This will fetch repo data from the server
        value = repo.get_config('VCS_CONNECTION')
        self.assertEqual(value, 'SSL')

        # The second request does not causes an HTTP request
        value = repo.get_config('VCS_CONNECTION')
        self.assertEqual(value, 'SSL')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_name}'), self)

    def test_get_config_no_key_ok(self):
        self.conn.set_responses(Response.with_json(status_code=200, json={'result': {'value': 'the value'}}))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)

        # This will fetch the configruation key value from the server
        value = repo.get_config('THE_KEY')
        self.assertEqual(value, 'the value')

        # The second request does not causes an HTTP request
        value = repo.get_config('THE_KEY')
        self.assertEqual(value, 'the value')

        # The update of keys did not break the cache
        value = repo.get_config('VCS_CONNECTION')
        self.assertEqual(value, 'SSL')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_name}/config/THE_KEY'), self)

    def test_get_config_error(self):
        messages = LogBuilder(exception='Get Config Error').get_contents()

        self.conn.set_responses(Response.with_json(status_code=500, json=messages))
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.get_config('THE_KEY')

        self.assertEqual(str(caught.exception), 'gCTS exception: Get Config Error')

    def test_clone_ok(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        repo.clone()

        self.assertIsNone(repo._data)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post(uri=f'repository/{self.repo_name}/clone'), self)

    def test_clone_error(self):
        messages = LogBuilder(exception='Clone Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.clone()

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Clone Error')

    def test_checkout_ok(self):
        self.conn.set_responses(Response.with_json(status_code=200, json={'result': {
            'fromCommit': '123',
            'toCommit': '456'
        }}))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        repo.checkout('the_other_branch')

        self.assertIsNone(repo._data)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get(adt_uri=f'repository/{self.repo_name}/branches/the_branch/switch', params={'branch': 'the_other_branch'}), self)

    def test_checkout_error(self):
        messages = LogBuilder(exception='Checkout Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.checkout('the_other_branch')

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Checkout Error')

    def test_delete_ok(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        repo.delete()

        self.assertIsNone(repo._data)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request(method='DELETE', adt_uri=f'repository/{self.repo_name}', params=None, headers=None, body=None), self)

    def test_delete_error(self):
        messages = LogBuilder(exception='Delete Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.delete()

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Delete Error')

    def test_log_ok(self):
        exp_commits = [{'id': '123'}]

        self.conn.set_responses(
            Response.with_json(status_code=200, json={
                'commits': exp_commits
            })
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        act_commits = repo.log()

        self.assertIsNotNone(repo._data)
        self.assertEqual(act_commits, exp_commits)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_name}/getCommit'), self)

    def test_log_error(self):
        messages = LogBuilder(exception='Log Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.log()

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Log Error')

    def test_pull(self):
        exp_log = {
            'fromCommit': '123',
            'toCommit': '456'
        }

        self.conn.set_responses(
            Response.with_json(status_code=200, json=exp_log )
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        act_log = repo.pull()

        self.assertIsNone(repo._data)
        self.assertEqual(act_log, exp_log)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_name}/pullByCommit'), self)

    def test_pull_error(self):
        messages = LogBuilder(exception='Pull Error').get_contents()
        self.conn.set_responses(
            Response.with_json(status_code=500, json=messages)
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.pull()

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Pull Error')

    def test_commit_transports(self):
        corrnr = 'CORRNR'
        message = 'Message'
        description = 'Description'

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=self.repo_server_data)
        response = repo.commit_transport(corrnr, message, description=description)

        self.conn.execs[0].assertEqual(
            Request.post_json(
                uri='repository/repo/commit',
                body={
                    'message': message,
                    'autoPush': 'true',
                    'objects': [{'object': corrnr, 'type': 'TRANSPORT'}],
                    'description': description
                }
            ),
            self
        )

        self.assertIsNone(repo._data)

    def test_set_url_change(self):
        CALL_ID_FETCH_REPO_DATA = 0
        CALL_ID_SET_URL = 1
        NEW_URL = 'https://random.github.org/awesome/success'

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': self.repo_server_data}),
            Response.ok()
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=None)
        response = repo.set_url(NEW_URL)

        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(
            Request.get_json(uri=f'repository/{self.repo_name}'),
            self
        )

        request_with_url = dict(self.repo_server_data)
        request_with_url['url'] = NEW_URL

        self.conn.execs[CALL_ID_SET_URL].assertEqual(
            Request.post_json(
                uri=f'repository/{self.repo_name}',
                body=request_with_url
            ),
            self
        )

    def test_set_url_nochange(self):
        CALL_ID_FETCH_REPO_DATA = 0
        NEW_URL = self.repo_server_data['url']

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': self.repo_server_data}),
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_name, data=None)
        response = repo.set_url(NEW_URL)

        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(
            Request.get_json(uri=f'repository/{self.repo_name}'),
            self
        )

        self.assertIsNone(response)


class TestgCTSSimpleAPI(GCTSTestSetUp, unittest.TestCase):

    def test_simple_clone_success(self):
        CALL_ID_CREATE = 0
        CALL_ID_CLONE = 1

        repository = dict(self.repo_server_data)
        repository['status'] = 'CREATED'

        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': repository}),
            Response.ok()
        )

        sap.rest.gcts.simple.clone(
            self.conn,
            self.repo_url,
            self.repo_name,
            vcs_token='THE_TOKEN'
        )

        data = dict(self.repo_data)
        data['config'] = [
            {'key': 'VCS_TARGET_DIR', 'value': 'src/'},
            {'key': 'CLIENT_VCS_AUTH_TOKEN', 'value': 'THE_TOKEN'}
        ]

        request_load = {
            'repository': self.repo_name,
            'data': data
        }

        self.assertEqual(len(self.conn.execs), 2)

        self.conn.execs[CALL_ID_CREATE].assertEqual(Request.post_json(uri='repository', body=request_load, accept='application/json'), self, json_body=True)
        self.conn.execs[CALL_ID_CLONE].assertEqual(Request.post(uri=f'repository/{self.repo_name}/clone'), self)

    @patch('sap.rest.gcts.remote_repo.Repository.is_cloned', new_callable=PropertyMock)
    @patch('sap.rest.gcts.remote_repo.Repository.create')
    def test_simple_clone_passing_parameters(self, fake_create, fake_is_cloned):
        fake_is_cloned.return_value = True

        def assertPassedParameters(url, vsid, config=None, role=None, typ=None):
            self.assertEqual(vsid, '0ZZ')
            self.assertEqual(role, 'TARGET')
            self.assertEqual(typ, 'GIT')
            self.assertEqual(config, {'VCS_TARGET_DIR': 'foo/', 'CLIENT_VCS_AUTH_TOKEN': 'THE_TOKEN'})

        fake_create.side_effect = assertPassedParameters

        sap.rest.gcts.simple.clone(
            self.conn,
            self.repo_url,
            self.repo_name,
            vcs_token='THE_TOKEN',
            vsid='0ZZ',
            start_dir='foo/',
            role='TARGET',
            typ='GIT'
        )

    def test_simple_clone_without_params_create_fail(self):
        log_builder = LogBuilder()
        messages = log_builder.log_error(make_gcts_log_error('Failure')).log_exception('Message', 'EERROR').get_contents()

        self.conn.set_responses([Response.with_json(status_code=500, json=messages)])

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            sap.rest.gcts.simple.clone(self.conn, self.repo_url, self.repo_name)

        self.assertEqual(str(caught.exception), 'gCTS exception: Message')

    def test_simple_clone_without_params_create_exists(self):
        log_builder = LogBuilder()
        log_builder.log_error(make_gcts_log_error('20200923111743: Error action CREATE_REPOSITORY Repository already exists'))
        log_builder.log_exception('Cannot create', 'EEXIST').get_contents()
        messages = log_builder.get_contents()

        self.conn.set_responses([Response.with_json(status_code=500, json=messages)])

        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoAlreadyExistsError) as caught:
            sap.rest.gcts.simple.clone(self.conn, self.repo_url, self.repo_name)

        self.assertEqual(str(caught.exception), 'gCTS exception: Cannot create')

    def test_simple_clone_without_params_create_exists_continue(self):
        CALL_ID_FETCH_REPO_DATA = 1

        log_builder = LogBuilder()
        log_builder.log_error(make_gcts_log_error('20200923111743: Error action CREATE_REPOSITORY Repository already exists'))
        log_builder.log_exception('Cannot create', 'EEXIST').get_contents()
        messages = log_builder.get_contents()

        new_repo_data = dict(self.repo_server_data)
        new_repo_data['status'] = 'CREATED'

        self.conn.set_responses([
            Response.with_json(status_code=500, json=messages),
            Response.with_json(status_code=200, json={'result': new_repo_data}),
            Response.ok()
        ])

        repo = sap.rest.gcts.simple.clone(self.conn, self.repo_url, self.repo_name, error_exists=False)
        self.assertIsNotNone(repo)
        self.assertEqual(len(self.conn.execs), 3)
        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(Request.get_json(uri=f'repository/{self.repo_name}'), self)

    def test_simple_clone_without_params_create_exists_continue_cloned(self):
        CALL_ID_FETCH_REPO_DATA = 1

        log_builder = LogBuilder()
        log_builder.log_error(make_gcts_log_error('20200923111743: Error action CREATE_REPOSITORY Repository already exists'))
        log_builder.log_exception('Cannot create', 'EEXIST').get_contents()
        messages = log_builder.get_contents()

        self.assertEqual(self.repo_server_data['status'], 'READY')

        self.conn.set_responses([
            Response.with_json(status_code=500, json=messages),
            Response.with_json(status_code=200, json={'result': self.repo_server_data}),
        ])

        repo = sap.rest.gcts.simple.clone(self.conn, self.repo_url, self.repo_name, error_exists=False)
        self.assertIsNotNone(repo)

        self.assertEqual(len(self.conn.execs), 2)
        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(Request.get_json(uri=f'repository/{self.repo_name}'), self)

    def test_simple_fetch_no_repo(self):
        self.conn.set_responses(
            Response.with_json(status_code=200, json={})
        )

        repos = sap.rest.gcts.simple.fetch_repos(self.conn)
        self.assertEqual(len(repos), 0)

    def test_simple_fetch_ok(self):
        REPO_ONE_ID=0
        repo_one = dict(self.repo_server_data)
        repo_one['name'] = repo_one['rid'] = 'one'

        REPO_TWO_ID=1
        repo_two = dict(self.repo_server_data)
        repo_two['name'] = repo_two['rid'] = 'two'

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result':
                [repo_one, repo_two]
            })
        )

        repos = sap.rest.gcts.simple.fetch_repos(self.conn)

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[REPO_ONE_ID].name, 'one')
        self.assertEqual(repos[REPO_TWO_ID].name, 'two')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository'), self)


    def test_simple_fetch_error(self):
        messages = LogBuilder(exception='Fetch Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            sap.rest.gcts.simple.fetch_repos(self.conn)

        self.assertEqual(str(caught.exception), 'gCTS exception: Fetch Error')

    @patch('sap.rest.gcts.simple.Repository')
    def test_simple_checkout_ok(self, fake_repository):
        fake_instance = Mock()
        fake_repository.return_value = fake_instance
        fake_instance.checkout = Mock()
        fake_instance.checkout.return_value = 'probe'

        response = sap.rest.gcts.simple.checkout(self.conn, 'the_new_branch', name=self.repo_name)
        fake_repository.assert_called_once_with(self.conn, self.repo_name)
        fake_instance.checkout.assert_called_once_with('the_new_branch')
        self.assertEqual(response, 'probe')

    @patch('sap.rest.gcts.simple.Repository')
    def test_simple_delete_ok(self, fake_repository):
        fake_instance = Mock()
        fake_repository.return_value = fake_instance
        fake_instance.delete = Mock()
        fake_instance.delete.return_value = 'probe'

        response = sap.rest.gcts.simple.delete(self.conn, self.repo_name)
        fake_repository.assert_called_once_with(self.conn, self.repo_name)
        fake_instance.delete.assert_called_once_with()
        self.assertEqual(response, 'probe')

    @patch('sap.rest.gcts.simple.Repository')
    def test_simple_log_name(self, fake_repository):
        fake_instance = Mock()
        fake_repository.return_value = fake_instance
        fake_instance.log = Mock()
        fake_instance.log.return_value = 'probe'

        response = sap.rest.gcts.simple.log(self.conn, name=self.repo_name)
        fake_repository.assert_called_once_with(self.conn, self.repo_name)
        fake_instance.log.assert_called_once_with()
        self.assertEqual(response, 'probe')

    def test_simple_log_repo(self):
        fake_instance = Mock()
        fake_instance.log = Mock()
        fake_instance.log.return_value = 'probe'

        response = sap.rest.gcts.simple.log(None, repo=fake_instance)
        self.assertEqual(response, 'probe')

    @patch('sap.rest.gcts.simple.Repository')
    def test_simple_pull_name(self, fake_repository):
        fake_instance = Mock()
        fake_repository.return_value = fake_instance
        fake_instance.pull = Mock()
        fake_instance.pull.return_value = 'probe'

        response = sap.rest.gcts.simple.pull(self.conn, name=self.repo_name)
        fake_repository.assert_called_once_with(self.conn, self.repo_name)
        fake_instance.pull.assert_called_once_with()
        self.assertEqual(response, 'probe')

    def test_simple_pull_repo(self):
        fake_instance = Mock()
        fake_instance.pull = Mock()
        fake_instance.pull.return_value = 'probe'

        response = sap.rest.gcts.simple.pull(None, repo=fake_instance)
        self.assertEqual(response, 'probe')

    def test_simple_set_user_api_token(self):
        connection = RESTConnection()

        api_url = 'https://api.url/'
        token = 'THETOKEN'
        response = sap.rest.gcts.simple.set_user_api_token(connection, api_url, token)

        self.assertEqual(connection.mock_methods(), [('POST', 'user/credentials')])
        connection.execs[0].assertEqual(
            Request.post_json(
                uri='user/credentials',
                body={
                    'endpoint': api_url,
                    'user': '',
                    'password': '',
                    'token': token,
                    'type': 'token'
                }
            ),
            self
        )

        self.assertEqual(response, None)
