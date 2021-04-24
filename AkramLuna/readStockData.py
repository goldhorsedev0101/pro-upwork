import quandl
import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from benzinga import news_data
from datetime import datetime, timedelta
from datetime import date
import yfinance as yf
import pandas
import xlsxwriter

load_dotenv(find_dotenv()) 
QUANDL_API = os.environ.get("QUANDL_API")
quandl.ApiConfig.api_key=QUANDL_API
BENZINGA_API = os.environ.get("BENZINGA_API")

TEST_STOCKS = ["AAPL","FB","AMZN","CAT","FB"]

def readQuandlMain(ticker, dateFrom=None, timeDim=None):
    if dateFrom == None and timeDim == None:
        erg = quandl.get_table('SHARADAR/SF1', ticker=ticker, dimension="MRY")
    elif dateFrom != None and timeDim == None:
        erg = quandl.get_table('SHARADAR/SF1', calendardate={'gte':dateFrom}, dimension="MRY", ticker=ticker)       
    elif dateFrom == None and timeDim != None:
        erg = quandl.get_table('SHARADAR/SF1', dimension=timeDim, ticker=ticker)
    elif dateFrom != None and timeDim != None:
        erg = quandl.get_table('SHARADAR/SF1', calendardate={'gte':dateFrom}, dimension=timeDim, ticker=ticker)
    else:
        erg = []
    return(erg)

def readQuandlEvents(ticker):
    erg = quandl.get_table('SHARADAR/EVENTS', ticker=ticker)
    return(erg)

def readQuandlMetadata(ticker):
    erg = quandl.get_table('SHARADAR/TICKERS', table='SF1', ticker='AAPL')
    return(erg)

def readQuandlDaily(ticker):
    erg = quandl.get_table('SHARADAR/DAILY', ticker='AAPL')
    return(erg)

def readQuandlActions(ticker):
    erg = quandl.get_table('SHARADAR/ACTIONS', ticker='AAPL')
    return(erg)

def readQuandlPrices(ticker):
    erg = quandl.get('WIKI/AAPL')
    return(erg)

def readBenzingaNews(ticker, date_from=None, date_to=None, maxCount=100, limit4PM=True):
    if date_from == None and date_to == None:
        endDay = datetime.today()
        startDay = endDay - timedelta(days=7)
    elif date_from != None and date_to == None:
        startDay = datetime.strptime(date_from, "%Y-%m-%d")
        endDay = startDay + timedelta(days=7) 
    elif date_from == None and date_to != None:
        endDay = datetime.strptime(date_to, "%Y-%m-%d")
        startDay = endDay - timedelta(days=7)  
    elif date_from != None and date_to != None:
        startDay = date_from
        endDay = date_to    
    else:
        print(f"Wrong date_from and/or date_to in function readBenzingaNews...")
        return {}

    if type(startDay) != str:
        startDay = datetime.strftime(startDay, "%Y-%m-%d")
    if type(endDay) != str:
        endDay = datetime.strftime(endDay, "%Y-%m-%d")

    print(f"News read from Benzinga for {ticker}, maximum {maxCount} articles, from {startDay} to {endDay}...")

    paper = news_data.News(BENZINGA_API)
    stories = paper.news(company_tickers=ticker, pagesize=maxCount, date_from=startDay, date_to=endDay)
    
    if limit4PM:
        finalestories = []
        for idx, elem in enumerate(stories):
            tmpStoryCreateDate = elem.get("created","N/A")
            tmpTime = tmpStoryCreateDate.split(" ")[-2]
            tmpHour = tmpTime.split(":")[0]
            # print(tmpStoryCreateDate)
            # print(type(tmpStoryCreateDate))
            # print(tmpTime)
            # print(tmpHour)
            if int(tmpHour) < 16:
                finalestories.append(elem)
        return(finalestories)
    else:
        return(stories)

def readYFSummary(ticker):
    dataYF = yf.Ticker(ticker)
    return(dataYF)

for stock in TEST_STOCKS:
    # quandlMain = readQuandlMain(stock)
    # quandlMain2 = readQuandlMain(stock, dateFrom="2018-01-01", timeDim ="MRT")
    # # quandlMain3 = readQuandlMain(stock, dateFrom="2018-01-01")
    # quandlEvents = readQuandlEvents(stock)
    # quandlMetadata = readQuandlMetadata(stock)
    # quandlDaily = readQuandlDaily(stock)
    # quandlActions = readQuandlActions(stock)
    # quandlPrices = readQuandlPrices(stock)
  
    benzingNews1 = readBenzingaNews(stock)
    # benzingNews2 = readBenzingaNews(stock, date_from="2021-04-21", date_to="2021-04-21")
    # benzingNews3 = readBenzingaNews(stock, date_from="2021-04-21")
    # benzingNews4 = readBenzingaNews(stock, date_to="2021-04-21")
    # benzingNews5 = readBenzingaNews(stock,limit4PM=False)   
    outputFinal = []
    for idx, elem in enumerate(benzingNews1):
        outputHeader = []
        outputRow = []
        for key, val in elem.items ():
            if idx == 0:
                outputHeader.append(key)
            if key in ["image","channels","stocks","tags"]:
                if val != []:
                    outputCell = []              
                    for inpCell in val:
                        for k,v in inpCell.items():
                            outputCell.append(v)
                    outputRow.append(outputCell)
                else:
                    outputRow.append("-")
            else:
                outputRow.append(val)
        if idx == 0:
            outputFinal.append(outputHeader)     
        outputFinal.append(outputRow)    
    # for idx, elem in enumerate(benzingNews1):
    #     print(f"\n\nStory {idx}:")
    #     for key, val in elem.items ():
    #         # if key == "created":
    #         print(f"{key} => {val}")    
    #     exit()

    writer = pd.ExcelWriter('basisReadData.xlsx', engine='xlsxwriter')
    # quandlMain.to_excel(writer, sheet_name="quandlMain"),	
    # quandlMain2.to_excel(writer, sheet_name="quandlMain_From2018_MRT")
    # quandlEvents.to_excel(writer, sheet_name="quandlEvents")
    # quandlMetadata.to_excel(writer, sheet_name="quandlMetadata")
    # quandlDaily.to_excel(writer, sheet_name="quandlDaily")
    # quandlActions.to_excel(writer, sheet_name="quandlActions")
    # quandlPrices.to_excel(writer, sheet_name="quandlPrices")
    pd.DataFrame (outputFinal).to_excel (writer, sheet_name="benzingNews", header=False, index=False) 
    writer.save()
    exit()





    # dataYF = readYFSummary(stock)
    # # Summary Infos
    # for key, val in dataYF.info.items ():
    #     if val not in [False,None]:
    #         print (f"{key} => {val} {type(val)}")
    # print(dataYF.financials)
    # print(dataYF.dividends)
    # print(dataYF.splits)
    # print(dataYF.major_holders)
    # print(dataYF.institutional_holders)
    # print(dataYF.balance_sheet)
    # print(dataYF.cashflow)
    # print(dataYF.earnings)
    # print(dataYF.sustainability)
    # print(dataYF.recommendations)
    # print(dataYF.calendar)  
    
    exit()


       
