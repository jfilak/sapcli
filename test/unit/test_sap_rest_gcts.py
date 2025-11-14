#!/usr/bin/env python3

import json
import unittest
import time
from unittest.mock import Mock, call, patch

from sap.rest.errors import HTTPRequestError, UnauthorizedError
from sap.rest.gcts.repo_task import RepositoryTask
import sap.rest.gcts
import sap.rest.gcts.remote_repo
import sap.rest.gcts.simple
import sap.rest.gcts.sugar

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

    def test_repository_already_exists_error(self):
        """Test that the error is raised when the repository already exists (format: CREATE_REPOSITORY: Error action...)"""
        messages = {
            'log': [{'message': 'CREATE_REPOSITORY: Error action Repository already exists'}],
            'exception': 'Repository already exists'
        }
        req = Request(method='GET', adt_uri='/epic/success', headers=None, body=None, params=None)
        res = Response.with_json(status_code=400, json=messages)

        orig_error = HTTPRequestError(req, res)
        new_error = sap.rest.gcts.errors.exception_from_http_error(orig_error)

        expected_error = sap.rest.gcts.errors.GCTSRepoAlreadyExistsError(messages)

        self.assertEqual(str(new_error), str(expected_error))

    def test_repository_already_exists_error_alternative_format(self):
        """Test that the error is raised when the repository already exists (format: Error action CREATE_REPOSITORY...)"""
        messages = {
            'log': [{'message': 'Error action CREATE_REPOSITORY Repository already exists'}],
            'exception': 'Repository already exists'
        }
        req = Request(method='GET', adt_uri='/epic/success', headers=None, body=None, params=None)
        res = Response.with_json(status_code=400, json=messages)

        orig_error = HTTPRequestError(req, res)
        new_error = sap.rest.gcts.errors.exception_from_http_error(orig_error)

        expected_error = sap.rest.gcts.errors.GCTSRepoAlreadyExistsError(messages)

        self.assertEqual(str(new_error), str(expected_error))


