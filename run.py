import json_formatter as jf
import websocket_realPrice
from websocket_realPrice import prices
import os
import time
import format_orders as fo

print("Program start working now ....")
print("Now you can stop the program ...")

prev_orders = {}

while True:
    try:
        orders = jf.read_orders("orders")
        if prev_orders != orders:
            for order in orders:
                if order not in prev_orders:
                    print("New signal for", order, "@", orders[order][0])
        for order in orders:
            if order in prices:
                if orders[order][-1] == "BUY":
                    if orders[order][0] >= prices[order][1]:
                        #buy_market_order
                        detail = fo.execute_buy_market_order(order, 15)
                        print(detail)
                        print("Placed buy market order for", order, "@", prices[order][1])
                        orders = jf.edit_order_side(orders, order, side = "SELL")
                        jf.save_orders("orders", orders)
                        orders = jf.read_orders("orders")

                if orders[order][-1] == "SELL":
                    if orders[order][1] <= prices[order][0]:
                        #sell_market_order
                        quantity = fo.get_token_balance(order, 0.15)
                        detail = fo.execute_sell_market_order(order, quantity)
                        print(detail)
                        print("Placed sell tp market order for", order, "@", prices[order][1])
                        orders = jf.edit_order_side(orders, order, side = "DEL")
                        jf.save_orders("orders", orders)
                        orders = jf.read_orders("orders")

                    if orders[order][2] >= prices[order][0]:
                        #sell_market_order
                        quantity = fo.get_token_balance(order, 0.15)
                        detail = fo.execute_sell_market_order(order, quantity)
                        print(detail)
                        print("Placed sell sl market order for", order, "@", prices[order][1])
                        orders = jf.edit_order_side(orders, order, side = "DEL")
                        jf.save_orders("orders", orders)
                        orders = jf.read_orders("orders")


                if orders[order][-1] == "DEL":
                    orders = jf.delete_order(orders, order)
                    jf.save_orders("orders", orders)
                    orders = jf.read_orders("orders")

        prev_orders = orders
        time.sleep(0.2)
    except KeyboardInterrupt:
        os._exit(0)
