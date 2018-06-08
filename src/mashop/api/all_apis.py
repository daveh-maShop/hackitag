import json

import pprint
import requests
from mashop.microtoolkit import APIError
from mashop.microtoolkit.toolkit import handle_exception


def get_cookie_headers():
    url = 'http://devapi2.shop.com/amp/portal/login'
    body = json.dumps({'username': 'maeagle\\daveh', 'password': 'Evrdy_Bun2y'})
    header = {'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}
    try:
        r = requests.post(url, headers=header, data=body, timeout=10)
        r.encoding = 'UTF-8'
        if r.status_code == 200:
            cookie_headers = {}
            cookie_headers['Cookie'] = r.headers._store['set-cookie'][1].split(';')[0]
            cookie_headers['X-XSRF-TOKEN'] = cookie_headers['Cookie'].split('=')[1]
            return cookie_headers
        else:
            custom_exception = Exception({'message': 'Bad backend HTTP request. HTTP Status: ' + str(r.status_code)})
            handle_exception(code='Bad backend HTTP request',
                             cause='Problem with backend HTTP request.',
                             error=custom_exception)
    except APIError as a_e:
        raise a_e
    except Exception as e:
        handle_exception(code='Failure making http request',
                         cause='Bad host/port/path/connection',
                         error=e)

def get_all_apis():
    header_data = get_cookie_headers()
    url = 'http://devapi2.shop.com/amp/portal/api/getallpublicapis'
    try:
        r = requests.get(url, headers=header_data, timeout=10)
        r.encoding = 'UTF-8'
        response_data = json.loads(r.text)
        if r.status_code == 200:
            return response_data
        else:
            custom_exception = Exception({'message': 'Bad backend HTTP request. HTTP Status: ' + str(r.status_code)})
            handle_exception(code='Bad backend HTTP request',
                             cause='Problem with backend HTTP request.',
                             error=custom_exception)
    except APIError as a_e:
        raise a_e
    except Exception as e:
        handle_exception(code='Failure making http request',
                         cause='Bad host/port/path/connection',
                         error=e)


def get_all_apis_select_info():
    all_api_data = get_all_apis()
    api_select_info = []
    for api_data in all_api_data:
        api_select_info.append({'api_name': api_data['name'], 'api_version': api_data['apiVersion'],
                                'api_tags': api_data['info']['tags'].split(',')})
    return sorted(api_select_info, key=lambda k: k['api_name'])


def get_api_tags_list():
    all_api_data = get_all_apis()
    tags_set = set()
    for api_data in all_api_data:
        tags = api_data['info']['tags'].split(',')
        for tag in tags:
            tags_set.add(tag)
    tags_list = list(tags_set)
    tags_list.remove('')
    return list(tags_list)

def get_apis_missing_tags_list():
    all_api_data = get_all_apis()
    apis_missing_tags_list = []
    for api_data in all_api_data:
        if api_data['info']['tags'] == '':
            apis_missing_tags_list.append(api_data['name'])
    return apis_missing_tags_list


def http_get(request, response, params):
    """Resource =
    /apitags-micro/apitags/v1/apis
    """
    api_data = get_all_apis_select_info()
    body = json.dumps({"data": api_data})
    response.body = body


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint((get_all_apis()))
    pp.pprint(get_all_apis_select_info())
    # pp.pprint(get_api_tags_list())
    # pp.pprint(get_apis_missing_tags_list())

