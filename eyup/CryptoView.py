# pyinstaller --onefile --hidden-import pycountry --exclude-module matplotlib CryptoView.py

import CryptoCrawler as cc
import StockCrawler as yc
import RapidTechTools as rtt
from datetime import datetime, timedelta
from datetime import date
import os
import xlwings as xw
import time
import sys
import msvcrt
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pymysql


import time

if __name__ == '__main__':
    SAVE_INTERVAL = 7
    START_TICKER = ""
    WAIT = 1
    HISTPRICE = True
    FN = "CryptoView.xlsx"
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    fn = path + "/" + FN
    wb = xw.Book (fn)
    ws = wb.sheets["Coins"]
    ws2 = wb.sheets["Init"]
    ws3 = wb.sheets["HistPrices"]

    # list = cc.readInitCMB()
    # for i,e in enumerate(list):
    #     ws2["A" + str (i+1)].value = e

    # read stocks for working on
    # maxRow = 5000
    # listCryptos = ws2.range ("A1:A5000").value
    # for idx,cont in enumerate(listCryptos):
    #     if cont == None:
    #         maxRow = int(idx)
    #         break
    # for e in listCryptos:
    #     erg = cc.readCurrencyCMB(e)
    #     for key, val in erg.items (): print (f"{key} => {val} {type(val)}")
 
    # read starting row parameter
    startRow = ws["B1"].value

    # read stocks for working on
    maxRow = 5000
    listCoins = ws.range ("A3:A5000").value
    for idx,cont in enumerate(listCoins):
        if cont == None:
            maxRow = int(idx)
            break
    idxRow = 3  

    # read first line in HistPrice worksheet
    if HISTPRICE:
        listPrices = ws3.range ("A1:A1000000").value
        for idx,cont in enumerate(listPrices):
            if cont == None:
                firstPriceRow = int(idx+1)
                break

    for idx, coin in enumerate(listCoins):
        if idx == maxRow:
            break
        if startRow != None and idxRow < startRow:
            idxRow += 1
            continue
        print (f"Read data for {coin} in row {idxRow}...")
        if ws["A" + str (idxRow)].value != coin:
            print(f"Error - work stopped - working coin {coin} is not ident with value in A{idxRow}...")
            break

        # read data
        summary = cc.readCurrencyCMB(coin)
        if summary == {}:            
            idxRow += 1
            continue

        time.sleep (WAIT)

        # write data to excel
        symbolCoin = summary.get("symbol","N/A")
        ws["B" + str (idxRow)].value = symbolCoin
        ws["C" + str (idxRow)].value = datetime.today ()  
        ws["D" + str (idxRow)].value = summary.get("Price","N/A")
        link = f"https://coinmarketcap.com/currencies/{coin}/"
        ws["E" + str (idxRow)].add_hyperlink(link,text_to_display=f"{symbolCoin} Chart")
        ws["F" + str (idxRow)].value = summary.get("Price Change24h Absolut","N/A")
        ws["G" + str (idxRow)].value = summary.get("Price Change24h Percent","N/A")
        
        tmp7DLow = summary.get("7d Low","N/A")
        tmp7DHigh = summary.get("7d High","N/A")
        tmp7d = (tmp7DLow + tmp7DHigh) / 2
        tmp7dAbs = ws["D" + str (idxRow)].value - tmp7d
        tmp7dPerc = round((ws["D" + str (idxRow)].value - tmp7d) / tmp7d * 100, 2)        
        ws["H" + str (idxRow)].value = tmp7dAbs
        ws["I" + str (idxRow)].value = tmp7dPerc

        ws["J" + str (idxRow)].value = summary.get("Market Cap Absolut","N/A")
        ws["K" + str (idxRow)].value = summary.get("Trading Volume24h Absolut","N/A")
        ws["L" + str (idxRow)].value = summary.get("Trading Volume24h Percent","N/A")
        ws["M" + str (idxRow)].value = summary.get("Circulating Supply","N/A")

        idxRow += 1

        if HISTPRICE:
            if coin in listPrices:
                print(f"Price update skipped - coin {coin} allready in worksheet HistPrices...")
                continue
            endDT = datetime.now().strftime("%Y-%m-%d")
            startDT = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            histPrice = cc.readHistPriceCMBapi(coin, start=startDT, end=endDT)
            for key, val in histPrice.items ():
                if key == "coin":
                    continue
                ws3["A" + str(firstPriceRow)].value = coin   
                ws3["B" + str(firstPriceRow)].value = key 
                ws3["C" + str(firstPriceRow)].value = val[0]
                ws3["D" + str(firstPriceRow)].value = val[1]
                ws3["E" + str(firstPriceRow)].value = val[2]
                ws3["F" + str(firstPriceRow)].value = val[3]
                ws3["G" + str(firstPriceRow)].value = val[4]
                ws3["H" + str(firstPriceRow)].value = val[5]
                firstPriceRow += 1

        if idxRow % 5 == 0:
            wb.save (fn)
            # wb.close()
            print ("Saved to disk...")

        time.sleep(WAIT)

    wb.save (fn)
    # wb.close()
    print ("Saved to disk...")

    TIMEOUT = 900
    startTime = time.time()
    inp = None
    print(f"Program finished - pls press <enter> to close the window or wait {round(TIMEOUT / 60, 2)} minutes...")
    while True:
        if msvcrt.kbhit():
            inp = msvcrt.getch()
            break
        elif time.time() - startTime > TIMEOUT:
            break
