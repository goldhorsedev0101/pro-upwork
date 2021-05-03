import modulesAkram as mod
import quandl
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import mysql.connector
from dotenv import load_dotenv, find_dotenv
from benzinga import news_data
from datetime import datetime, timedelta
from datetime import date
import yfinance as yf
import pandas
import xlsxwriter
import mysql.connector
import time
import re
import sys
import xlwings as xw

if __name__ == '__main__':
    load_dotenv(find_dotenv()) 
    QUANDL_API = os.environ.get("QUANDL_API")
    quandl.ApiConfig.api_key=QUANDL_API
    BENZINGA_API = os.environ.get("BENZINGA_API")
    MYSQL_PW = os.environ.get("MYSQL_PW")
    MYSQL_DBNAME = os.environ.get("MYSQL_DBNAME")

    c,mydb = mod.sql_connector("localhost", "root", MYSQL_PW, MYSQL_DBNAME)

    FORCE_TICKERS = []
    WORKON_MAIN = True
    WORKON_FINANCIALS = True
    WORKON_DAILYDATA = True
    WORKON_PRICES = True
    WORKON_NEWS = True
    STARTDATE_PRICES = "2010-01-01"
    STARTDATE_NEWS = "2021-04-01"
    MAXCOUNT_NEWS = 100

    # read tickers to read from excel
    FN = "StocksWork.xlsx"
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    fn = path + "/" + FN
    wb = xw.Book (fn)
    ws = wb.sheets["Work"]
    workStocksExcel = [x for x in ws.range ("A2:A2000").value if x != None]

    # read stocks to workon from stockmain
    sql = f"SELECT ticker FROM {MYSQL_DBNAME}.stockmain"
    var = []
    c.execute (sql, var)
    workTickers = []
    for dt_cont in c.fetchall():
        workTickers.append(dt_cont[0])

    # join workinglist together from excel and db and sort it finally
    workTickers = sorted(list(set(workTickers + workStocksExcel)))

    # read data and update db
    for stock in workTickers:
        if FORCE_TICKERS != [] and stock not in FORCE_TICKERS:
            continue

        # read data
        if WORKON_MAIN:
            quandlMetadata = ""
            quandlMetadata = mod.readQuandlMetadata(stock)
            if len(quandlMetadata) == 0:
                print(f"No Main data found for ticker {stock}... skipped...")
                continue        
            # for i,v in quandlMetadata.iterrows(): print(f"DEBUG: {i}, {v}")     
            yahooSummary = mod.read_yahoo_summary(stock,att=3,default=None)

        if WORKON_DAILYDATA:       
            quandlDaily = mod.readQuandlDaily(stock)   
            if len(quandlDaily) == 0:
                print(f"No Daily data found for ticker {stock}... skipped...")
                continue                   
        
        if WORKON_FINANCIALS:    
            quandlFinancials = mod.readQuandlMain(stock)  
            # pd.set_option('display.max_rows', None)            
            # for elem in quandlFinancials.iterrows():
            #     print(elem)

        if WORKON_PRICES:
            yahooPrices = mod.readYFPrices(stock, startDate=STARTDATE_PRICES)
            # print(yahooPrices)       
            # print(yahooPrices.index[0])
            # print(type(yahooPrices.index[0]))
            # exit()
                    
        if WORKON_NEWS:
            benzingaNews = mod.readBenzingaNews(stock, date_from = STARTDATE_NEWS, date_to = datetime.today(), limit4PM=True, api=BENZINGA_API)
            # for elem in benzingaNews:
            #     print(f"\n\n")
            #     for key, val in elem.items ():
            #         print (f"{key} => {val} {type(val)}")           
            # print(len(benzingaNews))
            # exit()

            sql = f"SELECT benzingaID, ticker FROM {MYSQL_DBNAME}.stocknews"
            c.execute (sql)
            benzingaIDExist = []
            for dt_cont in c.fetchall():
                benzingaIDExist.append(dt_cont)                  
            # for i in benzingaIDExist:
            #     print(i)
            # exit()                                          

        # update db
        if WORKON_MAIN:
            dt64 = quandlMetadata["firstpricedate"].values[0]
            dt64Time = str(dt64).split("T")[0]
            tmpInitialDate = datetime.strptime(dt64Time, "%Y-%m-%d")                
            tmpOlder1Year = datetime.today() - timedelta(days=365)
            if tmpInitialDate < tmpOlder1Year:
                tmpOlder1Year = "Y"
            else: 
                tmpOlder1Year = "N"         

            sql = f"UPDATE {MYSQL_DBNAME}.stockmain " \
                "SET lastUpdate=%s," \
                "name=%s," \
                "currency=%s," \
                "exchange=%s," \
                "fiftyDayRangeFrom=%s," \
                "fiftyDayRangeTo=%s," \
                "marketCap=%s," \
                "beta=%s," \
                "price1YEst=%s," \
                "actPrice=%s," \
                "companySite=%s," \
                "firstPriceDate=%s," \
                "older1Year=%s," \
                "sector=%s," \
                "industry=%s," \
                "famaindustry=%s," \
                "nextEarningsDate=%s," \
                "lastDividendDate=%s," \
                "forwardDividend=%s," \
                "dividendYield=%s" \
                " WHERE ticker=%s"
            cont = [(datetime.today (),
                    str(quandlMetadata["name"].values[0]),
                    str(quandlMetadata["currency"].values[0]),
                    yahooSummary.get("exchange",None),
                    yahooSummary.get("fifty_range_from",None),
                    yahooSummary.get("fifty_range_to",None),
                    yahooSummary.get("marketcap",None),
                    yahooSummary.get("beta",None),
                    yahooSummary.get("price1Yest",None),
                    yahooSummary.get("price",None),
                    str(quandlMetadata["companysite"].values[0]),
                    tmpInitialDate,
                    tmpOlder1Year,
                    str(quandlMetadata["sector"].values[0]),
                    str(quandlMetadata["industry"].values[0]),
                    str(quandlMetadata["famaindustry"].values[0]),
                    yahooSummary.get("next_earnings_date",None),
                    yahooSummary.get("last_dividend_date",None),
                    yahooSummary.get("forw_dividend",None),
                    yahooSummary.get("div_yield",None),
                    stock)]        

            c.executemany (sql, cont)
            mydb.commit ()
            print (f"Stock Main updated for {stock}...")

        if WORKON_DAILYDATA:
            # read max data from stockdailydata
            print(f"Inserting daily data for {stock}...")
            sql = f"SELECT MAX(dateMeasure) FROM {MYSQL_DBNAME}.stockdailydata WHERE ticker = %s"
            var = [(stock)]
            c.execute (sql, var)
            lastDate = c.fetchone ()[0]         
            if lastDate != None:                            
                print(f"Insert daily data from {lastDate}...")
                quandlDaily = quandlDaily[(quandlDaily['date'] > lastDate)]
            else:
                print(f"Insert all daily data for {stock}...")

            for idx,elem in quandlDaily.iterrows():
                sql = f"INSERT INTO {MYSQL_DBNAME}.stockdailydata (" \
                      "ticker," \
                      "dateMeasure," \
                      "ev," \
                      "evToEbit," \
                      "evToEbitda," \
                      "marketCap," \
                      "pbRatio," \
                      "peRatio," \
                      "psRatio)" \
                      " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cont = [(stock,
                        elem["date"],
                        float(elem["ev"]),
                        float(elem["evebit"]),
                        float(elem["evebitda"]),
                        float(elem["marketcap"]),
                        float(elem["pb"]),
                        float(elem["pe"]),
                        float(elem["ps"]))]
                c.executemany (sql, cont)
                mydb.commit ()

                if idx % 500 == 0 and idx > 0:
                    print(f"Daily rows are inserted for {stock} till {elem['date']}")

        if WORKON_FINANCIALS:      
            # delete all existing data
            sql = f"DELETE FROM {MYSQL_DBNAME}.stockfinancials " \
                  " WHERE ticker=%s"
            cont = [(stock,)]
            c.executemany (sql, cont)

            # load data for stock
            for idx,elem in quandlFinancials.iterrows():
                sql = f"INSERT INTO {MYSQL_DBNAME}.stockfinancials (" \
                      "ticker," \
                      "dateCal," \
                      "dateReport," \
                      "price," \
                      "netinc," \
                      "marketcap," \
                      "assets," \
                      "capex," \
                      "cashneq," \
                      "currentratio," \
                      "debt," \
                      "ebit," \
                      "ebitda," \
                      "ebitdamargin," \
                      "eps," \
                      "equity," \
                      "ev," \
                      "evebit," \
                      "evebidta," \
                      "fcf," \
                      "fcfps," \
                      "gp," \
                      "grossmargin," \
                      "inventory," \
                      "investments," \
                      "liabilities," \
                      "ncf," \
                      "netmargin," \
                      "payables," \
                      "pb," \
                      "pe," \
                      "ps," \
                      "receivables," \
                      "revenue," \
                      "rnd," \
                      "roa," \
                      "roe," \
                      "roic," \
                      "ros," \
                      "tangibles," \
                      "workingcapital)" \
                      " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cont = [(stock,
                        elem["calendardate"].to_pydatetime(),
                        elem["reportperiod"].to_pydatetime(),
                        float(elem["price"]),
                        float(elem["netinc"]),
                        float(elem["marketcap"]),
                        float(elem["assets"]),
                        float(elem["capex"]),
                        float(elem["cashneq"]),
                        float(elem["currentratio"]),
                        float(elem["debt"]),
                        float(elem["ebit"]),
                        float(elem["ebitda"]),
                        float(elem["ebitdamargin"]),
                        float(elem["eps"]),
                        float(elem["equity"]),
                        float(elem["ev"]),
                        float(elem["evebit"]),
                        float(elem["evebitda"]),
                        float(elem["fcf"]),
                        float(elem["fcfps"]),
                        float(elem["gp"]),
                        float(elem["grossmargin"]),
                        float(elem["inventory"]),
                        float(elem["investments"]),
                        float(elem["liabilities"]),
                        float(elem["ncf"]),
                        float(elem["netmargin"]),
                        float(elem["payables"]),
                        float(elem["pb"]),
                        float(elem["pe"]),
                        float(elem["ps"]),
                        float(elem["receivables"]),
                        float(elem["revenue"]),
                        float(elem["rnd"]),
                        float(elem["roa"]),
                        float(elem["roe"]),
                        float(elem["roic"]),
                        float(elem["ros"]),
                        float(elem["tangibles"]),
                        float(elem["workingcapital"]))]
                c.executemany (sql, cont)
                mydb.commit ()
            print (f"Stock Financials updated for {stock}...") 

        if WORKON_PRICES:
            # read max data from stockprices
            print(f"Inserting daily price data for {stock}...")
            sql = f"SELECT MAX(datePrice) FROM {MYSQL_DBNAME}.stockprices WHERE ticker = %s"
            var = [(stock)]
            c.execute (sql, var)
            lastDate = c.fetchone ()[0]         
            lastDate = pd.Timestamp(lastDate)            
            if lastDate != None:  
                # read min data from stockprices                          
                sql = f"SELECT MIN(datePrice) FROM {MYSQL_DBNAME}.stockprices WHERE ticker = %s"
                var = [(stock)]
                c.execute (sql, var)
                firstDate = c.fetchone ()[0]    
                firstDate = pd.Timestamp(firstDate)            
                firstDatePrice = yahooPrices.index[0]                               
                
                if firstDatePrice >= firstDate:
                    print(f"Insert daily data from {lastDate.to_pydatetime().date()}...")
                    yahooPrices = yahooPrices[(yahooPrices.index > lastDate)]
                else:
                    # delete all existing data
                    sql = f"DELETE FROM {MYSQL_DBNAME}.stockprices " \
                        " WHERE ticker=%s"
                    cont = [(stock,)]
                    c.executemany (sql, cont)                                        
                    
                    print(f"Insert all daily data for {stock}...")
            else:
                print(f"Insert all daily data for {stock}...")

            countPriceRows = 1
            for idx,elem in yahooPrices.iterrows():
                sql = f"INSERT INTO {MYSQL_DBNAME}.stockprices (" \
                      "ticker," \
                      "datePrice," \
                      "open," \
                      "high," \
                      "low," \
                      "close," \
                      "adjClose," \
                      "volume)" \
                      " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cont = [(stock,
                        idx.to_pydatetime(),
                        float(elem["Open"]),
                        float(elem["High"]),
                        float(elem["Low"]),
                        float(elem["Close"]),
                        float(elem["Adj Close"]),
                        float(elem["Volume"]))]
                c.executemany (sql, cont)
                mydb.commit ()
                countPriceRows += 1

                if countPriceRows % 500 == 0:
                    print(f"Daily prices are inserted for {stock} till {idx.to_pydatetime().date()}")

        if WORKON_NEWS:
            print(f"Inserting news for {stock}...")
            for elem in benzingaNews:
                if (elem.get("id"),stock) in benzingaIDExist:
                    continue
                for stockNews in elem["stocks"]:
                    if stockNews not in workTickers or (elem.get("id"),stockNews) in benzingaIDExist:
                        continue
                    sql = f"INSERT INTO {MYSQL_DBNAME}.stocknews (" \
                            "benzingaID," \
                            "ticker," \
                            "datetimeNews," \
                            "authorNews," \
                            "titleNews," \
                            "urlNews," \
                            "channelsNews," \
                            "tagsNews)" \
                            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    cont = [(elem["id"],
                            stockNews,
                            datetime.strptime(elem["created"], "%a, %d %b %Y %H:%M:%S %z"),
                            elem["author"],
                            elem["title"],
                            elem["url"],
                            elem["channels"],
                            elem["tags"])]
                    c.executemany (sql, cont)
                    mydb.commit ()
                    benzingaIDExist.append((elem.get("id"),stockNews))