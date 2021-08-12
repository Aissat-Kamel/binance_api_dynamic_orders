import json


def read_orders(file_name):
	with open(file_name+".json") as json_file:
		return dict(json.load(json_file))

def save_orders(file_name, orders):
	with open(file_name+".json", 'w') as json_file:
	  json_file.write(orders)

def json_format(orders, ticker, **kwargs):
	orders[ticker] = []
	for arg in kwargs:
		orders[ticker].append(kwargs[arg])
	return json.dumps(orders)

def delete_order(orders, ticker):
	del orders[ticker]
	return json.dumps(orders)

def edit_order_side(orders, ticker, **kwargs):
	for arg in kwargs:
		if arg == "side":
			orders[ticker][-1] = kwargs[arg]
	return json.dumps(orders)
