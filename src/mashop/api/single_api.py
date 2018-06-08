import json

import pprint
import requests
from mashop.microtoolkit import APIError
from mashop.microtoolkit.toolkit import handle_exception, status_codes
from mashop.api.all_apis import get_cookie_headers


def get_single_api_data(api_name, api_version):
    header_data = get_cookie_headers()
    url = 'http://devapi2.shop.com/amp/portal/api/{0}/{1}'.format(api_name, api_version)
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


def get_single_api_tags(api_name, api_version):
    api_data = get_single_api_data(api_name, api_version)
    return api_data['info']['tags'].split(',')


def update_api_tags(api_name, api_version, tags):
    api_data = get_single_api_data(api_name, api_version)
    api_data['info']['tags'] = ",".join(tags)
    body = json.dumps(api_data)
    header_data = get_cookie_headers()
    header_data['Content-Type'] = 'application/json'
    url = 'http://devapi2.shop.com/amp/portal/api/update?oldname={0}&oldversion={1}'.format(api_name, api_version)
    try:
        r = requests.post(url, headers=header_data, data=body, timeout=10)
        r.encoding = 'UTF-8'
        if r.status_code == 200:
            response_data = json.loads(r.text)
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


def http_get(request, response, params):
    """Resource =
    /apitags-micro/apitags/v1/api/{api_name}/version/{api_version}
    """
    api_data = get_single_api_tags(params['api_name'], params['api_version'])
    body = json.dumps({"data": api_data})
    response.body = body


def http_put(request, response, params):
    tags = request.body['tags']
    update_api_tags(params['api_name'], params['api_version'], tags)
    response.body = ''
    response.status = status_codes.HTTP_NO_CONTENT


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(get_single_api_data('suggest', 'v1'))
    pp.pprint(get_single_api_tags('suggest', 'v1'))
