import alpaca_trade_api as tradeapi
import time

if __name__ == '__main__':
    """
    With the Alpaca API, you can open a short position by submitting a sell
    order for a security that you have no open position with.
    """

    # First, open the API connection
    api = tradeapi.REST(
        'PKGOQ00DZV0F6I2PBJR7',
        'c5nm5IFiw4m3b30Wqw4VqQ2K/35lAH0eWy8Ue2OE',
        'https://paper-api.alpaca.markets'
    )

    # Submit a market order to buy 1 share of Apple at market price
    api.submit_order(
        symbol='MA',
        qty=1,
        side='buy',
        type='market',
        time_in_force='gtc'
    )

    # The security we'll be shorting
    symbol = 'TSLA'

    # Submit a market order to open a short position of one share
    order = api.submit_order(symbol, 1, 'sell', 'market', 'day')
    print("Market order submitted.")

    # Submit a limit order to attempt to grow our short position
    # First, get an up-to-date price for our symbol
    symbol_bars = api.get_barset(symbol, 'minute', 1).df.iloc[0]
    symbol_price = symbol_bars[symbol]['close']
    # Submit an order for one share at that price
    order = api.submit_order(symbol, 1, 'sell', 'limit', 'day', symbol_price)
    print("Limit order submitted.")

    # Wait a second for our orders to fill...
    print('Waiting...')
    time.sleep(1)

    # Check on our position
    position = api.get_position(symbol)
    if int(position.qty) < 0:
        print(f'Short position open for {symbol}')