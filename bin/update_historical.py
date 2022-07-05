#!/usr/bin/python3

import pandas as pd
import json
import pprint
import os
import datetime

pd.set_option('expand_frame_repr', False)

# Pandas dataframe
# cid
# category
# end date
# fy
# fp
# value

# Each stock will have a dictionary
# cik and year are indexes

# stocks['12345'] = {
#                    '2022' : {
#                                'CurrentAssets' : 123456,
#                                'Revenue' : 321
#                             },
#        
#                    '2021' : {
#                                'Assets' : 7676,
#                                'Revenue" : 98765
#                             }
#                    }
#category = {
#    "category" : "CurrentAssets",
#    "val", 1234
#}

categories = ['RevenueFromContractWithCustomerExcludingAssessedTax',
        'RevenueFromSaleOfGoods',
        'Revenues',
        'CostOfGoodsAndServicesSold',
        'CostOfInventoriesRecognizedAsExpenseDuringPeriod',
        'CostsAndExpenses',
        'OperatingCostsAndExpenses',
        'CostOfRevenue',
        'GrossProfit',
        'OperatingIncomeLoss',   # gross profit
        'Assets',
        'AssetsCurrent',
        'MarketableSecuritiesCurrent',
        'CashAndCashEquivalentsAtCarryingValue',
        'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',
        'InventoryNet',
        'InventoryFinishedGoodsNetOfReserves',
        'OtherAssetsCurrent',
        'AccruedLiabilitiesCurrent',
        'LiabilitiesCurrent',
        'DebtCurrent',
        'LongTermDebt',
        'LongTermDebtCurrent',
        'LongTermDebtNoncurrent',
        'AccountsReceivableNetCurrent',
        'AccountsNotesAndLoansReceivableNetCurrent',
        'ReceivablesNetCurrent',
        'AccountsPayableCurrent',
        'AccountsPayableTradeCurrent',
        'NetCashProvidedByUsedInOperatingActivities',
        'PaymentsToAcquirePropertyPlantAndEquipment',
        'PaymentsToAcquireProductiveAssets',
        'MarketableSecuritiesCurrent',
        'PaymentsToAcquireProductiveAssets']

# Revenue = RevenueFromContractWithCustomerExcludingAssessedTax, RevenueFromSaleOfGoods
# Cost of Revenue = 
pd.set_option('max_columns', 20)
pd.set_option('display.max_columns', 20)

date = datetime.date.today();
earliest_year = date.year - 6

filelist = os.listdir("historical")
for name in filelist:
    if not name.endswith("json"):
        filelist.remove(name)

#filelist = filelist[:300]

#print(filelist)
#filelist = ["CIK0000320193.json", "CIK0001903484.json", "CIK0000072971.json",
#    "CIK0001882781.json", "CIK0001110646.json"]
#filelist = ["CIK0000016058.json"]
#filelist = ["CIK0001318605.json"]

list_size = len(filelist)
current_record = 0

stocks = {}

for file in filelist:
    earliest_year = date.year - 6
    current_record = current_record + 1
    print("\b"*14 + str(100 * current_record // list_size) + "% complete", end="", flush=True)
    f = open("historical/" + file)
    j = json.load(f)
    formatted = json.dumps(j, indent=4)
    #pprint.pprint(formatted, depth=3)

    cik = str(int(file[3:-5]))

    if cik not in stocks:
        stocks[cik] = {}

    try:
        records = j['facts']['dei']['EntityCommonStockSharesOutstanding']['units']['shares']
    except:
        continue

    for record in records:
        fy = record['fy']
        fp = record['fp']
        val = record['val']

        if fy is None or fy < earliest_year:
            continue

        if fp not in ['FY', 'Q1', 'Q2', 'Q3']:
            continue

        if fy not in stocks[cik]:
            stocks[cik][fy] = {'FY': {}, 'Q1': {}, 'Q2': {}, 'Q3': {}}

        stocks[cik][fy][fp]['EntityCommonStockSharesOutstanding'] = val

    for category in categories:
        try:
            records = j['facts']['us-gaap'][category]['units']['USD']
        except:
            continue

        for record in records:
            fy = record['fy']
            fp = record['fp']
            val = record['val']

            try:
                frame = record['frame']
            except:
                frame = ""

            if fy is None or fy < earliest_year:
                continue

            if fp not in ['FY', 'Q1', 'Q2', 'Q3']:
                continue

            if fy not in stocks[cik]:
                stocks[cik][fy] = {'FY': {}, 'Q1': {}, 'Q2': {}, 'Q3': {}}

            if fp == 'FY' and len(frame) > 6:
                continue

            stocks[cik][fy][fp][category] = val
    

pretty_stocks = json.dumps(stocks, indent=4)
print(pretty_stocks)
outfile = open("data/stocks.json", "w")
outfile.write(pretty_stocks)
outfile.close()
