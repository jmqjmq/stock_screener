#!/usr/bin/python3

import pandas as pd
import json

#pd.set_option('max_columns', None)
pd.options.display.max_colwidth = 140
pd.set_option('display.float_format', '{:0.1f}'.format)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Get the mapping of CIK to name
handle = open("data/company_tickers.json", "r")
cik_json = json.load(handle)
handle.close()

stocks = pd.DataFrame()
cik_dict = {}

for key, cik_data in cik_json.items():
    cik_dict[cik_data['cik_str']] = {'ticker': cik_data['ticker'],
                                        'title': cik_data['title']}
    

handle = open("data/stocks.json", "r")
stocks_json = json.load(handle)
handle.close()

stock_list = []

for cik in cik_dict:
    ticker = cik_dict[cik]['ticker']
    title = cik_dict[cik]['title']


    # Find the most recent annual report for this stock
    most_recent_year = 0

    if str(cik) not in stocks_json:
        continue

    for year in stocks_json[str(cik)]:
        if stocks_json[str(cik)][year]['FY']:
            this_year = int(year)
            if this_year > most_recent_year:
                most_recent_year = this_year

    if most_recent_year == 0:
        continue

    #print(cik_dict[cik]['ticker'] + " " +cik_dict[cik]['title'] + " "+str(most_recent_year))

    stock_dict = stocks_json[str(cik)][str(most_recent_year)]['FY']
    stock_dict['cik'] = str(cik)
    stock_dict['ticker'] = ticker
    stock_dict['title'] = title
    stock_dict['revenue'] = stock_dict.get('Revenues', 0)
    #stock_dict['revenueCost'] = stock_dict.get('CostOfGoodsAndServicesSold', 0) + \