class GCTSTestSetUp:

    def setUp(self):
        self.repo_url = 'https://example.com/git/repo'
        self.repo_rid = 'repo-id'
        self.repo_name = 'the repo name'
        self.repo_vsid = '6IT'
        self.repo_start_dir = 'src/'
        self.repo_vcs_token = '12345'
        self.repo_data = {
            'rid': self.repo_rid,
            'name': self.repo_rid,
            'role': 'SOURCE',
            'type': 'GITHUB',
            'vsid': '6IT',
            'url': self.repo_url,
            'connection': 'ssl',
        }

        self.repo_request = {
            'repository': self.repo_rid,
            'data': {
                'rid': self.repo_rid,
                'name': self.repo_rid,
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
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data={})
        repo.wipe_data()
        self.assertIsNone(repo._data)

    def test_ctor_no_data(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        self.assertEqual(repo._http.connection, self.conn)
        self.assertEqual(repo.rid, self.repo_rid)
        self.assertIsNone(repo._data)

    def test_ctor_with_data(self):
        data = {}

        repo = sap.rest.gcts.remote_repo.Repository(None, self.repo_rid, data=data)

        self.assertIsNone(repo._http.connection)
        self.assertEqual(repo.rid, self.repo_rid)
        self.assertIsNotNone(repo._data)

    def test_properties_cached(self):
        repo = sap.rest.gcts.remote_repo.Repository(None, self.repo_rid, data=self.repo_server_data)

        self.assertEqual(repo.status, self.repo_server_data['status'])
        self.assertEqual(repo.rid, self.repo_server_data['rid'])
        self.assertEqual(repo.url, self.repo_server_data['url'])
        self.assertEqual(repo.branch, self.repo_server_data['branch'])
        self.assertEqual(repo.configuration, {'VCS_CONNECTION': 'SSL', 'CLIENT_VCS_URI': ''})

    def test_properties_fetch(self):
        response = {'result': self.repo_server_data}

        self.conn.set_responses([Response.with_json(json=response, status_code=200)])

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)

        self.assertEqual(repo.status, self.repo_server_data['status'])
        self.assertEqual(repo.rid, self.repo_server_data['rid'])
        self.assertEqual(repo.url, self.repo_server_data['url'])
        self.assertEqual(repo.branch, self.repo_server_data['branch'])

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}'), self)

    # exactly the same as test_properties_fetch but with 500 as status
    # testing gCTS' behavior for repos whose remote does not exist
    def test_properties_fetch_with_500(self):
        response = {'result': self.repo_server_data}

        self.conn.set_responses([Response.with_json(json=response, status_code=500)])

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)

        self.assertEqual(repo.status, self.repo_server_data['status'])
        self.assertEqual(repo.rid, self.repo_server_data['rid'])
        self.assertEqual(repo.url, self.repo_server_data['url'])
        self.assertEqual(repo.branch, self.repo_server_data['branch'])

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}'), self)

    def test_properties_fetch_error(self):
        messages = LogBuilder(exception='Get Repo Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            unused = repo.name

        self.assertEqual(str(caught.exception), 'gCTS exception: Get Repo Error')

    def test_create_no_self_data_no_config(self):
        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': self.repo_server_data})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        repo.create(self.repo_url, self.repo_vsid)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository', body=self.repo_request, accept='application/json'),
                                       self, json_body=True)

    def test_create_with_config_instance_none(self):
        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': self.repo_server_data})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
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

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data={
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

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)

        repo.create(self.repo_url, self.repo_vsid, role='TARGET', typ='GIT')

        repo_request = dict(self.repo_request)
        repo_request['data']['role'] = 'TARGET'
        repo_request['data']['type'] = 'GIT'

        self.maxDiff = None
        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository', body=repo_request, accept='application/json'),
                                       self, json_body=True)

    # Covered by TestgCTSSimpleClone
    # def test_create_generic_error(self):
    #    pass

    # Covered by TestgCTSSimpleClone
    # def test_create_already_exists_error(self):
    #    pass

    def test_set_config_success(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        repo.set_config('THE_KEY', 'the value')
        self.assertEqual(repo.get_config('THE_KEY'), 'the value')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository/{self.repo_rid}/config', body={'key': 'THE_KEY', 'value': 'the value'}), self, json_body=True)

    def test_set_config_success_overwrite(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        repo.set_config('VCS_CONNECTION', 'git')
        self.assertEqual(repo.get_config('VCS_CONNECTION'), 'git')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post_json(uri=f'repository/{self.repo_rid}/config', body={'key': 'VCS_CONNECTION', 'value': 'git'}), self, json_body=True)

    def test_set_config_error(self):
        messages = LogBuilder(exception='Set Config Error').get_contents()

        self.conn.set_responses(Response.with_json(status_code=500, json=messages))
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.set_config('THE_KEY', 'the value')

        self.assertEqual(str(caught.exception), 'gCTS exception: Set Config Error')

    def test_get_config_cached_ok(self):
        repo = sap.rest.gcts.remote_repo.Repository(None, self.repo_rid, data={
            'config': [
                {'key': 'THE_KEY', 'value': 'the value', 'category': 'connection'}
            ]
        })

        value = repo.get_config('THE_KEY')
        self.assertEqual(value, 'the value')

    def test_get_config_no_config_ok(self):
        self.conn.set_responses(Response.with_json(status_code=200, json={'result': self.repo_server_data}))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)

        # This will fetch repo data from the server
        value = repo.get_config('VCS_CONNECTION')
        self.assertEqual(value, 'SSL')

        # The second request does not causes an HTTP request
        value = repo.get_config('VCS_CONNECTION')
        self.assertEqual(value, 'SSL')

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}'), self)

    def test_get_config_no_key_ok(self):
        self.conn.set_responses(Response.with_json(status_code=200, json={'result': {'value': 'the value'}}))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)

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
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}/config/THE_KEY'), self)

    def test_get_config_no_value_ok(self):
        self.conn.set_responses(Response.with_json(status_code=200, json={'result': {}}))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        value = repo.get_config('THE_KEY')

        self.assertIsNone(value)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}/config/THE_KEY'), self)

    def test_get_config_error(self):
        messages = LogBuilder(exception='Get Config Error').get_contents()

        self.conn.set_responses(Response.with_json(status_code=500, json=messages))
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.get_config('THE_KEY')

        self.assertEqual(str(caught.exception), 'gCTS exception: Get Config Error')

    def test_repo_without_config(self):
        data = dict(self.repo_server_data)
        del data['config']

        self.conn.set_responses(Response.with_json(status_code=200, json={"result": data}))
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)

        self.assertEqual(repo.configuration, {})

    def test_delete_config_ok(self):
        key = 'CLIENT_VCS_URI'
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        repo.delete_config(key)

        expected_repo_config = {'VCS_CONNECTION': 'SSL', 'CLIENT_VCS_URI': ''}
        self.assertEqual(repo.configuration, expected_repo_config)
        self.conn.execs[0].assertEqual(Request.delete(f'repository/{self.repo_rid}/config/{key}'), self)

    def test_delete_config_key_not_in_config_ok(self):
        key = 'THE_KEY'
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        repo.delete_config(key)

        self.conn.execs[0].assertEqual(Request.delete(f'repository/{self.repo_rid}/config/{key}'), self)

    def test_clone_ok(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        repo.clone()

        self.assertIsNone(repo._data)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.post(uri=f'repository/{self.repo_rid}/clone'), self)

    def test_clone_error(self):
        messages = LogBuilder(exception='Clone Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.clone()

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Clone Error')

    def test_checkout_ok(self):
        self.conn.set_responses(Response.with_json(status_code=200, json={'result': {
            'fromCommit': '123',
            'toCommit': '456'
        }}))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        repo.checkout('the_other_branch')

        self.assertIsNone(repo._data)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get(adt_uri=f'repository/{self.repo_rid}/branches/the_branch/switch', params={'branch': 'the_other_branch'}), self)

    def test_checkout_error(self):
        messages = LogBuilder(exception='Checkout Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.checkout('the_other_branch')

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Checkout Error')

    def test_delete_ok(self):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        repo.delete()

        self.assertIsNone(repo._data)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request(method='DELETE', adt_uri=f'repository/{self.repo_rid}', params=None, headers=None, body=None), self)

    def test_delete_error(self):
        messages = LogBuilder(exception='Delete Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
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

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        act_commits = repo.log()

        self.assertIsNotNone(repo._data)
        self.assertEqual(act_commits, exp_commits)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}/getCommit'), self)

    def test_log_error(self):
        messages = LogBuilder(exception='Log Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
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
            Response.with_json(status_code=200, json=exp_log)
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        act_log = repo.pull()

        self.assertIsNone(repo._data)
        self.assertEqual(act_log, exp_log)

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}/pullByCommit'), self)

    def test_pull_error(self):
        messages = LogBuilder(exception='Pull Error').get_contents()
        self.conn.set_responses(
            Response.with_json(status_code=500, json=messages)
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            repo.pull()

        self.assertIsNotNone(repo._data)
        self.assertEqual(str(caught.exception), 'gCTS exception: Pull Error')

    def assert_repo_activities(self, query_params, expected_result, expected_params):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        result = repo.activities(query_params)

        self.assertEqual(result, expected_result)
        self.conn.execs[0].assertEqual(Request.get_json(uri=f'repository/{self.repo_rid}/getHistory',
                                                        params=expected_params), self)

    def test_activities_default_params(self):
        expected_params = {'limit': '10', 'offset': '0'}
        expected_result = ['activity']
        query_params = sap.rest.gcts.remote_repo.RepoActivitiesQueryParams()
        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': expected_result})
        )

        self.assert_repo_activities(query_params, expected_result, expected_params)

    def test_activities_all_params(self):
        expected_params = {'limit': '15', 'offset': '10', 'toCommit': '123', 'fromCommit': '456', 'type': 'CLONE'}
        expected_result = ['activity']

        query_params = sap.rest.gcts.remote_repo.RepoActivitiesQueryParams().set_limit(15).set_offset(10)\
            .set_tocommit('123').set_fromcommit('456').set_operation('CLONE')
        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': expected_result})
        )

        self.assert_repo_activities(query_params, expected_result, expected_params)

    def test_activities_empty_response(self):
        expected_params = {'limit': '10', 'offset': '0'}
        expected_result = []

        query_params = sap.rest.gcts.remote_repo.RepoActivitiesQueryParams()
        self.conn.set_responses(
            Response.with_json(status_code=200, json={})
        )

        self.assert_repo_activities(query_params, expected_result, expected_params)

    def test_activities_empty_result(self):
        query_params = sap.rest.gcts.remote_repo.RepoActivitiesQueryParams()
        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': []})
        )

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
            repo.activities(query_params)

        self.assertEqual(str(cm.exception), 'A successful gcts getHistory request did not return result')

    def test_commit_transports(self):
        corrnr = 'CORRNR'
        message = 'Message'
        description = 'Description'

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        response = repo.commit_transport(corrnr, message, description=description)

        self.conn.execs[0].assertEqual(
            Request.post_json(
                uri=f'repository/{self.repo_rid}/commit',
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

    def test_commit_package(self):
        package = 'Package'
        message = 'Message'
        description = 'Description'

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=self.repo_server_data)
        response = repo.commit_package(package, message, description=description)

        self.conn.execs[0].assertEqual(
            Request.post_json(
                uri=f'repository/{self.repo_rid}/commit',
                body={
                    'message': message,
                    'autoPush': 'true',
                    'objects': [{'object': package, 'type': 'FULL_PACKAGE'}],
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

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=None)
        response = repo.set_url(NEW_URL)

        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(
            Request.get_json(uri=f'repository/{self.repo_rid}'),
            self
        )

        request_with_url = {'url': NEW_URL}

        self.conn.execs[CALL_ID_SET_URL].assertEqual(
            Request.post_json(
                uri=f'repository/{self.repo_rid}',
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

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=None)
        response = repo.set_url(NEW_URL)

        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(
            Request.get_json(uri=f'repository/{self.repo_rid}'),
            self
        )

        self.assertIsNone(response)

    def test_set_item(self):
        CALL_ID_FETCH_REPO_DATA = 0
        CALL_ID_SET_URL = 1

        property_name = 'name'
        new_value = 'new_name'

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': self.repo_server_data}),
            Response.ok()
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=None)
        response = repo.set_item(property_name, new_value)

        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(
            Request.get_json(uri=f'repository/{self.repo_rid}'),
            self
        )

        expected_request_body = {property_name: new_value}

        self.conn.execs[CALL_ID_SET_URL].assertEqual(
            Request.post_json(
                uri=f'repository/{self.repo_rid}',
                body=expected_request_body
            ),
            self
        )

        self.assertIsNotNone(response)

    def test_set_item_incorrect_property(self):
        property_name = 'incorrect_property'

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=None)

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            repo.set_item(property_name, 'value')

        self.assertEqual(self.conn.execs, [])
        self.assertEqual(str(cm.exception), f'Cannot edit property "{property_name}".')

    def test_set_item_nochange(self):
        CALL_ID_FETCH_REPO_DATA = 0

        property_name = 'rid'
        new_value = self.repo_rid

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': self.repo_server_data}),
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=None)
        response = repo.set_item(property_name, new_value)

        self.conn.execs[CALL_ID_FETCH_REPO_DATA].assertEqual(
            Request.get_json(uri=f'repository/{self.repo_rid}'),
            self
        )

        self.assertIsNone(response)

    def test_set_role(self):
        CALL_ID_SET_ROLE = 1

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'result': self.repo_server_data}),
            Response.ok()
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=None)
        response = repo.set_role('TARGET')

        self.conn.execs[CALL_ID_SET_ROLE].assertEqual(
            Request.post_json(
                uri=f'repository/{self.repo_rid}',
                body={"role": "TARGET"}
            ),
            self
        )

    def test_create_branch(self):
        branch_name = 'branch'
        expected_response = {
            'name': branch_name,
            'type': 'active',
            'isSymbolic': False,
            'isPeeled': False,
            'ref': f'/refs/heads/{branch_name}',
        }

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'branch': expected_response})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        response = repo.create_branch(branch_name)

        self.conn.execs[0].assertEqual(
            Request.post_json(f'repository/{self.repo_rid}/branches', body={
                'branch': branch_name,
                'type': 'global',
                'isSymbolic': False,
                'isPeeled': False,
            }),
            self
        )
        self.assertEqual(response, expected_response)

    def test_create_branch_all_params(self):
        branch_name = 'branch'
        expected_response = {
            'name': branch_name,
            'type': 'active',
            'isSymbolic': True,
            'isPeeled': True,
            'ref': f'/refs/heads/{branch_name}',
        }

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'branch': expected_response})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        response = repo.create_branch(branch_name, symbolic=True, peeled=True, local_only=True)

        self.conn.execs[0].assertEqual(
            Request.post_json(f'repository/{self.repo_rid}/branches', body={
                'branch': branch_name,
                'type': 'local',
                'isSymbolic': True,
                'isPeeled': True,
            }),
            self,
        )
        self.assertEqual(response, expected_response)

    def test_delete_branch(self):
        branch_name = 'branch'

        self.conn.set_responses(
            Response.with_json(status_code=200, json={})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        response = repo.delete_branch(branch_name)

        self.conn.execs[0].assertEqual(
            Request.delete(f'repository/{self.repo_rid}/branches/{branch_name}'),
            self,
        )
        self.assertEqual(response, {})

    def test_list_branches(self):
        branches = [{'name': 'branch1', 'type': 'active', 'isSymbolic': False, 'isPeeled': False,
                     'ref': 'refs/heads/branch1'},
                    {'name': 'branch1', 'type': 'local', 'isSymbolic': False, 'isPeeled': False,
                     'ref': 'refs/heads/branch1'},
                    {'name': 'branch1', 'type': 'remote', 'isSymbolic': False, 'isPeeled': False,
                     'ref': 'refs/remotes/origin/branch1'}]

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'branches': branches})
        )
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        response = repo.list_branches()

        self.conn.execs[0].assertEqual(
            Request.get_json(f'repository/{self.repo_rid}/branches'),
            self
        )
        self.assertEqual(response, branches)

    def test_list_branches_wrong_response(self):
        self.conn.set_responses(
            Response.with_json(status_code=200, json={})
        )

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            repo.list_branches()

        self.assertEqual(str(cm.exception), "gCTS response does not contain 'branches'")

    def test_list_of_repository_objects(self):
        objects = [
            {'pgmid': 'R3TR', 'type': 'FUGR', 'object': 'OBJECT1', 'description': 'DESCRIPTION1'},
            {'pgmid': 'R3TR', 'type': 'DEVC', 'object': 'OBJECT2', 'description': 'DESCRIPTION2'},
            {'pgmid': 'R3TR', 'type': 'SUSH', 'object': 'OBJECT3', 'description': 'DESCRIPTION3'},
        ]
        self.conn.set_responses(
            Response.with_json(status_code=200, json={'objects': objects})
        )
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        response = repo.objects()
        self.assertEqual(response, objects)

    def test_list_of_repository_objects_wrong_response(self):
        self.conn.set_responses(
            Response.with_json(status_code=200, json={'something': 'else'})
        )
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)
        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            repo.objects()
        self.assertEqual(str(cm.exception), "A successful gcts getObjects request did not return the objects member")

    def test_list_of_repository_objects_empty_response(self):
        self.conn.set_responses(
            Response.with_json(status_code=200, json={})
        )
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid)

        responce = repo.objects()
        self.assertEqual(responce, [])

