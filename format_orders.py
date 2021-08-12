from ticker_rules import rules
from binance_client import client

#set price format
def format_price(ticker, price):
	float_format = "%."+str(rules[ticker][0])+"f"
	return float_format % price

#set quantity format
def format_quantity(ticker, quantity):
	return round(quantity, rules[ticker][3])

#check if quantity is valid
def check_min_notional(ticker, quantity):
	price = get_ticker_price(ticker)
	return quantity * price >= rules[ticker][4]

#get usdt balance and format
def get_usdt_balance(fee):
	balance = client.get_asset_balance(asset = "USDT")
	commission = (float(balance["free"]) / 100) * fee
	free_balance = float(balance["free"]) - commission
	free_balance = round(free_balance * 0.98, 2)
	return free_balance

#get asset balance and format
def get_token_balance(symbol, fee):
	asset = symbol.replace("USDT", "")
	balance = client.get_asset_balance(asset = asset)
	commission = (float(balance["free"]) / 100)*fee
	free_balance = float(balance["free"]) - commission
	free_balance = format_quantity(symbol, free_balance)
	return free_balance

#get average price for x ticker
def get_ticker_price(symbol):
	avg_price = client.get_avg_price(symbol = symbol)
	avg_price = float(avg_price["price"])
	return avg_price

#Calculating and format buying and selling prices
def price_calculator(symbol, price, **kwargs):
	result = {}
	for i in kwargs:
		prc = price + ((price * kwargs[i])/100)
		result[i] = str(format_price(ticker = symbol, price = prc))
	return result

#Calculating and format buying and selling quantities
def quantity_calculator(symbol, quantity, **kwargs):
	result = {}
	total = 0
	price = get_ticker_price(symbol)
	for i in kwargs:
		if kwargs[i] != "*":
			qty = quantity * (kwargs[i]/100)
			total = total + kwargs[i]
			if qty * price >= rules[symbol][4] and total <= 100:
				result[i] = format_quantity(ticker = symbol, quantity = qty)
			else:
				result[i] = "None"
				break
		else:
			rest = 100 - total
			qty = quantity * (rest/100)
			if qty * price >= rules[symbol][4] and total <= 100:
				result[i] = format_quantity(ticker = symbol, quantity = qty)
			else:
				result[i] = "None"
				break

	return result

def usdt_quantity_calculator(amount, **kwargs):
	result = {}
	total = 0
	for i in kwargs:
		if kwargs[i] != "*":
			qty = amount * (kwargs[i]/100)
			total = total + kwargs[i]
			if qty >= 10.5 and total <= 100:
				result[i] = round(qty, 2)
			else:
				result[i] = "None"
				break
		else:
			rest = 100 - total
			qty = amount * (rest/100)
			if amount >= 10.5 and total <= 100:
				result[i] = round(qty, 2)
			else:
				result[i] = "None"
				break

	return result



#convert the balance to the allowed purchase quantity < for market buy orders >.
def buy_market_quantity(symbol, usdt_amount):
	avg_price = client.get_avg_price(symbol = symbol)
	avg_price = float(avg_price["price"])
	quantity = (usdt_amount / avg_price)
	quantity = format_quantity(ticker = symbol, quantity = quantity)
	return quantity

#convert the balance to the allowed purchase quantity < for limit buy orders >.
def buy_limit_quantity(symbol, usdt_amount, price):
	quantity = (usdt_amount / float(price))
	quantity = format_quantity(ticker = symbol, quantity = quantity)
	return quantity

#buy market order execute
def execute_buy_market_order(symbol, usdt_amount):
	qty = buy_market_quantity(symbol, usdt_amount)
	order = client.order_market_buy(symbol=symbol, quantity=qty)
	deleted_elements = ["orderListId", "timeInForce", "clientOrderId", "fills"]
	price = float(order["cummulativeQuoteQty"])/float(order["origQty"])
	order["price"] = format_price(symbol, price)
	for elem in deleted_elements:
		del order[elem]
	return order

#sell market order execute
def execute_sell_market_order(symbol, quantity):
	order = client.order_market_sell(symbol=symbol, quantity=quantity)
	deleted_elements = ["orderListId", "timeInForce", "clientOrderId", "fills"]
	price = float(order["cummulativeQuoteQty"])/float(order["origQty"])
	order["price"] = format_price(symbol, price)
	for elem in deleted_elements:
		del order[elem]
	return order

#sell limit order execute
def execute_sell_limit_order(symbol, quantity, price):
	order = client.order_limit_sell(symbol=symbol, quantity=quantity, price=price)
	deleted_elements = ["orderListId", "timeInForce", "clientOrderId", "fills", "executedQty", "cummulativeQuoteQty", ]
	for elem in deleted_elements:
		del order[elem]
	return order

#buy limit execute
def execute_buy_limit_order(symbol, usdt_amount, price):
	quantity = buy_limit_quantity(symbol, usdt_amount, price)
	order = client.order_limit_buy(symbol=symbol, quantity=quantity, price=price)
	deleted_elements = ["orderListId", "timeInForce", "clientOrderId", "fills", "executedQty", "cummulativeQuoteQty", ]
	for elem in deleted_elements:
		del order[elem]
	return order

#oco order execute
def execute_sell_oco_order(symbol, quantity, stoplimit, price):
	trigger = float(stoplimit) + (float(stoplimit) * 0.001)
	trigger = format_price(symbol, trigger)
	order = client.create_oco_order(symbol = symbol,
									side = "SELL",
									stopLimitTimeInForce = "GTC",
									quantity = quantity,
									stopPrice = trigger,
									stopLimitPrice  = stoplimit,
									price = price )
	detail = {	"symbol":order["symbol"], "transactionTime":order["transactionTime"],
				"contingencyType": order["contingencyType"], "orderIdSLL":order["orderReports"][0]["orderId"],
				"orderIdLM":order["orderReports"][1]["orderId"], "origQty":order["orderReports"][0]["origQty"],
				"price":order["orderReports"][1]["price"],"stopPrice":order["orderReports"][0]["stopPrice"],
				"status":order["orderReports"][0]["status"], "type":order["contingencyType"],
				"side":order["orderReports"][0]["side"]
				}
	return detail
