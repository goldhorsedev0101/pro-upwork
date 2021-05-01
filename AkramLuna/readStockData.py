# Docu: https://www.quandl.com/databases/SF1/documentation
# Time Dimensions: https://www.quandl.com/databases/SF1/documentation?anchor=dimensions
# Data Organization: https://docs.quandl.com/docs/data-organization
# EventCodes: https://www.quandl.com/tables/SF1/SHARADAR-INDICATORS - download excel and search for eventcodes

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
    """
    Read main data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
        dateFrom (str in form "yyyy-mm-dd", optional): Set default from-Date. Defaults to None.
        timeDim (str, optional): Set used time-Dimension. Docu see here: 
        https://www.quandl.com/databases/SF1/documentation?anchor=dimensions 
        Defaults to None.
    """
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
    """
    Read Events Data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
    """
    erg = quandl.get_table('SHARADAR/EVENTS', ticker=ticker)
    return(erg)

def readQuandlMetadata(ticker):
    erg = quandl.get_table('SHARADAR/TICKERS', table='SF1', ticker='AAPL')
    return(erg)

def readQuandlDaily(ticker):
    """
    Read Daily Data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
    """
    erg = quandl.get_table('SHARADAR/DAILY', ticker='AAPL')
    return(erg)

def readQuandlActions(ticker):
    """
    Read Actions Data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
    """
    erg = quandl.get_table('SHARADAR/ACTIONS', ticker='AAPL')
    return(erg)

def readQuandlPrices(ticker):
    """
    Read Prices Data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
    """
    erg = quandl.get('WIKI/AAPL')
    return(erg)

def readBenzingaNews(ticker, date_from=None, date_to=None, maxCount=100, limit4PM=True):
    """
    Read Benzinga News-Data
    (test-api-key only limited to 100 news-messages it seems)
    Return: list with data
    Args:
        ticker (str): ticker-symbol
        date_from (str in form "yyyy-mm-dd", optional): Defaults to None.
            Start date from where the news should be read
        date_to (str in form "yyyy-mm-dd", optional): Defaults to None.
            End date to where the news should be read
            if both dates are none => news from actual day back for 7 days
            if date_from is none and date_to is not none => 7 days back from enddate
            if date_from is not none and date_to is none => 7 days from startdate forward
            if both dates are not none => take this timespan for reading news
        maxCount (int, optional): Defaults to 100.
            amount of news which should be read
            (test-api-key only limited to 100 news-messages it seems)
        limit4PM (bool, optional): [description]. Defaults to True.
    """

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
    """
    Read YF summary data
    Return: yfinance.ticker data
    Arguments:
        ticker (str): ticker-symbol
    """
    dataYF = yf.Ticker(ticker)
    return(dataYF)

def readYFPrices(ticker,startDate=None,endDate=None):
    """
    Read YF price data
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
        startDate (str in form "yyyy-mm-dd", optional): Defaults to None.
            Start date from where the prices should be read
        endDate (str in form "yyyy-mm-dd", optional): Defaults to None.
            End date to where the prices should be read
            if both dates are none => all prices are read
            if date_from is none and date_to is not none => read prices with starting from "1980-01-01"
            if date_from is not none and date_to is none => read prices from start-date to actual date
            if both dates are not none => take this timespan for reading prices
    """
    if startDate != None and endDate != None:
        startDT = datetime.strptime(startDate, "%Y-%m-%d")
        endDT = datetime.strptime(endDate, "%Y-%m-%d")
        erg = yf.download(ticker,start=startDT,end=endDT)
    elif startDate != None and endDate == None:
        startDT = datetime.strptime(startDate, "%Y-%m-%d")
        endDT = datetime.today()
        erg = yf.download(ticker,start=startDT,end=endDT)
    elif startDate == None and endDate != None:
        startDT = datetime.strptime("1980-01-01", "%Y-%m-%d")
        endDT = datetime.strptime(endDate, "%Y-%m-%d")      
        erg = yf.download(ticker,start=startDT,end=endDT) 
    elif startDate == None and endDate == None:
        erg = yf.download(ticker)
    return(erg)


