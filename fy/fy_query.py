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
        ratio = float(moneySupplyRequested) / float(moneySupply) * 100
    else:
        ratio = None
    conn.close()
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

    res['name'] = GoodsIds.get(goodsId, '')
    res['id']=goodsId
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
    return res


def GoodsCMP(v1, v2):
    r1 = 0
    r2 = 0
    if v1['ratio']:
        r1 = v1['ratio']
    if v2['ratio']:
        r2 = v2['ratio']
    return -cmp(r1, r2)

def getFyMoneySupply():
    res = []
    moneySupplyRequestedTotal = 0
    moneySupplyTotal = 0
    for k, v in GoodsIds.items():
        try:
            googdsInfo = getMoneyInfo(k)
            if googdsInfo['moneySupplyRequested']:
                moneySupplyRequestedTotal += int(googdsInfo['m1'])
            if googdsInfo['moneySupply']:
                moneySupplyTotal += int(googdsInfo['m2'])
            res.append(googdsInfo)
        except Exception:
            pass
    res.sort(GoodsCMP)
    mf1 = format(moneySupplyRequestedTotal / 100000000.0, ',.2f')
    mf2 = format(moneySupplyTotal / 100000000.0, ',.2f')
    out=[]
    if moneySupplyRequestedTotal<=0 or moneySupplyTotal<=0:
        out.append('数据异常,请在交易时间获取')
        out.append('委托受托申报时间：工作日09:00—11:30；13:30—16:15')
    else:
        for i in res:
            out.append('%s%s：%s%%'%(i.get('name',''),i.get('id',''),i.get('ratio_format','')))
        out.append('总委托资金：%s亿'%mf1)
        out.append('总受托资金：%s亿'%mf2)

    return '\n'.join(out)


if __name__=='__main__':
    test=getFyMoneySupply()
    print test



