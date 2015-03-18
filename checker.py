from bs4 import BeautifulSoup

import datetime
import pytz
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


def is_under_maintenance(html_soup):
    title = html_soup.title.string

    if 'maintenance' in title.lower():
        return True

    else:
        return False


def extract_item_name(html_soup):
    name = html_soup.find_all('h3', class_='ikea-find-in-store-indent')

    if len(name) == 1:
        return name[0].string

    else:
        return None


def extract_item_availability(html_soup):
    try:
        container = html_soup.find('div', class_='ikea-stockcheck-result').h3.contents

        if len(container) == 2:
            stock_text = container[0].string
            stock_count = container[1].string[0]

            if stock_text == 'Currently in stock at IKEA Damansara: ':
                return stock_count

        elif len(container) == 1:
            stock_text = container[0].string

            if stock_text == 'Currently not in stock at IKEA Damansara':
                return '0'

    except:
        return None


def extract_item_last_checked(html_soup):
    datetime_unformatted = html_soup.find_all('span', class_='boldDateTime')

    if len(datetime_unformatted) == 2:
        date_unformatted = datetime_unformatted[0].string
        time_unformatted = datetime_unformatted[1].string

        return date_unformatted + ' ' + time_unformatted

    else:
        return None


def convert_to_datetime(raw_datetime_string):
    try:
        datetime_object = datetime.datetime.strptime(raw_datetime_string, "%d.%B.%Y %H:%M %p")
        return datetime_object.replace(tzinfo=pytz.timezone('Asia/Kuala_Lumpur'))

    except:
        return None
