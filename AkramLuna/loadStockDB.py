import quandl
import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv, find_dotenv
from benzinga import news_data
from datetime import datetime, timedelta
from datetime import date
import yfinance as yf
import pandas
import xlsxwriter
import mysql.connector

def sql_connector(hostPM, userPM, passwdPM, databasePM):
    """
    create cursor and db-connector for database
    local Maria-DB: (host="localhost", user="root", passwd="I65faue#MB7#", database="stockdb")
    local MySQL-DB: (host="localhost",user="root",passwd="I65faue#ML5#",database="stockdb")
    a2hosting.com database: (host="nl1-ss18.a2hosting.com", user="rapidtec_Rapid1898", passwd="I65faue#AG9#", database="rapidtec_stockdb")
    :param hostPM: hostname
    :param userPM: username
    :param passwdPM: password
    :param databasePM: database name
    :return: db-cursor and db-connector
    """
    mydb = mysql.connector.connect (host=hostPM, user=userPM, passwd=passwdPM, database=databasePM)
    return(mydb.cursor(),mydb)

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
    erg = quandl.get_table('SHARADAR/TICKERS', table='SF1', ticker=ticker)
    return(erg)

def readQuandlDaily(ticker):
    """
    Read Daily Data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
    """
    erg = quandl.get_table('SHARADAR/DAILY', ticker=ticker)
    erg["date"] = erg["date"].dt.date
    return(erg)

def readQuandlActions(ticker):
    """
    Read Actions Data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
    """
    erg = quandl.get_table('SHARADAR/ACTIONS', ticker=ticker)
    return(erg)

def readQuandlPrices(ticker):
    """
    Read Prices Data from Quandl
    Return: dataframe with data
    Args:
        ticker (str): ticker-symbol
    """
    erg = quandl.get(f"WIKI/{ticker}")   
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


if __name__ == '__main__':

    load_dotenv(find_dotenv()) 
    QUANDL_API = os.environ.get("QUANDL_API")
    quandl.ApiConfig.api_key=QUANDL_API
    BENZINGA_API = os.environ.get("BENZINGA_API")
    MYSQL_PW = os.environ.get("MYSQL_PW")

    c,mydb = sql_connector("localhost","root","I65faue#MB7#","stockdb")

    WORKON_MAIN = False
    WORKON_FINANCIALS = False
    WORKON_DAILYDATA = True
    WORKON_PRICES = False
    WORKON_NEWS = False

    # read stocks to workon from stockmain
    sql = "SELECT ticker FROM stockdb_akramluna.stockmain"
    var = []
    c.execute (sql, var)
    workTickers = []
    for dt_cont in c.fetchall():
        workTickers.append(dt_cont[0])

    # read data and update db
    for stock in workTickers:
        # read data
        if WORKON_MAIN:
            quandlMetadata = ""
            quandlMetadata = readQuandlMetadata(stock)
            # for i,v in quandlMetadata.iterrows(): print(f"DEBUG: {i}, {v}")     
        if WORKON_DAILYDATA:       
            quandlDaily = readQuandlDaily(stock)   
            print(quandlDaily)
            exit()


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

            sql = "UPDATE stockdb_akramluna.stockmain " \
                "SET lastUpdate=%s," \
                "name=%s," \
                "currency=%s," \
                "companySite=%s," \
                "firstPriceDate=%s," \
                "older1Year=%s," \
                "sector=%s," \
                "industry=%s," \
                "famaindustry=%s" \
                " WHERE ticker=%s"
            cont = [(datetime.today (),
                    quandlMetadata["name"].values[0],
                    quandlMetadata["currency"].values[0],
                    quandlMetadata["companysite"].values[0],
                    tmpInitialDate,
                    tmpOlder1Year,
                    quandlMetadata["sector"].values[0],
                    quandlMetadata["industry"].values[0],
                    quandlMetadata["famaindustry"].values[0],
                    stock)]        

            c.executemany (sql, cont)
            mydb.commit ()
            print (f"Stock Main updated for {stock}...")

        if WORKON_DAILYDATA:
            # read max data from stockdailydata
            sql = "SELECT MAX(dateMeasure) FROM stockdb_akramluna.stockdailydata WHERE ticker = %s"
            var = [(stock)]
            c.execute (sql, var)
            dt_exist = []
            lastDate = c.fetchone ()[0]

            for idx,elem in quandlDaily.iterrows():
                print(idx)
                # elem = elem["date"].to_pydatetime()
                print(elem["date"])
                print(type(elem["date"]))
                exit()


           