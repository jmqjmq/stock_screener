#!/usr/bin/python3

import pandas as pd
import json
import requests

company = pd.read_json("data/company_tickers.json")

# https://query1.finance.yahoo.com/v7/finance/quote?symbols=T

company = company.transpose()

symbols = company['ticker'].tolist()
symbols.sort()

#symbols = symbols[:200]

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
}

prices = pd.DataFrame()

for symbol in symbols:
    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=" + symbol
    print(symbol)

    try:
        r = requests.get(url, headers=headers, timeout = 2)
    except:
        print("error on get")
        pass

    try:
        quote = r.json()
    except:
        print("error on r.json")
        pass
 
    stock = {}

    try:
        stock['name'] = quote['quoteResponse']['result'][0]['longName']
        stock['symbol'] = quote['quoteResponse']['result'][0]['symbol']
        stock['div_yield'] = quote['quoteResponse']['result'][0]['trailingAnnualDividendYield']
        stock['price'] = quote['quoteResponse']['result'][0]['ask']
        stock['market_cap'] = quote['quoteResponse']['result'][0]['marketCap']
    except:
        continue
 
    stock_df = pd.DataFrame([stock])
    prices = prices.append(stock_df)


prices.reset_index(inplace=True)

print(prices.to_string())
prices.to_json('data/prices.json')
