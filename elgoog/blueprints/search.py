# coding=utf-8

import random
from urllib.parse import quote

import requests
from flask import Blueprint, request, abort, jsonify

from xpaw import Selector

from elgoog import config
from elgoog.defender import Defender
from elgoog.cache import MemCache

search_blueprint = Blueprint('search', __name__)

defender = Defender()
cache = MemCache()


@search_blueprint.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    page = data.get('page')
    timestamp = data.get('timestamp')
    nonce = data.get('nonce')
    signature = data.get('signature')

    success, message = defender.verify(query, page, timestamp, nonce, signature)
    if not success:
        return abort(403, message)

    res = cache.get(query, page)
    if res is None:
        headers = config.default_headers
        headers['User-Agent'] = random_user_agent()
        if page > 0:
            headers['Referer'] = 'https://www.google.com.hk/search?q={}'.format(quote(query))
        else:
            headers['Referer'] = 'https://www.google.com.hk/'
        url = 'https://www.google.com.hk/search?q={}&start={}'.format(quote(query), page * 10)
        resp = requests.get(url, verify=False, timeout=5, headers=headers)
        res = parse_results(resp.text)
        cache.update(query, page, res)

    return jsonify(res)


def random_user_agent():
    chrome_version = '{}.0.{}.{}'.format(random.randint(51, 70),
                                         random.randint(0, 9999), random.randint(0, 99))
    webkit = '{}.{}'.format(random.randint(531, 600), random.randint(0, 99))
    os = 'Macintosh; Intel Mac OS X 10_10_4'
    return ('Mozilla/5.0 ({}) AppleWebKit/{} (KHTML, like Gecko) '
            'Chrome/{} Safari/{}').format(os, webkit, chrome_version, webkit)


def parse_results(text):
    res = []
    selector = Selector(text)
    for item in selector.css('div.g'):
        try:
            title = item.css('h3>a')[0].text.strip()
            text = None
            span_st = item.css('span.st')
            if len(span_st) > 0:
                text = span_st[0].text.strip()
            url = item.css('h3>a')[0].attr('href').strip()
            if text is not None:
                res.append({'title': title, 'text': text, 'url': url})
        except Exception:
            pass
    return res
