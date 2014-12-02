# coding=utf-8
# Date: 14/12/1
# Time: 12:59
# Email:fanjunwei003@163.com
import json
import requests
from django.core.cache import cache

__author__ = u'范俊伟'


def login(username, password):
    url = 'https://118.145.29.67:16831/portal/member/report_account_info'
    data = {'_password_': password,
            'merchantId': username,
            '_language_': 'zh'}
    r = requests.post(url, data=data, verify=False)
    res_json = json.loads(r.text)

    status = res_json.get('params', {}).get('status', None)
    if status == 'ACTIVE':
        return True, res_json.get('params', {}).get('merchantName', '')
    else:
        return False, res_json.get('params', {}).get('_message_', '')


def cash_summary(username, password):
    url = 'https://118.145.29.67:16831/portal/account/report_cash_summary'
    data = {'_password_': password,
            'merchantId': username,
            '_language_': 'zh'}
    r = requests.post(url, data=data, verify=False)
    res_json = json.loads(r.text)
    params = res_json.get('params', {})
    error_message = params.get('_message_', '')
    if error_message:
        return False, error_message
    else:
        return True, params


def pending_orders(username, password):
    '''
    未成交查询
    :param username:
    :param password:
    :return:
    '''
    url = 'https://118.145.29.67:16831/portal/trading/report_pending_orders'
    data = {'_password_': password,
            'merchantId': username,
            '_language_': 'zh'}
    r = requests.post(url, data=data, verify=False)
    res_json = json.loads(r.text)
    params = res_json.get('params', {})
    tables = res_json.get('tables')
    error_message = params.get('_message_', '')
    if error_message:
        return False, error_message
    else:
        res = []
        columns = tables.get('orders', {}).get('columns', None)
        if columns:
            rows = tables.get('orders', {}).get('rows', None)
            if rows:
                for row in rows:
                    item = {}
                    for i in range(0, len(row)):
                        item[columns[i]] = row[i]
                    if item.get('method') == 'LEND' and item.get('action') == 'ACQUIRE':
                        item['my_type'] = '资金受托'
                    elif item.get('method') == 'LEND' and item.get('action') == 'DELIVER':
                        item['my_type'] = '资金受托终止'
                    else:
                        item['my_type'] = item.get('method') + ":" + item.get('action')

                    res.append(item)
        return True, res


def cancel_order(username, password, orderId):
    url = 'https://118.145.29.67:16831/portal/trading/cancel_order'
    data = {'_password_': password,
            'merchantId': username,
            'orderId': orderId,
            '_language_': 'zh'}
    r = requests.post(url, data=data, verify=False)
    res_json = json.loads(r.text)
    params = res_json.get('params', {})
    error_message = params.get('_message_', '')
    if error_message:
        return False, error_message
    else:
        return True, params


def all_googds():
    url = 'http://118.145.29.68:16850/quotation/quotecast/report_trading_market_all_prices'
    data = {'_language_': 'zh'}
    r = requests.post(url, data=data, verify=False)
    res_json = json.loads(r.text)
    params = res_json.get('params', {})
    tables = res_json.get('tables')
    error_message = params.get('_message_', '')
    if error_message:
        return False, error_message
    else:
        res = []
        columns = tables.get('goods', {}).get('columns', None)
        if columns:
            rows = tables.get('goods', {}).get('rows', None)
            if rows:
                for row in rows:
                    item = {}
                    for i in range(0, len(row)):
                        item[columns[i]] = row[i]
                    res.append(item)
        return True, res


def get_money_info(goodsId, goodsName):
    res = {}
    # params = urllib.urlencode({'goodsId': goodsId})
    # headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # conn = httplib.HTTPConnection("118.145.29.68:16850")
    # conn.request(method="POST", url="/quotation/quotecast/report_financing_market_digest", body=params, headers=headers)
    # response = conn.getresponse()
    # data = response.read()
    # js = json.loads(data)
    url = 'http://118.145.29.68:16850/quotation/quotecast/report_financing_market_digest'
    data = {'goodsId': goodsId}
    r = requests.post(url, data=data, verify=False)
    js = json.loads(r.text)
    params = js.get('params', {})
    error_message = params.get('_message_', '')
    if error_message:
        return False, error_message
    else:
        moneySupplyRequested = js['params'].get('moneySupplyRequested', None)
        moneySupply = js['params'].get('moneySupply', None)

        if moneySupplyRequested and moneySupply and float(moneySupply) != 0:
            ratio = float(moneySupplyRequested) / float(moneySupply) * 100
        else:
            ratio = None
        recommendation = js['params'].get('recommendation', None)
        financePrice = js['params'].get('financePrice', None)
        if recommendation and financePrice:
            mini = min(float(recommendation), float(financePrice)) / 100.0
        elif recommendation:
            mini = float(recommendation) / 100.0
        elif financePrice:
            mini = float(financePrice) / 100.0
        else:
            mini = 0

        res['name'] = goodsName
        res['id'] = goodsId
        if moneySupplyRequested:
            res['moneySupplyRequested'] = format(int(moneySupplyRequested), ',')
        else:
            res['moneySupplyRequested'] = None
        if moneySupply:
            res['moneySupply'] = format(int(moneySupply), ',')
        else:
            res['moneySupply'] = None
        res['ratio'] = ratio
        if ratio:
            res['ratio_format'] = format(float(ratio), ',.2f')
        else:
            res['ratio_format'] = ''
        if recommendation:
            res['recommendation'] = format(float(recommendation) / 100.0, ',.2f')
        else:
            res['recommendation'] = None
        if financePrice:
            res['financePrice'] = format(float(financePrice) / 100.0, ',.2f')
        else:
            res['financePrice'] = None

        if moneySupplyRequested:
            res['m1'] = int(moneySupplyRequested) * mini
        else:
            res['m1'] = 0

        if moneySupply:
            res['m2'] = int(moneySupply) * mini
        else:
            res['m2'] = 0
        return True, res


def goods_CMP(v1, v2):
    r1 = 0
    r2 = 0
    if v1['ratio']:
        r1 = v1['ratio']
    if v2['ratio']:
        r2 = v2['ratio']
    return -cmp(r1, r2)


def trading_limit(username, password, goodsId):
    cache_key = "trading_limit%s%s%s" % (username, password, goodsId)
    data = cache.get(cache_key)
    if not data:
        url = 'https://118.145.29.67:16831/portal/trading/report_trading_limits'
        data = {'_password_': password,
                'merchantId': username,
                'goodsId': goodsId,
                'method': 'LEND',
                'action': 'ACQUIRE',
                'isSelling': '0',
                '_language_': 'zh'}
        r = requests.post(url, data=data, verify=False)
        res_json = json.loads(r.text)
        params = res_json.get('params', {})
        error_message = params.get('_message_', '')
        if error_message:
            return False, error_message
        else:
            data = int(params.get('limit', 0))
            cache.set(cache_key, data)
            return True, data
    return True, data


if __name__ == '__main__':
    check, res = trading_limit('0724000238', '618033', 'SB')
    check, res = all_googds()
    if check:
        for item in res:
            goodsId = item.get('goodsId')
            goodsName = item.get('goodsName')
            check, res = get_money_info(goodsId, goodsName)
            print res
            pass


