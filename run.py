import websocket, json, sys
import dateutil.parser
from config import * 
from alpaca_order import place_order
from datetime import datetime

minutes_processed = {}
candlesticks = []
curr_price = None
prev_price = None
in_position = False


def on_open(ws):
    print("Opened")
    auth_data = {
        "action":"auth",
        "params":API_KEY_ID
    }
    ws.send(json.dumps(auth_data))

    channel_data = {
        "action": "subscribe",
        "params": TICKERS
    }

    ws.send(json.dumps(channel_data))

def on_message(ws, message):
    global curr_price, prev_price, in_position, candlesticks

    # Calculate candles
    prev_price = curr_price
    curr_price = json.loads(message)[0]

    tick_datetime_object = datetime.utcfromtimestamp(curr_price['t']/1000)
    tick_dt = tick_datetime_object.strftime('%Y-%m-%d %H:%M')

    if not tick_dt in minutes_processed:
        # Make a new candle
        minutes_processed[tick_dt] = True
    
        if len(candlesticks) > 0:
            candlesticks[-1]['close'] = prev_price['bp']

        candlesticks.append({
            "minute": tick_dt,
            "open": curr_price['bp'],
            "high": curr_price['bp'],
            "low": curr_price['bp']
        })
        
    if len(candlesticks) > 0:
        current_candlestick = candlesticks[-1]
        if curr_price['bp'] > current_candlestick['high']:
            current_candlestick['high'] = curr_price['bp']
        if curr_price['bp'] < current_candlestick['low']:
            current_candlestick['low'] = curr_price['bp']

    if len(candlesticks) > 3:
        last_candle = candlesticks[-2]
        previous_candle = candlesticks[-3]
        first_candle = candlesticks[-4]

        if last_candle['close'] > previous_candle['close'] and previous_candle['close'] > first_candle['close']:
            distance = last_candle['close'] - first_candle['open']
            profit_price = last_candle['close'] + (distance * 2)
            loss_price = first_candle['open']

            if not in_position:
                print("== Placing order and setting in position to true ==")
                in_position = True
                place_order(profit_price, loss_price)
                sys.exit()


def on_close(ws):
    print("closed connection")

if __name__ == '__main__':

    socket = "wss://alpaca.socket.polygon.io/stocks"

    ws = websocket.WebSocketApp(
        socket,
        on_open=on_open, 
        on_message=on_message,
        on_close=on_close
    )

    ws.run_forever()