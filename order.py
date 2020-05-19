from config import * 
import requests, json

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)

HEADERS = {'APCA-API-KEY-ID': API_KEY_ID, 'APCA-API-SECRET-KEY': API_SECRET_KEY}

def get_buying_power():
    return json.loads(requests.get(ACCOUNT_URL, headers=HEADERS).content)['buying_power']

# Limit buy with limit sell triggered when stop price is reached
def stop_limit_order(stop_price, buy_limit_price, sell_limit_price, symbol):
    data = {
        "symbol": symbol,
        "qty": 1,
        "side": "buy",
        "type": "limit",
        "limit_price": buy_limit_price,
        "time_in_force": "gtc",
        "order_class": "oto",
        "stop_loss": {
            "limit_price": sell_limit_price, # stop-limit price must not be greater than stop price
            "stop_price": stop_price
        }
    }

    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    response = json.loads(r.content)
    print(response)

# Submit both entry and exit order
def bracket_order(profit_price, loss_price, symbol):
    data = {
        "symbol": symbol,
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "take_profit": {
            "limit_price": profit_price
        },
        "stop_loss": {
            "stop_price": loss_price
        }
    }

    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    response = json.loads(r.content)
    print(response)


# if __name__ == '__main__':
#     stop_limit_order(stop_price=53.50, buy_limit_price=54.00, sell_limit_price=52.00,symbol='COST')