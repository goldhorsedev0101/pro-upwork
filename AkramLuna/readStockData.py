import quandl
import os
from dotenv import load_dotenv, find_dotenv
from benzinga import news_data
from datetime import datetime, timedelta
from datetime import date

load_dotenv(find_dotenv()) 
QUANDL_API = os.environ.get("QUANDL_API")
quandl.ApiConfig.api_key=QUANDL_API

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

def readBenzingaNews(ticker, date_from=None, date_to=None, maxCount=100):
    if date_from == None and date_to == None:
        endday = datetime.today()
        startDay = tday - timedelta(days=7) 
    elif date_from != None and date_to == None:
        startDay = datetime.strptime(date_from, "%Y-%m-%d")
        endday = startDay + timedelta(days=7) 
    elif date_from != None and date_to == None:
        startDay = datetime.strptime(date_from, "%Y-%m-%d")
        endDay = datetime.strptime(date_to, "%Y-%m-%d")

    paper = news_data.News(api_key)
    stories = paper.news(pagesize=30, date_from="2021-04-19", date_to="2021-04-23")




for stock in TEST_STOCKS:
    quandlMain = readQuandlMain(stock)
    # quandlMain = readQuandlMain(stock, dateFrom="2018-01-01")
    # quandlMain = readQuandlMain(stock, dateFrom="2018-01-01", timeDim ="MRT")
    # quandlMain = readQuandlMain(stock, timeDim ="MRT")
    quandlEvents = readQuandlEvents(stock)
    quandlMetadata = readQuandlMetadata(stock)
    quandlDaily = readQuandlDaily(stock)
    quandlActions = readQuandlActions(stock)
    quandlPrices = readQuandlPrices(stock)
    
    print(quandlEvents)
    print(quandlEvents.columns)
       
