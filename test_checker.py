import httpretty
import requests
import unittest

from unittest.mock import Mock

from bs4 import BeautifulSoup

from checker import (
    extract_item_availability,
    extract_item_last_checked,
    extract_item_name,
    is_status_code_200,
    request_from_api,
    soupify_html,
)


base_api_url = 'http://m.ikea.com/my/en/store/availability/?storeCode=438&itemType=art&itemNo='

valid_item_id = 60192954
invalid_item_id = 6019295488888


def url_helper(item_type):
    if item_type == 'valid':
        itemNo = valid_item_id

    elif item_type == 'invalid':
        itemNo = invalid_item_id

    return base_api_url + str(itemNo)


def ConnectionError_callback(request, uri, headers):
    raise requests.exceptions.ConnectionError


def HTTPError_callback(request, uri, headers):
    raise requests.exceptions.HTTPError


def Timeout_callback(request, uri, headers):
    raise requests.exceptions.Timeout


def TooManyRedirects_callback(request, uri, headers):
    raise requests.exceptions.TooManyRedirects


def RequestException_callback(request, uri, headers):
    raise requests.exceptions.RequestException


def html_fixture_loader(file_path):
    with open(file_path, 'r', newline='') as f:
        return f.read()


class RequestFromApiTest(unittest.TestCase):

    @httpretty.activate
    def test_successful_api_call_returns_200_status_code(self):
        httpretty.register_uri(httpretty.GET, url_helper('valid'), status=200)
        r = request_from_api(valid_item_id)
        self.assertIn(httpretty.last_request().path, url_helper('valid'))
        self.assertEqual(r.status_code, 200)

    @httpretty.activate
    def test_api_call_with_invalid_item_id_returns_404_status_code(self):
        httpretty.register_uri(httpretty.GET, url_helper('invalid'), status=404)
        r = request_from_api(invalid_item_id)
        self.assertIn(httpretty.last_request().path, url_helper('invalid'))
        self.assertEqual(r.status_code, 404)


class StatusCodeCheckerTest(unittest.TestCase):

    def test_response_code_checker_should_return_true_for_status_code_200(self):
        r = Mock()
        r.status_code = 200
        self.assertTrue(is_status_code_200(r))

    def test_response_code_checker_should_return_false_for_status_code_other_than_200(self):
        r = Mock()
        status_codes = [100, 101, 102, 103, 122,
                        201, 202, 203, 204, 205, 206, 207, 208, 226,
                        300, 301, 302, 303, 304, 305, 306, 307, 308,
                        400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415,
                        416, 417, 418, 422, 423, 424, 425, 426, 428, 429, 431, 444, 449, 450, 451, 499,
                        500, 501, 502, 503, 504, 505, 506, 507, 509, 510,
                        ' ', 'a', None]

        for code in status_codes:
            r.status_code = code
            self.assertFalse(is_status_code_200(r))


class RequestsExceptionHelperTest(unittest.TestCase):

    @httpretty.activate
    def raise_request_exceptions(self, callback):
        httpretty.register_uri(httpretty.GET, url_helper('valid'), body=callback)
        with self.assertRaises(requests.exceptions.RequestException):
            requests.get(url_helper('valid'))
        self.assertIn(httpretty.last_request().path, url_helper('valid'))

    def test_ConnectionError_should_raise_RequestException(self):
        self.raise_request_exceptions(ConnectionError_callback)

    def test_HTTPError_should_raise_RequestException(self):
        self.raise_request_exceptions(HTTPError_callback)

    def test_Timeout_should_raise_RequestException(self):
        self.raise_request_exceptions(Timeout_callback)

    def test_TooManyRedirects_should_raise_RequestException(self):
        self.raise_request_exceptions(TooManyRedirects_callback)

    def test_RequestException_should_raise_RequestException(self):
        self.raise_request_exceptions(RequestException_callback)


class RequestFromApiExceptionHandlingTest(unittest.TestCase):

    @httpretty.activate
    def simulate_api_request_exceptions(self, callback):
        httpretty.register_uri(httpretty.GET, url_helper('valid'), body=callback)
        r = request_from_api(valid_item_id)
        self.assertIsNone(r)
        self.assertIn(httpretty.last_request().path, url_helper('valid'))

    def test_request_with_ConnectionError_should_return_none_response(self):
        self.simulate_api_request_exceptions(ConnectionError_callback)

    def test_request_with_HTTPError_should_return_none_response(self):
        self.simulate_api_request_exceptions(HTTPError_callback)

    def test_request_with_Timeout_should_return_none_response(self):
        self.simulate_api_request_exceptions(Timeout_callback)

    def test_request_with_TooManyRedirects_should_return_none_response(self):
        self.simulate_api_request_exceptions(TooManyRedirects_callback)

    def test_request_with_RequestException_should_return_none_response(self):
        self.simulate_api_request_exceptions(RequestException_callback)


class ParseHtmlTest(unittest.TestCase):

    def test_fixture_loader_helper_should_return_html_string(self):
        output = html_fixture_loader('fixtures/valid_instock.html')
        self.assertIn('<script>', output)
        self.assertIsInstance(output, str)

    def test_soupify_html_should_return_soup_object(self):
        expected_soup = soupify_html('<h1>')
        self.assertIsInstance(expected_soup, BeautifulSoup)

    def test_extract_item_name_should_return_name_if_it_exists(self):
        soup = BeautifulSoup(html_fixture_loader('fixtures/valid_instock.html'))
        self.assertEqual(extract_item_name(soup), 'LENNART')

    def test_extract_item_name_should_return_none_if_it_doesnt_exist(self):
        soup = BeautifulSoup(html_fixture_loader('fixtures/invalid_item.html'))
        self.assertEqual(extract_item_name(soup), None)

    def test_extract_item_availability_should_return_stock_count_if_it_exists(self):
        soup = BeautifulSoup(html_fixture_loader('fixtures/valid_instock.html'))
        self.assertEqual(extract_item_availability(soup), '4')

    def test_extract_item_availability_should_return_none_if_container_doesnt_exist(self):
        soup = BeautifulSoup(html_fixture_loader('fixtures/invalid_item.html'))
        self.assertEqual(extract_item_availability(soup), None)

    def test_extract_item_last_checked_should_return_datetime_string(self):
        soup = BeautifulSoup(html_fixture_loader('fixtures/valid_instock.html'))
        expected_datetime_unformatted = ['3.March.2015', '19:06 PM']
        self.assertEqual(extract_item_last_checked(soup), expected_datetime_unformatted)

    def test_extract_item_last_checked_should_return_none_if_datetime_string_doesnt_exist(self):
        soup = BeautifulSoup(html_fixture_loader('fixtures/invalid_item.html'))
        self.assertEqual(extract_item_last_checked(soup), None)