class TestRepositoryTask(unittest.TestCase):

    def setUp(self):
        """Set up test data for RepositoryTask tests"""

        self.conn = RESTConnection()
        self.rid = 'repo-id'
        self.task_data = {
            'tid': '123',
            'jobId': 'job-456',
            'log': 'Task log message',
            'variant': 'default',
            'name': 'Test Task',
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.RUNNING.value,
            'createdBy': 'test_user',
            'createdAt': int(time.time() * 1000),
            'changedBy': 'test_user',
            'changedAt': int(time.time() * 1000),
            'startAt': int(time.time() * 1000),
            'scheduledAt': int(time.time() * 1000)
        }

    def test_task_creation_with_data(self):
        """Test RepositoryTask creation with initial data"""
        task = RepositoryTask(self.conn, self.rid, self.task_data)

        self.assertEqual(task.tid, self.task_data['tid'])
        self.assertEqual(task.rid, self.rid)
        self.assertEqual(task.jobId, self.task_data['jobId'])
        self.assertEqual(task.log, self.task_data['log'])
        self.assertEqual(task.variant, self.task_data['variant'])
        self.assertEqual(task.name, self.task_data['name'])
        self.assertEqual(task.type, self.task_data['type'])
        self.assertEqual(task.status, self.task_data['status'])
        self.assertEqual(task.createdBy, self.task_data['createdBy'])
        self.assertEqual(task.createdAt, self.task_data['createdAt'])
        self.assertEqual(task.changedBy, self.task_data['changedBy'])
        self.assertEqual(task.changedAt, self.task_data['changedAt'])
        self.assertEqual(task.startAt, self.task_data['startAt'])
        self.assertEqual(task.scheduledAt, self.task_data['scheduledAt'])

    def test_task_creation_without_data(self):
        """Test RepositoryTask creation without initial data"""
        task = RepositoryTask(self.conn, self.rid)

        self.assertEqual(task.rid, self.rid)
        self.assertIsNone(task.tid)
        self.assertIsNone(task.jobId)
        self.assertIsNone(task.log)
        self.assertIsNone(task.variant)
        self.assertIsNone(task.name)
        self.assertIsNone(task.type)
        self.assertIsNone(task.status)
        self.assertIsNone(task.createdBy)
        self.assertIsNone(task.createdAt)
        self.assertIsNone(task.changedBy)
        self.assertIsNone(task.changedAt)
        self.assertIsNone(task.startAt)
        self.assertIsNone(task.scheduledAt)

    def test_task_creation_with_empty_data(self):
        """Test RepositoryTask creation with empty data dictionary"""
        task = RepositoryTask(self.conn, self.rid, {})

        self.assertEqual(task.rid, self.rid)
        self.assertIsNone(task.tid)
        self.assertIsNone(task.jobId)
        self.assertIsNone(task.log)
        self.assertIsNone(task.variant)
        self.assertIsNone(task.name)
        self.assertIsNone(task.type)
        self.assertIsNone(task.status)
        self.assertIsNone(task.createdBy)
        self.assertIsNone(task.createdAt)
        self.assertIsNone(task.changedBy)
        self.assertIsNone(task.changedAt)
        self.assertIsNone(task.startAt)
        self.assertIsNone(task.scheduledAt)

    def test_update_task_data(self):
        """Test updating task data"""
        task = RepositoryTask(self.conn, self.rid, self.task_data)

        new_data = {
            'status': RepositoryTask.TaskStatus.FINISHED.value,
            'changedAt': 1640995204000,
        }
        task.update_data(new_data)

        # Check updated fields
        self.assertEqual(task.status, new_data['status'])
        self.assertEqual(task.changedAt, new_data['changedAt'])

    def test_update_data_empty(self):
        """Test updating task data with empty dictionary"""
        task = RepositoryTask(self.conn, self.rid, self.task_data)
        original_data = task._data.copy()

        task.update_data({})

        self.assertEqual(task._data, original_data)

    def test_get_task_status(self):
        """Test get_status method"""
        task = RepositoryTask(self.conn, self.rid, self.task_data)

        self.assertEqual(task.get_status(), self.task_data['status'])
        self.assertEqual(task.get_status(), task.status)

    def test_get_task_status_none(self):
        """Test get_status method when status is None"""
        task = RepositoryTask(self.conn, self.rid)

        self.assertIsNone(task.get_status())

    def test_task_definition_enum(self):
        """Test TaskDefinition enum values"""

        self.assertEqual(RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value, 'clone_repository')
        self.assertEqual(RepositoryTask.TaskDefinition.SWITCH_BRANCH.value, 'switch_branch')
        self.assertEqual(RepositoryTask.TaskDefinition.PULL_COMMIT.value, 'pull_commit')
        self.assertEqual(RepositoryTask.TaskDefinition.DEPLOY.value, 'deploy')
        self.assertEqual(RepositoryTask.TaskDefinition.MERGE_BRANCH.value, 'merge_branch')
        self.assertEqual(RepositoryTask.TaskDefinition.MIGRATE_REPOSITORY.value, 'migrate_repository')

    def test_task_status_enum(self):
        """Test TaskStatus enum values"""

        self.assertEqual(RepositoryTask.TaskStatus.READY.value, 'READY')
        self.assertEqual(RepositoryTask.TaskStatus.RUNNING.value, 'RUNNING')
        self.assertEqual(RepositoryTask.TaskStatus.SCHEDULED.value, 'SCHEDULED')
        self.assertEqual(RepositoryTask.TaskStatus.ABORTED.value, 'ABORTED')
        self.assertEqual(RepositoryTask.TaskStatus.SUSPENDED.value, 'SUSPENDED')
        self.assertEqual(RepositoryTask.TaskStatus.FINISHED.value, 'FINISHED')
        self.assertEqual(RepositoryTask.TaskStatus.PRELIMINARY.value, 'PRELIMINARY')

    def test_task_parameters_creation_empty(self):
        """Test TaskParameters creation with no parameters"""

        params = RepositoryTask.TaskParameters()

        self.assertIsNone(params.branch)
        self.assertIsNone(params.commit)
        self.assertIsNone(params.deploy_scope)
        self.assertIsNone(params.merge_strategy)
        self.assertIsNone(params.merge_fast_forward)
        self.assertIsNone(params.commit_message)
        self.assertIsNone(params.objects)
        self.assertIsNone(params.trkorr)
        self.assertIsNone(params.deploy_operation)
        self.assertIsNone(params.layout)

    def test_task_parameters_creation_with_values(self):
        """Test TaskParameters creation with all parameters"""

        params = RepositoryTask.TaskParameters(
            branch='main',
            commit='abc123',
            deploy_scope='PACKAGE',
            merge_strategy='MERGE',
            merge_fast_forward=True,
            commit_message='Test commit',
            objects=['obj1', 'obj2'],
            trkorr='TR123',
            deploy_operation='DEPLOY',
            layout='standard'
        )

        self.assertEqual(params.branch, 'main')
        self.assertEqual(params.commit, 'abc123')
        self.assertEqual(params.deploy_scope, 'PACKAGE')
        self.assertEqual(params.merge_strategy, 'MERGE')
        self.assertEqual(params.merge_fast_forward, True)
        self.assertEqual(params.commit_message, 'Test commit')
        self.assertEqual(params.objects, ['obj1', 'obj2'])
        self.assertEqual(params.trkorr, 'TR123')
        self.assertEqual(params.deploy_operation, 'DEPLOY')
        self.assertEqual(params.layout, 'standard')

    def test_task_parameters_to_dict_empty(self):
        """Test TaskParameters to_dict with no parameters"""

        params = RepositoryTask.TaskParameters()
        result = params.to_dict()

        self.assertEqual(result, {})

    def test_task_parameters_to_dict_all_values(self):
        """Test TaskParameters to_dict with all parameters"""

        params = RepositoryTask.TaskParameters(
            branch='main',
            commit='abc123',
            deploy_scope='PACKAGE',
            merge_strategy='MERGE',
            merge_fast_forward=True,
            commit_message='Test commit',
            objects=['obj1', 'obj2'],
            trkorr='TR123',
            deploy_operation='DEPLOY',
            layout='standard'
        )
        result = params.to_dict()

        expected = {
            'branch': 'main',
            'commit': 'abc123',
            'deploy_scope': 'PACKAGE',
            'merge_strategy': 'MERGE',
            'merge_fast_forward': True,
            'commit_message': 'Test commit',
            'objects': ['obj1', 'obj2'],
            'trkorr': 'TR123',
            'deploy_operation': 'DEPLOY',
            'layout': 'standard'
        }

        self.assertEqual(result, expected)

    def test_task_parameters_to_dict_partial_values(self):
        """Test TaskParameters to_dict with some parameters"""

        params = RepositoryTask.TaskParameters(
            branch='main',
            commit_message='Test commit',
            objects=['obj1']
        )
        result = params.to_dict()

        expected = {
            'branch': 'main',
            'commit_message': 'Test commit',
            'objects': ['obj1']
        }

        self.assertEqual(result, expected)

    def test_task_parameters_to_dict_none_values(self):
        """Test TaskParameters to_dict excludes None values"""

        params = RepositoryTask.TaskParameters(
            branch='main',
            commit=None,
            deploy_scope='PACKAGE',
            merge_strategy=None,
            commit_message='Test commit'
        )
        result = params.to_dict()

        expected = {
            'branch': 'main',
            'deploy_scope': 'PACKAGE',
            'commit_message': 'Test commit'
        }

        self.assertEqual(result, expected)

    def test_task_property_access_missing_keys(self):
        """Test property access when keys are missing from data"""
        task = RepositoryTask(self.conn, self.rid, {'tid': '123'})

        self.assertEqual(task.tid, '123')
        self.assertEqual(task.rid, self.rid)
        self.assertIsNone(task.jobId)
        self.assertIsNone(task.log)
        self.assertIsNone(task.variant)
        self.assertIsNone(task.name)
        self.assertIsNone(task.type)
        self.assertIsNone(task.status)
        self.assertIsNone(task.createdBy)
        self.assertIsNone(task.createdAt)
        self.assertIsNone(task.changedBy)
        self.assertIsNone(task.changedAt)
        self.assertIsNone(task.startAt)
        self.assertIsNone(task.scheduledAt)

    def test_clone_task_create_and_schedule_success(self):
        """Test async clone task create and schedule"""
        task_scheduledAt = int(time.time() * 1000)  # /ms
        task_id = '123'
        self.conn.set_responses(
            # Response for create_task
            Response.with_json(status_code=200, json={
                'task': {
                    'tid': task_id,
                    'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                    'status': RepositoryTask.TaskStatus.PRELIMINARY.value
                }
            }),
            # Response for schedule_task
            Response.with_json(status_code=200, json={
                'task': {
                    'tid': task_id,
                    'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                    'status': RepositoryTask.TaskStatus.RUNNING.value,
                    'scheduledAt': task_scheduledAt
                }
            })
        )

        # repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.rid, data=self.repo_server_data)
        task = RepositoryTask(self.conn, self.rid).create(RepositoryTask.TaskDefinition.CLONE_REPOSITORY).schedule_task()

        self.assertIsNotNone(task)
        self.assertTrue(isinstance(task, RepositoryTask))
        self.assertEqual(task.scheduledAt, task_scheduledAt)
        self.assertEqual(task.tid, task_id)
        self.assertEqual(task.type, RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value)
        self.assertEqual(task.status, RepositoryTask.TaskStatus.RUNNING.value)
        self.assertEqual(task.scheduledAt, task_scheduledAt)

        self.assertEqual(len(self.conn.execs), 2)

        # Check create_task call
        create_request = self.conn.execs[0]
        self.assertEqual(create_request.method, 'POST')
        self.assertEqual(create_request.adt_uri, f'repository/{self.rid}/task')

        # Check schedule_task call
        schedule_request = self.conn.execs[1]
        self.assertEqual(schedule_request.method, 'GET')
        self.assertEqual(schedule_request.adt_uri, f'repository/{self.rid}/task/{task_id}/schedule')

    def test_clone_task_create_success(self):
        """Test async clone task create only"""
        task_id = '123'
        self.conn.set_responses(
            # Response for create_task
            Response.with_json(status_code=200, json={
                'task': {
                    'tid': task_id,
                    'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                    'status': RepositoryTask.TaskStatus.PRELIMINARY.value
                }
            })
        )

        task = RepositoryTask(self.conn, self.rid).create(RepositoryTask.TaskDefinition.CLONE_REPOSITORY)

        self.assertIsNotNone(task)
        self.assertTrue(isinstance(task, RepositoryTask))
        self.assertEqual(task.tid, task_id)
        self.assertEqual(task.type, RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value)
        self.assertEqual(task.status, RepositoryTask.TaskStatus.PRELIMINARY.value)

        self.assertEqual(len(self.conn.execs), 1)

        # Check create_task call
        create_request = self.conn.execs[0]
        self.assertEqual(create_request.method, 'POST')
        self.assertEqual(create_request.adt_uri, f'repository/{self.rid}/task')

    def test_clone_task_create_with_parameters_success(self):
        """Test create with task parameters"""
        task_id = '123'
        task_response = {
            'task': {
                'tid': task_id,
                'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                'status': RepositoryTask.TaskStatus.PRELIMINARY.value,
                'parameters': {
                    'branch': 'main'
                }
            }
        }
        self.conn.set_responses(Response.with_json(status_code=200, json=task_response))

        # Create task parameters
        parameters = RepositoryTask.TaskParameters()
        parameters.branch = 'main'

        task = RepositoryTask(self.conn, self.rid).create(
            RepositoryTask.TaskDefinition.CLONE_REPOSITORY,
            parameters
        )

        self.assertIsNotNone(task)
        self.assertEqual(task.tid, task_id)
        self.assertEqual(task.type, RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value)
        self.assertEqual(len(self.conn.execs), 1)

        create_request = self.conn.execs[0]
        self.assertEqual(create_request.method, 'POST')
        self.assertEqual(create_request.adt_uri, f'repository/{self.rid}/task')

        request_data = json.loads(create_request.body)
        self.assertIn('parameters', request_data)
        self.assertEqual(request_data['parameters']['branch'], 'main')

    def test__clone_task_create_repository_not_set_error(self):
        """Test create when repository is not set (rid is None)"""
        task = RepositoryTask(self.conn, self.rid)
        task._rid = None

        with self.assertRaises(sap.rest.gcts.errors.SAPCliError) as caught:
            task.create(RepositoryTask.TaskDefinition.CLONE_REPOSITORY)

        self.assertEqual(str(caught.exception), 'Repository is not set')
        self.assertEqual(len(self.conn.execs), 0)  # No HTTP request should be made

    def test_clone_task_create_general_request_error(self):
        """Test create when HTTP request returns a general error"""
        messages = LogBuilder(exception='Create Task Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            RepositoryTask(self.conn, self.rid).create(RepositoryTask.TaskDefinition.CLONE_REPOSITORY)

        self.assertEqual(str(caught.exception), 'gCTS exception: Create Task Error')
        self.assertEqual(len(self.conn.execs), 1)

        create_request = self.conn.execs[0]
        self.assertEqual(create_request.method, 'POST')
        self.assertEqual(create_request.adt_uri, f'repository/{self.rid}/task')

    def test_clone_task_repository_not_exists_error(self):
        """Test create when repository does not exist"""
        messages = LogBuilder(exception='No relation between system and repository').get_contents()
        self.conn.set_responses(Response.with_json(status_code=404, json=messages))

        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoNotExistsError) as caught:
            RepositoryTask(self.conn, self.rid).create(RepositoryTask.TaskDefinition.CLONE_REPOSITORY)

        self.assertEqual(str(caught.exception), 'gCTS exception: Repository does not exist')
        self.assertEqual(len(self.conn.execs), 1)

        create_request = self.conn.execs[0]
        self.assertEqual(create_request.method, 'POST')
        self.assertEqual(create_request.adt_uri, f'repository/{self.rid}/task')

    def test_clone_task_schedule_success(self):
        """Test async clone task schedule only"""
        task_scheduledAt = int(time.time() * 1000)  # /ms
        task_id = '123'
        self.conn.set_responses(
            # Response for schedule_task
            Response.with_json(status_code=200, json={
                'task': {
                    'tid': task_id,
                    'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                    'status': RepositoryTask.TaskStatus.RUNNING.value,
                    'scheduledAt': task_scheduledAt
                }
            })
        )

        # Create a task instance with preliminary data
        task = RepositoryTask(self.conn, self.rid)
        task.update_data({
            'tid': task_id,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.PRELIMINARY.value
        })

        scheduled_task = task.schedule_task()

        self.assertIsNotNone(scheduled_task)
        self.assertTrue(isinstance(scheduled_task, RepositoryTask))
        self.assertEqual(scheduled_task.scheduledAt, task_scheduledAt)
        self.assertEqual(scheduled_task.tid, task_id)
        self.assertEqual(scheduled_task.type, RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value)
        self.assertEqual(scheduled_task.status, RepositoryTask.TaskStatus.RUNNING.value)

        self.assertEqual(len(self.conn.execs), 1)

        # Check schedule_task call
        schedule_request = self.conn.execs[0]
        self.assertEqual(schedule_request.method, 'GET')
        self.assertEqual(schedule_request.adt_uri, f'repository/{self.rid}/task/{task_id}/schedule')

    def test_schedule_task_task_not_set_error(self):
        """Test schedule_task when task is not set (tid is None)"""
        task = RepositoryTask(self.conn, self.rid)

        with self.assertRaises(sap.rest.gcts.errors.SAPCliError) as caught:
            task.schedule_task()

        self.assertEqual(str(caught.exception), 'Task is not set')
        self.assertEqual(len(self.conn.execs), 0)  # No HTTP request should be made

    def test_schedule_task_task_not_preliminary_error(self):
        """Test schedule_task when task is not in PRELIMINARY status"""
        task = RepositoryTask(self.conn, self.rid)
        task.update_data({
            'tid': '123',
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.RUNNING.value  # Not PRELIMINARY
        })

        with self.assertRaises(sap.rest.gcts.errors.SAPCliError) as caught:
            task.schedule_task()

        self.assertEqual(str(caught.exception), 'Task is not in PRELIMINARY status')
        self.assertEqual(len(self.conn.execs), 0)  # No HTTP request should be made

    def test_schedule_task_general_request_error(self):
        """Test schedule_task when HTTP request returns a general error"""
        task_id = '123'
        messages = LogBuilder(exception='Schedule Task Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        task = RepositoryTask(self.conn, self.rid)
        task.update_data({
            'tid': task_id,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.PRELIMINARY.value
        })

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            task.schedule_task()

        self.assertEqual(str(caught.exception), 'gCTS exception: Schedule Task Error')
        self.assertEqual(len(self.conn.execs), 1)

        schedule_request = self.conn.execs[0]
        self.assertEqual(schedule_request.method, 'GET')
        self.assertEqual(schedule_request.adt_uri, f'repository/{self.rid}/task/{task_id}/schedule')

    def test_schedule_task_repository_not_exists_error(self):
        """Test schedule_task when repository does not exist"""
        task_id = '123'
        messages = LogBuilder(exception='No relation between system and repository').get_contents()
        self.conn.set_responses(Response.with_json(status_code=404, json=messages))

        task = RepositoryTask(self.conn, self.rid)
        task.update_data({
            'tid': task_id,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.PRELIMINARY.value
        })

        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoNotExistsError) as caught:
            task.schedule_task()

        self.assertEqual(str(caught.exception), 'gCTS exception: Repository does not exist')
        self.assertEqual(len(self.conn.execs), 1)

        schedule_request = self.conn.execs[0]
        self.assertEqual(schedule_request.method, 'GET')
        self.assertEqual(schedule_request.adt_uri, f'repository/{self.rid}/task/{task_id}/schedule')

    def test_delete_task_success(self):
        """Test delete task success"""
        task_id = '123'
        task = RepositoryTask(self.conn, self.rid, self.task_data)
        task.update_data({'tid': task_id})

        self.conn.set_responses(
            Response.with_json(status_code=200, json={})
        )

        result = task.delete()

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, RepositoryTask))
        self.assertEqual(result, task)

        self.assertEqual(len(self.conn.execs), 1)
        delete_request = self.conn.execs[0]
        self.assertEqual(delete_request.method, 'DELETE')
        self.assertEqual(delete_request.adt_uri, f'repository/{self.rid}/task/{task_id}')

    def test_delete_task_general_request_error(self):
        """Test delete task when HTTP request returns a general error"""
        task_id = '123'
        messages = LogBuilder(exception='Delete Task Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        task = RepositoryTask(self.conn, self.rid, self.task_data)
        task.update_data({'tid': task_id})

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            task.delete()

        self.assertEqual(str(caught.exception), 'gCTS exception: Delete Task Error')
        self.assertEqual(len(self.conn.execs), 1)

        delete_request = self.conn.execs[0]
        self.assertEqual(delete_request.method, 'DELETE')
        self.assertEqual(delete_request.adt_uri, f'repository/{self.rid}/task/{task_id}')

    def test_delete_task_repository_not_exists_error(self):
        """Test delete task when repository does not exist"""
        task_id = '123'
        messages = LogBuilder(exception='No relation between system and repository').get_contents()
        self.conn.set_responses(Response.with_json(status_code=404, json=messages))

        task = RepositoryTask(self.conn, self.rid, self.task_data)
        task.update_data({'tid': task_id})

        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoNotExistsError) as caught:
            task.delete()

        self.assertEqual(str(caught.exception), 'gCTS exception: Repository does not exist')
        self.assertEqual(len(self.conn.execs), 1)

        delete_request = self.conn.execs[0]
        self.assertEqual(delete_request.method, 'DELETE')
        self.assertEqual(delete_request.adt_uri, f'repository/{self.rid}/task/{task_id}')

    def test_delete_task_clone_task_delete_error(self):
        """Test delete task when clone task deletion fails"""

        messages = LogBuilder(exception='Job GCTS_CLONE_REPO could not be deleted: FM BP_JOB_DELETE failed with sy-subrc 16').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        task = RepositoryTask(self.conn, self.rid, self.task_data)
        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoCloneTaskDeleteError) as caught:
            task.delete()

        self.assertEqual(str(caught.exception), 'gCTS exception: Task unable to delete. Already performed clone operation.')
        self.assertEqual(len(self.conn.execs), 1)

        delete_request = self.conn.execs[0]
        self.assertEqual(delete_request.method, 'DELETE')
        self.assertEqual(delete_request.adt_uri, f'repository/{self.rid}/task/{task.tid}')

    def test_get_list_success(self):
        """Test get_list method with successful response"""
        task_list = [
            {
                'tid': '123',
                'rid': self.rid,
                'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                'status': RepositoryTask.TaskStatus.FINISHED.value,
                'name': 'Clone Task',
                'createdBy': 'test_user',
                'createdAt': int(time.time() * 1000)
            },
            {
                'tid': '456',
                'rid': self.rid,
                'type': RepositoryTask.TaskDefinition.SWITCH_BRANCH.value,
                'status': RepositoryTask.TaskStatus.RUNNING.value,
                'name': 'Switch Branch Task',
                'createdBy': 'test_user',
                'createdAt': int(time.time() * 1000)
            }
        ]

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'tasks': task_list})
        )

        task = RepositoryTask(self.conn, self.rid)
        result = task.get_list()

        self.assertEqual(result, task_list)
        self.assertEqual(len(self.conn.execs), 1)

        get_request = self.conn.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, f'repository/{self.rid}/task')

    def test_get_list_empty_response(self):
        """Test get_list method with empty task list"""
        self.conn.set_responses(
            Response.with_json(status_code=200, json={'tasks': []})
        )

        task = RepositoryTask(self.conn, self.rid)
        result = task.get_list()

        self.assertEqual(result, [])
        self.assertEqual(len(self.conn.execs), 1)

        get_request = self.conn.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, f'repository/{self.rid}/task')

    def test_get_list_general_request_error(self):
        """Test get_list method when HTTP request returns a general error"""
        messages = LogBuilder(exception='Get Task List Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        task = RepositoryTask(self.conn, self.rid)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            task.get_list()

        self.assertEqual(str(caught.exception), 'gCTS exception: Get Task List Error')
        self.assertEqual(len(self.conn.execs), 1)

        get_request = self.conn.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, f'repository/{self.rid}/task')

    def test_get_list_repository_not_exists_error(self):
        """Test get_list method when repository does not exist"""
        messages = LogBuilder(exception='No relation between system and repository').get_contents()
        self.conn.set_responses(Response.with_json(status_code=404, json=messages))

        task = RepositoryTask(self.conn, self.rid)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoNotExistsError) as caught:
            task.get_list()

        self.assertEqual(str(caught.exception), 'gCTS exception: Repository does not exist')
        self.assertEqual(len(self.conn.execs), 1)

        get_request = self.conn.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, f'repository/{self.rid}/task')

    def test_get_by_id_success(self):
        """Test get_by_id method with successful response"""
        task_id = '123'
        task_data = {
            'tid': task_id,
            'rid': self.rid,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.FINISHED.value,
            'name': 'Test Task',
            'createdBy': 'test_user',
            'createdAt': int(time.time() * 1000)
        }

        self.conn.set_responses(
            Response.with_json(status_code=200, json={'task': task_data})
        )

        task = RepositoryTask(self.conn, self.rid)
        result = task.get_by_id(task_id)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, RepositoryTask))
        self.assertEqual(result.tid, task_id)
        self.assertEqual(result.rid, self.rid)
        self.assertEqual(result.type, task_data['type'])
        self.assertEqual(result.status, task_data['status'])
        self.assertEqual(result.name, task_data['name'])
        self.assertEqual(result.createdBy, task_data['createdBy'])
        self.assertEqual(result.createdAt, task_data['createdAt'])

        self.assertEqual(len(self.conn.execs), 1)
        get_request = self.conn.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, f'repository/{self.rid}/task/{task_id}')

    def test_get_by_id_general_request_error(self):
        """Test get_by_id method when HTTP request returns a general error"""
        task_id = '123'
        messages = LogBuilder(exception='Get Task Error').get_contents()
        self.conn.set_responses(Response.with_json(status_code=500, json=messages))

        task = RepositoryTask(self.conn, self.rid)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            task.get_by_id(task_id)

        self.assertEqual(str(caught.exception), 'gCTS exception: Get Task Error')
        self.assertEqual(len(self.conn.execs), 1)

        get_request = self.conn.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, f'repository/{self.rid}/task/{task_id}')

    def test_get_by_id_repository_not_exists_error(self):
        """Test get_by_id method when repository does not exist"""
        task_id = '123'
        messages = LogBuilder(exception='No relation between system and repository').get_contents()
        self.conn.set_responses(Response.with_json(status_code=404, json=messages))

        task = RepositoryTask(self.conn, self.rid)

        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoNotExistsError) as caught:
            task.get_by_id(task_id)

        self.assertEqual(str(caught.exception), 'gCTS exception: Repository does not exist')
        self.assertEqual(len(self.conn.execs), 1)

        get_request = self.conn.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(get_request.adt_uri, f'repository/{self.rid}/task/{task_id}')


