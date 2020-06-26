import alpaca_trade_api as alpaca
import asyncio
from config import * 
import pandas as pd
import sys
from strategy import RSIstrategy

import logging
logger = logging.getLogger()

def main(args):
    api = alpaca.REST(API_KEY_ID, API_SECRET_KEY, api_version='v2')
    stream = alpaca.StreamConn(LIVE_API_KEY_ID, LIVE_API_SECRET_KEY) # need live account to access streaming

    fleet = {}
    symbols = [symbol.strip() for symbol in TRADE_SYMBOLS.split(',')]
    for symbol in symbols:
        algo = RSIstrategy(symbol, lot=args.lot)
        fleet[symbol] = algo

    # Event handlers: 
    @stream.on(r'^AM')
    async def on_bars(conn, channel, data):
        if data.symbol in fleet:
            fleet[data.symbol].on_bar(data)

    @stream.on(r'trade_updates')
    async def on_trade_updates(conn, channel, data):
        logger.info(f'trade_updates {data}')
        symbol = data.order['symbol']
        if symbol in fleet:
            fleet[symbol].on_order_update(data.event, data.order)

    async def periodic():
        while True:
            if not api.get_clock().is_open:
                logger.info('exit as market is not open')
                sys.exit(0)
            await asyncio.sleep(30)
            positions = api.list_positions()
            for symbol, algo in fleet.items():
                pos = [p for p in positions if p.symbol == symbol]
                algo.checkup(pos[0] if len(pos) > 0 else None)

    channels = ['trade_updates'] + [
        'AM.' + symbol for symbol in symbols
    ]

    loop = stream.loop
    loop.run_until_complete(asyncio.gather(
        stream.subscribe(channels),
        periodic(),
    ))
    loop.close()

if __name__ == '__main__':
    import argparse

    fmt = '%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    fh = logging.FileHandler('console.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(fmt))
    logger.addHandler(fh)

    parser = argparse.ArgumentParser()
    parser.add_argument('--lot', type=float, default=2000)

    main(parser.parse_args())
