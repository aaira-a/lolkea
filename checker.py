import requests


def request_from_api(item_id):

    URL = 'http://m.ikea.com/my/en/store/availability/?'
    DATA = {'storeCode': '438', 'itemType': 'art', 'itemNo': item_id}

    return requests.get(URL, params=DATA)
