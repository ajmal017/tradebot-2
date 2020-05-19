import sys, argparse, datetime
import pandas as pd
import backtrader as bt
from generate_data import get_data
from strategies.SMACrossover import SMACrossover
from strategies.RSIpattern import RSIpattern

strategies = {
    "SMACrossover": SMACrossover,
    "RSIpattern": RSIpattern
}

parser = argparse.ArgumentParser()
parser.add_argument("--strategy", help="which strategy to run", type=str)
parser.add_argument("--ticker", help="which ticker symbol to run on", type=str)
args = parser.parse_args()

if not args.strategy in strategies:
    print("invalid strategy, must be one of {}".format(strategies.keys()))
    sys.exit()

cerebro = bt.Cerebro()
cerebro.broker.setcash(100000)

#Set data parameters and add to Cerebro
data = bt.feeds.YahooFinanceCSVData(
    dataname='data/SPY.csv',
    fromdate=datetime.datetime(2015, 1, 1),
    todate=datetime.datetime(2020, 5, 8)
)
cerebro.adddata(data)

cerebro.addstrategy(strategies[args.strategy])
cerebro.run()

#Get final portfolio Value
portvalue = cerebro.broker.getvalue()
pnl = portvalue - 100000

#Print out the final result
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

cerebro.plot()
