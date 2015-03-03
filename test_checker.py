import httpretty
import requests
import unittest

from checker import request_from_api


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
