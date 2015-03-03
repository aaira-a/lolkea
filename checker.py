import requests


def request_from_api(item_id):

    URL = 'http://m.ikea.com/my/en/store/availability/?'
    DATA = (('storeCode', '438'), ('itemType', 'art'), ('itemNo', item_id))

    try:
        return requests.get(URL, params=DATA)

    except:
        return None


def is_status_code_200(response):
    return bool(response.status_code == 200)
