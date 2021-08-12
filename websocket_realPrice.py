from binance_client import client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
from tickers import pairs
import time
from alive_progress import alive_bar

prices = {}


def streaming_data_process(msg):

	"""
	{
				"u":400900217,     // order book updateId
				"s":"BNBUSDT",     // symbol
				"b":"25.35190000", // best bid price
				"B":"31.21000000", // best bid qty
				"a":"25.36520000", // best ask price
				"A":"40.66000000"  // best ask qty
			}
	"""
	# 0 = best_buy_price, 1 = best_sell_price
	prices[msg['s']]=[float(msg['b']), float(msg['a'])]


bm = BinanceSocketManager(client)
print("start init streaming ...")
print("You can't stop the program until it has finished initializing \n")
for pair in pairs:
	conn_key = bm.start_symbol_book_ticker_socket(pair, streaming_data_process)

bm.start()
with alive_bar(len(pairs)) as bar:  # or a 1000 in the loop example.
    for i in range(len(pairs)):
        time.sleep(15/len(pairs))
        bar()
print("\nend init streaming ....")
