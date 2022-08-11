import time
import requests, json
from binance.client import Client
import configure
import hmac
import hashlib
from itertools import count
from binance.enums import *

poloniexStocksResponse = requests.get('https://api.poloniex.com/markets/price').json()

poloniexStocks = {
        poloniexStocksResponse[i]['symbol']: poloniexStocksResponse[i]['price'] for i in
        range(0, len(poloniexStocksResponse))
}


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

client = Client(configure.biKey, configure.biSecret)
def makeBiBuyOrder(coin, buyPower):
    buyPayLoad = client.create_order(
        symbol=nS(coin),
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=round(buyPower, 2),
    )
    return buyPayLoad

def biWithdraw(coin):
    accountData = client.get_account()["balances"]
    coinAmount = {
        accountData[i]['asset']: accountData[i]['free'] for i in
        range(0, len(accountData))
    }[coin]
    response = client.withdraw(
        coin=coin,
        address=configure.polyDepositAddress,
        amount=coinAmount
    )
    return response

def is_profitable_after_fee(buy, sell, marketFee):
    finalBuyPrice = get_adjusted_prices(marketFee(float(buy)))[1],
    finalSellPrice = get_adjusted_prices(float(sell))[0]

    expected_profit_raw = finalBuyPrice[0] - finalSellPrice,
    expected_profit = expected_profit_raw[0]

    procentDifference = str((abs(finalBuyPrice[0] - finalSellPrice) / ((finalBuyPrice[0] + finalSellPrice)/2.0)) * 100) + "%"

    if expected_profit > 0.0:
        return True, expected_profit, procentDifference,
    return False, expected_profit, procentDifference,

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
    currency = '{}'.format(spiltName[0])
    crypto = '{}'.format(spiltName[1])
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

def polySellOrder(coin, amount):
    splitCoinName = coin.split("_")
    newCoinName = splitCoinName[1] +"_"+ splitCoinName[0]
    buyPayLoad = {
        'command': 'sell',
        'currencyPair': newCoinName,
        'rate': '10.0',
        'amount': round(amount, 2),
        'clientOrderId': str(time.time())
    }
    return getPolyData(buyPayLoad).json()

def polyWithdraw(coin):
    maxAmount = getPolyData(accountPayLoad).json()["exchange"][coin]["available"]
    withdrawPayLoad = {
        'command': 'withdraw',
        'currency': coin,
        'amount': maxAmount,
        'address': configure.biDepositAddress
    }
    return getPolyData(withdrawPayLoad).json()


accountPayLoad = {'command': 'returnCompleteBalances',
               'account': 'all'}

withdrawPayLoad = {'command': 'withdraw',
               'currency': 'ETH',
               'amount': '1',
               'address': '0x84a90e21d9d02e30ddcea56d618aa75ba90331ff'}


something = False

while True:
    something2 = False
    if (something):
        time.sleep(10)
        something = False

    listOfProfitableCoins = []

    for coin in configure.cryptoCoins:
        coinBuy = poloniexStocks[coin]
        coinSell = binaceStocks[nS(coin)]

        is_profitable = is_profitable_after_fee(coinBuy, coinSell, poloniex_fee)
        if (coin == configure.cryptoCoins[len(configure.cryptoCoins) - 1]):
            if (something2):
                something = True
                bestCoin = listOfProfitableCoins[0]
                bestCoinName = bestCoin[0].split("_")[0]
                polyBuyPower = getPolyData(accountPayLoad).json()["exchange"]["USDT"]["available"]
                maxAmount = float(polyBuyPower) / float(poloniexStocks[bestCoin[0]])

                print("buying", bestCoin)
                print(makeBiBuyOrder(bestCoin[0], maxAmount))
                print(biWithdraw(bestCoinName))
                print(polySellOrder(bestCoin[0], maxAmount))
                print(polyWithdraw(bestCoinName))
                print("done")

        if is_profitable[0]:
            something2 = True
            listOfProfitableCoins.insert(len(listOfProfitableCoins) - 1, [coin, is_profitable[2]])