for stock in TEST_STOCKS:
   
    # erg = quandl.get_table('SHARADAR/INDICATORS', table='SF1')
    # print(erg)

    #  read quandl
    # quandlMain = readQuandlMain(stock)
    # quandlMain2 = readQuandlMain(stock, dateFrom="2018-01-01", timeDim ="MRT")
    # # quandlMain3 = readQuandlMain(stock, dateFrom="2018-01-01")
    # print (quandlMain.iloc[-1])
    # for i,v in quandlMain.iloc[-1].items():
    #     print(i, v)    

    # quandlMetadata = readQuandlMetadata(stock)
    # print(quandlMetadata)
    # for i,v in quandlMetadata.iterrows():
    #     print(i, v)       
    
    quandlDaily = readQuandlDaily(stock)
    quandlDaily["date"] = quandlDaily["date"].dt.date
    print(quandlDaily["date"].iloc[-1])
    print(type(quandlDaily["date"].iloc[-1]))
    
    # quandlActions = readQuandlActions(stock)
    # print (quandlActions)    
    
    # quandlPrices = readQuandlPrices(stock)
    # print(quandlPrices)



    # # # read benzingNews
    # benzingNews1 = readBenzingaNews(stock)
    # print(benzingNews1)

    # # benzingNews2 = readBenzingaNews(stock, date_from="2021-04-21", date_to="2021-04-21")
    # # benzingNews3 = readBenzingaNews(stock, date_from="2021-04-21")
    # # benzingNews4 = readBenzingaNews(stock, date_to="2021-04-21")
    # # benzingNews5 = readBenzingaNews(stock,limit4PM=False)   
    # outputFinal = []
    # for idx, elem in enumerate(benzingNews1):
    #     outputHeader = []
    #     outputRow = []
    #     for key, val in elem.items ():
    #         if idx == 0:
    #             outputHeader.append(key)
    #         if key in ["image","channels","stocks","tags"]:
    #             if val != []:
    #                 outputCell = []              
    #                 for inpCell in val:
    #                     for k,v in inpCell.items():
    #                         outputCell.append(v)
    #                 outputRow.append(outputCell)
    #             else:
    #                 outputRow.append("-")
    #         else:
    #             outputRow.append(val)
    #     if idx == 0:
    #         outputFinal.append(outputHeader)     
    #     outputFinal.append(outputRow)    
    
    # for idx,elem in enumerate(outputFinal):
    #     print(f"\n\n{idx}")
    #     for idx2,elem2 in enumerate(elem):
    #         print(idx2,elem2)

    # for idx, elem in enumerate(benzingNews1):
    #     print(f"\n\nStory {idx}:")
    #     for key, val in elem.items ():
    #         # if key == "created":
    #         print(f"{key} => {val}")    
    #     exit()


    # # read YFinance
    # dataYF = readYFSummary(stock)
    # # Summary Infos
    # tmpKey = []
    # tmpVal = []
    # listFinal = []
    # for key, val in dataYF.info.items ():
    #     tmpKey.append(key)
    #     tmpVal.append(val)
    #     if val not in [False,None]:
    #         print (f"{key} => {val} {type(val)}")
    # listFinal.append(tmpKey)
    # listFinal.append(tmpVal)
    # YFfinancials = dataYF.financials
    # YFdividends = dataYF.dividends
    # YFsplits = dataYF.splits
    # YFmajorholders = dataYF.major_holders
    # YFinstholders = dataYF.institutional_holders
    # YFbalsheet = dataYF.balance_sheet
    # YFcashflow = dataYF.cashflow
    # YFearnings = dataYF.earnings
    # print(YFearnings)
    # YFsustain = dataYF.sustainability
    # YFrecommend = dataYF.recommendations
    # YFcalendar = dataYF.calendar  
    # print(YFcalendar)
    # pricesYF = readYFPrices(stock)
    # # pricesYF = readYFPrices(stock,startDate="2020-01-01",endDate="2020-12-31")
    # # pricesYF = readYFPrices(stock,startDate="2020-01-01")
    # # pricesYF = readYFPrices(stock,endDate="1999-12-31")
    # print(pricesYF)


    # # write to excel
    # writer = pd.ExcelWriter('basisReadData.xlsx', engine='xlsxwriter')
    # quandlMain.to_excel(writer, sheet_name="quandlMain"),	
    # quandlMain2.to_excel(writer, sheet_name="quandlMain_From2018_MRT")
    # quandlEvents.to_excel(writer, sheet_name="quandlEvents")
    # quandlMetadata.to_excel(writer, sheet_name="quandlMetadata")
    # quandlDaily.to_excel(writer, sheet_name="quandlDaily")
    # quandlActions.to_excel(writer, sheet_name="quandlActions")
    # quandlPrices.to_excel(writer, sheet_name="quandlPrices")
    # pd.DataFrame (outputFinal).to_excel (writer, sheet_name="benzingNews", header=False, index=False) 
    # pd.DataFrame (listFinal).to_excel (writer, sheet_name="yFinance Info", header=False, index=False) 
    # YFfinancials.to_excel(writer, sheet_name="YFfinancials")
    # YFdividends.to_excel(writer, sheet_name="YFdividends")
    # YFsplits.to_excel(writer, sheet_name="YFsplits")
    # YFmajorholders.to_excel(writer, sheet_name="YFmajorholders")
    # YFinstholders.to_excel(writer, sheet_name="YFinstholders")
    # YFbalsheet.to_excel(writer, sheet_name="YFbalsheet")
    # YFcashflow.to_excel(writer, sheet_name="YFcashflow")
    # YFearnings.to_excel(writer, sheet_name="YFearnings")
    # YFsustain.to_excel(writer, sheet_name="YFsustain")
    # YFrecommend.to_excel(writer, sheet_name="YFrecommend")
    # YFcalendar.to_excel(writer, sheet_name="YFcalendar")
    # YFprices.to_excel(writer, sheet_name="YFprices")
    # writer.save()
  

    exit()


       
