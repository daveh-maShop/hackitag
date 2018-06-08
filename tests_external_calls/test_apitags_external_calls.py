import datetime
import json
import os
import unittest
import uuid

from mashop.microtoolkit.toolkit import status_codes, APIError

from mashop.sql_server import get_sql_connection, get_sql_cursor, execute_sql_statement
from src.mashop.warehouse.rfid import http_get, http_post, get_scanned_date, update_backend, get_view_data
from tests.common import Request, Response, set_environment


class TestRFID(unittest.TestCase):
    def setUp(self):
        set_environment()
        self.req = Request()
        self.resp = Response()
        self.params = ''
        self.req.body = ''
        self.req.params = ''
        self.date_formatting = '%m-%d-%Y'

    def test_get_view_data_with_valid_scanned_date(self):
        self.req.params = {'scanned_date': datetime.datetime.now().strftime(self.date_formatting)}
        test_result = get_view_data(get_scanned_date(self.params))
        self.assertIsInstance(test_result, list, msg='Failed get_view_data_with_valid_scanned_date test.')

    def test_get_view_data_with_missing_scanned_date(self):
        test_result = get_view_data(get_scanned_date(self.params))
        self.assertIsInstance(test_result, list, msg='Failed get_view_data_with_missing_scanned_date test.')

    def test_http_get_with_valid_scanned_date(self):
        self.req.correlation_id = str(uuid.uuid4())
        self.req.params = {'scanned_date': '04-30-2018'}
        http_get(self.req, self.resp, self.params)
        resp_body = json.loads(self.resp.body)
        activity_list = resp_body['data']['data']

        self.assertEqual(status_codes.HTTP_200, self.resp.status, msg='Failed post warehouse HTTP code test')
        self.assertIsInstance(activity_list, list, msg='Failed post warehouse body data type test')

    def test_http_get_without_scanned_date(self):
        self.req.correlation_id = str(uuid.uuid4())
        http_get(self.req, self.resp, self.params)
        resp_body = json.loads(self.resp.body)
        activity_list = resp_body['data']['data']

        self.assertEqual(status_codes.HTTP_200, self.resp.status, msg='Failed post warehouse HTTP code test')
        self.assertIsInstance(activity_list, list, msg='Failed post warehouse body data type test')

    def test_http_post_with_valid_scanned_date(self):
        self.req.correlation_id = str(uuid.uuid4())
        self.params = {'scanned_date': '04-30-2018'}
        http_post(self.req, self.resp, self.params)
        resp_body = json.loads(self.resp.body)

        self.assertEqual(status_codes.HTTP_200, self.resp.status, msg='Failed post HTTP code test')
        self.assertIn('transaction_id', resp_body['data'], msg='Failed post  body data has transaction id key')
        self.assertIsInstance(resp_body['data']['transaction_id'], str, msg='Failed post transaction id data type test')

    def test_http_post_with_missing_scanned_date(self):
        self.req.correlation_id = str(uuid.uuid4())
        http_post(self.req, self.resp, self.params)
        resp_body = json.loads(self.resp.body)

        self.assertEqual(status_codes.HTTP_200, self.resp.status, msg='Failed post HTTP code test')
        self.assertIn('transaction_id', resp_body['data'], msg='Failed post  body data has transaction id key')
        self.assertIsInstance(resp_body['data']['transaction_id'], str, msg='Failed post transaction id data type test')


class TestRFIDFailures(unittest.TestCase):
    def setUp(self):
        set_environment()
        self.req = Request()
        self.resp = Response()
        self.params = ''
        self.req.params = ''
        self.req.body = ''

    # common routine for testing failure variations for sql connection parameters
    def sql_connection_test(self, cause_script, failed_msg):
        with self.assertRaises(APIError) as context:
            get_sql_connection()
        self.assertEqual(context.exception.cause,
                         cause_script,
                         msg=failed_msg)

    def test_http_get_with_invalid_scanned_date(self):
        self.req.correlation_id = str(uuid.uuid4())
        http_get(self.req, self.resp, self.params)
        self.req.params = {'scanned_date': 'bad scanned date'}
        resp_body = json.loads(self.resp.body)
        activity_list = resp_body['data']['data']

        self.assertEqual(status_codes.HTTP_200, self.resp.status, msg='Failed post warehouse HTTP code test')
        self.assertIsInstance(activity_list, list, msg='Failed post warehouse body data type test')

    def test_rfid_bad_sql_driver(self):
        os.environ['SQL_DRIVER'] = "Bad SQL Server driver for this test's purposes"
        self.sql_connection_test('InterfaceError occurred', 'Failed SQL Bad SQL Driver test.')

    def test_rfid_bad_sql_connection_string(self):
        os.environ['SQL_SERVER'] = '0.0.0.0'
        os.environ['SQL_PORT'] = '?'
        self.sql_connection_test('OperationalError occurred', 'Failed SQL Bad SQL SERVER Connection test.')

    def test_rfid_bad_sql_database(self):
        os.environ['SQL_DATABASE'] = "bad_database"
        self.sql_connection_test('InterfaceError occurred', 'Failed Bad SQL DATABASE Connection test.')

    def test_rfid_bad_sql_uid(self):
        os.environ['SQL_UID'] = "bad_UID"
        self.sql_connection_test('InterfaceError occurred', 'Failed Bad SQL UID test.')

    def test_rfid_bad_sql_pwd(self):
        os.environ['SQL_PWD'] = "bad_UID"
        self.sql_connection_test('InterfaceError occurred', 'Failed Bad SQL PWD test.')

    def test_rfid_bad_sql_cursor(self):
        connection = None
        with self.assertRaises(APIError) as context:
            get_sql_cursor(connection)
        self.assertEqual(context.exception.cause, 'AttributeError occurred', msg='Failed Bad SQL Cursor test.')

    def test_rfid_sql_query_failed(self):
        connection = get_sql_connection()
        cursor = get_sql_cursor(connection)
        statement = 'bad sql statement'
        with self.assertRaises(APIError) as context:
            execute_sql_statement(cursor, statement)
        self.assertEqual(context.exception.cause, 'ProgrammingError occurred', msg='Failed Bad SQL Cursor test.')

    def test_update_backend_request_http_timeout(self):
        os.environ['HTTP_REQUEST_TIMEOUT'] = '.001'
        with self.assertRaises(APIError) as context:
            update_backend([], 'test_correlation_id')
        self.assertEqual(context.exception.cause, 'Bad host/port/path/connection',
                         msg='Failed Update Backend Timeout test.')

    def test_update_backend_request_bad_http_host(self):
        os.environ['HTTP_REQUEST_HOST'] = 'bad_http_request_host'
        with self.assertRaises(APIError) as context:
            update_backend([], str(uuid.uuid4()))
        self.assertEqual(context.exception.cause, 'Bad host/port/path/connection',
                         msg='Failed Update Backend Bad REST Host test.')

    def test_update_backend_request_bad_http_port(self):
        os.environ['HTTP_REQUEST_PORT'] = '9999'
        with self.assertRaises(APIError) as context:
            update_backend([], str(uuid.uuid4()))
        self.assertEqual(context.exception.cause, 'Bad host/port/path/connection',
                         msg='Failed Update Backend Bad HTTP Port test.')

    def test_update_backend_request_bad_http_path(self):
        os.environ['HTTP_REQUEST_PATH'] = 'bad/http/path'
        with self.assertRaises(APIError) as context:
            update_backend([], str(uuid.uuid4()))
        self.assertEqual(context.exception.cause, 'Problem with backend HTTP request.',
                         msg='Failed Update Backend Bad HTTP Path test.')