class TestRepoActivitiesQueryParams(unittest.TestCase):

    def setUp(self):
        self.params = sap.rest.gcts.remote_repo.RepoActivitiesQueryParams()

    def test_set_operation_invalid(self):
        with self.assertRaises(sap.rest.errors.SAPCliError) as caught:
            self.params.set_operation('FOO')

        self.assertEqual(str(caught.exception), 'Invalid gCTS Activity Operation: FOO')

    def test_set_operation_valid(self):
        for operation in sap.rest.gcts.remote_repo.RepoActivitiesQueryParams.allowed_operations():
            self.params.set_operation(operation)


class TestgCTSSimpleAPI(GCTSTestSetUp, unittest.TestCase):

    def test_simple_schedule_clone_success(self):
        repo_data = dict(self.repo_server_data)
        repo_data['status'] = 'CREATED'
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repo_data)

        task_id = '123'
        task_scheduledAt = int(time.time() * 1000)  # /ms

        self.conn.set_responses(
            Response.with_json(status_code=200, json={
                'task': {
                    'tid': task_id,
                    'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                    'status': RepositoryTask.TaskStatus.PRELIMINARY.value
                }
            }),
            Response.with_json(status_code=200, json={
                'task': {
                    'tid': task_id,
                    'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
                    'status': RepositoryTask.TaskStatus.RUNNING.value,
                    'scheduledAt': task_scheduledAt
                }
            })
        )

        result = sap.rest.gcts.simple.schedule_clone(self.conn, repo)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, RepositoryTask))
        self.assertEqual(result.tid, task_id)

        self.assertEqual(len(self.conn.execs), 2)

        create_request = self.conn.execs[0]
        self.assertEqual(create_request.method, 'POST')
        self.assertEqual(create_request.adt_uri, f'repository/{self.repo_rid}/task')

        schedule_request = self.conn.execs[1]
        self.assertEqual(schedule_request.method, 'GET')
        self.assertEqual(schedule_request.adt_uri, f'repository/{self.repo_rid}/task/{task_id}/schedule')

    @patch('sap.rest.gcts.simple._mod_log')
    @patch('sap.rest.gcts.simple.RepositoryTask')
    def test_simple_schedule_clone_repo_already_cloned(self, mock_repository_task, fake_mod_log):
        """Test that RepositoryTask methods are NOT called when repository is already cloned"""
        repo_data = dict(self.repo_server_data)
        repo_data['status'] = 'READY'
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repo_data)

        mock_task_instance = Mock()
        mock_repository_task.return_value = mock_task_instance

        result = sap.rest.gcts.simple.schedule_clone(self.conn, repo)

        mock_repository_task.assert_not_called()
        mock_task_instance.create.assert_not_called()
        mock_task_instance.schedule_task.assert_not_called()
        self.assertIsNone(result)
        fake_mod_log.return_value.info.assert_called_once_with('Repository "%s" cloning not scheduled: already performed or repository is not created.', self.repo_rid)

    @patch('sap.rest.gcts.simple._mod_log')
    def test_simple_schedule_clone_repo_not_created(self, fake_mod_log):
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data={})
        with patch.object(repo, 'clone', wraps=repo.clone) as spy_clone:
            sap.rest.gcts.simple.schedule_clone(self.conn, repo)
            spy_clone.assert_not_called()
            fake_mod_log.return_value.info.assert_called_once_with('Repository "%s" cloning not scheduled: already performed or repository is not created.', self.repo_rid)

    @patch('sap.rest.gcts.simple.create')
    def test_simple_clone_success_sync(self, fake_create):
        repo_data = dict(self.repo_server_data)
        repo_data['status'] = 'CREATED'
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repo_data)
        fake_create.return_value = repo
        with patch.object(repo, 'clone', wraps=repo.clone) as spy_clone:
            self.conn.set_responses(
                Response.ok()
            )

            returned_repo = sap.rest.gcts.simple.clone(
                connection=self.conn,
                url=self.repo_url,
                rid=self.repo_rid,
                vsid=self.repo_vsid,
                start_dir=self.repo_start_dir,
                vcs_token=self.repo_vcs_token,
                error_exists=True,
                role='SOURCE',
                typ='GITHUB'
            )

            self.assertFalse(isinstance(returned_repo, tuple))

            fake_create.assert_called_once_with(
                connection=self.conn,
                url=self.repo_url,
                rid=self.repo_rid,
                vsid=self.repo_vsid,
                start_dir=self.repo_start_dir,
                vcs_token=self.repo_vcs_token,
                error_exists=True,
                role='SOURCE',
                typ='GITHUB'
            )

            spy_clone.assert_called_once()

            self.assertEqual(len(self.conn.execs), 1)
            self.conn.execs[0].assertEqual(Request.post(uri=f'repository/{self.repo_rid}/clone'), self)
            self.assertEqual(returned_repo, repo)

    @patch('sap.rest.gcts.simple.create')
    def test_simple_clone_default_parameters(self, fake_create):
        repo_data = dict(self.repo_server_data)
        repo_data['status'] = 'CREATED'
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repo_data)
        fake_create.return_value = repo
        with patch.object(repo, 'clone', wraps=repo.clone) as spy_clone:
            self.conn.set_responses(
                Response.ok()
            )

            returned_repo = sap.rest.gcts.simple.clone(
                connection=self.conn,
                url=self.repo_url,
                rid=self.repo_rid,
            )

            fake_create.assert_called_once_with(
                connection=self.conn,
                url=self.repo_url,
                rid=self.repo_rid,
                vsid='6IT',  # default vsid
                start_dir='src/',  # default start dir
                vcs_token=None,  # default vcs token
                error_exists=True,  # default error exists
                role='SOURCE',  # default role
                typ='GITHUB'  # default type
            )

            # default sync way
            spy_clone.assert_called_once()

            self.assertEqual(len(self.conn.execs), 1)
            self.conn.execs[0].assertEqual(Request.post(uri=f'repository/{self.repo_rid}/clone'), self)
            self.assertEqual(returned_repo, repo)

    @patch('sap.rest.gcts.simple.create')
    @patch('sap.rest.gcts.simple._mod_log')
    def test_simple_clone_repo_already_cloned(self, fake_mod_log, fake_create):
        repo_data = dict(self.repo_server_data)
        repo_data['status'] = 'READY'
        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repo_data)
        fake_create.return_value = repo
        with patch.object(repo, 'clone', wraps=repo.clone) as spy_clone:
            returned_repo = sap.rest.gcts.simple.clone(
                connection=self.conn,
                url=self.repo_url,
                rid=self.repo_rid,
                error_exists=True,
            )

            spy_clone.assert_not_called()
            fake_mod_log.return_value.info.assert_called_once_with('Not cloning the repository "%s": already performed', self.repo_rid)
            self.assertEqual(returned_repo, repo)

    def test_simple_create_success_with_http(self):
        CALL_ID_CREATE = 0

        repository = dict(self.repo_server_data)
        repository['status'] = 'CREATED'

        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': repository})
        )

        repo = sap.rest.gcts.simple.create(
            self.conn,
            self.repo_url,
            self.repo_rid,
            vcs_token='THE_TOKEN'
        )

        data = dict(self.repo_data)
        data['config'] = [
            {'key': 'VCS_TARGET_DIR', 'value': 'src/'},
            {'key': 'CLIENT_VCS_AUTH_TOKEN', 'value': 'THE_TOKEN'}
        ]

        request_load = {
            'repository': self.repo_rid,
            'data': data
        }

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[CALL_ID_CREATE].assertEqual(Request.post_json(uri='repository', body=request_load, accept='application/json'), self, json_body=True)
        self.assertIsNotNone(repo)

    @patch('sap.rest.gcts.simple.Repository')
    def test_simple_create_success_with_mock_repo(self, mock_repository_class):
        mock_repo_instance = Mock()
        mock_repository_class.return_value = mock_repo_instance

        repo = sap.rest.gcts.simple.create(
            self.conn,
            self.repo_url,
            self.repo_rid,
            vcs_token='THE_TOKEN'
        )

        mock_repository_class.assert_called_once_with(self.conn, self.repo_rid)

        mock_repo_instance.create.assert_called_once_with(
            self.repo_url,
            '6IT',
            config={'VCS_TARGET_DIR': 'src/', 'CLIENT_VCS_AUTH_TOKEN': 'THE_TOKEN'},
            role='SOURCE',
            typ='GITHUB'
        )

        self.assertEqual(repo, mock_repo_instance)

    def test_simple_create_passing_parameters(self):
        CALL_ID_CREATE = 0

        repository = dict(self.repo_server_data)
        repository['status'] = 'CREATED'

        self.conn.set_responses(
            Response.with_json(status_code=201, json={'repository': repository})
        )

        repo = sap.rest.gcts.simple.create(
            self.conn,
            self.repo_url,
            self.repo_rid,
            vcs_token='THE_TOKEN',
            vsid='0ZZ',
            start_dir='foo/',
            role='TARGET',
            typ='GIT'
        )

        data = dict(self.repo_data)
        data['vsid'] = '0ZZ'
        data['role'] = 'TARGET'
        data['type'] = 'GIT'
        data['config'] = [
            {'key': 'VCS_TARGET_DIR', 'value': 'foo/'},
            {'key': 'CLIENT_VCS_AUTH_TOKEN', 'value': 'THE_TOKEN'}
        ]

        request_load = {
            'repository': self.repo_rid,
            'data': data
        }

        self.assertEqual(len(self.conn.execs), 1)
        self.conn.execs[CALL_ID_CREATE].assertEqual(Request.post_json(uri='repository', body=request_load, accept='application/json'), self, json_body=True)
        self.assertIsNotNone(repo)

    def test_simple_create_fail(self):
        log_builder = LogBuilder()
        messages = log_builder.log_error(make_gcts_log_error('Failure')).log_exception('Message', 'EERROR').get_contents()

        self.conn.set_responses([Response.with_json(status_code=500, json=messages)])

        with self.assertRaises(sap.rest.gcts.errors.GCTSRequestError) as caught:
            sap.rest.gcts.simple.create(self.conn, self.repo_url, self.repo_rid)

        self.assertEqual(str(caught.exception), 'gCTS exception: Message')

    def test_simple_create_exists(self):
        log_builder = LogBuilder()
        log_builder.log_error(make_gcts_log_error('20200923111743: Error action CREATE_REPOSITORY Repository already exists'))
        log_builder.log_exception('Cannot create', 'EEXIST').get_contents()
        messages = log_builder.get_contents()

        self.conn.set_responses([Response.with_json(status_code=500, json=messages)])

        with self.assertRaises(sap.rest.gcts.errors.GCTSRepoAlreadyExistsError) as caught:
            sap.rest.gcts.simple.create(self.conn, self.repo_url, self.repo_rid)

        self.assertEqual(str(caught.exception), 'gCTS exception: Cannot create')

    def test_simple_create_exists_continue(self):
        log_builder = LogBuilder()
        log_builder.log_error(make_gcts_log_error('20200923111743: Error action CREATE_REPOSITORY Repository already exists'))
        log_builder.log_exception('Cannot create', 'EEXIST').get_contents()
        messages = log_builder.get_contents()

        new_repo_data = dict(self.repo_server_data)
        new_repo_data['status'] = 'CREATED'

        self.conn.set_responses([
            Response.with_json(status_code=500, json=messages),
        ])

        repo = sap.rest.gcts.simple.create(self.conn, self.repo_url, self.repo_rid, error_exists=False)
        self.assertIsNotNone(repo)
        self.assertEqual(len(self.conn.execs), 1)

    def test_simple_create_exists_continue_cloned(self):
        log_builder = LogBuilder()
        log_builder.log_error(make_gcts_log_error('20200923111743: Error action CREATE_REPOSITORY Repository already exists'))
        log_builder.log_exception('Cannot create', 'EEXIST').get_contents()
        messages = log_builder.get_contents()

        self.assertEqual(self.repo_server_data['status'], 'READY')

        self.conn.set_responses([
            Response.with_json(status_code=500, json=messages),
        ])

        repo = sap.rest.gcts.simple.create(self.conn, self.repo_url, self.repo_rid, error_exists=False)
        self.assertIsNotNone(repo)

        self.assertEqual(len(self.conn.execs), 1)

    @patch('sap.rest.gcts.simple._mod_log')
    def test_simple_wait_for_clone(self, fake_mod_log):
        repository = dict(self.repo_server_data)
        repository['status'] = 'CREATED'

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repository)
        repo.wipe_data = Mock(side_effect=repo.wipe_data)

        self.conn.set_responses([
            Response.with_json(status_code=200, json={'result': self.repo_server_data})
        ])

        sap.rest.gcts.simple.wait_for_operation(repo, lambda r: r.is_cloned, 10, None)
        repo.wipe_data.assert_called_once()
        fake_mod_log.return_value.debug.assert_not_called()

    @patch('sap.rest.gcts.simple._mod_log')
    def test_simple_wait_for_clone_with_retries(self, fake_mod_log):
        repository = dict(self.repo_server_data)
        repository['status'] = 'CREATED'

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repository)
        repo.wipe_data = Mock(side_effect=repo.wipe_data)

        self.conn.set_responses([
            Response(status_code=500, text='Test HTTP Request Exception'),
            Response.with_json(status_code=200, json={'result': repository}),
            Response.with_json(status_code=200, json={'result': self.repo_server_data})
        ])

        sap.rest.gcts.simple.wait_for_operation(repo, lambda r: r.is_cloned, 10, None)
        self.assertEqual(repo.wipe_data.mock_calls, [call(), call(), call()])
        fake_mod_log.return_value.debug.assert_called_once_with('Failed to get status of the repository %s', repo.name)

    @patch('sap.rest.gcts.simple.time.time')
    def test_simple_wait_for_clone_timeout(self, fake_time):
        repository = dict(self.repo_server_data)
        repository['status'] = 'CREATED'

        fake_time.side_effect = [0, 1, 2]

        self.conn.set_responses([
            Response.with_json(status_code=200, json={'result': repository}),
        ])

        repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.repo_rid, data=repository)
        http_error = HTTPRequestError(None, Response(status_code=500, text='Test HTTP Request Exception'))

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            sap.rest.gcts.simple.wait_for_operation(repo, lambda r: r.is_cloned, 2, http_error)

        self.assertEqual(str(cm.exception), 'Waiting for the operation timed out\n'
                                            '500\nTest HTTP Request Exception')

    def test_simple_wait_for_task_execution_success(self):
        """Test wait_for_task_execution when task finishes successfully"""
        fake_print_gcts_task_info = Mock()

        task_id = 'test-task-123'

        task_data_running = {
            'tid': task_id,
            'rid': self.repo_rid,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.RUNNING.value,
        }
        task_data = {
            'tid': task_id,
            'rid': self.repo_rid,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.FINISHED.value
        }
        arguments_stub = [
            [None, task_data_running],
            [None, task_data_running],
            ['Test HTTP Request Exception', None],
            [None, task_data_running],
            [None, task_data],
        ]
        wrong_stats_code = 500
        responses = []
        for arguments in arguments_stub:
            if arguments[0] is None:
                responses.append(Response.with_json(status_code=200, json={'task': arguments[1]}))
            else:
                responses.append(Response(status_code=wrong_stats_code, text=arguments[0]))

        self.conn.set_responses(responses)

        task = sap.rest.gcts.repo_task.RepositoryTask(self.conn, self.repo_rid, data={'tid': task_id})

        with patch.object(task, 'get_by_id', wraps=task.get_by_id) as spy_get_by_id:

            sap.rest.gcts.simple.wait_for_task_execution(task, wait_for_ready=10, poll_period=1, poll_cb=fake_print_gcts_task_info)
            self.assertEqual(spy_get_by_id.call_count, 5)
            for i, call_args in enumerate(spy_get_by_id.call_args_list):
                args, _kwargs = call_args
                self.assertEqual(args[0], task_id)

            call_count = fake_print_gcts_task_info.call_count
            self.assertEqual(call_count, 5)

            call_args_list = fake_print_gcts_task_info.call_args_list
            self.assertEqual(len(call_args_list), call_count)

            for i, call_args in enumerate(call_args_list):
                args, _kwargs = call_args
                self.assertEqual(len(args), 2,)
                if arguments_stub[i][0] is not None:
                    expected_error_msg = f'{wrong_stats_code}\n{arguments_stub[i][0]}'
                    self.assertEqual(f'Failed to get status of the task {task_id}: {expected_error_msg}', args[0])
                else:
                    self.assertEqual(arguments_stub[i][0], args[0])

                if arguments_stub[i][1] is not None:
                    self.assertEqual(arguments_stub[i][1]['status'], args[1]['status'])
                else:
                    self.assertIsNone(args[1])

    def test_simple_wait_for_task_execution_while_task_is_running(self):
        """Test wait_for_task_execution while task is running.When the task is finished, wait_for_task_execution exit from the loop."""
        fake_print_gcts_task_info = Mock()

        task_id = 'test-task-123'

        task_data_running = {
            'tid': task_id,
            'rid': self.repo_rid,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.RUNNING.value,
        }
        task_data = {
            'tid': task_id,
            'rid': self.repo_rid,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.FINISHED.value
        }
        expected_calls = 3
        arguments_stub = [
            [None, task_data_running],  # 1
            [None, task_data_running],  # 2
            [None, task_data],  # 3 last call  returns finished status
            ['Test HTTP Request Exception', None],  # 4 This should not be called
            [None, task_data_running],  # 5 This should not be called
        ]
        responses = []
        for arguments in arguments_stub:
            if arguments[0] is None:
                responses.append(Response.with_json(status_code=200, json={'task': arguments[1]}))
            else:
                responses.append(Response(status_code=500, text=arguments[0]))

        self.conn.set_responses(responses)

        task = sap.rest.gcts.repo_task.RepositoryTask(self.conn, self.repo_rid, data={'tid': task_id})

        with patch.object(task, 'get_by_id', wraps=task.get_by_id) as spy_get_by_id:

            sap.rest.gcts.simple.wait_for_task_execution(task, wait_for_ready=10, poll_period=1, poll_cb=fake_print_gcts_task_info)
            self.assertEqual(spy_get_by_id.call_count, expected_calls)
            for i, call_args in enumerate(spy_get_by_id.call_args_list):
                args, _kwargs = call_args
                self.assertEqual(args[0], task_id)

            call_count = fake_print_gcts_task_info.call_count
            self.assertEqual(call_count, expected_calls)

            call_args_list = fake_print_gcts_task_info.call_args_list
            self.assertEqual(len(call_args_list), call_count)

            for i, call_args in enumerate(call_args_list):
                args, _kwargs = call_args
                self.assertEqual(len(args), 2,)
                self.assertEqual(args[0], arguments_stub[i][0])
                self.assertIsNone(args[0])

                self.assertEqual(args[1]['status'], arguments_stub[i][1]['status'])
                if i == len(arguments_stub) - 1:
                    self.assertEqual(args[1]['status'], RepositoryTask.TaskStatus.FINISHED.value)

    def test_simple_wait_for_task_execution_timeout(self):
        """Test wait_for_task_execution timeout scenario"""

        task_id = 'test-task-123'
        task_data_running = {
            'tid': task_id,
            'rid': self.repo_rid,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.RUNNING.value
        }

        task = sap.rest.gcts.repo_task.RepositoryTask(self.conn, self.repo_rid, data=task_data_running)

        self.conn.set_responses([
            Response.with_json(status_code=200, json={'task': task_data_running}),
            Response.with_json(status_code=200, json={'task': task_data_running}),
            Response.with_json(status_code=200, json={'task': task_data_running}),
        ])

        with self.assertRaises(sap.errors.OperationTimeoutError) as cm:
            # don't have enough time to wait for the task to finish
            sap.rest.gcts.simple.wait_for_task_execution(task, wait_for_ready=2, poll_period=1)

        expected_message = f'Waiting for the task execution timed out: task {task_id} for repository {self.repo_rid}.'
        self.assertEqual(str(cm.exception), expected_message)

    def test_simple_wait_for_task_execution_aborted(self):
        """Test wait_for_task_execution when task is aborted"""

        task_id = 'test-task-123'
        task_data = {
            'tid': task_id,
            'rid': self.repo_rid,
            'type': RepositoryTask.TaskDefinition.CLONE_REPOSITORY.value,
            'status': RepositoryTask.TaskStatus.ABORTED.value
        }

        task = sap.rest.gcts.repo_task.RepositoryTask(self.conn, self.repo_rid, data=task_data)

        self.conn.set_responses([
            Response.with_json(status_code=200, json={'task': task_data})
        ])

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            sap.rest.gcts.simple.wait_for_task_execution(task, 10, 1)

        expected_message = f'Task execution aborted: task {task_id} for repository {task.rid}.'
        self.assertEqual(str(cm.exception), expected_message)

    def test_simple_fetch_no_repo(self):
        self.conn.set_responses(
            Response.with_json(status_code=200, json={})
        )

        repos = sap.rest.gcts.simple.fetch_repos(self.conn)
        self.assertEqual(len(repos), 0)

    def test_simple_fetch_ok(self):
        REPO_ONE_ID = 0
        repo_one = dict(self.repo_server_data)
        repo_one['name'] = repo_one['rid'] = 'one'

        REPO_TWO_ID = 1
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

        response = sap.rest.gcts.simple.checkout(self.conn, 'the_new_branch', rid=self.repo_rid)
        fake_repository.assert_called_once_with(self.conn, self.repo_rid)
        fake_instance.checkout.assert_called_once_with('the_new_branch')
        self.assertEqual(response, 'probe')

    @patch('sap.rest.gcts.simple.Repository')
    def test_simple_delete_name(self, fake_repository):
        fake_instance = Mock()
        fake_repository.return_value = fake_instance
        fake_instance.delete = Mock()
        fake_instance.delete.return_value = 'probe'

        response = sap.rest.gcts.simple.delete(self.conn, rid=self.repo_rid)
        fake_repository.assert_called_once_with(self.conn, self.repo_rid)
        fake_instance.delete.assert_called_once_with()
        self.assertEqual(response, 'probe')

    def test_simple_delete_repo(self):
        fake_instance = Mock()
        fake_instance.delete.return_value = 'probe'

        response = sap.rest.gcts.simple.delete(None, repo=fake_instance)
        self.assertEqual(response, 'probe')

    @patch('sap.rest.gcts.simple.Repository')
    def test_simple_log_name(self, fake_repository):
        fake_instance = Mock()
        fake_repository.return_value = fake_instance
        fake_instance.log = Mock()
        fake_instance.log.return_value = 'probe'

        response = sap.rest.gcts.simple.log(self.conn, rid=self.repo_rid)
        fake_repository.assert_called_once_with(self.conn, self.repo_rid)
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

        response = sap.rest.gcts.simple.pull(self.conn, rid=self.repo_rid)
        fake_repository.assert_called_once_with(self.conn, self.repo_rid)
        fake_instance.pull.assert_called_once_with()
        self.assertEqual(response, 'probe')

    def test_simple_pull_repo(self):
        fake_instance = Mock()
        fake_instance.pull = Mock()
        fake_instance.pull.return_value = 'probe'

        response = sap.rest.gcts.simple.pull(None, repo=fake_instance)
        self.assertEqual(response, 'probe')

    def test_simple_get_user_credentials(self):
        user_credentials = [{"domain": "url", "endpointType": "THETYPE", "subDomain": "api.url",
                             "endpoint": "https://api.url", "type": "token", "state": "false"}]

        self.conn.set_responses([
            Response.with_json(json={
                'user': {
                    'config': [{'key': 'USER_AUTH_CRED_ENDPOINTS', 'value': json.dumps(user_credentials)}]
                }
            })
        ])

        response = sap.rest.gcts.simple.get_user_credentials(self.conn)

        self.assertEqual(self.conn.mock_methods(), [('GET', 'user')])
        self.conn.execs[0].assertEqual(
            Request.get_json(uri='user'),
            self
        )

        self.assertEqual(response, user_credentials)

    def test_simple_get_user_credentials_no_user_data(self):
        self.conn.set_responses([
            Response.with_json(json={})
        ])

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            sap.rest.gcts.simple.get_user_credentials(self.conn)

        self.assertEqual(self.conn.mock_methods(), [('GET', 'user')])
        self.assertEqual(str(cm.exception), 'gCTS response does not contain \'user\'')

    def test_simple_get_user_credentials_no_config_data(self):
        self.conn.set_responses([
            Response.with_json(json={
                'user': {}
            })
        ])

        response = sap.rest.gcts.simple.get_user_credentials(self.conn)

        self.assertEqual(self.conn.mock_methods(), [('GET', 'user')])
        self.assertEqual(response, [])

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

    def test_simple_delete_user_credentials(self):
        api_url = 'https://api.url'
        response = sap.rest.gcts.simple.delete_user_credentials(self.conn, api_url)

        self.assertEqual(self.conn.mock_methods(), [('POST', 'user/credentials')])
        self.conn.execs[0].assertEqual(
            Request.post_json(
                uri='user/credentials',
                body={
                    'endpoint': api_url,
                    'user': '',
                    'password': '',
                    'token': '',
                    'type': 'none'
                }
            ),
            self
        )

        self.assertEqual(response, None)

    def test_simple_get_system_config_property(self):
        config_key = 'THE_KEY'
        expected_response = {
            'key': config_key,
            'value': 'the_value'
        }

        self.conn.set_responses([
            Response.with_json({'result': expected_response})
        ])

        response = sap.rest.gcts.simple.get_system_config_property(self.conn, config_key)
        self.assertEqual(response, expected_response)

        self.conn.execs[0].assertEqual(
            Request.get_json(
                uri=f'system/config/{config_key}',
            ),
            self
        )

    def test_simple_get_system_config_property_no_result(self):
        self.conn.set_responses([
            Response.with_json({})
        ])

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            sap.rest.gcts.simple.get_system_config_property(self.conn, 'THE_KEY')

        self.assertEqual(str(cm.exception), "gCTS response does not contain 'result'")

    def test_simple_list_system_config(self):
        expected_response = [
            {
                'key': 'THE_KEY1',
                'value': 'THE_VALUE1',
                'category': 'CATEGORY',
                'changedAt': 20220101000000,
                'changedBy': 'TEST',
            },
            {
                'key': 'THE_KEY2',
                'value': 'THE_VALUE2',
                'category': 'CATEGORY',
                'changedAt': 20220101000000,
                'changedBy': 'TEST',
            }
        ]
        self.conn.set_responses([
            Response.with_json({'result': {'config': expected_response}})
        ])

        response = sap.rest.gcts.simple.list_system_config(self.conn)
        self.assertEqual(response, expected_response)

        self.conn.execs[0].assertEqual(
            Request.get_json('system'),
            self
        )

    def test_simple_list_system_config_no_config(self):
        self.conn.set_responses([
            Response.with_json({'result': {}})
        ])

        response = sap.rest.gcts.simple.list_system_config(self.conn)
        self.assertEqual(response, [])

        self.conn.execs[0].assertEqual(
            Request.get_json('system'),
            self
        )

    def test_simple_list_system_config_no_result(self):
        self.conn.set_responses([
            Response.with_json({})
        ])

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            sap.rest.gcts.simple.list_system_config(self.conn)

        self.assertEqual(str(cm.exception), "gCTS response does not contain 'result'")

    def test_simple_set_system_config_property(self):
        config_key = 'THE_KEY'
        value = 'the_value'
        expected_response = {
            'key': config_key,
            'value': value
        }

        self.conn.set_responses([
            Response.with_json({'result': expected_response})
        ])

        response = sap.rest.gcts.simple.set_system_config_property(self.conn, config_key, value)
        self.assertEqual(response, expected_response)

        self.conn.execs[0].assertEqual(
            Request.post_json(
                uri='system/config',
                body={'key': config_key, 'value': value}
            ),
            self
        )

    def test_simple_set_system_config_property_no_result(self):
        self.conn.set_responses([
            Response.with_json({})
        ])

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            sap.rest.gcts.simple.set_system_config_property(self.conn, 'THE_KEY', 'the_value')

        self.assertEqual(str(cm.exception), "gCTS response does not contain 'result'")

    def test_simple_delete_system_config_property(self):
        config_key = 'THE_KEY'
        self.conn.set_responses([
            Response.with_json({})
        ])

        response = sap.rest.gcts.simple.delete_system_config_property(self.conn, config_key)
        self.assertEqual(response, {})

        self.conn.execs[0].assertEqual(
            Request.delete(
                uri=f'system/config/{config_key}',
                headers={'Accept': 'application/json'}
            ),
            self
        )