#        stock_dict.get('CostOfRevenue', 0) + stock_dict.get('CostsAndExpenses', 0)
    stock_dict['inventory'] = stock_dict.get('InventoryNet', 0)
    stock_dict['cash'] = stock_dict.get('CashAndCashEquivalentsAtCarryingValue', 0)
    stock_dict['receivables'] = stock_dict.get('AccountsReceivableNetCurrent', 0)
    stock_dict['currentAssets'] = stock_dict.get('AssetsCurrent', 0)
    stock_dict['accountsPayable'] = stock_dict.get('AccountsPayableCurrent', 0) + \
        stock_dict.get('AccountsPayableTradeCurrent', 0)

    stock_dict['shortTermDebt'] = stock_dict.get('LongTermDebtCurrent', 0)
    stock_dict['longTermDebt'] = stock_dict.get('LongTermDebtNoncurrent', 0)
    stock_dict['currentLiabilities'] = stock_dict.get('LiabilitiesCurrent', 0)
    stock_dict['cashFromOps'] = stock_dict.get('NetCashProvidedByUsedInOperatingActivities', 0)

    stock_dict['_revenue'] = stock_dict.get('RevenueFromContractWithCustomerExcludingAssessedTax', 0) + \
        stock_dict.get('RevenueFromSaleOfGoods', 0) + \
        stock_dict.get('Revenues', 0)

    stock_dict['_cost_of_revenue'] = stock_dict.get('CostOfGoodsAndServicesSold', 0) + \
            stock_dict.get('CostOfInventoriesRecognizedAsExpenseDuringPeriod', 0) + \
            stock_dict.get('CostOfRevenue', 0)

    stock_dict['_gross_profit'] = stock_dict.get('GrossProfit', 0)
    if stock_dict['_gross_profit'] == 0:
        stock_dict['_gross_profit'] = stock_dict['_revenue'] - stock_dict['_cost_of_revenue']

    stock_dict['_cash'] = stock_dict.get('cash', 0) + \
        stock_dict.get('MarketableSecuritiesCurrent', 0) + \
        stock_dict.get('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 0)

    stock_dict['_receivables'] = stock_dict.get('AccountsReceivableNetCurrent', 0) + \
        stock_dict.get('ReceivablesNetCurrent', 0) + \
        stock_dict.get('AccountsNotesAndLoansReceivableNetCurrent', 0)

    stock_dict['_inventory'] = stock_dict.get('InventoryNet', 0) + \
        stock_dict.get('InventoryFinishedGoodsNetOfReserves', 0)

    stock_dict['_current_assets'] = stock_dict.get('AssetsCurrent', 0)
    stock_dict['_accounts_payable'] = stock_dict.get('accountsPayable', 0)
    
    stock_dict['_short_term_debt'] = stock_dict.get('shortTermDebt', 0) + \
        stock_dict.get('DebtCurrent', 0) 

    stock_dict['_long_term_debt'] = stock_dict.get('LongTermDebtNoncurrent', 0) + \
        stock_dict.get('LongTermDebt', 0)

    stock_dict['_long_term_debt_current'] = stock_dict.get('LongTermDebtCurrent', 0)

    stock_dict['_current_liabilities'] = stock_dict.get('LiabilitiesCurrent', 0)

    stock_dict['_cash_from_ops'] = stock_dict.get('NetCashProvidedByUsedInOperatingActivities', 0)
    stock_dict['_capex'] = stock_dict.get('PaymentsToAcquirePropertyPlantAndEquipment', 0) + \
        stock_dict.get('PaymentsToAcquireProductiveAssets', 0)

    stock_list.append(stock_dict)


stocks_df = pd.DataFrame(stock_list)
print(stocks_df.transpose())
exit()

# Read CIKs
# cik, symbol
company_info = pd.read_json("company_tickers.json").transpose()
company_info = company_info.rename(columns = {'cik_str' : 'cik'})
company_info = company_info.rename(columns = {'ticker' : 'symbol'})
del company_info['title']

# Read stock_info json
# name, symbol, div_yield, price, market_cap
stock_info = pd.read_json("prices.json")
stock_info['div_yield'] = stock_info['div_yield'] * 100


# Balance 
# end_date, cash, cik, current_assets, inventory, accounts_payable, current_liabilities, long_term_debt,
# accounts_receivable, short_term_investments, cash_from_banks, other_receivables
balance = pd.read_json("balance.json")

# Income
# start, end, revenue, filing_period, form, frame, cik, gross_profile, cost_of_goods, net revenue
income = pd.read_json("income.json")
#print(income.to_string())
#exit()

# Cash
# end_data, op_cash_flow, cik, capex, fy, fp
cash  = pd.read_json("cash.json")
cash = cash[cash['fp'] == 'FY']
cash = cash[cash['fy'] >= 2021]
cash = cash.sort_values(by='fy', ascending=False)
cash = cash.drop_duplicates(['cik'])

stock_info = stock_info.merge(company_info)

stock_info = stock_info.merge(balance[['cik', 'cash', 'long_term_debt']])

stock_info = stock_info.drop_duplicates(['cik'])

stock_info['ev'] = stock_info['market_cap'] - stock_info['cash'] + stock_info['long_term_debt']

stock_info = stock_info.merge(cash[['cik', 'end', 'op_cash_flow']])

stock_info = stock_info.sort_values('symbol')

stock_info = stock_info.fillna(0)

stock_info['market_cap'] = stock_info['market_cap'].astype(int)
stock_info['div_yield'] = stock_info['div_yield'].astype(float)
stock_info['cash'] = stock_info['cash'].astype(int)
stock_info['long_term_debt'] = stock_info['long_term_debt'].astype(int)

stock_info['ev'] = stock_info['market_cap'] - stock_info['cash'] + stock_info['long_term_debt']
stock_info['ev'] = stock_info['ev'].astype(int)
stock_info['op_cash_flow'] = stock_info['op_cash_flow'].astype(int)
stock_info = stock_info[stock_info['op_cash_flow'] > 0]
stock_info['ratio'] = 100 * stock_info['op_cash_flow'] / stock_info['ev']

stock_info = stock_info.sort_values('ratio', ascending = False)
#stock_info = stock_info[stock_info['eps'] > 0]
stock_info = stock_info[stock_info['price'] > 0]
#stock_info = stock_info[stock_info['market_cap'] > 10000000]

stock_info['market_cap'] = stock_info['market_cap'].map("{:,}".format)
stock_info['cash'] = stock_info['cash'].map("{:,}".format)
stock_info['long_term_debt'] = stock_info['long_term_debt'].map("{:,}".format)
stock_info['ev'] = stock_info['ev'].map("{:,}".format)
stock_info['op_cash_flow'] = stock_info['op_cash_flow'].map("{:,}".format)

del stock_info['price']
del stock_info['index']
stock_info = stock_info.sort_values(by='end', ascending=False)
#stock_info = stock_info.drop_duplicates(['cik'])
del stock_info['cik']
stock_info = stock_info.sort_values('symbol', ascending = True)

print(stock_info.to_string())
stock_info.to_json("data/total.json")
