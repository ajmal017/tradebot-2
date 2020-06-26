import alpaca_trade_api as alpaca
import pandas as pd
from order import *
from config import * 
import logging

logger = logging.getLogger()
api = alpaca.REST(API_KEY_ID, API_SECRET_KEY, api_version='v2')

class RSIstrategy:
    """
    Positions for a stock cycle through four states:
    1. TO_BUY: no position, no order. Can transition to BUY_SUBMITTED
    2. BUY_SUBMITTED: buy order has been submitted. Can transition to TO_BUY or TO_SELL
    3. TO_SELL: buy is filled and holding position. Can transition to SELL_SUBMITTED
    4. SELL_SUBMITTED: sell order has been submitted. Can transition to TO_SELL or TO_BUY
    """
    def __init__(self, symbol, lot):
        self._symbol = symbol
        self._lot = lot
        self._bars = []
        self._l = logger.getChild(self._symbol)

        # initialization code from https://github.com/alpacahq/example-scalping
        # get bars for the current day 
        now = pd.Timestamp.now(tz='America/New_York').floor('1min')
        market_open = now.replace(hour=9, minute=30)
        today = now.strftime('%Y-%m-%d')
        tomorrow = (now + pd.Timedelta('1day')).strftime('%Y-%m-%d')
        data = api.polygon.historic_agg_v2(
            symbol, 1, 'minute', today, tomorrow, unadjusted=False).df
        bars = data[market_open:]
        self._bars = bars

        symbol = self._symbol
        orders = [o for o in get_orders() if o and o['symbol'] == symbol]
        positions = [p for p in get_positions() if p['symbol'] == symbol]
        self._order = orders[0] if len(orders) > 0 else None
        self._position = positions[0] if len(positions) > 0 else None

        # set state by checking existing position and order status
        if self._position is not None:
            if self._order is None:
                self._state = 'TO_SELL'
            else:
                self._state = 'SELL_SUBMITTED'
                if self._order['side'] != 'sell':
                    self._l.warn(
                        f'state {self._state} mismatch order {self._order}')
        else:
            if self._order is None:
                self._state = 'TO_BUY'
            else:
                self._state = 'BUY_SUBMITTED'
                if self._order['side'] != 'buy':
                    self._l.warn(
                        f'state {self._state} mismatch order {self._order}')

    def _outofmarket(self):
        return pd.Timestamp.now(tz='America/New_York').time() >= pd.Timestamp('15:55').time()

    def _calc_buy_signal(self):
        """ 
        Generates buy signal based on bar data when the state is TO_BUY.
        """
        mavg = self._bars.rolling(20).mean().close.values
        closes = self._bars.close.values
        if closes[-2] < mavg[-2] and closes[-1] > mavg[-1]:
            self._l.info(
                f'buy signal: closes[-2] {closes[-2]} < mavg[-2] {mavg[-2]} '
                f'closes[-1] {closes[-1]} > mavg[-1] {mavg[-1]}')
            return True
        else:
            self._l.info(
                f'closes[-2:] = {closes[-2:]}, mavg[-2:] = {mavg[-2:]}')
            return False

    def on_bar(self, bar):
        """
        Processes minute bar data and reads buy signals
        """
        self._bars = self._bars.append(pd.DataFrame({
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume,
        }, index=[bar.start]))

        self._l.info(f'received bar start = {bar.start}, close = {bar.close}, len(bars) = {len(self._bars)}')

        if len(self._bars) < 21: # wait until 20 minutes after market open to create signals 
            return
        if self._outofmarket():
            return
        if self._state == 'TO_BUY':
            signal = self._calc_buy_signal()
            if signal:
                # trigger limit buy and update state 
                trade = api.polygon.last_trade(self._symbol) # limit price will be the price for the last trade
                amount = int(self._lot / trade.price)
                order = limit_buy(amount, self._symbol, trade.price)
                if order == "Failed":
                    self._state = 'TO_BUY'
                else: 
                    # Order was successfully placed
                    self._order = order
                    self._l.info(f'submitted buy {order}')
                    self._state = 'BUY_SUBMITTED'

    
    def _submit_sell(self, market=False):
        if market:
            order = market_order(self._position.qty, self._symbol, is_buy=False)
        else:
            current_price = float(api.polygon.last_trade(self._symbol).price)
            cost_basis = float(self._position.avg_entry_price)
            limit_price = max(cost_basis + 0.01, current_price)
            order = limit_sell(self._position.qty, self._symbol, limit_price)
        
        if order == "Failed": 
            self._state = 'TO_SELL'
            self._l.error(f'sell order for {self._position.qty} shares of {self._symbol} at {limit_price} failed')
        else:
            self._order = order
            self._l.info(f'submitted sell {order}')
            self._state = 'SELL_SUBMITTED'


    def on_order_update(self, event, order):
        """
        Sets up state transitions for order updates 
        """
        self._l.info(f'order update: {event} = {order}')
        if event == 'fill':
            self._order = None
            if self._state == 'BUY_SUBMITTED':
                self._position = api.get_position(self._symbol)
                self._state = 'TO_SELL'
                self._submit_sell()
                return
            elif self._state == 'SELL_SUBMITTED':
                self._position = None
                self._state = 'TO_BUY'
                return
        elif event == 'partial_fill':
            self._position = api.get_position(self._symbol)
            self._order = api.get_order(order['id'])
            return
        elif event in ('canceled', 'rejected'):
            if event == 'rejected':
                self._l.warn(f'order rejected: current order = {self._order}')
            self._order = None
            if self._state == 'BUY_SUBMITTED':
                if self._position is not None:
                    self._state = 'TO_SELL'
                    self._submit_sell()
                else:
                    self._state = 'TO_BUY'
            elif self._state == 'SELL_SUBMITTED':
                self._state= 'TO_SELL'
                self._submit_sell(market=True)
            else:
                self._l.warn(f'unexpected state for {event}: {self._state}')

    def checkup(self, position):
        # periodically cancel unexecuted orders from at least 2 minutes back
        now = pd.Timestamp.now(tz='America/New_York')
        order = self._order
        if (order is not None and
            order['side'] == 'buy' and now -
                pd.Timestamp(order['submitted_at'], tz='America/New_York') > pd.Timedelta('2 min')):
            last_price = api.polygon.last_trade(self._symbol).price
            cancel_order(order['id'])

        if self._position is not None and self._outofmarket():
            self._submit_sell(market=True)



