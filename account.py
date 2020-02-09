import alpaca_trade_api as tradeapi

if __name__ == '__main__':
    """
    With the Alpaca API, you can check on your daily profit or loss by
    comparing your current balance to yesterday's balance.
    """

    # First, open the API connection
    api = tradeapi.REST(
        'PKGOQ00DZV0F6I2PBJR7',
        'c5nm5IFiw4m3b30Wqw4VqQ2K/35lAH0eWy8Ue2OE',
        'https://paper-api.alpaca.markets'
    )

    # Get account info
    account = api.get_account()

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')

    # Check how much money we can use to open new positions.
    print('${} is available as buying power.'.format(account.buying_power))

    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')