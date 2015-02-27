import httpretty
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


class RequestFromApiTest(unittest.TestCase):

    @httpretty.activate
    def test_successful_api_call_returns_200_status_code(self):
        httpretty.register_uri(httpretty.GET, url_helper('valid'), status=200)
        r = request_from_api(valid_item_id)
        self.assertEqual(r.status_code, 200)

    @httpretty.activate
    def test_api_call_with_invalid_item_id_returns_404_status_code(self):
        httpretty.register_uri(httpretty.GET, url_helper('invalid'), status=404)
        r = request_from_api(invalid_item_id)
        self.assertEqual(r.status_code, 404)
