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


def format_money(raw):
    if raw == None or raw == '':
        return None
    else:
        return format(float(raw) / 100.0, ',.2f')


def cash_summary(username, password):
    url = 'https://118.145.29.67:16831/portal/account/report_cash_summary'
    data = {'_password_': password,
            'merchantId': username,
            '_language_': 'zh'}
    r = requests.post(url, data=data, verify=False, timeout=5)
    if r.ok:
        res_json = json.loads(r.text)
        params = res_json.get('params', {})
        error_message = params.get('_message_', '')
        if error_message:
            return False, error_message
        else:
            return True, params
    else:
        return False, r.reason


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
                    set_mytype(item)

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
    exclude_goodsId = ['TS100', 'TS200', 'TS500', 'TS1000']
    cache_key = 'all_googds'
    data = cache.get(cache_key)
    if data == None:
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
                        if not item.get('goodsId') in exclude_goodsId:
                            res.append(item)
            data = res
            cache.set(cache_key, data, 3600)

    return True, data


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


def trading_limit(username, password, goodsId, my_type='money_begin', for_cache=False):
    '''

    :param username:
    :param password:
    :param goodsId:
    :param my_type:money_begin,money_end,goods_begin,goods_end
    :return:
    '''
    cache_key = "trading_limit%s%s%s%s" % (username, password, goodsId, my_type)
    data = cache.get(cache_key)
    if data == None or not for_cache:
        if my_type == 'money_begin':
            method = 'LEND'
            action = 'ACQUIRE'
            isSelling = 0
        elif my_type == 'money_end':
            method = 'LEND'
            action = 'DELIVER'
            isSelling = 1
        elif my_type == 'goods_begin':
            method = 'LEND'
            action = 'ACQUIRE'
            isSelling = 1
        elif my_type == 'goods_end':
            method = 'LEND'
            action = 'DELIVER'
            isSelling = 0
        else:
            raise Exception('my_type error')

        url = 'https://118.145.29.67:16831/portal/trading/report_trading_limits'
        data = {'_password_': password,
                'merchantId': username,
                'goodsId': goodsId,
                'method': method,
                'action': action,
                'isSelling': isSelling,
                '_language_': 'zh'}
        r = requests.post(url, data=data, verify=False)
        res_json = json.loads(r.text)
        params = res_json.get('params', {})
        error_message = params.get('_message_', '')
        if error_message:
            return False, error_message
        else:
            data = int(params.get('limit', 0))
            cache.set(cache_key, data, 300)
            return True, data
    return True, data


def submit_order(username, password, goodsId, order_count, my_type='money_begin'):
    '''
    提交申购请求
    :param username:
    :param password:
    :param goodsId:
    :param my_type:money_begin,money_end,goods_begin,goods_end
    :return:
    '''
    if my_type == 'money_begin':
        method = 'LEND'
        action = 'ACQUIRE'
        isSelling = 0
    elif my_type == 'money_end':
        method = 'LEND'
        action = 'DELIVER'
        isSelling = 1
    elif my_type == 'goods_begin':
        method = 'LEND'
        action = 'ACQUIRE'
        isSelling = 1
    elif my_type == 'goods_end':
        method = 'LEND'
        action = 'DELIVER'
        isSelling = 0
    else:
        raise Exception('my_type error')

    url = 'https://118.145.29.67:16831/portal/trading/submit_order'
    data = {'_password_': password,
            'merchantId': username,
            'goodsId': goodsId,
            'method': method,
            'action': action,
            'isSelling': isSelling,
            'quantity': order_count,
            'type': 'LIMIT',
            'style': 'NORMAL',
            '_language_': 'zh'}
    r = requests.post(url, data=data, verify=False)
    res_json = json.loads(r.text)
    params = res_json.get('params', {})
    error_message = params.get('_message_', '')
    if error_message:
        return False, error_message
    else:
        return True, ''


def set_mytype(item):
    if item.get('method') == 'ORDER' and item.get('action') == 'ACQUIRE' and \
                    item.get('isSelling') == 0:
        item['my_type'] = u'买入（委托）'
    elif item.get('method') == 'ORDER' and item.get('action') == 'DELIVER' and \
                    item.get('isSelling') == 0:
        item['my_type'] = u'买入（委托）还款收货申报'
    elif item.get('method') == 'ORDER' and item.get('action') == 'TRANSFER' and \
                    item.get('isSelling') == 0:
        item['my_type'] = u'卖出（委托）终止'
    elif item.get('method') == 'ORDER' and item.get('action') == 'ACQUIRE' and \
                    item.get('isSelling') == 1 and item.get('isOnGoods') == 1:
        item['my_type'] = u'卖出（申报）'
    elif item.get('method') == 'ORDER' and item.get('action') == 'ACQUIRE' and \
                    item.get('isSelling') == 1 and item.get('isOnGoods') == 0:
        item['my_type'] = u'卖出（委托）'
    elif item.get('method') == 'ORDER' and item.get('action') == 'DELIVER' and \
                    item.get('isSelling') == 1:
        item['my_type'] = u'卖出（申报）终止'
    elif item.get('method') == 'ORDER' and item.get('action') == 'TRANSFER' and \
                    item.get('isSelling') == 1:
        item['my_type'] = u'买入（委托）终止'
    elif item.get('method') == 'LEND' and item.get('action') == 'DELIVER' and \
                    item.get('isSelling') == 0:
        item['my_type'] = u'货物受托终止'
    elif item.get('method') == 'LEND' and item.get('action') == 'ACQUIRE' and \
                    item.get('isSelling') == 0:
        item['my_type'] = u'资金（受托）'
    elif item.get('method') == 'LEND' and item.get('action') == 'DELIVER' and \
                    item.get('isSelling') == 1:
        item['my_type'] = u'资金受托终止'
    elif item.get('method') == 'LEND' and item.get('action') == 'ACQUIRE' and \
                    item.get('isSelling') == 1:
        item['my_type'] = u'货物（受托）'
    else:
        item['my_type'] = u"method:%s,action:%s,isSelling:%s" % (
            item.get('method'), item.get('action'), item.get('isSelling'))


def consolidated(username, password):
    '''
    交易资产汇总
    :param username:
    :param password:
    :return:
    '''
    url = 'https://118.145.29.67:16831/portal/trading/report_consolidated_contracts'
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
        columns = tables.get('consolidated', {}).get('columns', None)
        if columns:
            rows = tables.get('consolidated', {}).get('rows', None)
            if rows:
                for row in rows:
                    item = {}
                    for i in range(0, len(row)):
                        item[columns[i]] = row[i]

                    set_mytype(item)
                    item['price'] = float(item['price']) / 100
                    item['lendingDiff'] = float(item['lendingDiff']) / 100
                    item['financingDiff'] = float(item['financingDiff']) / 100
                    item['orderingDiff'] = float(item['orderingDiff']) / 100

                    res.append(item)
        return True, res


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


