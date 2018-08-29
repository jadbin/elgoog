# coding=utf-8

import random
from urllib.parse import quote

import requests
from flask import Blueprint, request, abort, Response

from elgoog import config
from elgoog.defender import Defender

search_blueprint = Blueprint('search', __name__)

defender = Defender()


@search_blueprint.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    start = data.get('start')
    timestamp = data.get('timestamp')
    nonce = data.get('nonce')
    signature = data.get('signature')

    success, message = defender.verify(query, start, timestamp, nonce, signature)
    if not success:
        return abort(403, message)

    headers = config.default_headers
    headers['User-Agent'] = random_user_agent()
    url = 'https://www.google.com.hk/search?q={}&start={}'.format(quote(query), start)
    resp = requests.get(url, verify=False, timeout=5, headers=headers)
    resp_headers = remove_invalid_response_headers(dict(resp.headers))
    return Response(response=resp.content, status=200, headers=resp_headers)


def remove_invalid_response_headers(headers):
    for i in config.invalid_response_headers:
        if i in headers:
            del headers[i]
    return headers


def random_user_agent():
    chrome_version = '{}.0.{}.{}'.format(random.randint(51, 70),
                                         random.randint(0, 9999), random.randint(0, 99))
    webkit = '{}.{}'.format(random.randint(531, 600), random.randint(0, 99))
    os = 'Macintosh; Intel Mac OS X 10_10_4'
    return ('Mozilla/5.0 ({}) AppleWebKit/{} (KHTML, like Gecko) '
            'Chrome/{} Safari/{}').format(os, webkit, chrome_version, webkit)
