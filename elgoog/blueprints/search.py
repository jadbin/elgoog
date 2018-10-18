# coding=utf-8

import random
from urllib.parse import quote, unquote
import re

import requests
from flask import Blueprint, request, abort, jsonify, Response

from xpaw import Selector

from elgoog import config
from elgoog.defender import Defender
from elgoog.cache import MemCache
from elgoog.errors import ServiceBanError

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
    engine = data.get('engine')
    if engine is None:
        engine = 'Google'

    success, message = defender.verify(query, page, timestamp, nonce, signature)
    if not success:
        return abort(403, message)

    res = cache.get((query, page, engine))
    if res is None:
        headers = config.default_headers
        headers['User-Agent'] = random_user_agent()
        if engine == 'Google':
            if page > 0:
                headers['Referer'] = 'https://www.google.com.hk/search?q={}'.format(quote(query))
            else:
                headers['Referer'] = 'https://www.google.com.hk/'
            url = 'https://www.google.com.hk/search?q={}&start={}'.format(quote(query), page * 10)
        elif engine == 'Yahoo':
            if page > 0:
                headers['Referer'] = 'https://hk.search.yahoo.com/search?p={}'.format(quote(query))
            else:
                headers['Referer'] = 'https://hk.search.yahoo.com/'
            url = 'https://hk.search.yahoo.com/search?p={}&b={}'.format(quote(query), page * 10 + 1)
        elif engine == 'Ask':
            if page > 0:
                headers['Referer'] = 'https://www.search.ask.com/web?q={}'.format(quote(query))
            else:
                headers['Referer'] = 'https://www.search.ask.com/'
            url = 'https://www.search.ask.com/web?q={}&page={}'.format(quote(query), page + 1)
        elif engine == 'Bing':
            if page > 0:
                headers['Referer'] = 'https://www.bing.com/search?q={}'.format(quote(query))
            else:
                headers['Referer'] = 'https://www.bing.com/'
            url = 'https://www.bing.com/search?q={}&first={}'.format(quote(query), page * 10 + 1)
        else:
            return abort(400)
        resp = requests.get(url, verify=False, timeout=4, headers=headers)
        try:
            if resp.status_code / 100 != 2:
                raise ServiceBanError
            res = parse_results(engine, resp)
        except ServiceBanError:
            return Response(status=593)
        cache.update((query, page, engine), res)

    return jsonify(res)


def random_user_agent():
    chrome_version = '{}.0.{}.{}'.format(random.randint(51, 70),
                                         random.randint(0, 9999), random.randint(0, 99))
    webkit = '{}.{}'.format(random.randint(531, 600), random.randint(0, 99))
    os = 'Macintosh; Intel Mac OS X 10_10_4'
    return ('Mozilla/5.0 ({}) AppleWebKit/{} (KHTML, like Gecko) '
            'Chrome/{} Safari/{}').format(os, webkit, chrome_version, webkit)


yahoo_url_reg = re.compile(r'/RU=(.+?)/')


def parse_results(engine, resp):
    res = []
    selector = Selector(resp.text)
    if engine == 'Google':
        if 'google.com.hk/sorry/' in resp.url:
            raise ServiceBanError
        topstuff = selector.css('#topstuff').text
        if len(topstuff) > 0 and '未找到符合' in topstuff[0]:
            pass
        else:
            for item in selector.css('div.g'):
                try:
                    title = item.css('h3')[0].text.strip()
                    text = None
                    span_st = item.css('span.st')
                    if len(span_st) > 0:
                        text = span_st[0].text.strip()
                    url = item.css('div.r>a')[0].attr('href').strip()
                    if text is not None:
                        res.append({'title': title, 'text': text, 'url': url})
                except Exception:
                    pass
    elif engine == 'Yahoo':
        for item in selector.css('div.algo-sr'):
            try:
                title = item.css('h3>a')[0].text.strip()
                text = None
                p_lh_l = item.css('p.lh-l')
                if len(p_lh_l) > 0:
                    text = p_lh_l[0].text.strip()
                url = item.css('h3>a')[0].attr('href').strip()
                url = unquote(yahoo_url_reg.search(url).group(1))
                if text is not None:
                    res.append({'title': title, 'text': text, 'url': url})
            except Exception:
                pass
    elif engine == 'Ask':
        for item in selector.css('li.algo-result'):
            try:
                title = item.css('a.algo-title')[0].text.strip()
                text = None
                span = item.css('span.algo-summary')
                if len(span) > 0:
                    text = span[0].text.strip()
                url = item.css('a.algo-title')[0].attr('href').strip()
                if text is not None:
                    res.append({'title': title, 'text': text, 'url': url})
            except Exception:
                pass
    elif engine == 'Bing':
        for item in selector.css('li.b_algo'):
            try:
                title = item.css('h2>a')[0].text.strip()
                text = None
                span = item.css('div.b_caption>p')
                if len(span) > 0:
                    text = span[0].text.strip()
                url = item.css('h2>a')[0].attr('href').strip()
                if text is not None:
                    res.append({'title': title, 'text': text, 'url': url})
            except Exception:
                pass
    return res
