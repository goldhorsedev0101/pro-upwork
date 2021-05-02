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

def replace_more (inp_str, list_chars, target_char=""):
    """
    Replace several chars in a string
    :param inp_str: string which should be changed
    :param list_chars: which chars should be changed in list-form
    :param target_char: with which char the list_chars should be replaced - default is ""
    :return: changed string
    """
    for i in list_chars:
        inp_str = inp_str.replace(i,target_char)
    return inp_str

def clean_value(value, dp=".", tcorr=False, out="None"):
    """
    clean value to Float / Int / Char / None
    :param value: value which will be worked on
    :param dp: decimalpüint <.> or <,>
    :param tcorr: thousand corecction - if True numeric value will be multiplicated by 1000 - if False not
    :param out: output value in case of an invalid value
    :return: cleaned value (or error-value "N/A", None, "" defined in out)
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pattern1 = re.compile ("^[a-zA-Z]{3} [0-9]{2}, [0-9]{4}$")
    pattern2 = re.compile ("^[0-9]{4}-[0-9]{2}$")
    pattern3 = re.compile ("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    pattern4 = re.compile ("^[0-9]{1,2}/[0-9]{2}/[0-9]{4}$")
    pattern5 = re.compile ("^[a-zA-Z]{3}[0-9]{2}$")
    pattern6 = re.compile ("^[a-zA-Z]{3}[0-9]{4}$")
    value = replace_more(str(value).strip(), ["%","+-","+","$","€"])

    if pattern1.match(value) != None:
        value = datetime.strftime((datetime.strptime (value,"%b %d, %Y")),"%Y-%m-%d")
        return(value)
    elif pattern2.match(value) != None:
        dt = datetime.strptime (value, "%Y-%m")
        y = dt.year
        m = dt.month
        ultimo = calendar.monthrange (y, m)[1]
        value = datetime.strftime(date(y,m,ultimo), "%Y-%m-%d")
        return(value)
    elif pattern3.match(value) != None: return(value)
    elif pattern4.match (value) != None:
        value = datetime.strftime ((datetime.strptime (value, "%m/%d/%Y")), "%Y-%m-%d")
        return (value)
    elif pattern5.match (value) != None or pattern6.match (value) != None:
        if pattern5.match (value) != None:
            searchText = "%b%y"
        if pattern6.match (value) != None:
            searchText = "%b%Y"
        dt = datetime.strptime (value, searchText)
        m = dt.month
        y = dt.year
        ultimo = calendar.monthrange (y, m)[1]
        value = datetime.strftime (date (y, m, ultimo), "%Y-%m-%d")
        return(value)
    elif value in ["N/A","None","nan","-","—","","∞","-∞","Invalid Date","�","undefined"]:
        if out == "None": return(None)
        elif out == "N/A": return("N/A")
    elif ("M" in value or "B" in value or "T" in value or "k" in value) and replace_more(value, [",",".","M","B","T","k","-","$"]).isdigit():
        if "M" in value: char = "M"
        elif "B" in value: char = "B"
        elif "T" in value: char = "T"
        elif "k" in value: char = "k"
        decimal_place = value.find(dp)
        b_place = value.find(char)
        if decimal_place == -1:
            b_place = 1
            decimal_place = 0
        if char in ["M", "B", "T"]: value = replace_more(value, [".",",",char])
        # million
        if char == "M":
            for i in range (3 - (b_place - decimal_place - 1)): value = value + "0"
        # billion
        if char == "B":
            for i in range(6 - (b_place - decimal_place -1)): value = value + "0"
        # trillion
        if char == "T":
            for i in range(9 - (b_place - decimal_place -1)): value = value + "0"
        # thousand
        if char == "k":
            value = value.replace("k","")
        value = float(value)
        if tcorr: return (value * 1000)
        else: return (value)
    elif ":" in value: return(value)
    elif replace_more(value, [",",".","-","$"]).isdigit () == True:
        if dp == ",":
            if "." in value and "," in value: value = value.replace(".","")
            if "," in value: value = float(value.replace(",","."))
            else: value = int(value.replace(".",""))
            if tcorr: return(value * 1000)
            else: return (value)
        elif dp == ".":
            if "," in value and "." in value: value = value.replace(",","")
            if "." in value: value = float(value)
            else: value = int(value.replace(",",""))
            if tcorr: return(value * 1000)
            else: return (value)
        else: print(f"Wrong dp parameter vor {value}")
    else: return(value)

def read_yahoo_summary(stock,out=True,att=5,default="N/A"):
    """
    Read summary stock data from yahoo
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :param att: number of attempts how often the reading should be repeated in case of problems
    :return: dictionary with line per value
    """
    erg = {}
    link = "https://finance.yahoo.com/quote/" + stock
    if out: print ("Reading summary web data for", stock, "...")
    erg["symbol"] = stock
    attempt = 1
    while attempt < att:
        try:
            page = requests.get (link)
            soup = BeautifulSoup (page.content, "html.parser")
            time.sleep(1)
            table = soup.find ('div', id="quote-header-info")
        except Exception as e:
            print(f"Error: {e}")
            pass
        if table != None: break
        if out: print ("Read attempt name failed... Try", attempt)
        time.sleep (.5 + attempt)
        attempt += 1

    if table == None: return ({})
    else: header = table.find ("h1").text

    erg["name"] = header.strip ()

    erg["currency"] = table.find (["span"]).text.strip()[-3:].upper()
    erg["exchange"] = table.find (["span"]).text.split("-")[0].strip()

    tmp_vol = soup.find('td', attrs={"data-test": "TD_VOLUME-value"})
    if tmp_vol != None: tmp_vol = tmp_vol.text.strip().replace(",","")
    if tmp_vol != default and tmp_vol != None: erg["vol"] = float (tmp_vol.replace (",", ""))
    else: erg["vol"] = default

    tmp_avg_vol = soup.find('td', attrs={"data-test": "AVERAGE_VOLUME_3MONTH-value"})
    if tmp_avg_vol != None: tmp_avg_vol = tmp_avg_vol.text.strip().replace(",","")
    if tmp_avg_vol != default and tmp_avg_vol != None: erg["avg_vol"] = float (tmp_avg_vol.replace (",", ""))
    else: erg["avg_vol"] = default

    # find price and change of day
    sp = table.find_all ("span")
    if sp != None:
        for i_idx, i in enumerate (sp):
            if i.text.replace (",", "").replace (".", "").strip ().isdigit ():
                erg["price"] = clean_value (sp[i_idx].text.strip ())
                change = sp[i_idx + 1].text.strip ()
                daychange_tmp = change.split ("(")
                if daychange_tmp != [""]:
                    erg["daychange_abs"] = clean_value (daychange_tmp[0].strip ())
                    erg["daychange_perc"] = clean_value (daychange_tmp[1][:-1].strip ())
                else:
                    erg["daychange_abs"] = default
                    erg["daychange_perc"] = default
                break
    else:
        erg["price"] = default
        erg["daychange_abs"] = default
        erg["daychange_perc"] = default

    d_r_tmp = soup.find ('td', attrs={"data-test": "DAYS_RANGE-value"})
    if d_r_tmp != None:
        d_r_tmp = d_r_tmp.text.strip ().split ('-')
        erg["day_range_from"] = clean_value(d_r_tmp[0].strip().replace(",",""))
        erg["day_range_to"] = clean_value(d_r_tmp[1].strip().replace(",",""))
    else:
        erg["day_range_from"] = default
        erg["day_range_to"] = default

    f_r_tmp = soup.find ('td', attrs={"data-test": "FIFTY_TWO_WK_RANGE-value"})
    if f_r_tmp != None and len(f_r_tmp.text.strip()) != 0:
        f_r_tmp = f_r_tmp.text.strip ().split ('-')
        erg["fifty_range_from"] = clean_value(f_r_tmp[0].strip().replace(",",""))
        erg["fifty_range_to"] = clean_value(f_r_tmp[1].strip().replace(",",""))
    else:
        erg["fifty_range_from"] = default
        erg["fifty_range_to"] = default

    tmp_marketcap = soup.find ('td', attrs={"data-test": "MARKET_CAP-value"})
    if tmp_marketcap != None: tmp_marketcap = tmp_marketcap.text.strip()
    if tmp_marketcap != default and tmp_marketcap != None: erg["marketcap"] = clean_value(tmp_marketcap) * 1000
    else: erg["marketcap"] = default

    tmp_beta = soup.find('td', attrs={"data-test": "BETA_5Y-value"})
    if tmp_beta != None: tmp_beta = tmp_beta.text.strip()
    if tmp_beta not in [None,default] and len(tmp_beta) < 10: erg["beta"] = clean_value(tmp_beta)
    else: erg["beta"] = None

    tmp_pe_ratio = soup.find ('td', attrs={"data-test": "PE_RATIO-value"})
    if tmp_pe_ratio != None: tmp_pe_ratio = tmp_pe_ratio.text.strip()
    if tmp_pe_ratio != default and tmp_pe_ratio != None: erg["pe_ratio"] = clean_value(tmp_pe_ratio)
    else: erg["pe_ratio"] = default

    tmp_eps = soup.find ('td', attrs={"data-test": "EPS_RATIO-value"})
    if tmp_eps != None: erg["eps_ratio"] = clean_value(tmp_eps.text.strip())
    else: erg["eps_ratio"] = default

    temp_div = soup.find ('td', attrs={"data-test": "DIVIDEND_AND_YIELD-value"})
    if temp_div != None: temp_div = temp_div.text.strip ().split ("(")
    if temp_div == None:
        erg["forw_dividend"] = default
        erg["div_yield"] = default
    elif temp_div[0].strip() == None:
        erg["forw_dividend"] = default
        erg["div_yield"] = default
    else:
        erg["forw_dividend"] = clean_value(temp_div[0])
        erg["div_yield"] = clean_value(temp_div[1][:-1])

    tmp_oytp = soup.find ('td', attrs={"data-test": "ONE_YEAR_TARGET_PRICE-value"})
    if tmp_oytp != None: tmp_oytp = tmp_oytp.text.strip()
    if tmp_oytp != default and tmp_oytp != None: erg["price1Yest"] = float (tmp_oytp.replace (",", ""))
    else: erg["price1Yest"] = default

    tmp_next_ed = soup.find ('td', attrs={"data-test": "EARNINGS_DATE-value"})
    if tmp_next_ed == None: erg["next_earnings_date"] = default
    else:
        tmp_next_ed = tmp_next_ed.text.strip()
        if len(tmp_next_ed) > 15 and "-" in tmp_next_ed:
            tmp_next_ed = tmp_next_ed.split("-")[0].strip()
        if tmp_next_ed != default:
            erg["next_earnings_date"] = datetime.strftime((datetime.strptime (tmp_next_ed,"%b %d, %Y")),"%Y-%m-%d")

    tmp_ex_dd = soup.find ('td', attrs={"data-test": "EX_DIVIDEND_DATE-value"})
    if tmp_ex_dd == None: erg["last_dividend_date"] = default
    else:
        tmp_ex_dd = tmp_ex_dd.text.strip()
        if len (tmp_ex_dd) > 15: tmp_ex_dd = default
        if tmp_ex_dd not in ["N/A",None]:
            erg["last_dividend_date"] = datetime.strftime((datetime.strptime (tmp_ex_dd,"%b %d, %Y")),"%Y-%m-%d")

    return(erg)

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

    WORKON_MAIN = True
    WORKON_FINANCIALS = False
    WORKON_DAILYDATA = False
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
            yahooSummary = read_yahoo_summary(stock,att=3,default=None)
        if WORKON_DAILYDATA:       
            quandlDaily = readQuandlDaily(stock)   
            print(quandlDaily)

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
                    quandlMetadata["name"].values[0],
                    quandlMetadata["currency"].values[0],
                    yahooSummary.get("exchange",None),
                    yahooSummary.get("fifty_range_from",None),
                    yahooSummary.get("fifty_range_to",None),
                    yahooSummary.get("marketcap",None),
                    yahooSummary.get("beta",None),
                    yahooSummary.get("price1Yest",None),
                    yahooSummary.get("price",None),
                    quandlMetadata["companysite"].values[0],
                    tmpInitialDate,
                    tmpOlder1Year,
                    quandlMetadata["sector"].values[0],
                    quandlMetadata["industry"].values[0],
                    quandlMetadata["famaindustry"].values[0],
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