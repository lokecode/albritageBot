import requests, json
from binance.spot import Spot as Client
import configure
import hmac
import hashlib

from itertools import count
import time

poloniexStocks = requests.get('https://api2.binance.com/api/v3/ticker/price').json()

binaceStocksResponse = requests.get('https://api2.binance.com/api/v3/ticker/price').json()

binaceStocks = {
        binaceStocksResponse[i]['symbol']: binaceStocksResponse[i]['price'] for i in
        range(0, len(binaceStocksResponse))
}

slippage = 1.0

#bi

params = {
    "symbol": "ETHUSDT",
    "side": "BUY",
    "type": "MARKET",
    "timeInForce": "GTC",
    "quantity": 0.001,
    "price": 9500,
}

def makeBiOrder():
    #https://api2.binance.com/api/v3/order
    client = Client(configure.biKey, configure.biSecret, base_url="https://api2.binance.com/api/v3/order")
    response = client.new_order(**params)
    return response

def biWithdraw():
    spot_client = Client(configure.keyS, configure.secretS, show_header=True, base_url="https://api2.binance.com/sapi/v1/capital/withdraw/apply")
    return spot_client.withdraw(coin="BNB", amount=0.01, address=configure.with_draw)

def is_profitable_after_fee(buy, sell, marketFee):
    expected_profit_raw = get_adjusted_prices(marketFee(float(buy)))[1] - get_adjusted_prices(float(sell))[0],
    expected_profit = expected_profit_raw[0]

    if expected_profit > 0.0:
        return True, expected_profit,
    return False, expected_profit,

def binance_fee(price):
    fee = 0.155
    expenses = (slippage + fee)

    Ratio = expenses / 100

    Procent = Ratio * price

    return (price + Procent)

def poloniex_fee(price):
    fee = 0.155
    expenses = (slippage + fee)

    Ratio = expenses / 100

    Procent = Ratio * price

    return (price + Procent)

def get_adjusted_prices(price):
    Ratio = 1 / 100

    Procent = Ratio * price

    adj_buy_price = (price - Procent)
    adj_sell_price = (price + Procent)

    return adj_sell_price, adj_buy_price

def nS(name):
    spiltName = name.split('_')
    currency = '{}'.format(spiltName[1])
    crypto = '{}'.format(spiltName[0])
    return currency + crypto


class BodyDigestSignature(object):
    def __init__(self, secret, header='Sign', algorithm=hashlib.sha512):
        self.secret = secret
        self.header = header
        self.algorithm = algorithm

    def __call__(self, request):
        body = request.body
        if not isinstance(body, bytes):   # Python 3
            body = body.encode('latin1')  # standard encoding for HTTP
        signature = hmac.new(self.secret, body, digestmod=self.algorithm)
        request.headers[self.header] = signature.hexdigest()
        return request

def getPolyData(payload):
    headers = {'nonce': '',
               'Key': configure.polyKey,
               'Sign': '', }

    secret = configure.polySecret

    request = requests.Request(
        'POST', 'https://poloniex.com/tradingApi',
        data=payload, headers=headers)
    prepped = request.prepare()
    tosign = b'' + bytes(prepped.body.encode('utf8'))
    signature = hmac.new(secret, tosign, hashlib.sha512)
    prepped.headers['Sign'] = signature.hexdigest()
    with requests.Session() as session:
        response = session.send(prepped)

    NONCE_COUNTER = count(int(time.time() * 1000))

    # then every time you create a request
    payload['nonce'] = next(NONCE_COUNTER)

    response3 = requests.post(
        'https://poloniex.com/tradingApi',
        data=payload, headers=headers, auth=BodyDigestSignature(secret))

    return response3


accountPayLoad = {'command': 'returnCompleteBalances',
               'account': 'all'}

withdrawPayLoad = {'command': 'withdraw',
               'currency': 'ETH',
               'amount': '1',
               'address': '0x84a90e21d9d02e30ddcea56d618aa75ba90331ff'}

buyPayLoad = {'command': 'buy',
               'currencyPair': 'USDT_AAVE',
               'rate': '1.00',
               'amount': '1',
               'clientOrderId': '12345'}

sellPayLoad = {'command': 'sell',
               'currencyPair': 'USDT_AAVE',
               'rate': '10.0',
               'amount': '1',
               'clientOrderId': '12345'}

something = False










NONCE_COUNTER = count(int(time.time() * 1000))
base_uri = "https://fapi.binance.com/fapi/v1/order?"
API_Key = configure.biKey
Secret_Key = configure.biSecret
symbol = "XRPUSDT"
side = "BUY"
type = "MARKET"
timeInForce = "GTC"
quantity = 20
recvWindow = 5000
timestamp = next(NONCE_COUNTER)
queryString = "symbol=" + symbol + "&side=" + side + "type=" + type + "&timeInForce=" + timeInForce
signature = hmac.new(configure.biSecret, b'' + bytes(queryString.encode('utf8')), hashlib.sha512)

Payload = {
    'Quantity': str(quantity),
    'RecvWindow': str(recvWindow),
    'Timestamp': str(timestamp),
    'Signature': str(signature),
}

headers = {
    'X-MBX-APIKEY': configure.biKey,
}

request = requests.Request(
        'POST', base_uri,
        data=Payload, headers=headers)

response3 = requests.post(
        base_uri,
        data=Payload, headers=headers, auth=BodyDigestSignature(configure.biSecret)
)

print(response3.content)


while True:
    something2 = False
    if (something):
        time.sleep(10)
        something = False

    listOfProfitableCoins = []

    for coin in configure.cryptoCoins:
        coinBuy = binaceStocks[nS(coin)]
        coinSell = binaceStocks[nS('USDT_AAVE')]

        is_profitable = is_profitable_after_fee(coinBuy, coinSell, poloniex_fee)
        if (coin == configure.cryptoCoins[len(configure.cryptoCoins) - 1]):
            if (something2):
                something = True
                print(listOfProfitableCoins)



        if is_profitable[0]:
            something2 = True
            listOfProfitableCoins.insert(len(listOfProfitableCoins) - 1, [coin, is_profitable[1]])
            print(coin, is_profitable[1], (binaceStocks[nS(coin)]), binaceStocks[nS(coin)])