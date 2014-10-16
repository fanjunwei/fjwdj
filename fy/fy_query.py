# coding=utf-8
__author__ = 'fanjunwei003'
import httplib, urllib
import json

GoodsIds = {"IN": "铟", "GE": "锗", "CO": "电积钴", "APT": "仲钨酸铵", "GA": "金属镓", "BI": "铋",
            "AG": "白银", "VP": "五氧化二钒", "SB": "锑锭", "TE": "碲", "SE": "硒粉",
            # "SI": "硅","TS100": "银条", "TS200": "银条", "TS500": "银条", "TS1000": "银条"
}


def getMoneyInfo(goodsId):
    res = {}
    params = urllib.urlencode({'goodsId': goodsId})
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    conn = httplib.HTTPConnection("118.145.29.68:16850")
    conn.request(method="POST", url="/quotation/quotecast/report_financing_market_digest", body=params, headers=headers)
    response = conn.getresponse()
    data = response.read()
    js = json.loads(data)
    moneySupplyRequested = js['params'].get('moneySupplyRequested', None)
    moneySupply = js['params'].get('moneySupply', None)

    if moneySupplyRequested and moneySupply and float(moneySupply) != 0:
        ratio = float(moneySupplyRequested) / float(moneySupply)*100
    else:
        ratio = None
    conn.close()
    recommendation = js['params'].get('recommendation', None)
    financePrice = js['params'].get('financePrice', None)
    if recommendation and financePrice:
        mini = min(float(recommendation), float(financePrice))/100.0
    elif recommendation:
        mini = float(recommendation)/100.0
    elif financePrice:
        mini = float(financePrice)/100.0
    else:
        mini = 0

    res['name'] = GoodsIds.get(goodsId, '') + goodsId
    res['moneySupplyRequested'] = moneySupplyRequested
    res['moneySupply'] = moneySupply

    res['ratio'] = ratio
    res['recommendation'] = recommendation
    res['financePrice'] = financePrice
    if moneySupplyRequested:
        res['m1'] = int(moneySupplyRequested) * mini
    else:
        res['m1'] = 0
    if financePrice:
        res['m2'] = int(financePrice) * mini
    else:
        res['m2'] = 0
    return res


def GoodsCMP(v1, v2):
    r1 = 0
    r2 = 0
    if v1['ratio']:
        r1 = v1['ratio']
    if v2['ratio']:
        r2 = v2['ratio']
    return -cmp(r1, r2)