class TestgCTSSugar(GCTSTestSetUp, unittest.TestCase):

    def setUp(self):
        self.fake_repo = Mock()
        self.progress = sap.rest.gcts.sugar.LogSugarOperationProgress()
        self.new_branch = 'new_branch'

        self.fake_log_info = Mock()
        fake_get_logger = patch('sap.rest.gcts.sugar.get_logger').start()
        fake_get_logger.return_value.info = self.fake_log_info

    @patch.multiple(sap.rest.gcts.sugar.SugarOperationProgress, __abstractmethods__=set())
    def test_sugar_operation_progress(self):
        progress = sap.rest.gcts.sugar.SugarOperationProgress()

        self.assertEqual(progress.recover_message, None)

        with self.assertRaises(NotImplementedError):
            progress.update('message', 'recover_message')

        self.assertEqual(progress.recover_message, 'recover_message')

    def test_log_sugar_operation_progress(self):
        log_msg = 'Log message.'
        recover_msg = 'Recover message.'

        self.progress.update(log_msg, recover_message=recover_msg)

        self.assertEqual(self.progress.recover_message, recover_msg)
        self.fake_log_info.assert_called_once_with(log_msg)

    def test_abap_modifications_disabled_reset(self):
        self.fake_repo.get_config.return_value = ''

        with sap.rest.gcts.sugar.abap_modifications_disabled(self.fake_repo, self.progress):
            log_info_calls = [call('Disabling imports by setting the config VCS_NO_IMPORT = "X" ...'),
                              call('Successfully changed the config VCS_NO_IMPORT = "" -> "X"')]
            self.fake_log_info.assert_has_calls(log_info_calls)
            self.fake_repo.set_config.assert_called_once_with('VCS_NO_IMPORT', 'X')
            self.assertEqual(self.progress.recover_message,
                             'Please set the configuration option VCS_NO_IMPORT = "" manually')

        log_info_calls += [call('Resetting the config VCS_NO_IMPORT = "" ...'),
                           call('Successfully reset the config VCS_NO_IMPORT = ""')]
        self.fake_log_info.assert_has_calls(log_info_calls)
        self.fake_repo.set_config.assert_called_with('VCS_NO_IMPORT', '')
        self.assertEqual(self.progress.recover_message, None)

    def test_abap_modifications_disabled_reset_error(self):
        self.fake_repo.get_config.return_value = ''

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            with sap.rest.gcts.sugar.abap_modifications_disabled(self.fake_repo, self.progress):
                self.fake_repo.set_config.side_effect = sap.rest.errors.SAPCliError('Set of configuration failed.')

        self.assertEqual(str(cm.exception), 'Set of configuration failed.')
        self.assertEqual(self.progress.recover_message,
                         'Please set the configuration option VCS_NO_IMPORT = "" manually')

    def test_abap_modifications_disabled_delete(self):
        self.fake_repo.get_config.return_value = None

        with sap.rest.gcts.sugar.abap_modifications_disabled(self.fake_repo, self.progress):
            log_info_calls = [call('Disabling imports by setting the config VCS_NO_IMPORT = "X" ...'),
                              call('Successfully added the config VCS_NO_IMPORT = "X"')]
            self.fake_log_info.assert_has_calls(log_info_calls)
            self.fake_repo.set_config.assert_called_once_with('VCS_NO_IMPORT', 'X')
            self.assertEqual(self.progress.recover_message,
                             'Please delete the configuration option VCS_NO_IMPORT manually')

        log_info_calls += [call('Removing the config VCS_NO_IMPORT ...'),
                           call('Successfully removed the config VCS_NO_IMPORT')]
        self.fake_log_info.assert_has_calls(log_info_calls)
        self.fake_repo.delete_config.assert_called_once_with('VCS_NO_IMPORT')
        self.assertEqual(self.progress.recover_message, None)

    def test_abap_modifications_disabled_delete_error(self):
        self.fake_repo.get_config.return_value = None

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            with sap.rest.gcts.sugar.abap_modifications_disabled(self.fake_repo, self.progress):
                self.fake_repo.delete_config.side_effect = sap.rest.errors.SAPCliError('Delete config failed.')

        self.assertEqual(str(cm.exception), 'Delete config failed.')
        self.assertEqual(self.progress.recover_message,
                         'Please delete the configuration option VCS_NO_IMPORT manually')

    def test_abap_modifications_disabled_donothing(self):
        self.fake_repo.get_config.return_value = 'X'

        with sap.rest.gcts.sugar.abap_modifications_disabled(self.fake_repo, self.progress):
            log_info_calls = [call('Disabling imports by setting the config VCS_NO_IMPORT = "X" ...'),
                              call('The config VCS_NO_IMPORT was already set to "X"')]
            self.fake_log_info.assert_has_calls(log_info_calls)
            self.fake_repo.set_config.assert_called_once_with('VCS_NO_IMPORT', 'X')

        log_info_calls += [call('The config VCS_NO_IMPORT has not beed changed')]
        self.fake_log_info.assert_has_calls(log_info_calls)
        self.assertEqual(self.progress.recover_message, None)

    def test_abap_modifications_disabled_without_progress(self):
        self.fake_repo.get_config.return_value = 'X'

        with sap.rest.gcts.sugar.abap_modifications_disabled(self.fake_repo):
            log_info_calls = [call('Disabling imports by setting the config VCS_NO_IMPORT = "X" ...'),
                              call('The config VCS_NO_IMPORT was already set to "X"')]
            self.fake_log_info.assert_has_calls(log_info_calls)
            self.fake_repo.set_config.assert_called_once_with('VCS_NO_IMPORT', 'X')

        log_info_calls += [call('The config VCS_NO_IMPORT has not beed changed')]
        self.fake_log_info.assert_has_calls(log_info_calls)

    def test_temporary_switched_branch_checkout(self):
        self.fake_repo.branch = 'old_branch'

        with sap.rest.gcts.sugar.temporary_switched_branch(self.fake_repo, self.new_branch, self.progress):
            log_info_calls = [call(f'Temporary switching to the updated branch {self.new_branch} ...'),
                              call(f'Successfully switched to the updated branch {self.new_branch}')]
            self.fake_log_info.assert_has_calls(log_info_calls)
            self.fake_repo.checkout.assert_called_once_with(self.new_branch)
            self.assertEqual(self.progress.recover_message, 'Please switch to the branch old_branch manually')

        log_info_calls += [call('Restoring the previously active branch old_branch ...'),
                           call('Successfully restored the previously active branch old_branch')]
        self.fake_log_info.assert_has_calls(log_info_calls)
        self.fake_repo.checkout.assert_called_with('old_branch')
        self.assertEqual(self.progress.recover_message, None)

    def test_temporary_switched_branch_checkout_error(self):
        self.fake_repo.branch = 'old_branch'

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            with sap.rest.gcts.sugar.temporary_switched_branch(self.fake_repo, self.new_branch, self.progress):
                self.fake_repo.checkout.side_effect = sap.rest.errors.SAPCliError('Checkout failed.')

        self.assertEqual(str(cm.exception), 'Checkout failed.')
        self.assertEqual(self.progress.recover_message,
                         'Please double check if the original branch old_branch is active')

    def test_temporary_switched_branch_pre_checkout_error(self):
        self.fake_repo.branch = 'old_branch'
        self.fake_repo.checkout.side_effect = sap.rest.errors.SAPCliError('Checkout failed.')

        with self.assertRaises(sap.rest.errors.SAPCliError) as cm:
            with sap.rest.gcts.sugar.temporary_switched_branch(self.fake_repo, self.new_branch, self.progress):
                self.assertEqual(self.progress.recover_message,
                                 'Please double check if the original branch old_branch is active')

        self.assertEqual(str(cm.exception), 'Checkout failed.')

    def test_temporary_switched_branch_donothing(self):
        self.fake_repo.branch = self.new_branch

        with sap.rest.gcts.sugar.temporary_switched_branch(self.fake_repo, self.new_branch, self.progress):
            log_info_calls = [call(f'The updated branch {self.new_branch} is already active')]
            self.fake_log_info.assert_has_calls(log_info_calls)
            self.assertEqual(self.progress.recover_message, None)

        log_info_calls += [call(f'The updated branch {self.new_branch} remains active')]
        self.fake_log_info.assert_has_calls(log_info_calls)
        self.assertEqual(self.progress.recover_message, None)
        self.fake_repo.checkout.assert_not_called()

    def test_temporary_switched_branch_without_progress(self):
        self.fake_repo.branch = self.new_branch

        with sap.rest.gcts.sugar.temporary_switched_branch(self.fake_repo, self.new_branch):
            log_info_calls = [call(f'The updated branch {self.new_branch} is already active')]
            self.fake_log_info.assert_has_calls(log_info_calls)

        log_info_calls += [call(f'The updated branch {self.new_branch} remains active')]
        self.fake_log_info.assert_has_calls(log_info_calls)
        self.fake_repo.checkout.assert_not_called()
