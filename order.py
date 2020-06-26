from config import * 
import requests, json

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
POSITIONS_URL = "{}/v2/positions".format(BASE_URL)

HEADERS = {'APCA-API-KEY-ID': API_KEY_ID, 'APCA-API-SECRET-KEY': API_SECRET_KEY}

def get_buying_power():
    return json.loads(requests.get(ACCOUNT_URL, headers=HEADERS).content)['buying_power']

def get_positions():
    return json.loads(requests.get(POSITIONS_URL, headers=HEADERS).content) 

def get_orders():
    return json.loads(requests.get(ORDERS_URL, headers=HEADERS).content) 

def cancel_order(order_id):
    url = ORDERS_URL + "/" + order_id 
    requests.delete(url, headers=HEADERS)

def market_order(amount, symbol, is_buy): 
    data = {
        "symbol": symbol,
        "qty": amount,
        "type": "market",
        "time_in_force": "day"
    } 
    if is_buy:
        data["side"] = "buy"
    else: 
        data["side"] = "sell"
    
    try:
        order = requests.post(ORDERS_URL, json=data, headers=HEADERS)
        return json.loads(order.content)
    except Exception as e:
        print(e)
        return "Failed"

def limit_buy(amount, symbol, limit_price):
    try:
        print("submitted order: BUY {} of {} at {}".format(amount, symbol, limit_price))
        data = {
            "symbol": symbol,
            "qty": amount,
            "side": "buy",
            "type": "limit",
            "limit_price": limit_price,
            "time_in_force": "day"
        } 
        order = requests.post(ORDERS_URL, json=data, headers=HEADERS)
        return json.loads(order.content)
    except Exception as e:
        print(e)
        return "Failed"

def limit_sell(amount, symbol, limit_price):
    try:
        print("submitted order: SELL {} of {} at {}".format(amount, symbol, limit_price))
        data = {
            "symbol": symbol,
            "qty": amount,
            "side": "sell",
            "type": "limit",
            "limit_price": limit_price,
            "time_in_force": "day"
        } 
        order = requests.post(ORDERS_URL, json=data, headers=HEADERS)
        return json.loads(order.content)
    except Exception as e:
        print(e)
        return "Failed"

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
    return response

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
    return response

# if __name__ == '__main__':
#     order = limit_buy(1, 'AMD', 52.00)
#     print(order['side'])

