from bs4 import BeautifulSoup

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


def soupify_html(html_str):
    return BeautifulSoup(html_str)


def extract_item_name(html_soup):
    name = html_soup.find_all('h3', class_='ikea-find-in-store-indent')

    if len(name) == 1:
        return name[0].string

    else:
        return None
