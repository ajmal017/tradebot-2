import alpaca_trade_api as tradeapi

# First, open the API connection
api = tradeapi.REST(
    'PKGOQ00DZV0F6I2PBJR7',
    'c5nm5IFiw4m3b30Wqw4VqQ2K/35lAH0eWy8Ue2OE',
    'https://paper-api.alpaca.markets'
)

# Get a list of all active assets.
active_assets = api.list_assets(status='active')

# Filter the assets down to just those on NASDAQ.
nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']
print(nasdaq_assets)

# Check if AAPL is tradable on the Alpaca platform.
aapl_asset = api.get_asset('AAPL')
if aapl_asset.tradable:
    print('We can trade AAPL.')