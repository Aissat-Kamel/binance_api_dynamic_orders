from ticker_rules import rules
from legal_coins import legal_list

def get_usdt_List(dict):
    list = []
    for key in dict.keys():
        if "USDT" in key and key in legal_list:
            list.append(key)
    return list

def get_usdt_lists(dict):
    list = []
    for key in dict.keys():
        if "USDT" in key and key in legal_list:
            list.append(key)
    lists = [list[i: i+6] for i in range(0, len(list), 6)]
    return lists



def get_btc_List(dict):
    list = []
    for key in dict.keys():
        if "BTC" in key:
            list.append(key)
    return list

pairs = get_usdt_List(rules)
