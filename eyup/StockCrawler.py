# Read stock data from Yahoo Finance, Morningstar, Zacks, WSJ and other modules
# clean_value: clean value and returns cleaned data
# print_num_abr: returns abbreviaton of numeric value (input in thousands) - Million, Billion, Trillion
# isdigit: check if value is digit (with replacing several chars and abbreviation)
# read_dayprice: read price of a specific date - when date not available take nearest day in history from the date
# read_yahoo_summary: read yahoo summary data for stock
# read_yahoo_profile: read yahoo profile data for stock
# read_yahoo_statistics: read yahoo statistic data for stock+
# read_yahoo_income_statement: read yahoo income statement data for stock
# read_yahoo_balance_sheet: read yahoo balance sheet data for stock
# read_yahoo_cashflow: read yahoo cashflow data for stock
# read_yahoo_analysis: read yahoo analysis data for stock

import RapidTechTools as rtt
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import calendar
import sys, os
import re
from selenium.webdriver.chrome.options import Options
from sys import platform
import urllib.request,urllib.error
import codecs
import csv
from datetime import datetime, timedelta
from datetime import date
from selenium.common.exceptions import NoSuchElementException
import numpy_financial as nf
import locale
import json
import timeit
# locale.setlocale(category=locale.LC_ALL,locale="German")
# import pycountry
# from icecream import ic

USE_PYCOUNTRY = False

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
    value = rtt.replace_more(str(value).strip(), ["%","+-","+","$","€"])

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
    elif ("M" in value or "B" in value or "T" in value or "k" in value) and rtt.replace_more(value, [",",".","M","B","T","k","-","$"]).isdigit():
        if "M" in value: char = "M"
        elif "B" in value: char = "B"
        elif "T" in value: char = "T"
        elif "k" in value: char = "k"
        decimal_place = value.find(dp)
        b_place = value.find(char)
        if decimal_place == -1:
            b_place = 1
            decimal_place = 0
        if char in ["M", "B", "T"]: value = rtt.replace_more(value, [".",",",char])
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
    elif rtt.replace_more(value, [",",".","-","$"]).isdigit () == True:
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

def isdigit(value):
    """
    clean value and check if it is digit
    :param value: value to be checked
    :return: TRUE if value is digit - FALSE if value is not fully digit
    """
    value = rtt.replace_more(str(value),["-",",",".","%","B","M","T"])
    return (value.isdigit())

def read_yahoo_summary(stock,out=True,att=5):
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
        except:
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
    if tmp_vol != "N/A" and tmp_vol != None: erg["vol"] = float (tmp_vol.replace (",", ""))
    else: erg["vol"] = "N/A"

    tmp_avg_vol = soup.find('td', attrs={"data-test": "AVERAGE_VOLUME_3MONTH-value"})
    if tmp_avg_vol != None: tmp_avg_vol = tmp_avg_vol.text.strip().replace(",","")
    if tmp_avg_vol != "N/A" and tmp_avg_vol != None: erg["avg_vol"] = float (tmp_avg_vol.replace (",", ""))
    else: erg["avg_vol"] = "N/A"

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
                    erg["daychange_abs"] = "N/A"
                    erg["daychange_perc"] = "N/A"
                break
    else:
        erg["price"] = "N/A"
        erg["daychange_abs"] = "N/A"
        erg["daychange_perc"] = "N/A"

    d_r_tmp = soup.find ('td', attrs={"data-test": "DAYS_RANGE-value"})
    if d_r_tmp != None:
        d_r_tmp = d_r_tmp.text.strip ().split ('-')
        erg["day_range_from"] = clean_value(d_r_tmp[0].strip().replace(",",""))
        erg["day_range_to"] = clean_value(d_r_tmp[1].strip().replace(",",""))
    else:
        erg["day_range_from"] = "N/A"
        erg["day_range_to"] = "N/A"

    f_r_tmp = soup.find ('td', attrs={"data-test": "FIFTY_TWO_WK_RANGE-value"})
    if f_r_tmp != None and len(f_r_tmp.text.strip()) != 0:
        f_r_tmp = f_r_tmp.text.strip ().split ('-')
        erg["fifty_range_from"] = clean_value(f_r_tmp[0].strip().replace(",",""))
        erg["fifty_range_to"] = clean_value(f_r_tmp[1].strip().replace(",",""))
    else:
        erg["fifty_range_from"] = "N/A"
        erg["fifty_range_to"] = "N/A"

    tmp_marketcap = soup.find ('td', attrs={"data-test": "MARKET_CAP-value"})
    if tmp_marketcap != None: tmp_marketcap = tmp_marketcap.text.strip()
    if tmp_marketcap != "N/A" and tmp_marketcap != None: erg["marketcap"] = clean_value(tmp_marketcap) * 1000
    else: erg["marketcap"] = "N/A"

    tmp_beta = soup.find('td', attrs={"data-test": "BETA_5Y-value"})
    if tmp_beta != None: tmp_beta = tmp_beta.text.strip()
    if tmp_beta not in [None,"N/A"] and len(tmp_beta) < 10: erg["beta"] = clean_value(tmp_beta)
    else: erg["beta"] = None

    tmp_pe_ratio = soup.find ('td', attrs={"data-test": "PE_RATIO-value"})
    if tmp_pe_ratio != None: tmp_pe_ratio = tmp_pe_ratio.text.strip()
    if tmp_pe_ratio != "N/A" and tmp_pe_ratio != None: erg["pe_ratio"] = clean_value(tmp_pe_ratio)
    else: erg["pe_ratio"] = "N/A"

    tmp_eps = soup.find ('td', attrs={"data-test": "EPS_RATIO-value"})
    if tmp_eps != None: erg["eps_ratio"] = clean_value(tmp_eps.text.strip())
    else: erg["eps_ratio"] = "N/A"

    temp_div = soup.find ('td', attrs={"data-test": "DIVIDEND_AND_YIELD-value"})
    if temp_div != None: temp_div = temp_div.text.strip ().split ("(")
    if temp_div == None:
        erg["forw_dividend"] = "N/A"
        erg["div_yield"] = "N/A"
    elif "N/A" in temp_div[0].strip():
        erg["forw_dividend"] = "N/A"
        erg["div_yield"] = "N/A"
    else:
        erg["forw_dividend"] = clean_value(temp_div[0])
        erg["div_yield"] = clean_value(temp_div[1][:-1])

    tmp_oytp = soup.find ('td', attrs={"data-test": "ONE_YEAR_TARGET_PRICE-value"})
    if tmp_oytp != None: tmp_oytp = tmp_oytp.text.strip()
    if tmp_oytp != "N/A" and tmp_oytp != None: erg["price1Yest"] = float (tmp_oytp.replace (",", ""))
    else: erg["price1Yest"] = "N/A"

    tmp_next_ed = soup.find ('td', attrs={"data-test": "EARNINGS_DATE-value"})
    if tmp_next_ed == None: erg["next_earnings_date"] = "N/A"
    else:
        tmp_next_ed = tmp_next_ed.text.strip()
        if len(tmp_next_ed) > 15 and "-" in tmp_next_ed:
            tmp_next_ed = tmp_next_ed.split("-")[0].strip()
        if tmp_next_ed != "N/A":
            erg["next_earnings_date"] = datetime.strftime((datetime.strptime (tmp_next_ed,"%b %d, %Y")),"%Y-%m-%d")

    tmp_ex_dd = soup.find ('td', attrs={"data-test": "EX_DIVIDEND_DATE-value"})
    if tmp_ex_dd == None: erg["last_dividend_date"] = "N/A"
    else:
        tmp_ex_dd = tmp_ex_dd.text.strip()
        if len (tmp_ex_dd) > 15: tmp_ex_dd = "N/A"
        if tmp_ex_dd != "N/A":
            erg["last_dividend_date"] = datetime.strftime((datetime.strptime (tmp_ex_dd,"%b %d, %Y")),"%Y-%m-%d")

    return(erg)

def read_yahoo_profile(stock,out=True):
    """
    Read profile stock data from yahoo
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with line per value
    """
    erg = {}
    if out: print("Reading profile web data for",stock,"...")
    link = "https://finance.yahoo.com/quote/" + stock + "/profile?p=" + stock
    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep (0.5)
    erg["symbol"] = stock

    table = soup.find ('div', attrs={"class": "asset-profile-container"})
    if table == None:
        return ({})
    else:
        spans = table.find_all ("span")
    if len(spans[5].text.strip()) == 0:
        erg["empl"] = "N/A"
    else:
        erg["empl"] = int(spans[5].text.strip ().replace (",", ""))
    erg["sector"] = spans[1].text.strip ()
    erg["industry"] = spans[3].text.strip ()

    ps = table.find_all("a")
    erg["tel"] = ps[0].text
    erg["url"] = ps[1].text

    # if "." in ps[1].text:
    #     if USE_PYCOUNTRY:
    #         land = ps[1].text.split(".")[-1].upper()
    #         if land == "COM":
    #             erg["country"] = "USA"
    #         else:
    #             country = pycountry.countries.get (alpha_2=land)
    #             if country != None:
    #                 erg["country"] = country.name
    #             else:
    #                 erg["country"] = "N/A"
    #     else:
    #         erg["country"] = "N/A"
    # else: erg["country"] = "N/A"

    listPElems = []
    pElems = table.find_all ("p")
    for elem in pElems[0]:
        elem = str(elem)
        listPElems.append(elem)
    for idx,elem in enumerate(listPElems):
        if ("href" in elem and "tel:" in elem) or ("http://" in elem):
            if ("href" in elem and "tel:" in elem):
                diffIDX = 3
            else:
                diffIDX = 5
            erg["country"] = listPElems[idx - diffIDX].strip()
            if erg["country"] == "United States":
                erg["country"] = "USA"
            break

    table = soup.find ('section', attrs={"class": "quote-sub-section Mt(30px)"})
    if table == None: erg["desc"] = "N/A"
    else: erg["desc"] = table.find ("p").text.strip ()

    return(erg)

def read_yahoo_statistics(stock,out=True,wait=0):
    """
    Read statistics stock data from yahoo
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :param wait: how many seconds the processing should wait during pauses
    :return: 2 dictionaries - 1 with statistics main data and 1 statisics table data with timeslots
    """
    erg = {}
    link = "https://finance.yahoo.com/quote/" +stock + "/key-statistics?p=" + stock
    if out: print ("Reading statistics web data for", stock, "...")
    erg["symbol"] = stock

    page = requests.get (link)
    time.sleep (wait)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep (wait)
    if soup == None:
        return ({},{})

    erg_stat = {}
    erg_val = {}
    tmp_list = []
    tmp_list_stat = []
    tmp_list_val = []

    for e in soup.find_all(["th","td"]): tmp_list.append(e.text.strip())
    #for i in tmp_list: print(i)        # DEBUG
    for idx,cont in enumerate(tmp_list):
        if "Beta" in cont:
            tmp_list_stat = list(tmp_list[idx:])
            tmp_list_val =  list(tmp_list[:idx])

    # check if everything is empty
    if tmp_list_stat == [] and tmp_list_val == []:
        return ({},{})
    # check if no results and redirected to symbol serach site (check header symbols)
    if "Symbol" in tmp_list_val and "Name" in tmp_list_val and "Industry / Category" in tmp_list_val:
        return ({},{})
    #print("DEBUG TmpListStat: ", tmp_list_stat)
    #print("DEBUG TmpListVal: ",tmp_list_val)

    for i in range(0,len(tmp_list_stat),2):
        matches = ["Shares Short","Short Ratio","Short % of Float","Short % of Shares Outstanding","Shares Short"]
        if any (x in tmp_list_stat[i] for x in matches):
            if "Shares Short (prior month" in tmp_list_stat[i]:
                tmp_list_stat[i] = tmp_list_stat[i].split("(")[0].strip() + " (prior month)"
            else:
                tmp_list_stat[i] = tmp_list_stat[i].split("(")[0].strip()
        if tmp_list_stat[i][-1] in ["1","2","3","4","5","6"]: tmp_list_stat[i] = tmp_list_stat[i][:len(tmp_list_stat[i])-2]
        erg_stat[tmp_list_stat[i]] = clean_value(tmp_list_stat[i+1])

    if all (x not in tmp_list_val for x in ["Price/Sales (ttm)"]):
        erg_val = {}
    else:
        for idx_header, cont_header in enumerate(tmp_list_val):
            if "Market Cap" in cont_header: break
        if idx_header > 0:
            # logic when the there is a table on the statistic site
            for i in range(0,len(tmp_list_val),idx_header):
                if tmp_list_val[i] != "":
                    if tmp_list_val[i][-1] in ["1","2","3","4","5","6"]:
                        tmp_list_val[i] = tmp_list_val[i][:len(tmp_list_val[i])-2]
                else: tmp_list_val[i] = "Header"
                erg_val[tmp_list_val[i]] = tmp_list_val[i+1:i+idx_header]
        else:
            # logic when there is no table on the statistic site
            erg_val["Header"] = ["Actual"]
            for idx, elem in enumerate(tmp_list_val):
                if idx % 2 == 0:
                    elem = elem.replace(" 5","").replace(" 3","").replace(" 1","").replace(" 6","")
                    erg_val[elem] = [tmp_list_val[idx+1]]

    # Calculate dividend growth
    forwardDividend = erg_stat.get ("Forward Annual Dividend Rate", "N/A")
    trailingDividend = erg_stat.get ("Trailing Annual Dividend Rate", "N/A")
    if forwardDividend not in ["N/A","",None] and trailingDividend not in ["N/A","",None] and trailingDividend != 0:
        erg_stat["Dividend Growth"] = round ((forwardDividend - trailingDividend) / trailingDividend * 100, 2)
    else:
        erg_stat["Dividend Growth"] = "N/A"

    # Cleanup the values finally
    if "Header" in erg_val:
        erg_val["Header"][0] = "Current"
    else: return ({},{})

    for key,val in erg_val.items():
        for idx,cont in enumerate(val):
            if key in ["Market Cap (intraday)","Enterprise Value"]:
                erg_val[key][idx] = clean_value (erg_val[key][idx],tcorr=True)
            else:
                erg_val[key][idx] = clean_value (erg_val[key][idx])
    for key,val in erg_stat.items():
        if key in ["Shares Outstanding", "Float", "Shares Short","Shares Short (prior month)","Revenue (ttm)",
                   "Gross Profit (ttm)","EBITDA","Net Income Avi to Common (ttm)","Total Cash (mrq)","Total Debt (mrq)",
                   "Operating Cash Flow (ttm)","Levered Free Cash Flow (ttm)","Avg Vol (10 day)","Avg Vol (3 month)"]:
            erg_stat[key] = clean_value(val,tcorr=True)
        else:
            erg_stat[key] = clean_value(val)

    return (erg_stat,erg_val)

def readYahooIncomeStatement(stock, out=True, calc=False, wait=1):
    """
    Read income statement stock data from yahoo (without expanding all details)
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with one line per value and dates in columns
    """

    # start = timeit.default_timer ()

    erg = {"Header": stock}
    link = "https://finance.yahoo.com/quote/" + stock + "/financials?p=" + stock
    if out: print ("Reading income statement web data for", stock)

    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep(wait)

    # check if cooldown is necessary
    tmpSpans = []
    cooldown = 180
    for elem in soup.find_all ("span"):
        tmpSpans.append(elem.text)
    if "We’re sorry, we weren’t able to find any data." in tmpSpans \
        and "Please try reloading the page." in tmpSpans:
        print(f"No data for stock - probably cooldown necessary......")
        for i in range (cooldown, 0, -1):  # Delay for 30 seconds - countdown in one row
            sys.stdout.write (str (i) + ' ')  # Countdown output
            sys.stdout.flush ()
            time.sleep (1)
            if i == 1:
                print("\n")

    # read header of table
    divHeader = soup.find ("div", attrs={"class": "D(tbr) C($primaryColor)"})
    time.sleep (wait)
    tmpHeader = []

    if divHeader == None:
        print(f"No income statement data for stock {stock}...")
        return {}
    for colHeader in divHeader.find_all("span"):
        if colHeader.text in ["Header","Breakdown"]:
            continue
        else:
            tmpHeader.append(clean_value(colHeader.text))
    erg["Breakdown"] = tmpHeader

    # read content of table
    divTable = soup.find_all ("div", attrs={"data-test": "fin-row"})
    for idx, elem in enumerate(divTable):
        # print(f"DEBUG: {idx}")
        # print(f"DEBUG: {elem.prettify()}")

        # read first column
        tmpName = elem.find ("span")
        # print(f"DEBUG: {tmpName.text}")

        # read value from ttm
        tmpDiv = elem.find_all ("div", attrs={"data-test": "fin-col"})
        tmpCont = []
        for divElem in tmpDiv:
            tmpValue = divElem.find ("span")
            # print(f"DEBUG: {tmpValue}")
            if tmpValue != None:
                tmpCont.append(clean_value(tmpValue.text,tcorr=True))
            else:
                tmpCont.append(None)
        erg[tmpName.text] = tmpCont

    if calc:
        erg["Calc_EPSGrowth1Y"] = clean_value(rtt.growthCalc(erg.get("EBIT", "[]"),2))
        erg["Calc_EPSGrowthHist"] = clean_value(rtt.growthCalc(erg.get("EBIT", "[]"),-1))
        erg["Calc_RevenueGrowth1Y"] = clean_value(rtt.growthCalc(erg.get("Total Revenue", "[]"),2))
        erg["Calc_RevenueGrowthHist"] = clean_value(rtt.growthCalc(erg.get("Total Revenue", "[]"),-1))
        erg["Calc_NetIncomeGrowthHist"] = clean_value(rtt.growthCalc(erg.get("Net Income Common Stockholders", "[]"),-1))
        erg["Calc_OperatingIncomeGrowthHist"] = clean_value(rtt.growthCalc(erg.get("Operating Income", "[]"),-1))
        erg["Calc_ShareBuybacks"] = clean_value (rtt.growthCalc (erg.get ("Diluted Average Shares", "[]"), -1))
        # check if drawback for earnings in the last years
        drawback = False
        drawbackPerc = 0
        listEPS = erg.get("EBIT", "[]")
        for i,e in enumerate(listEPS):
            if i < len(listEPS) - 2 and drawback == False:
                tmpGrowth = (e - listEPS[i + 1]) / listEPS[i + 1] * 100
                if tmpGrowth < -50:
                    drawback = True
                    drawbackPerc = tmpGrowth
        if drawback == False:
            erg["Calc_EBITDrawback"] = 1
        else:
            erg["Calc_EBITDrawback"] = clean_value(drawbackPerc)

    # stop = timeit.default_timer ()
    # ic(round(stop-start,2))

    return (erg)

def read_yahoo_income_statement(stock, out=True):
    """
    Read income statement stock data from yahoo (with expanding all details)
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with one line per value and dates in columns
    """
    # start = timeit.default_timer ()

    erg = {}
    link = "https://finance.yahoo.com/quote/" + stock + "/financials?p=" + stock
    if out: print("Reading income statement web data for", stock, "...approx 6sec...")
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option ('excludeSwitches', ['enable-logging'])

    path = os.path.abspath (os.path.dirname (sys.argv[0]))
    attempt = 1
    while attempt <6:
        try:
            if platform == "win32": cd = '/chromedriver.exe'
            elif platform == "linux": cd = '/chromedriver_linux'
            elif platform == "darwin": cd = '/chromedriver'
            driver = webdriver.Chrome (path + cd, options=options)
            driver.get (link)  # Read link
            time.sleep (2)  # Wait till the full site is loaded
            try:
                driver.find_element_by_name ("agree").click ()
                time.sleep (2)
            except:
                pass
            driver.find_element_by_xpath ('//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span').click ()
            time.sleep (2)
            soup = BeautifulSoup (driver.page_source, 'html.parser')  # Read page with html.parser
            time.sleep (2)
            driver.quit ()
            break
        except NoSuchElementException:
            erg["Basic Average Shares"] = ["N/A","N/A","N/A","N/A","N/A"]
            erg["Net Income"] = ["N/A","N/A","N/A","N/A","N/A"]
            erg["Breakdown"] = ["N/A","N/A","N/A","N/A","N/A"]
            erg["Total Revenue"] = ["N/A","N/A","N/A","N/A","N/A"]
            return (erg)
        except:
            attempt += 1
            time.sleep (1 + attempt)
            if out: print("Problems reading - try again attempt",attempt,"...")

    # check if cooldown is necessary
    tmpSpans = []
    cooldown = 180
    for elem in soup.find_all ("span"):
        tmpSpans.append(elem.text)
    if "We’re sorry, we weren’t able to find any data." in tmpSpans \
        and "Please try reloading the page." in tmpSpans:
        print(f"No data for stock - probably cooldown necessary......")
        for i in range (cooldown, 0, -1):  # Delay for 30 seconds - countdown in one row
            sys.stdout.write (str (i) + ' ')  # Countdown output
            sys.stdout.flush ()
            time.sleep (1)
            if i == 1:
                print("\n")

    div_id = soup.find(id="Col1-1-Financials-Proxy")
    table = soup.find (id="quote-header-info")
    erg["Header"] = [stock, "in thousands", table.find (["span"]).text.strip ()]

    list_div = []
    for e in div_id.find_all (["div"]): list_div.append (e.text.strip ())

    if all (x not in list_div for x in ["Total Revenue", "Net Income"]): return({})

    while list_div[0] != "Breakdown": list_div.pop (0)
    for i in range (len (list_div) - 1, 0, -1):
        if list_div[i].replace (".", "").replace (",", "").replace ("-", "").isdigit () or list_div[i] == "-": continue
        elif i == len (list_div) - 1: del list_div[i]
        elif len (list_div[i]) == 0: del list_div[i]
        elif len (list_div[i]) > 50: del list_div[i]
        # elif i == 0: break
        elif list_div[i] == list_div[i - 1]: del list_div[i]
        elif list_div[i + 1] in list_div[i]: del list_div[i]

    if "Total Revenue" not in list_div: return {}
    else: pos = list_div.index("Total Revenue")

    idx = 0
    while idx < len (list_div):
        if list_div[idx].replace (",", "").replace ("-", "").isdigit () == False and list_div[idx] != "-":
            idx += pos
        else:
            while list_div[idx].replace (",", "").replace ("-", "").isdigit () == True or list_div[idx] == "-":
                del list_div[idx]

    for i in range(len(list_div)-1):
        if list_div[i].replace(".", "").replace(",", "").replace("-", "").isdigit():
            list_div[i] = float(list_div[i].replace(",",""))

    idx = 0
    while idx < len (list_div):
        erg[list_div[idx]] = list_div[idx + 1:idx + pos]
        idx += pos

    for key,val in erg.items():
        for idx,cont in enumerate(val):
            erg[key][idx] = clean_value(erg[key][idx],tcorr=True)

    # skip one day future
    # when reading online the ultimo is 1 day minus in contrast to the csv-reading
    for idx,cont in enumerate(erg["Breakdown"]):
        if cont == "ttm": continue
        tmp = datetime.strptime(cont, "%Y-%m-%d") + timedelta(days=1)
        erg["Breakdown"][idx] = datetime.strftime(tmp, "%Y-%m-%d")

    # stop = timeit.default_timer ()
    # ic(round(stop-start,2))

    return (erg)

def readYahooBalanceSheet (stock, out=True, calc=False):
    """
    Read actual balance sheet stock data from yahoo (without expanding details)
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :param calc: when True then also some additional values will be calculated (eg. growths)
    :return: dictionary with one line per value and dates in columns
    """

    # start = timeit.default_timer ()

    erg = {"Header": stock}
    link = "https://finance.yahoo.com/quote/" + stock + "/balance-sheet?p=" + stock
    if out: print ("Reading balance sheet web data for", stock)

    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep(1)

    # read header of table
    divHeader = soup.find ("div", attrs={"class": "D(tbr) C($primaryColor)"})
    tmpHeader = []

    if divHeader != None:
        for colHeader in divHeader.find_all("span"):
            if colHeader.text in ["Header","Breakdown"]:
                continue
            else:
                tmpHeader.append(clean_value(colHeader.text))
        erg["Breakdown"] = tmpHeader
    else:
        return{}

    # read content of table
    divTable = soup.find_all ("div", attrs={"data-test": "fin-row"})
    for idx, elem in enumerate(divTable):
        # print(f"DEBUG: {idx}")
        # print(f"DEBUG: {elem.prettify()}")

        # read first column
        tmpName = elem.find ("span")
        # print(f"DEBUG: {tmpName.text}")

        # read value from ttm
        tmpDiv = elem.find_all ("div", attrs={"data-test": "fin-col"})
        tmpCont = []
        for divElem in tmpDiv:
            tmpValue = divElem.find ("span")
            # print(f"DEBUG: {tmpValue}")
            if tmpValue != None:
                tmpCont.append(clean_value(tmpValue.text,tcorr=True))
            else:
                tmpCont.append(None)
        erg[tmpName.text] = tmpCont

    if calc:
        erg["Calc_BookValueGrowthHist"] = clean_value(rtt.growthCalc(erg.get("Tangible Book Value", "[]"),-1))

    # stop = timeit.default_timer ()
    # ic(round(stop-start,2))

    return (erg)

def read_yahoo_balance_sheet(stock, out=True):
    """
    Read balance sheet stock data from yahoo (with expanding details)
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with one line per value and dates in columns
    """
    erg = {}
    link = "https://finance.yahoo.com/quote/" + stock + "/balance-sheet?p=" + stock

    if out: print("Reading balance sheet web data for", stock, "...approx 6sec...")
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option ('excludeSwitches', ['enable-logging'])

    path = os.path.abspath (os.path.dirname (sys.argv[0]))
    attempt = 1
    while attempt <6:
        try:
            if platform == "win32": cd = '/chromedriver.exe'
            elif platform == "linux": cd = '/chromedriver_linux'
            elif platform == "darwin": cd = '/chromedriver'
            driver = webdriver.Chrome (path + cd, options=options)
            driver.get (link)
            time.sleep (2)
            try:
                driver.find_element_by_name ("agree").click ()
                time.sleep (2)
            except:
                pass
            driver.find_element_by_xpath ('//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span').click ()
            time.sleep (2)
            soup = BeautifulSoup (driver.page_source, 'html.parser')
            time.sleep (2)
            driver.quit ()
            break
        except NoSuchElementException:
            erg["Stockholders' Equity"] = ["N/A","N/A","N/A","N/A","N/A"]
            erg["Total Assets"] = ["N/A","N/A","N/A","N/A","N/A"]
            erg["Breakdown"] = ["N/A", "N/A", "N/A", "N/A", "N/A"]
            return (erg)
        except:
            attempt += 1
            time.sleep (1 + attempt)
            if out: print("Problems reading - try again attempt",attempt,"...")

    table = soup.find (id="quote-header-info")
    erg["Header"] = [stock, "in thousands", table.find (["span"]).text.strip ()]
    table = soup.find (id="Col1-1-Financials-Proxy")

    list_div = []
    for e in table.find_all (["div"]): list_div.append (e.text.strip ())

    if "Breakdown" not in list_div: return({})

    while list_div[0] != "Breakdown": list_div.pop(0)
    for i in range (len (list_div) - 1, 0, -1):
        if list_div[i].replace (".", "").replace (",", "").replace ("-", "").isdigit () or list_div[i] == "-": continue
        elif i == len (list_div) - 1: del list_div[i]
        elif len (list_div[i]) == 0: del list_div[i]
        elif len (list_div[i]) > 50: del list_div[i]
        elif i == 0: break
        elif list_div[i] == list_div[i - 1]: del list_div[i]
        elif list_div[i + 1] in list_div[i]: del list_div[i]

    # Eliminate numeric entries on the false position
    if "Total Assets" in list_div: pos = list_div.index ("Total Assets")
    else: return({})
    idx = 0
    # If the element is a Digit - this is wrong and the elements got deleted as long they are an digit
    while idx < len (list_div):
        # When Non-Digit - jump POS forward
        if list_div[idx].replace (",", "").replace ("-", "").replace (".", "").isdigit () == False and list_div[idx] != "-":
            idx += pos
        else:
            while list_div[idx].replace (",", "").replace ("-", "").replace (".", "").isdigit () == True or list_div[idx] == "-":
                del list_div[idx]
                # if the wrong digit values are at the very end - check if end of list is reached
                if idx == len(list_div):
                    break

    for i in range(len(list_div)-1):
        if list_div[i].replace(".", "").replace(",", "").replace("-", "").isdigit():
            list_div[i] = float(list_div[i].replace(",",""))

    idx = 0
    while idx < len (list_div):
        erg[list_div[idx]] = list_div[idx + 1:idx + pos]
        idx += pos

    for key,val in erg.items():
        for idx,cont in enumerate(val):
            erg[key][idx] = clean_value(erg[key][idx],tcorr=True)

    # skip one day future
    # when reading online the ultimo is 1 day minus in contrast to the csv-reading
    for idx,cont in enumerate(erg["Breakdown"]):
        if cont == "ttm": continue
        tmp = datetime.strptime(cont, "%Y-%m-%d") + timedelta(days=1)
        erg["Breakdown"][idx] = datetime.strftime(tmp, "%Y-%m-%d")

    return (erg)

def readYahooCashflow (stock, out=True, calc=False):
    """
    Read cashflow stock data from yahoo (without expanding details)
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with one line per value and dates in columns
    """

    # start = timeit.default_timer ()

    erg = {"Header": stock}
    link = "https://finance.yahoo.com/quote/" + stock + "/cash-flow?p=" + stock
    if out: print ("Reading cashflow web data for", stock)

    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep(1)

    # read header of table
    divHeader = soup.find ("div", attrs={"class": "D(tbr) C($primaryColor)"})
    tmpHeader = []
    if divHeader == None:
        print(f"No data available for stock {stock} currently...")
        return
    for colHeader in divHeader.find_all("span"):
        if colHeader.text in ["Header","Breakdown"]:
            continue
        else:
            tmpHeader.append(clean_value(colHeader.text))
    erg["Breakdown"] = tmpHeader

    # read content of table
    divTable = soup.find_all ("div", attrs={"data-test": "fin-row"})
    for idx, elem in enumerate(divTable):
        # print(f"DEBUG: {idx}")
        # print(f"DEBUG: {elem.prettify()}")

        # read first column
        tmpName = elem.find ("span")
        # print(f"DEBUG: {tmpName.text}")

        # read value from ttm
        tmpDiv = elem.find_all ("div", attrs={"data-test": "fin-col"})
        tmpCont = []
        for divElem in tmpDiv:
            tmpValue = divElem.find ("span")
            # print(f"DEBUG: {tmpValue}")
            if tmpValue != None:
                tmpCont.append(clean_value(tmpValue.text,tcorr=True))
            else:
                tmpCont.append(None)
        erg[tmpName.text] = tmpCont

    if calc:
        erg["Calc_FCFGrowthHist"] = clean_value(rtt.growthCalc(erg.get("Free Cash Flow", "[]"),-1))

    # stop = timeit.default_timer ()
    # ic(round(stop-start,2))

    return (erg)

def read_yahoo_cashflow(stock, out=True):
    """
    Read cashflow stock data from yahoo (with expanding details)
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with one line per value and dates in columns
    """
    erg = {}
    if out: print("Reading cashflow web data for", stock, "...approx 6sec...")
    link = "https://finance.yahoo.com/quote/" + stock + "/cash-flow?p=" + stock
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option ('excludeSwitches', ['enable-logging'])

    path = os.path.abspath (os.path.dirname (sys.argv[0]))
    attempt = 1
    while attempt <6:
        try:
            if platform == "win32": cd = '/chromedriver.exe'
            elif platform == "linux": cd = '/chromedriver_linux'
            elif platform == "darwin": cd = '/chromedriver'
            driver = webdriver.Chrome (path + cd, options=options)
            driver.get (link)  # Read link
            time.sleep (2)  # Wait till the full site is loaded
            try:
                driver.find_element_by_name ("agree").click ()
                time.sleep (2)
            except:
                pass
            driver.find_element_by_xpath ('//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span').click ()
            time.sleep (2)
            soup = BeautifulSoup (driver.page_source, 'html.parser')  # Read page with html.parser
            time.sleep (2)
            driver.quit ()
            break
        except NoSuchElementException:
            return (erg)
        except:
            attempt += 1
            time.sleep (1 + attempt)
            if out: print("Problems reading - try again attempt",attempt,"...")

    div_id = soup.find(id="Col1-1-Financials-Proxy")
    table  = soup.find(id="quote-header-info")
    erg["Header"] = [stock,"in thousands",table.find(["span"]).text.strip()]

    list_div = []
    for e in div_id.find_all (["div"]): list_div.append (e.text.strip ())

    if all (x not in list_div for x in ["Operating Cash Flow", "Free Cash Flow", "Cash Dividends Paid"]): return({})

    while list_div[0] != "Breakdown": list_div.pop (0)
    for i in range (len (list_div) - 1, 0, -1):
        if list_div[i].replace (".", "").replace (",", "").replace ("-", "").isdigit () or list_div[i] == "-": continue
        elif i == len (list_div) - 1: del list_div[i]
        elif len (list_div[i]) == 0: del list_div[i]
        elif len (list_div[i]) > 50: del list_div[i]
        elif i == 0: break
        elif list_div[i] == list_div[i - 1]: del list_div[i]
        elif list_div[i + 1] in list_div[i]: del list_div[i]

    # read counts of columns with values
    if "Operating Cash Flow" not in list_div:
        # if there is no "operating cash flow" entry - generate one at the right positon
        for i in range(len(list_div)):
            pattern = re.compile ("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$")  # looks like m/dd/yyyy
            if list_div[i] not in ["ttm","Breakdown"] and pattern.match(list_div[i]) == None:
                break
        list_div.insert(i,"Operating Cash Flow")
    pos = list_div.index ("Operating Cash Flow")
    # if operating cashflow on wrong position
    if pos > 7:
        for i in range(len(list_div)):
            pattern = re.compile ("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$")  # looks like m/dd/yyyy
            if list_div[i] not in ["ttm","Breakdown"] and pattern.match(list_div[i]) == None:
                break
        list_div[pos] = "Opearting Cash Flow 2"
        list_div.insert (i, "Operating Cash Flow")
        pos = i

    idx = 0
    while idx < len (list_div):
        if list_div[idx].replace (",", "").replace ("-", "").isdigit () == False and list_div[idx] != "-":
            idx += pos
        else:
            while list_div[idx].replace (",", "").replace ("-", "").isdigit () == True or list_div[idx] == "-":
                del list_div[idx]

    idx = 0
    while idx < len (list_div):
        erg[list_div[idx]] = list_div[idx + 1:idx + pos]
        idx += pos

    for key,val in erg.items():
        for idx,cont in enumerate(val):
            erg[key][idx] = clean_value(erg[key][idx],tcorr=True)

    # skip one day future
    # when reading online the ultimo is 1 day minus in contrast to the csv-reading
    for idx,cont in enumerate(erg["Breakdown"]):
        if cont == "ttm": continue
        tmp = datetime.strptime(cont, "%Y-%m-%d") + timedelta(days=1)
        erg["Breakdown"][idx] = datetime.strftime(tmp, "%Y-%m-%d")

    return (erg)

def read_yahoo_analysis(stock, out=True, rating=False):
    """
    Read analysis stock data from yahoo
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with one line per value and dates in columns
    """

    start = timeit.default_timer ()

    erg = {}
    link = "https://finance.yahoo.com/quote/" + stock + "/analysis?p=" + stock
    if out: print("Reading analysis web data for", stock)

    attempt = 1
    table = None
    while attempt < 5 and table == None:
        try:
            page = requests.get (link)
            time.sleep (0.5)
            soup = BeautifulSoup (page.content, "html.parser")
            time.sleep (0.5)
            table = soup.find(id="YDC-Col1")
            break
        except:
            attempt += 1
            time.sleep (1 + attempt)
            print("Problems reading Analysis - try again attempt",attempt,"...")

    if table == None: return ({})

    erg = {}
    list_table = []
    for e in table.find_all (["th", "td"]):
        if e.text.strip () == "0": list_table.append("N/A")
        else: list_table.append(clean_value(e.text.strip ()))
    for i in range (0, len (list_table), 5): erg[list_table[i]] = list_table[i + 1:i + 5]

    for key,val in erg.items():
        for idx,cont in enumerate(val):
            if key in ["Avg. Estimate","Low Estimate","High Estimate","Year Ago Sales"]:
                erg[key][idx] = clean_value (erg[key][idx],tcorr=True)
            else:
                erg[key][idx] = clean_value(erg[key][idx])

    #for key in ["Earnings History", "EPS Est.", "EPS Actual", "Difference", "Surprise %"]:
    #    if key in erg: erg[key].reverse()
    # stop = timeit.default_timer ()
    # print(f"Runtime: {round (stop - start, 2)}")

    if rating:
        options = Options ()
        options.add_argument ('--headless')
        options.add_argument ("--window-size=1920,1080")
        options.add_experimental_option ('excludeSwitches', ['enable-logging'])
        path = os.path.abspath (os.path.dirname (sys.argv[0]))
        if platform == "win32":
            cd = '/chromedriver.exe'
        elif platform == "linux":
            cd = '/chromedriver_linux'
        elif platform == "darwin":
            cd = '/chromedriver'
        driver = webdriver.Chrome (path + cd, options=options)
        driver.get (link)
        wait = WebDriverWait (driver, 2)
        WebDriverWait (driver, 5).until (EC.presence_of_element_located ((By.NAME, "agree"))).click ()
        WebDriverWait (driver, 5).until (EC.presence_of_element_located ((By.ID, "YDC-Col1")))
        element = driver.find_element_by_id ("YDC-Col1")
        driver.execute_script ("arguments[0].scrollIntoView();", element)
        time.sleep (1)
        soup = BeautifulSoup (driver.page_source, 'html.parser')
        table = soup.find (id="YDC-Col2")
        rating = table.find ("div", attrs={"data-test": "rec-rating-txt"})
        if rating not in [None,""]:
            erg["Rating"] = clean_value(rating.text)

        spans = table.find_all ("span")
        for idx, span in enumerate (spans):
            if span.text in ["Current", "Average", "Low", "High"]:
                erg["Price Target 1Y " + span.text] = clean_value(spans[idx + 1].text)

    if "Earnings Estimate" in erg or "Rating" in erg: return (erg)
    else: return ({})

def read_tasi_index(read_to=datetime(1950,1,1), out=True):
    """
    read data from tasi index
    :param read_to: date in datetime-format (year,month,day)
    :param out: when True then output some status informations during program running
    :return: return tasi index information
    """
    erg = {}
    list_erg = []
    link = "https://www.tadawul.com.sa/wps/portal/tadawul/markets/equities/indices/today/!ut/p/z1/pZG7DoJAEEW_xYKWGQTx0W1MRAyakAjiNgbMihjYVR7i54tYaXTVON1MzinuHaAQAOXhOYnDMhE8TJt9Tc1NtzseaEMDHXT6GhLTQtudG7o1QVjJALQ0oD_5lr3oI3HJ1J_4y8bX__PR-M7HN0Pws0-lyEKTA21Fj8CLDqTALWQLSFLMgMapiO4fJTzSBzHQnO1YznK1ypvzviyPxUhBBeu6VlkqThXjhboVmYIJj8TllbkXRQnBswDHzPO8ABP70EvPDulcAQ1PZW4!/p0/IZ7_NHLCH082KGN530A68FC4AN2O63=CZ6_22C81940L0L710A6G0IQM43GF0=MEtabIndex!Performance=chart_tasi_current_sector!TASI==/?"
    if out: print("Reading historical index price web data for Index TASI...")
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option ('excludeSwitches', ['enable-logging'])

    path = os.path.abspath (os.path.dirname (sys.argv[0]))

    attempt = 1
    while attempt < 6:
        try:
            if platform == "win32": cd = '/chromedriver.exe'
            elif platform == "linux": cd = '/chromedriver_linux'
            elif platform == "darwin": cd = '/chromedriver'
            driver = webdriver.Chrome (path + cd, options=options)
            driver.get (link)  # Read link
            time.sleep (1)
            driver.find_element_by_xpath ('//*[@id="performance_wrapper"]/div[1]/div/ul/li[6]').click ()
            time.sleep (1)
            soup = BeautifulSoup (driver.page_source, 'html.parser')  # Read page with html.parser
            break
        except NoSuchElementException:
            if out: print("Error - No Such Element")
            return (erg)
        except:
            attempt += 1
            time.sleep (1 + attempt)
            if out: print ("Problems reading - try again attempt", attempt, "...")

    initial = True
    tmp_dt = 0

    while True:
        if initial == False:
            driver.find_element_by_xpath ('//*[@id="pageing_next"]').click ()
            time.sleep (.5)
            soup = BeautifulSoup (driver.page_source, 'html.parser')  # Read page with html.parser
        else: initial = False

        table = soup.find (id="performance")
        for e in table.find_all (["tr","td"]):
            if len(e.text.strip()) < 20: list_erg.append (e.text.strip ())

        #print("Working on",list_erg[0])
        for i in range(0,len(list_erg)-1,6):
            dt = datetime.strftime ((datetime.strptime (list_erg[i], "%Y/%m/%d")), "%Y-%m-%d")
            erg[dt] = [clean_value(list_erg[1]), clean_value(list_erg[2]), clean_value(list_erg[3]),
                       clean_value(list_erg[4]),"", clean_value(list_erg[5])]

        dt_check = datetime.strptime(list_erg[0], "%Y/%m/%d")

        if tmp_dt == list_erg[0] or dt_check < read_to: return(erg)
        tmp_dt = list_erg[0]
        list_erg = []

def read_yahoo_histprice(stock, readFrom=datetime(1950,1,1), readTo=datetime.today(), keyString=True, out=True):
    """
    read historic stock prices
    :param stock: ticker-symbol which should be read
    :param readFROM: datetime - how long in the past the prices should be read
    :param keyString: if True key-output as String in format yyyy-mm-dd - if False output as datetime
    :param out: when True then output some status informations during program running
    :return: dictionary with daily stock prices for the ticker
    """
    if stock.upper () == "AEX25": stock = "%5Eaex"
    if stock.upper () == "ASX200": stock = "%5EAXJO"
    if stock.upper () == "ATX": stock = "%5EATX"
    if stock.upper () == "BEL20": stock = "%5EBFX"
    if stock.upper () == "CAC40": stock = "%5EFCHI"
    if stock.upper () == "DAX": stock = "%5EGDAXI"
    if stock.upper () == "DOWJONES": stock = "%5EDJI"
    if stock.upper () == "EUROSTOXX50": stock = "%5ESTOXX50E"
    if stock.upper () == "EUROSTOXX600": stock = "%5Estoxx"
    if stock.upper () == "FTSE100": stock = "%5EFTSE"
    if stock.upper () == "HANGSENG": stock = "%5EHSI"
    if stock.upper () == "IBEX35": stock = "%5EIBEX"
    if stock.upper () == "MDAX": stock = "%5EMDAXI"
    # if stock.upper () == "MIB": stock = "%FTSEMIB.MI"     # currently no prices available on yahoo finance
    if stock.upper () == "NASDAQ": stock = "%5EIXIC"
    if stock.upper () == "NIFTY50": stock = "%5ENSEI"
    if stock.upper () == "NIKKEI225": stock = "%5EN225"
    if stock.upper () == "SDAX": stock = "%5ESDAXI"
    if stock.upper () == "SENSEX": stock = "%5EBSESN"
    if stock.upper () == "SMI": stock = "%5ESSMI"
    if stock.upper () == "SP500": stock = "%5EGSPC"
    if stock.upper () == "TSX": stock = "%5EGSPTSE"

    if stock.upper() == "TASI": return(read_tasi_index(readFrom))

    erg = {}
    tmp_list = []
    # if readTo == False:
    #     readTo = datetime.today()
    # dt_readto = datetime.strftime (read_to, "%Y-%m-%d")
    # iso_dt = datetime.fromisoformat (str (datetime.now ())).timestamp ()
    # iso_dt = str(int(round (iso_dt, 0)))
    # #print("DEBUG-ISODATE:",iso_dt)

    if readFrom.year < 2000:
        isoFrom = "345427200"
    else:
        isoFrom = datetime.fromisoformat (str (readFrom)).timestamp ()
        isoFrom = str (int (round (isoFrom, 0)))
    isoTo = datetime.fromisoformat (str (readTo)).timestamp ()
    isoTo = str (int (round (isoTo, 0)))

    link = "https://query1.finance.yahoo.com/v7/finance/download/" + stock + "?period1=" + isoFrom + "&period2=" + isoTo

    if out: print("Reading historical share price data for", stock, "...")
    try:
        ftpstream = urllib.request.urlopen(link)
    except urllib.error.URLError as e:
        print("CSV-Link can not be opened...")
        print(f"Reason: {e.reason}")
        return erg

    csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))
    for row in csvfile:
        #print("DEBUG-ROW:",row)
        if row[1] != "null": tmp_list.append(row)
    tmp_list.reverse()
    #print("DEBUG-TMP_LIST:",tmp_list)

    erg[tmp_list[-1][0]] = tmp_list[-1][1:]
    for i in range(len(tmp_list)):
        # if dt_readto > tmp_list[i][0]: break
        if keyString or tmp_list[i][0] in ["Date"]:
            erg[tmp_list[i][0]] = tmp_list[i][1:]
        else:
            tmpKeyDateTime = datetime.strptime(tmp_list[i][0], "%Y-%m-%d")
            erg[tmpKeyDateTime] = tmp_list[i][1:]
    for key, val in erg.items ():
        for i_idx,i_cont in enumerate(val):
            erg[key][i_idx] = clean_value (i_cont,dp=".")

    return erg

def readYahooPriceCalcs (stock, daysList):
    erg = {}
    maxDays = max(daysList)
    ergPrices = read_yahoo_histprice (stock, datetime.today () - timedelta (days=maxDays+10))

    if ergPrices == {}:
        print(f"Stock prices currently not available...")
        return(erg)

    for days in daysList:
        # calculate SMAs
        ergSum = 0
        ergCount = 0
        ergListSMA = []
        for key, val in ergPrices.items ():
            if key == "Date":
                continue
            if ergCount == days:
                break
            ergCount += 1
            ergSum += val[3]
            ergListSMA.append(val[3])
        # print(ergListSMA)
        # print(len(ergListSMA))

        if len(ergListSMA) != 0:
            erg[f"SMA{days}"] = round(sum(ergListSMA) / len(ergListSMA),2)
            erg[f"MIN{days}"] = round(min(ergListSMA),2)
            erg[f"MAX{days}"] = round(max(ergListSMA),2)
        else:
            erg[f"SMA{days}"] = "N/A"
            erg[f"MIN{days}"] = "N/A"
            erg[f"MAX{days}"] = "N/A"

        # calculate SMAs 5 days back
        ergSum = 0
        ergCount = 0
        ergListSMA5D = []
        countDaysMAX = 5
        countDays = 0
        for key, val in ergPrices.items ():
            if key == "Date" or countDays < countDaysMAX:
                countDays += 1
                continue
            if ergCount == days:
                break
            ergCount += 1
            ergSum += val[3]
            ergListSMA5D.append(val[3])
        # print(ergListSMA5D)
        # print(len(ergListSMA5D))

        if len(ergListSMA5D) != 0:
            erg[f"SMA{days} 5DaysBack"] = round(sum(ergListSMA5D) / len(ergListSMA5D),2)
            erg[f"MIN{days} 5DaysBack"] = round(min(ergListSMA5D),2)
            erg[f"MAX{days} 5DaysBack"] = round(max(ergListSMA5D),2)
        else:
            erg[f"SMA{days} 5DaysBack"] = "N/A"
            erg[f"MIN{days} 5DaysBack"] = "N/A"
            erg[f"MAX{days} 5DaysBack"] = "N/A"

        # calculate EMAs
        # print(f"SMA{days}: {sum(ergListSMA) / len(ergListSMA)}")
        ergList2 = list(reversed(ergListSMA))
        # print(ergList2)
        ergListEMA = []
        for idx,elem in enumerate(ergList2):
            if idx == 0:
                continue
            tmpValue = (elem * (2 / (1 + abs(idx-len(ergList2))))) + (ergList2[idx-1] * (1 - (2 / (1 + abs(idx-len(ergList2))))))
            ergListEMA.append(tmpValue)
        # print(ergListEMA)
        if len(ergListEMA) != 0:
            erg[f"EMA{days}"] = round(sum(ergListEMA) / len(ergListEMA),2)
        else:
            erg[f"EMA{days}"] = "N/A"
        # print(f"EMA{days}: {sum(ergListEMA) / len(ergListEMA)}")

        # calculate EMAs days back
        # print(f"SMA{days}: {sum(ergListSMA) / len(ergListSMA)}")
        ergList25D = list(reversed(ergListSMA5D))
        # print(ergList2)
        ergListEMA5D = []
        for idx,elem in enumerate(ergList25D):
            if idx == 0:
                continue
            tmpValue = (elem * (2 / (1 + abs(idx-len(ergList25D))))) + (ergList25D[idx-1] * (1 - (2 / (1 + abs(idx-len(ergList25D))))))
            ergListEMA5D.append(tmpValue)
        # print(ergListEMA)
        if len(ergListEMA5D) != 0:
            erg[f"EMA{days} 5DaysBack"] = round(sum(ergListEMA5D) / len(ergListEMA5D),2)
        else:
            erg[f"EMA{days} 5DaysBack"] = "N/A"
        # print(f"EMA{days}: {sum(ergListEMA) / len(ergListEMA)}")

        listGain = []
        listLoss = []
        countDays = avgGain = avgLoss = 0
        if days > 16:
            for idx, elem in enumerate (ergList2):
                if idx < 14:
                    if idx == 0:
                        continue
                    tmpChange = elem - ergList2[idx-1]
                    if tmpChange >= 0:
                        listGain.append(tmpChange)
                        listLoss.append(0)
                    else:
                        listLoss.append(tmpChange * (-1))
                        listGain.append(0)
                    countDays += 1
                elif idx == 14:
                    avgGain = sum(listGain) / 14
                    avgLoss = sum(listLoss) / 14
                else:
                    tmpChange = elem - ergList2[idx - 1]
                    if tmpChange >= 0:
                        avgGain = ((avgGain * 13) + tmpChange) / 14
                        avgLoss = ((avgLoss * 13) + 0) / 14
                    else:
                        avgGain = ((avgGain * 13) + 0) / 14
                        avgLoss = ((avgLoss * 13) + (tmpChange * (-1))) / 14
            if avgLoss == 0:
                relativeStrength = 0
                relativeStrengthIndex = 100
            else:
                relativeStrength =  avgGain / avgLoss
                relativeStrengthIndex = 100 - (100 / (1 + relativeStrength))
            erg[f"14dayRS{days}"] = round(relativeStrength,2)
            erg[f"14dayRSI{days}"] = round(relativeStrengthIndex,2)
    return(erg)

def read_dayprice(prices,date,direction):
# read price of a specific date
# when date not available take nearest day in history from the date
    """
    read price for a specific date
    when date not available take nearest day in history from the date
    :param prices: list of prices
    :param date: date for what the price should be searched (in format 2020-12-24)
    :param direction: if "+" then skip 1 day to future when no price is found
                      if "-" go one day in the past when nothing ist found
    :return: date and price as list (or default pair when nothing is found)
    """
    nr = 0
    while nr < 100:
        if date in prices: return [date, float(prices[date][3])]
        else:
            dt1 = datetime.strptime (date, "%Y-%m-%d")
            if direction == "+": newdate = dt1 + timedelta (days=1)
            elif direction == "-": newdate = dt1 - timedelta (days=1)
            date = datetime.strftime (newdate, "%Y-%m-%d")
            nr +=1
    return ["1900-01-01",999999999]

def readDayPrice(stock, date):
# read price of a specific date
# when date not available take nearest day in history from the date
    """
    read price for a specific date
    when date not available take nearest day in history from the date
    :param date: date for what the price should be searched (in format 2020-12-24)
    :return: historical price for the date
    """
    dateDT = datetime.strptime(date, "%Y-%m-%d") + timedelta(1)
    isoTo = datetime.fromisoformat (str (dateDT)).timestamp ()
    isoTo = str(int(round (isoTo, 0)))
    isoFrom = dateDT - timedelta(5)
    isoFrom = datetime.fromisoformat (str (isoFrom)).timestamp ()
    isoFrom = str(int(round(isoFrom,0)))

    link = "https://finance.yahoo.com/quote/" + stock + "/history?period1=" + isoFrom + "&period2=" + isoTo

    # print (f"DEBUG: {link}")

    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep (1)

    table = soup.find("tbody")
    spans = table.find_all("span")
    return clean_value(spans[4].text)

def read_yahoo_histdividends(stock, read_to=datetime(1950,1,1), out=True):
    """
    read historic dividends payments from the stock
    # from eg. here: https://finance.yahoo.com/quote/AAPL/history?period1=1568445190&period2=1600067590&interval=div%7Csplit&filter=div&frequency=1d
    :param stock: ticker-symbol which should be read
    :param read_to: datetime - how long in the past the dividends should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with historic dividend payouts
    """
    erg = {}
    tmp_list = []

    #generate iso-format for actual date
    iso_dt = datetime.fromisoformat (str (datetime.now()- timedelta(days=1))).timestamp ()
    iso_dt = str(int(round (iso_dt, 0)))

    link = "https://query1.finance.yahoo.com/v7/finance/download/" + stock + "?period1=345427200&period2=" + iso_dt + "&interval=1d&events=div"
    #print("DEBUG Link:", link)

    if out: print("Reading historical dividends data for", stock, "...")
    try:
        ftpstream = urllib.request.urlopen(link)
    except urllib.error.URLError:
        return erg

    csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))
    for row in csvfile:
        if row[1] != "null": tmp_list.append(row)
    tmp_list.reverse()
    erg[tmp_list[-1][0]] = tmp_list[-1][1:]
    for i in range(len(tmp_list)):
        erg[tmp_list[i][0]] = clean_value(tmp_list[i][1])

    # sort dict
    erg = {k: v for k, v in sorted (erg.items (), key=lambda item: item[0], reverse=True)}

    return erg

def read_yahoo_histsplits (stock, read_to=datetime(1950,1,1), out=True):
    """
    read historic stock splits
    # from eg. here: https://finance.yahoo.com/quote/AAPL/history?period1=1568445190&period2=1600067590&interval=div%7Csplit&filter=split&frequency=1d
    :param stock: ticker-symbol which should be read
    :param read_to: datetime - how long in the past the splits should be searched
    :param out: when True then output some status informat
    :return: dictionary with historic stock splits
    """
    erg = {}
    tmp_list = []

    #generate iso-format for actual date
    iso_dt = datetime.fromisoformat (str (datetime.now()- timedelta(days=1))).timestamp ()
    iso_dt = str(int(round (iso_dt, 0)))

    link = "https://query1.finance.yahoo.com/v7/finance/download/" + stock + "?period1=345427200&period2=" + iso_dt + "&interval=1d&events=split"
    if out: print("Reading historical split data for", stock, "...")
    try:
        ftpstream = urllib.request.urlopen(link)
    except urllib.error.URLError:
        return erg

    csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))
    for row in csvfile:
        if row[1] != "null": tmp_list.append(row)
    tmp_list.reverse()
    erg[tmp_list[-1][0]] = tmp_list[-1][1:]
    for i in range(len(tmp_list)):
        erg[tmp_list[i][0]] = tmp_list[i][1:]

    # sort dict
    erg = {k: v for k, v in sorted (erg.items (), key=lambda item: item[0], reverse=True)}

    return erg

def read_ipos(read_from=datetime.today(), read_to=datetime(1950,1,1), usdOnly = False):
    """
    read ipo ticker symbols and store in list
    :param read_from: starting date from which the ipos should be read
    :param read_to: end date to which the ipos should be read
    :param usdOnly: read only tickers without "." in ticker-name
    :return: list with ipos ticker symbols as list
    """
    list_erg = []
    # find last sunday for datetime.today or datetime-parameter from function
    sunday = read_from - timedelta(days=read_from.isoweekday())

    while sunday > read_to:
        dt1 = datetime.strftime(sunday, "%Y-%m-%d")
        dt2 = datetime.strftime(sunday+timedelta(days=6), "%Y-%m-%d")
        for i in range(7):
            dt3 = datetime.strftime(sunday+timedelta(days=i), "%Y-%m-%d")
            print("Working on",dt3)
            link = "https://finance.yahoo.com/calendar/ipo?from=" + dt1 + "&to=" + dt2 + "&day=" + dt3
            #print("DEBUG LINK:",link)
            #print("DEBUG DT3:",dt3)

            page = requests.get (link)
            soup = BeautifulSoup (page.content, "html.parser")
            time.sleep (1)

            check = soup.find_all ('span', attrs={"data-reactid": "7"})
            if "We couldn't find" in check[1].text: continue

            table = soup.find (id="fin-cal-table")
            for e in table.find_all (["td"]):
                f = e.find("a")
                if f != None and len(f) > 0 and f.text not in list_erg:
                    if usdOnly:
                        if "." not in f.text:
                            list_erg.append((f.text,dt3))
                    else:
                        list_erg.append((f.text,dt3))
            print("DEBUG list_erg: ",list_erg)
        sunday -= timedelta (days=7)
    return(list_erg)

def read_yahoo_earnings_cal(stock, out=True):
    """
    read earnings calender for stock
    future earnings calls and past earnings calls with eps results
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with line per date and different values in columns
    """
    erg = {}
    erg["Header"] = ["Symbol", "Company", "EPS_Estimate", "Reported_EPS", "Surprise"]

    link = "https://finance.yahoo.com/calendar/earnings/?symbol=" + stock
    if out: print("Reading earnings calender web data for",stock,"...")
    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep (4)

    tmp_list = []
    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    table = soup.find (id="fin-cal-table")
    for row in soup.find_all ("td"): tmp_list.append (row.text.strip ())
    idx = 0

    #for i in tmp_list: print(i)        # DEBUG

    while idx < len (tmp_list):
        # cut timezone at the end of the string - sometimes 3chars - sometimes 4chars
        tmp = tmp_list[idx + 2]
        ampm_idx = tmp.find ("AM")
        if ampm_idx == -1: ampm_idx = tmp.find ("PM")
        tz_cut = ampm_idx + 2
        tmp = tmp[:tz_cut]
        #print("DEBUG TMP2: ",tmp)

        dt1 = datetime.strptime (tmp, "%b %d, %Y, %I %p")
        dt2 = datetime.strftime (dt1, "%Y-%m-%d")
        erg[dt2] = [clean_value(tmp_list[idx + 0]),
                    clean_value(tmp_list[idx + 1]),
                    clean_value(tmp_list[idx + 3]),
                    clean_value(tmp_list[idx + 4]),
                    clean_value(tmp_list[idx + 5])]
        idx += 6

    # if there is only the header and no entries => set the erg-result to {}
    if len(list(erg.keys())) == 1: erg = {}

    return(erg)

def read_yahoo_options(stock,read_to=datetime(2099,1,1), what="ALL", out=True):
# Read options stock data from yahoo
    """
    read options for stock
    :param stock: ticker-symbol which should be read
    :param read_to: how long int future the options should be read
    :param what: if "ALL" read puts/calls - if "Puts" read only Puts - if "Calls" read only Calls
    :param out: when True then output some status informations during program running
    :return: dictionary with line per dates and different informations in columns
    """
    erg = {}
    if out: print("Reading options web data for",stock,"...")
    link = "https://finance.yahoo.com/quote/" + stock + "/options"
    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep (1)

    # read different dates from drop box
    table = soup.find_all ('option')
    dates = []
    for i in table:
        val = int(i.get("value").strip())
        dt = datetime.fromtimestamp(val * 1000 / 1e3)
        #print("DEBUG Text: ", i.text)
        #print("DEBUG Value: ",val)
        #print("DEBUG Date: ",dt)
        dates.append([dt,val])
    dates.sort()
    #print("DEBUG: ",dates)
    #for i in dates: print(i)    #DEBUG

    # read puts and calls for stock
    erg["header"] = ["call_put","date","lasttrade_date","strike","last_price","bid","ask","change","change_perc","vol","open_interest","implied_volatility"]

    # read through possible dates
    for dt in dates:
        # if actual date > date-parameter: return results
        if dt[0] > read_to + timedelta(days=1): break
        print("Working for stock",stock,"on date",dt[0],"...")

        last_strike = 0
        option = "Calls"
        link = "https://finance.yahoo.com/quote/" + stock + "/options?date=" + str(dt[1]) + "&p=" + stock
        #print("DEBUG Link: ",link)
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (1)
        table = soup.find ('div', id="Main")
        tr = table.find_all("tr")
        for i in tr:
            dt_str = datetime.strftime(dt[0], "%Y-%m-%d")
            td = i.find_all("td")
            if td != None and len(td) > 0:
                row = [option, dt_str]
                contract = td[0].text.strip()
                for j_idx, j_cont in enumerate(td[1:]):
                    if j_idx == 1:
                        if float(j_cont.text.strip().replace(".","").replace(",","")) >= last_strike:
                            last_strike = float(j_cont.text.strip().replace(".","").replace(",",""))
                        else:
                            option = "Puts"
                            row[0] = "Puts"
                    row.append(j_cont.text.strip())
                if what == "ALL" or (what == "Calls" and option == "Calls") or (what == "Puts" and option == "Puts"):
                    erg[contract] = row

        for key,val in erg.items():
            for idx,cont in enumerate(val):
                erg[key][idx] = clean_value(erg[key][idx])

    return(erg)

def readYahooInsiderTransactions (stock, out=True):
    erg = {}
    link = "https://finance.yahoo.com/quote/" + stock +  "/insider-transactions"
    if out: print ("Reading insider transactions data for", stock, "...")
    erg["symbol"] = stock

    page = requests.get (link)
    soup = BeautifulSoup (page.content, "html.parser")

    table = soup.find("table", attrs={"data-test": "insider-purchases"})
    # print(f"DEBUG: {table.prettify()}")

    listTable = []
    for e in table.find_all (["td"]):
        listTable.append(clean_value(e.text.replace("% Net","Perc Net").strip ()))

    for idx,cont in enumerate(listTable):
        if idx % 3 == 0:
            erg[cont + " Shares"] = listTable[idx+1]
            erg[cont + " Trans"] = listTable[idx+2]

    return(erg)

def read_wsj_rating(stock, out=True):
    """
    read rating for stock according to wsj wall street journal
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with informations per line and timespans in columns
    """

    start = timeit.default_timer ()

    erg = {}
    if out: print("Reading wsj rating web data for", stock, "...approx 3sec...")
    if ".DE" in stock: country = "XE/XETR/"
    elif ".AS" in stock: country = "NL/XAMS/"
    elif ".AX" in stock: country = "AU/XASX/"
    elif ".BR" in stock: country = "BE/XBRU/"
    elif ".CO" in stock: country = "DK/XCSE/"
    elif ".FI" in stock: country = "FI/XHEL/"
    elif ".HE" in stock: country = "FI/XHEL/"
    elif ".HK" in stock: country = "HK/XHKG/"
    elif ".IR" in stock: country = "IE/XDUB/"
    elif ".KS" in stock: country = "KR/XKRX/"
    elif ".LS" in stock: country = "PT/XLIS/"
    elif ".L" in stock: country = "UK/XLON/"
    elif ".MC" in stock: country = "ES/MABX/"
    elif ".MI" in stock: country = "IT/XMIL/"
    elif ".OL" in stock: country = "NO/XOSL/"
    elif ".PA" in stock: country = "FR/XPAR/"
    elif ".PR" in stock: country = "CZ/XPRA/"
    elif ".ST" in stock: country = "SE/XSTO/"
    elif ".SW" in stock: country = "CH/XSWX/"
    elif ".TO" in stock: country = "CA/XTSE/"
    elif ".T" in stock: country = "JP/XTKS/"
    elif ".VI" in stock: country = "AT/XWBO/"
    elif ".VX" in stock: country = "CH/XSWX/"
    else: country = ""

    stock = stock.split(".")[0]
    link = "https://www.wsj.com/market-data/quotes/" + country + stock + "/research-ratings"

    attempt = 1
    while attempt < 5:
        try:
            options = Options ()
            options.add_argument ('--headless')
            options.add_experimental_option ('excludeSwitches', ['enable-logging'])
            path = os.path.abspath (os.path.dirname (sys.argv[0]))
            if platform == "win32":
                cd = '/chromedriver.exe'
            elif platform == "linux":
                cd = '/chromedriver_linux'
            elif platform == "darwin":
                cd = '/chromedriver'
            driver = webdriver.Chrome (path + cd, options=options)
            driver.get (link)
            break
        except:
            if out: print("TRY AGAIN... Read WJS-Data...",attempt)
            attempt += 1

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit ()
    div_id = soup.find(id="historicalCol")

    if div_id == None:
        erg["Rating"] = ["N/A","N/A","N/A","N/A"]
        for i in ["Buy","Overweight","Hold","Underweight","Sell"]: erg[i] = ["N/A","N/A","N/A","N/A"]
        return (erg)

    tmp = []
    for row in div_id.find_all("span"):
        if len(row.text.strip()) != 0: tmp.append(row.text.strip())

    if "Buy" not in tmp:
        erg["Rating"] = ["N/A","N/A","N/A","N/A"]
        for i in ["Buy","Overweight","Hold","Underweight","Sell"]: erg[i] = ["N/A","N/A","N/A","N/A"]
        return (erg)

    erg["Header"] = ["Current","1 Month Ago","3 Month Ago"]
    idx_tmp = 0
    while idx_tmp < len(tmp):
        if tmp[idx_tmp] in ["Buy","Overweight","Hold","Underweight","Sell"]:
            erg[tmp[idx_tmp]] = [int(tmp[idx_tmp+3]),int(tmp[idx_tmp+2]),int(tmp[idx_tmp+1])]
            idx_tmp += 4
        else: idx_tmp += 1

    rating_hist = []
    rating_opinions = []
    for idx_head,cont_head in enumerate(erg["Header"]):
        rat = 0
        sum_rat = 0
        count_rat = 0
        for idx,cont in enumerate(["Buy","Overweight","Hold","Underweight","Sell"]):
            sum_rat += erg[cont][idx_head] * (idx+1)
            count_rat += erg[cont][idx_head]
        if count_rat != 0: rat = round(sum_rat / count_rat,2)
        else: count_rat = 0
        if idx_head == 0: erg["Rating"] = [rat,'1Buy to 5Sell',count_rat,"Analyst Opinions"]
        rating_hist.append(rat)
        rating_opinions.append(count_rat)
    erg["RatingHist"] = rating_hist
    erg["RatingOpinions"] = rating_opinions

    for key,val in erg.items():
        for idx,cont in enumerate(val):
            erg[key][idx] = clean_value(erg[key][idx])

    stop = timeit.default_timer ()
    # print(f"Time run: {round(stop-start,2)}")

    return (erg)

def read_morningstars_financials(stock_ms, out=True):
    """
    Read morningstar stock data from yahoo
    :param stock: ticker-code from morningstar which should be read
    :param out: when True then output some status informations during program running
    :return: dictionary with one line per value and dates in columns
    """
    erg = {}
    link = "https://financials.morningstar.com/ratios/r.html?t=" + stock_ms + "&culture=en&platform=sal"
    if out: print("Reading morningstar financials web data for", stock_ms, "...approx 3sec...")
    options = Options ()
    options.add_argument ('--headless')
    options.add_experimental_option ('excludeSwitches', ['enable-logging'])

    path = os.path.abspath (os.path.dirname (sys.argv[0]))
    if platform == "win32":
        cd = '/chromedriver.exe'
    elif platform == "linux":
        cd = '/chromedriver_linux'
    elif platform == "darwin":
        cd = '/chromedriver'
    driver = webdriver.Chrome (path + cd, options=options)

    driver.get (link)
    time.sleep (2)
    soup = BeautifulSoup (driver.page_source, 'html.parser')

    tmp_list = []
    for e in soup.find_all(["th","td"]):
        if len(e.text.strip()) == 0: continue
        elif e.text.strip() in ["Revenue %","Operating Income %","Net Income %","EPS %"]:
            tmp_list.append (e.text.strip ())
            for i in range(11): tmp_list.append("")
        else: tmp_list.append(e.text.strip())
    tmp_list.insert(0,"Header")

    if "Interest Coverage" not in tmp_list: return {}
    idx = tmp_list.index("Interest Coverage")
    tmp_list.insert(idx+12,"Growth")

    row = 1
    for i in range(0,len(tmp_list),12):
        key = tmp_list[i]
        if row == 2: key = "Revenue Mil bc"
        elif row == 4: key = "Operating Income Mil bc"
        elif row == 6: key = "Net Income Mil bc"
        elif row == 7: key = "Earnings Per Share"
        elif row == 8: key = "Dividends bc"
        elif row == 9: key = "Payout Ratio %"
        elif row == 11: key = "Book Value Per Share bc"
        elif row == 12: key = "Operating Cash Flow Mil bc"
        elif row == 13: key = "Cap Spending Mil bc"
        elif row == 14: key = "Free Cash Flow Mil bc"
        elif row == 15: key = "Free Cash Flow Per Share bc"
        elif row == 16: key = "Working Capital Mil bc"
        elif row in [38, 39, 40, 41]: key = "Revenue "+key+" %"
        elif row in [43, 44, 45, 46]: key = "Operating Income " + key + " %"
        elif row in [48, 49, 50, 51]: key = "Net Income " + key + " %"
        elif row in [53, 54, 55, 56]: key = "EPS " + key + " %"
        erg[key] = tmp_list[i+1:i+12]
        row += 1

    for key,val in erg.items():
        for idx,cont in enumerate(val):
            erg[key][idx] = clean_value(erg[key][idx])
        erg[key].reverse()

    return(erg)

def read_ecoCal(from_dt, to_dt, country, hl=True):
    """
    read event messages from the economic calendr on investing.com
    :param from_dt: from which date the events should be read
    :param to_dt: to which date the events should be read
    :param country: events from which country should be read
    USA country5, GBP country4, GER country17, FRA country22
    :param hl: TRUE to work in headless mode in the background - of FALSE to work on the front
    :return:
    """
    driver = rtt.define_driver(headless=hl)
    #driver = rtt.defineDriverFF (headless=hl)
    popup_close = False
    SLEEP = 3
    from_dt = datetime.strftime(from_dt, "%d/%m/%Y")
    to_dt = datetime.strftime(to_dt, "%d/%m/%Y")

    print ("Fetching data from site...")
    locale.setlocale (category=locale.LC_ALL, locale="German")
    link = "https://de.investing.com/economic-calendar/"
    #link = "https://www.investing.com/economic-calendar/"
    driver.get (link)
    time.sleep (SLEEP)

    try:
        rtt.close_popup (driver,mode="id",cont="onetrust-accept-btn-handler")
        time.sleep (SLEEP)
    except:
        pass

    # open filter
    print("Select Filter...")
    while True:
        if popup_close == False: popup_close = rtt.close_popup (driver, mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        time.sleep (SLEEP)
        try:
            driver.find_element_by_id ("filterStateAnchor").click ()
            time.sleep (SLEEP)
            break
        except:
            "Trying again to close popup..."

    if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    element = driver.find_element_by_xpath ('//*[@id="calendarFilterBox_country"]/div[1]/a[2]')
    webdriver.ActionChains (driver).move_to_element (element).click (element).perform ()
    time.sleep (SLEEP)

    print("Select Country...")
    if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    driver.find_element_by_id (country).click ()
    time.sleep (SLEEP)

    """
    # select 2star importance
    print ("Select Importance...")
    while True:
        if popup_close == False: popup_close = rtt.close_popup (driver, mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        time.sleep (SLEEP)
        try:
            driver.find_element_by_id ("importance2").click ()
            time.sleep (SLEEP)
            break
        except:
            "Trying again to close popup..."

    # select 3star importance
    if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    driver.find_element_by_id ("importance3").click ()
    time.sleep (SLEEP)
    """

    if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    element = driver.find_element_by_id ('ecSubmitButton')
    webdriver.ActionChains (driver).move_to_element (element).click (element).perform ()
    # driver.find_element_by_id("ecSubmitButton").click()
    time.sleep (SLEEP)

    print("Search Items From Filter...")
    if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    element = driver.find_element_by_id ('datePickerToggleBtn')
    webdriver.ActionChains (driver).move_to_element (element).click (element).perform ()
    time.sleep (SLEEP)

    while True:
        if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        try:
            driver.find_element_by_id ("startDate").clear ()
            time.sleep (SLEEP)
            break
        except:
            pass

    print("Select Start Date...")
    if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    element = driver.find_element_by_id ('startDate')
    if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    # webdriver.ActionChains(driver).move_to_element(element ).send_keys ("01/01/2016")
    element.send_keys (from_dt)
    # driver.find_element_by_id("startDate").send_keys ("01/01/2016")
    time.sleep (SLEEP)

    print ("Select End Date...")
    while True:
        if popup_close == False: popup_close = rtt.close_popup (driver,mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        try:
            driver.find_element_by_id ("endDate").clear ()
            time.sleep (SLEEP)
            break
        except:
            pass

    if popup_close == False: popup_close = rtt.close_popup (driver, mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    element = driver.find_element_by_id ('endDate')
    if popup_close == False: popup_close = rtt.close_popup (driver, mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
    # webdriver.ActionChains(driver).move_to_element(element ).send_keys ("01/01/2018")
    element.send_keys (to_dt)
    # driver.find_element_by_id("endDate").send_keys ("01/01/2018")
    time.sleep (SLEEP)

    print("Search For Data...")
    while True:
        if popup_close == False: popup_close = rtt.close_popup (driver, mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        try:
            element = driver.find_element_by_id ('applyBtn')
            webdriver.ActionChains (driver).move_to_element (element).click (element).perform ()
            time.sleep (SLEEP)
            break
        except:
            pass

    # ScrollDown Variant2
    # Get scroll height
    last_height = driver.execute_script ("return document.body.scrollHeight")
    sitenr = 1
    while True:
        #time.sleep (SLEEP)
        rtt.wait_countdown (SLEEP)
        try:
            print("Try to close PopUp...")
            rtt.close_popup (driver, mode="xpath",cont='//*[@id="PromoteSignUpPopUp"]/div[2]/i')
            # time.sleep (SLEEP)
            rtt.wait_countdown (SLEEP)
        except:
            pass

        for i in range (1):
            #driver.find_element_by_xpath ('/html/body').send_keys (Keys.PAGE_UP)
            driver.execute_script ("window.scrollTo(0, document.body.scrollHeight * 0.75)")
            print("Page Up triggered...")
        #time.sleep (SLEEP)
        rtt.wait_countdown (SLEEP)

        # Scroll down to bottom
        print("Scroll Down To Bottom...")
        driver.execute_script ("window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep (SLEEP)
        rtt.wait_countdown (SLEEP)

        # Wait to load page
        print("Waiting to load...")
        #time.sleep (SLEEP+4)
        rtt.wait_countdown (SLEEP+4)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script ("return document.body.scrollHeight")
        print ("LenOfPage: ", new_height)
        print ("Reading data from site", sitenr, "...")
        sitenr += 1
        if new_height == last_height: break
        last_height = new_height

    list_cont = []
    soup = BeautifulSoup (driver.page_source, 'html.parser')
    rows = soup.find_all ("tr")

    for row in rows:
        list_row = []
        cells = row.find_all ("td")

        # append only when it is a row for date (len 1) or with all entries (len 8)
        if len (cells) in [1, 8]:
            for i_idx, i_cont in enumerate (cells):
                if i_idx == 2:
                    stars = i_cont.find_all ("i", attrs={"class": "grayFullBullishIcon"})
                    list_row.append (len (stars))
                else:
                    i_cont = i_cont.text.replace ("/xa0", "")
                    list_row.append (i_cont.strip ())

                # print (list_row)
                # print ("DEBUG LENCells, list_row", len (cells), list_row)
            if len (list_row) > 1: list_row.pop ()
            if list_row[0] in ["Offen"] or "min" in list_row[0]: continue
            list_cont.append (list_row)
    erg = {}
    erg["Header"] = ["country", "relevance", "event", "actual", "forecast", "before"]
    tmp_cont = []
    act_date = 0
    for idx, i in enumerate(list_cont):
        if len (i) == 1:
            act_date = i[0]
        else:
            tmp_dt = act_date + " " + i[0]
            # print("Debug I: ",i)
            # print(tmp_dt,len(tmp_dt),type(tmp_dt))
            dt = datetime.strptime (tmp_dt, "%A, %d. %B %Y %H:%M")
            dt = str(dt) + "#" + str(idx)
            erg[dt] = i[1:]
    driver.quit ()
    return (erg)

def readInvestingTechnical(stock=False, stockFN=False, period=False, out=True, wait=2):
    if stock == False and stockFN == False:
        return {}
    erg = {}

    link = "https://www.investing.com/equities/" + stockFN + "-technical"
    if out: print(f"Reading investing.com data for {stock} ...approx 6sec...")

    options = Options ()
    options.add_argument ('--headless')
    options.add_experimental_option ('excludeSwitches', ['enable-logging'])
    path = os.path.abspath (os.path.dirname (sys.argv[0]))
    if platform == "win32":
        cd = '/chromedriver.exe'
    elif platform == "linux":
        cd = '/chromedriver_linux'
    elif platform == "darwin":
        cd = '/chromedriver'
    driver = webdriver.Chrome (path + cd, options=options)
    driver.get (link)
    time.sleep (wait)
    try:
        driver.find_element_by_id ("onetrust-accept-btn-handler").click ()
        time.sleep (wait)
    except:
        pass

    if period == "1min": tmpPath = '//*[@id="timePeriodsWidget"]/li[1]/a'
    elif period == "5min": tmpPath = '//*[@id="timePeriodsWidget"]/li[2]/a'
    elif period == "15min": tmpPath = '//*[@id="timePeriodsWidget"]/li[3]/a'
    elif period == "30min": tmpPath = '//*[@id="timePeriodsWidget"]/li[4]/a'
    elif period == "1hour": tmpPath = '//*[@id="timePeriodsWidget"]/li[5]/a'
    elif period == "5hour": tmpPath = '//*[@id="timePeriodsWidget"]/li[6]/a'
    elif period == "1day": tmpPath = '//*[@id="timePeriodsWidget"]/li[7]/a'
    elif period == "1week": tmpPath = '//*[@id="timePeriodsWidget"]/li[8]/a'
    elif period == "1month": tmpPath = '//*[@id="timePeriodsWidget"]/li[9]/a'
    else: print(f"Error - wrong period information...")

    driver.find_element_by_xpath (tmpPath).click ()
    time.sleep (wait)
    soup = BeautifulSoup (driver.page_source, 'html.parser')
    time.sleep (wait)
    driver.quit ()

    table = soup.find("table", class_="technicalIndicatorsTbl")
    elems = table.find_all("td")

    for idx,elem in enumerate(elems):
        if idx % 3 == 0:
            tmpKey = elem.text.strip()
            tmpValue = elems[idx+1].text.strip()
            tmpAction = elems[idx+2].text.strip()
            erg[tmpKey] = clean_value(tmpValue)
            erg[tmpKey + " Action"] = clean_value(tmpAction)

        if "Bull/Bear" in tmpKey:
            break
    for idx,elem in enumerate(elems):
        tmpElem = elem.text.strip()
        matchesStr = ["Buy:","Sell:","Neutral:","Summary:"]
        if any(x in tmpElem for x in matchesStr):
            for i in tmpElem.splitlines():
                if i != "":
                    erg["TechnIndicator " + i.split(":")[0].strip()] = clean_value(i.split(":")[1].strip())

    table = soup.find("table", class_="movingAvgsTbl")
    elems = table.find_all("td")
    for idx,elem in enumerate(elems):
        matchesStr = ["Buy:","Sell:","Neutral:","Summary:"]
        if any(x in elem.text for x in matchesStr):
            break
        if idx % 3 == 0:
            tmpKey = elem.text.strip()

            tmpCont = []
            for i in elems[idx+1].text.splitlines():
                if i != "":
                    tmpCont.append(i.strip())
            erg["S"+tmpKey] = clean_value(tmpCont[0])
            erg["S"+tmpKey + " Action"] = clean_value(tmpCont[1])

            tmpCont = []
            for i in elems[idx+2].text.splitlines():
                if i != "":
                    tmpCont.append(i.strip())
            erg["E"+tmpKey] = clean_value(tmpCont[0])
            erg["E"+tmpKey + " Action"] = clean_value(tmpCont[1])

    for idx,elem in enumerate(elems):
        tmpElem = elem.text.strip()
        matchesStr = ["Buy:","Sell:","Neutral:","Summary:"]
        if any(x in tmpElem for x in matchesStr):
            for i in tmpElem.splitlines():
                if i != "":
                    erg["MovAvg " + i.split(":")[0].strip()] = clean_value(i.split(":")[1].strip())

    table = soup.find("table", class_="crossRatesTbl")
    elems = table.find_all("td")
    for idx,elem in enumerate(elems):
        if idx % 8 == 0:
            tmpTxt = elem.text.strip()
            erg[tmpTxt+" S3"] = clean_value(elems[idx+1].text.strip())
            erg[tmpTxt+" S2"] = clean_value(elems[idx+2].text.strip())
            erg[tmpTxt+" S1"] = clean_value(elems[idx+3].text.strip())
            erg[tmpTxt+" PivotPoints"] = clean_value(elems[idx+4].text.strip())
            erg[tmpTxt+" R1"] = clean_value(elems[idx+5].text.strip())
            erg[tmpTxt+" R2"] = clean_value(elems[idx+6].text.strip())
            erg[tmpTxt+" R3"] = clean_value(elems[idx+7].text.strip())

    table = soup.find("div", class_="summary")
    erg["Summary Technical Analysis"] = table.text.split(":")[1].strip()

    return (erg)

def read_gurufocus_data(stock,out=True,wait=1,
                        readOwnerEarnings=True,
                        readGrahamNumber=True,
                        readLynchValue=True,
                        readROIC=True,
                        readSummary=True,
                        readSummarySlow=True,
                        readIntrinsicValue=True):
    """
    read gurufocus stock data
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :param wait: wait for x seconds during progress
    :param read*: read the specific part / info from the webpage
    :return: dictionary with values per line
    """
    erg = {}
    if out: print ("Reading gurufocus data for", stock, "...")

    if readOwnerEarnings:
        link = "https://www.gurufocus.com/term/Owner_Earnings/" + stock + "/"
        erg["symbol"] = stock

        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (wait)
        table = soup.find(id="def_body_detail_height")
        if table != None:
            infoFont = table.findAll("font")
            # check if there is no data from gurufocus for the stock
            if infoFont[0].text.strip() == ": (As of . 20)": return {}

            erg["OE per Share"] = clean_value(infoFont[0].text.split(" ")[1])
            if not isinstance(erg["OE per Share"],float): return {}

            infoStrong = table.findAll("strong")
            lstStrong = []
            for i in infoStrong: lstStrong.append(i.text.strip())

            # print(f"DEBUG: {lstStrong}")

            pattern1 = re.compile ("^[a-zA-Z]{3}. [0-9]{4}$")
            for i,e in enumerate(lstStrong):
                if i > 3: break
                if pattern1.match (lstStrong[0]) != None:
                    if i == 0: erg["OE per Share Date"] = clean_value(datetime.strftime(datetime.strptime (e, "%b. %Y"), "%Y-%m-%d"))
                    if i == 2:
                        if e == "today": erg["Price To OE Date"] = clean_value(str(datetime.today().date()))
                        else: erg["Price To OE Date"] = clean_value(e)
                    if i == 3 and (isdigit(clean_value(e))):
                        erg["Price To OE"] = clean_value(e)
                else:
                    if i == 0:
                        erg["Price To OE Date"] = clean_value (str (datetime.today ().date ()))                # print(f"Stock: {stock}")
                        # print(f"DEBUG: {e}")
                        if "Current:" in e and (isdigit(clean_value (e.split("Current:")[1].strip()))):
                            erg["Price To OE"] = clean_value (e.split("Current:")[1].strip())
                        else:
                            print(f"No valid Price To OE in Gurufocus for Stock {stock}")
                            erg["Price To OE"] = "N/A"
                            erg["Price To OE Date"] = "N/A"
                        infoFont = table.find ("font").text.strip()
                        tmpDate = infoFont.split("(As of ")[1].replace(")","")
                        erg["OE per Share Date"] = clean_value(datetime.strftime(datetime.strptime (tmpDate, "%b. %Y"), "%Y-%m-%d"))
        else:
            print (f"Warning - Owner Earnings not accessable...")

    if readGrahamNumber:
        link = "https://www.gurufocus.com/term/grahamnumber/" + stock + "/"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (wait)
        table = soup.find(id="def_body_detail_height")
        if table != None:
            infoFont = table.findAll("font")
            #for i in infoFont: print(i.text)
            erg["Graham Number"] = clean_value(infoFont[0].text.split(" ")[1].replace("$",""))
        else:
            print(f"Warning - Graham Number not accesable...")

    if readLynchValue:
        link = "https://www.gurufocus.com/term/lynchvalue/" + stock + "/"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (wait)
        table = soup.find(id="def_body_detail_height")
        if table != None:
            infoFont = table.findAll("font")
            erg["Lynch Fair Value"] = clean_value(infoFont[0].text.split(" ")[1].replace("$",""))
        else:
            print(f"Warning - Lynchvalue not accessable...")

    if readROIC:
        link = "https://www.gurufocus.com/term/ROIC/" + stock + "/"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (wait)
        div = soup.find(id="target_def_historical_data")
        if div != None:
            tr = div.find_all("tr")
            listTitle = []
            listValues = []
            for idx,elem in enumerate(tr):
                if "Annual Data" in tr[idx].text:
                    tmplistTitle = tr[idx+1].text.split("\n")
                    tmplistValues = tr[idx+2].text.split("\n")
                    tmplistTitle.reverse()
                    tmplistValues.reverse()
                    tmplistTitle = [value for value in tmplistTitle if value != '']
                    tmplistValues = [value for value in tmplistValues if value != '']
                    for idx,elem in enumerate(tmplistValues):
                        if elem != "0.00" and elem.replace(".","").replace("-","").isdigit():
                            listValues.append(clean_value(elem))
                            listTitle.append(clean_value(tmplistTitle[idx]))
                    erg["ROIC_HistDates"] = listTitle
                    erg["ROIC_HistValues"] = listValues
                    break
            erg["Calc_ROICGrowthHist"] = clean_value (rtt.growthCalc (listValues, -1))
        else:
            print(f"Warning - ROIC data not accessable...")

    if readIntrinsicValue:
        link = "https://www.gurufocus.com/term/iv_dcEarning/" + stock + "/"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (1)
        table = soup.find (id="def_body_detail_height")
        infoFont = table.findAll ("font")
        if infoFont[0].text.strip () == ": $ (As of Today)": return {}
        erg["IntrinsicValue_DCF_EarningsBased"] = clean_value (infoFont[0].text.split (" ")[1])

        link = "https://www.gurufocus.com/term/iv_dcf/" + stock + "/"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (1)
        table = soup.find (id="def_body_detail_height")
        infoFont = table.findAll ("font")
        if infoFont[0].text.strip () == ": $ (As of Today)": return {}
        erg["IntrinsicValue_DCF_FCF_Based"] = clean_value (infoFont[0].text.split (" ")[1])

        link = "https://www.gurufocus.com/term/iv_dcf_share/" + stock + "/"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (1)
        table = soup.find (id="def_body_detail_height")
        infoFont = table.findAll ("font")
        if infoFont[0].text.strip () == ": $ (As of Today)": return {}
        erg["IntrinsicValue_ProjectedFCF"] = clean_value (infoFont[0].text.split (" ")[1])

        link = "https://www.gurufocus.com/term/gf_value/" + stock + "/"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (1)
        table = soup.find (id="def_body_detail_height")
        infoFont = table.findAll ("font")
        if infoFont[0].text.strip () == ": $ (As of Today)": return {}
        erg["IntrinsicValue_GuruFocus"] = clean_value (infoFont[0].text.split (" ")[1])

    if readSummary:
        link = "https://www.gurufocus.com/stock/" + stock + "/summary"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep (wait)

        tmpDiv = soup.find ("div", {"id": "valuation"})
        if tmpDiv == None:
            return {}
        lstCont = []
        tmpTD = tmpDiv.find_all ("td")
        for i in tmpTD:
            if len(i.text.strip()) > 0 and i.text.strip() != "N/A":
                lstCont.append(i.text.strip())
        lstCont.pop(0)
        if len(lstCont) > 0:
            if len(lstCont) % 2 != 0:
                print(f"WARNING - ListCount is not even - problem in the summary table...")
            for i,e in enumerate(lstCont):
                if i % 2 == 0:
                    erg[e] = clean_value(lstCont[i+1])

        tmpDiv = soup.find ("div", {"id": "financial-strength"})
        lstCont = []
        tmpTD = tmpDiv.find_all ("td")
        for idx,e in enumerate(tmpTD):
            if len(e.text.strip()) > 0 and len(e.text.strip()) < 20 and "WACC" not in e.text.strip():
                if e.text.strip() != "N/A": lstCont.append(e.text.strip())
            if "ROIC" in e.text.strip() and "WACC" in e.text.strip() and "%" in e.text.strip():
                tmpElem = e.text.strip().split(" ")
                tmpROIC = tmpElem[1].split("%")[0]
                tmpWACC = tmpElem[2].replace("%","")
                lstCont.extend(["ROIC",tmpROIC,"WACC",tmpWACC])

        if len(lstCont) >=3 and lstCont[2] == "Cash-To-Debt":
            lstCont = lstCont[2:]
        elif len(lstCont) >=2 and lstCont[1] == "Cash-To-Debt":
            lstCont = lstCont[1:]
        else:
            print(f"Warning - Cash-To-Debt not on right place for stock {stock}...")

        if len(lstCont) > 1:
            if len(lstCont) % 2 != 0:
                print(f"WARNING - ListCount is not even - problem in the financial strength table...")

            for i,e in enumerate(lstCont):
                if i % 2 == 0:
                    erg[e] = clean_value(lstCont[i+1])
                    if isinstance(erg[e],str): erg[e] = "N/A"

        tmpDiv = soup.find ("div", {"id": "ratios"})
        tmpTD = tmpDiv.find_all ("td")
        lstCont = []
        for idx, elem in enumerate(tmpTD):
            if elem.text.strip() not in ["","N/A","Valuation Rank"] and "/" not in elem.text:
                lstCont.append(elem.text.strip())
        if len(lstCont) > 0:
            if len(lstCont) % 2 != 0:
                print(f"WARNING - ListCount is not even - problem in the ratios table...")
            for idx, elem in enumerate(lstCont):
                if idx % 2 == 0:
                    erg[elem] = clean_value(lstCont[idx+1])

        tmpDiv = soup.find ("div", {"id": "dividend"})
        tmpTD = tmpDiv.find_all ("td")
        lstCont = []
        for idx, elem in enumerate(tmpTD):
            if elem.text.strip() not in ["","N/A"]:
                lstCont.append(elem.text.strip())
        del lstCont[0]
        if len(lstCont) > 0:
            if len(lstCont) % 2 != 0:
                print(f"WARNING - ListCount is not even - problem in the dividend table...")
            for idx, elem in enumerate(lstCont):
                if idx % 2 == 0:
                    erg[elem] = clean_value(lstCont[idx+1])

        tmpDiv = soup.find ("div", {"id": "profitability"})
        tmpTD = tmpDiv.find_all ("td")
        lstCont = []
        for idx, elem in enumerate(tmpTD):
            if elem.text.strip() not in ["","N/A","Profitability Rank"] and "/" not in elem.text:
                lstCont.append(elem.text.strip())

        if len(lstCont) > 1:
            if len(lstCont) % 2 != 0:
                print(f"WARNING - ListCount is not even - problem in the profitability table...")
            for idx, elem in enumerate(lstCont):
                if idx % 2 == 0:
                    erg[elem] = clean_value(lstCont[idx+1])

    if readSummarySlow:
        link = "https://www.gurufocus.com/stock/" + stock + "/summary"
        options = Options()
        options.add_argument('--headless')
        options.add_experimental_option ('excludeSwitches', ['enable-logging'])
        path = os.path.abspath (os.path.dirname (sys.argv[0]))
        if platform == "win32":
            cd = '/chromedriver.exe'
        elif platform == "linux":
            cd = '/chromedriver_linux'
        elif platform == "darwin":
            cd = '/chromedriver'
        driver = webdriver.Chrome (path + cd, options=options)
        driver.get (link)  # Read link
        time.sleep (3)  # Wait till the full site is loaded

        element = driver.find_element_by_id ("analyst-estimate")
        driver.execute_script ("arguments[0].scrollIntoView();", element)
        time.sleep (3)

        soup = BeautifulSoup (driver.page_source, 'html.parser')
        tmpDiv = soup.find ("div", {"id": "analyst-estimate"})
        tmpTD = tmpDiv.find_all ("td")
        lstCont = []
        for idx, elem in enumerate (tmpTD):
            if elem.text.strip () not in ["", "N/A"]:
                lstCont.append (elem.text.strip ())
        if len(lstCont) >= 3:
            for idx in range(3):
                lstCont[idx] = clean_value(lstCont[idx].replace(" ",""))
        erg["AnalystEst_Header"] = lstCont[0:3]
        del lstCont[0:3]

        # add empty elemnts to list
        if len (lstCont) > 1:
            idx = 0
            countValues = 0
            while idx < len (lstCont):
                if "(" in lstCont[idx] and countValues < 3 and idx != 0:
                    lstCont.insert (idx, "N/A")
                    countValues += 1
                elif "(" in lstCont[idx] and countValues == 3:
                    countValues = 0
                elif "(" not in lstCont[idx]:
                    countValues += 1
                idx += 1

        title = False
        valueList = []
        for idx, elem in enumerate (lstCont):
            if "(" in elem and ")" in elem:
                if idx > 0:
                    erg[title] = valueList
                    title = False
                    valueList = []
                title = "AnalystEst_" + elem.split(" (")[0].strip()
            else:
                valueList.append(elem)
            if idx == len(lstCont) - 1:
                erg[title] = valueList
                title = False
                valueList = []

    return(erg)

def calcFairValue(stock, out=True, earningsGrowth=None, fcfGrowth=None):
    """
    Calculate Fair Value for the stock using the DCF and PE-Ratio method
    :param stock: ticker-symbol for which the fair value should be calculated
    :param out: when True then output some status informations during program running
    :param earningsGrowth: when parameter used this earnings growth will be used for the calculation (instead of the online-data)
    :param fcfGrowth: when parameter used this free cashflow growth will be used for the calculation (instead of the online-data)
    :return: dictionary with endresult and detail - one line per value
    """

    # start = timeit.default_timer ()
    erg = {}
    if out: print ("Calculating fairvalue for", stock, "...")

    # read summary data
    summary = read_yahoo_summary (stock)
    if summary in [None,"",{}]:
        return(erg)
    if "next_earnings_date" not in summary: summary["next_earnings_date"] = "N/A"

    # read profile data
    profile = read_yahoo_profile(stock)

    # read statistic data
    list_eps = []
    stat1, stat2 = read_yahoo_statistics (stock)
    if "Diluted EPS (ttm)" in stat1:
        if stat1["Diluted EPS (ttm)"] not in [None,"N/A"]:
            eps_ttm = stat1["Diluted EPS (ttm)"]
            list_eps.append(eps_ttm)
        else: eps_ttm = "N/A"
    else: eps_ttm = "N/A"

    # read income statement data
    incstat = readYahooIncomeStatement (stock)
    if "Diluted EPS" in incstat and incstat["Diluted EPS"][1] not in [None,"N/A"]:
        eps_lastyear = incstat["Diluted EPS"][1]
        list_eps.append(eps_lastyear)
    else: eps_lastyear = "N/A"

    # read cashflow data
    cashflow = readYahooCashflow (stock)
    if cashflow == None:
        cashflow = {}
    if "Free Cash Flow" not in cashflow:
        cashflow["Free Cash Flow"] = ["N/A"]
        freecashflow_ttm = "N/A"
    else: freecashflow_ttm = cashflow["Free Cash Flow"][0]

    if "Shares Outstanding" in stat1:
        shares_outstanding = stat1["Shares Outstanding"]
    else:
        shares_outstanding = "N/A"

    if freecashflow_ttm not in [None,"N/A"] and shares_outstanding not in [None, "N/A"]:
        freecashflow_per_share = round(freecashflow_ttm / shares_outstanding,2)
        list_eps.append(freecashflow_per_share)
    else: freecashflow_per_share = "N/A"
    if len(list_eps) > 0:
        final_eps = sum(list_eps) / len(list_eps)
    else:
        final_eps = 0

    list_eps_growth = []
    list_temp_growth = []
    count_netinc = 0
    sum_netinc_growth = 0

    if "Net Income Common Stockholders" not in incstat: netinc_growth_history  = "N/A"
    else:
        for idx, cont in enumerate(incstat["Net Income Common Stockholders"]):
            if idx == len (incstat["Net Income Common Stockholders"])-1: break
            if cont in [None, "N/A", "-"] or incstat["Net Income Common Stockholders"][idx + 1] in [None, "N/A", "-"]: continue
            temp_growth = (cont - incstat["Net Income Common Stockholders"][idx + 1]) / incstat["Net Income Common Stockholders"][idx + 1] * 100
            if temp_growth < 30 and temp_growth > -30:
                list_temp_growth.append(temp_growth)
                sum_netinc_growth += temp_growth
                count_netinc += 1
        if count_netinc > 0: netinc_growth_history = round(sum_netinc_growth / count_netinc,2)
        else: netinc_growth_history = "N/A"

    list_eps_growth.append(netinc_growth_history)

    # read analysis stock data
    analysis = read_yahoo_analysis (stock)
    if "Next 5 Years (per annum)" in analysis and analysis["Next 5 Years (per annum)"][0] != None:
        list_eps_growth.append (analysis["Next 5 Years (per annum)"][0])
        eps_growth_next5y = analysis["Next 5 Years (per annum)"][0]
    else:
        eps_growth_next5y = 0
    if "Past 5 Years (per annum)" in analysis and analysis["Past 5 Years (per annum)"][0] != None:
        list_eps_growth.append (analysis["Past 5 Years (per annum)"][0])
        eps_growth_past5y = analysis["Past 5 Years (per annum)"][0]
    else:
        eps_growth_past5y = 0

    if earningsGrowth != None:
        final_eps_growth = earningsGrowth
    else:
        if "N/A" in list_eps_growth:
            final_eps_growth = "N/A"
        else:
            final_eps_growth = round(sum(list_eps_growth) / len(list_eps_growth),2)

    list_future_pe = []

    if final_eps_growth in ["N/A",None]: pe_windage = "N/A"
    else: pe_windage = round(final_eps_growth * 2,2)
    if pe_windage != None: list_future_pe.append(pe_windage)

    if "Forward P/E" not in stat2:
        stat2["Forward P/E"] = ["N/A"]
        pe_forward_ttm = "N/A"
    else: pe_forward_ttm = stat2["Forward P/E"][0]

    if "Forward P/E" in stat2 and stat2["Forward P/E"][0] != None:
        list_future_pe.append (pe_forward_ttm)
    if "N/A" in list_future_pe:
        final_future_pe = "N/A"
        future_10y_eps = "N/A"
        future_10y_shareprice = "N/A"
    else:
        final_future_pe = sum(list_future_pe) / len(list_future_pe)
        future_10y_eps = round(nf.fv (final_eps_growth / 100, 10, 0, final_eps * (-1), "end"),2)
        future_10y_shareprice = round(final_future_pe * future_10y_eps,2)

    if future_10y_shareprice != "N/A":
        fv_10perc_kgv = round(nf.pv (10 / 100, 10, 0, future_10y_shareprice * (-1), "end"),2)
        fv_15perc_kgv = round(nf.pv (15 / 100, 10, 0, future_10y_shareprice * (-1), "end"),2)
        fv_10perc_kgv_mos25perc = round(fv_10perc_kgv * 0.75,2)
        fv_10perc_kgv_mos50perc = round(fv_10perc_kgv * 0.5,2)
        fv_15perc_kgv_mos25perc = round(fv_15perc_kgv * 0.75,2)
        fv_15perc_kgv_mos50perc = round(fv_15perc_kgv * 0.5,2)
    else:
        fv_10perc_kgv = fv_15perc_kgv = fv_10perc_kgv_mos25perc = fv_10perc_kgv_mos50perc = fv_15perc_kgv_mos25perc = fv_15perc_kgv_mos50perc = "N/A"

    final_freecashflow = freecashflow_ttm

    count_fcf = 0
    sum_fcf_growth = 0
    for idx, cont in enumerate(cashflow["Free Cash Flow"]):
        if idx == len (cashflow["Free Cash Flow"])-1: break
        if cont in [None, "N/A", "-"] or cashflow["Free Cash Flow"][idx + 1] in [None, "N/A", "-"]: continue
        temp_growth = (cont - cashflow["Free Cash Flow"][idx + 1]) / cashflow["Free Cash Flow"][idx + 1] * 100
        if temp_growth < 30 and temp_growth > -30:
            sum_fcf_growth += temp_growth
            count_fcf += 1

    if count_fcf in [0,None,"N/A"]: fcf_growth_history = "N/A"
    else: fcf_growth_history = sum_fcf_growth / count_fcf

    if fcfGrowth != None:
        final_freecashflow_growth = fcfGrowth
    else:
        if fcf_growth_history not in ["N/A", None] and final_eps_growth not in ["N/A", None]:
            final_freecashflow_growth = round ((fcf_growth_history + final_eps_growth) / 2, 2)
        else:
            final_freecashflow_growth = "N/A"

    balance_sheet = read_yahoo_balance_sheet(stock)

    cash_casheq = rtt.check_element_dict("Cash, Cash Equivalents & Short Term Investments", balance_sheet, 0,0)
    long_term_debt = rtt.check_element_dict("Long Term Debt", balance_sheet, 0,0)
    if long_term_debt == 0:
        long_term_debt = rtt.check_element_dict("Long Term Debt And Capital Lease Obligation", balance_sheet, 0,0)
    short_term_debt = rtt.check_element_dict("Short Term Debt", balance_sheet, 0,0)

    final_netto_cash = cash_casheq - long_term_debt - short_term_debt


    if final_freecashflow not in ["N/A", None] and final_freecashflow_growth not in ["N/A",
                                                                                     None] and final_netto_cash not in [
        "N/A", None] and shares_outstanding not in ["N/A", None]:
        fv_10perc_dcf, dcf1, tv1 = rtt.dcf_calc (final_freecashflow, final_freecashflow_growth / 100, 10 / 100,
                                             final_netto_cash, shares_outstanding)
        fv_15perc_dcf, dcf2, tv2 = rtt.dcf_calc (final_freecashflow, final_freecashflow_growth / 100, 15 / 100,
                                             final_netto_cash, shares_outstanding)
        fv_10perc_dcf_mos25perc, dcf3, tv3 = rtt.dcf_calc (final_freecashflow, final_freecashflow_growth / 100, 10 / 100,
                                                       final_netto_cash, shares_outstanding, 0.75)
        fv_10perc_dcf_mos50perc, dcf4, tv4 = rtt.dcf_calc (final_freecashflow, final_freecashflow_growth / 100, 10 / 100,
                                                       final_netto_cash, shares_outstanding, 0.5)
        fv_15perc_dcf_mos25perc, dcf5, tv5 = rtt.dcf_calc (final_freecashflow, final_freecashflow_growth / 100, 15 / 100,
                                                       final_netto_cash, shares_outstanding, 0.75)
        fv_15perc_dcf_mos50perc, dcf6, tv6 = rtt.dcf_calc (final_freecashflow, final_freecashflow_growth / 100, 15 / 100,
                                                       final_netto_cash, shares_outstanding, 0.5)
    else:
        fv_10perc_dcf = dcf1 = tv1 = fv_15perc_dcf = dcf2 = tv2 = fv_10perc_dcf_mos25perc = fv_10perc_dcf_mos50perc = fv_15perc_dcf_mos25perc = fv_15perc_dcf_mos50perc = "N/A"

    dt1 = datetime.strftime (datetime.today (), "%Y-%m-%d")

    if "Market Cap (intraday)" not in stat2:
        marketcap = None
    else:
        marketcap = stat2["Market Cap (intraday)"][0]
    if marketcap == None: marketcap = summary["marketcap"]
    if marketcap == None: cap = "N/A"

    print_cap = rtt.printNumAbbr (marketcap)

    if ".DE" in stock:
        ind = "DAX"
    elif ".AS" in stock:
        ind = "AEX25"
    elif ".AX" in stock:
        ind = "ASX200"
    elif ".BR" in stock:
        ind = "BEL20"
    elif ".CO" in stock:
        ind = "EUROSTOXX600"
    elif ".FI" in stock:
        ind = "EUROSTOXX600"
    elif ".HE" in stock:
        ind = "EUROSTOXX600"
    elif ".HK" in stock:
        ind = "HANGSENG"
    elif ".IR" in stock:
        ind = "EUROSTOXX600"
    elif ".KS" in stock:
        ind = "NIKKEI225"
    elif ".L" in stock:
        ind = "FTSE100"
    elif ".LS" in stock:
        ind = "EUROSTOXX600"
    elif ".MC" in stock:
        ind = "IBEX35"
    elif ".MI" in stock:
        ind = "EUROSTOXX600"
    elif ".OL" in stock:
        ind = "EUROSTOXX600"
    elif ".PA" in stock:
        ind = "CAC40"
    elif ".PR" in stock:
        ind = "EUROSTOXX600"
    elif ".SR" in stock:
        ind = "TASI"
    elif ".ST" in stock:
        ind = "EUROSTOXX600"
    elif ".SW" in stock:
        ind = "SMI"
    elif ".T" in stock:
        ind = "NIKKEI225"
    elif ".TO" in stock:
        ind = "TSX"
    elif ".VI" in stock:
        ind = "ATX"
    elif ".VX" in stock:
        ind = "SMI"
    else:
        ind = "SP500"

    # assign result data in erg-dict
    erg["symbol"] = stock
    erg["name"] = summary["name"]
    erg["currency"] = summary["currency"]
    erg["index"] = ind
    erg["marketcap"] = print_cap
    if profile != None:
        erg["sector"] = profile.setdefault("sector","N/A")
        erg["industry"] = profile.setdefault("industry","N/A")
        erg["empl"] = profile.setdefault("empl","N/A")
    else:
        erg["sector"] = "N/A"
        erg["industry"] = "N/A"
        erg["empl"] = "N/A"

    erg["price"] = summary["price"]
    erg["day_range_from"] = summary["day_range_from"]
    erg["day_range_to"] = summary["day_range_to"]
    erg["fifty_range_from"] = summary["fifty_range_from"]
    erg["fifty_range_to"] = summary["fifty_range_to"]
    erg["price1Yest"] = summary["price1Yest"]
    erg["pe_ratio"] = summary["pe_ratio"]
    erg["next_earnings_date"] = summary["next_earnings_date"]

    erg["fv_10perc_dcf"] = fv_10perc_dcf
    erg["fv_15perc_dcf"] = fv_15perc_dcf
    erg["fv_10perc_dcf_mos25perc"] = fv_10perc_dcf_mos25perc
    erg["fv_10perc_dcf_mos50perc"] = fv_10perc_dcf_mos50perc
    erg["fv_15perc_dcf_mos25perc"] = fv_15perc_dcf_mos25perc
    erg["fv_15perc_dcf_mos50perc"] = fv_15perc_dcf_mos50perc

    erg["fv_10perc_kgv"] = fv_10perc_kgv
    erg["fv_15perc_kgv"] = fv_15perc_kgv
    erg["fv_10perc_kgv_mos25perc"] = fv_10perc_kgv_mos25perc
    erg["fv_10perc_kgv_mos50perc"] = fv_10perc_kgv_mos50perc
    erg["fv_15perc_kgv_mos25perc"] = fv_15perc_kgv_mos25perc
    erg["fv_15perc_kgv_mos50perc"] = fv_15perc_kgv_mos50perc

    erg["final_freecashflow"] = final_freecashflow
    erg["final_freecashflow_growth"] = final_freecashflow_growth
    erg["sum_discCashFlow_10y_15marr_noMos"] = dcf1
    erg["sum_terminalValue_10y_15marr_noMos"] = tv1
    erg["cash_casheq"] = cash_casheq
    erg["long_term_debt"] = long_term_debt
    erg["short_term_debt"] = short_term_debt
    erg["final_netto_cash"] = final_netto_cash
    erg["shares_outstanding"] = shares_outstanding

    erg["eps_ttm"] = eps_ttm
    erg["eps_lastyear"] = eps_lastyear
    erg["freecashflow_per_share"] = freecashflow_per_share
    erg["final_eps"] = final_eps
    erg["netinc_growth_history"] = netinc_growth_history
    erg["eps_growth_next5y"] = eps_growth_next5y
    erg["eps_growth_past5y"] = eps_growth_past5y
    erg["final_eps_growth"] = final_eps_growth
    erg["pe_windage"] = pe_windage
    erg["pe_forward_ttm"] = clean_value(pe_forward_ttm)

    if final_future_pe not in ["N/A","",None]:
        erg["final_future_pe"] = round(final_future_pe,2)
    else:
        erg["final_future_pe"] = "N/A"

    erg["future_10y_eps"] = future_10y_eps
    erg["future_10y_shareprice"] = future_10y_shareprice

    # stop = timeit.default_timer ()
    # print(round (stop - start, 2))
    return(erg)

def calcFundamentalPoints (stock, out=True):
    erg = {}
    fundamentalScore = 0
    if out: print ("Calculating Fundamental Points for", stock, "...")

    balSheet = readYahooBalanceSheet (stock, calc=True)
    statData, statTable = read_yahoo_statistics (stock, wait=0)
    incStat = readYahooIncomeStatement (stock, calc=True)
    cashFlow = readYahooCashflow(stock, calc=True)
    guruFocus = read_gurufocus_data (stock, wait=0.5)
    analysis = read_yahoo_analysis(stock)

    # row42
    if balSheet.get("Calc_BookValueGrowthHist","N/A") >= 10:
        fundamentalScore += 1
        erg["Calc_BookValueGrowthHist"] = [balSheet.get("Calc_BookValueGrowthHist","N/A"), ">=10", 1]
    else:
        erg["Calc_BookValueGrowthHist"] = [balSheet.get("Calc_BookValueGrowthHist","N/A"), ">=10", 0]

    # Row43
    if statData.get("Diluted EPS (ttm)","N/A") > 0:
        fundamentalScore += 1
        erg["Diluted EPS (ttm)"] = [statData.get("Diluted EPS (ttm)","N/A"), ">0", 1]
    else:
        erg["Diluted EPS (ttm)"] = [statData.get("Diluted EPS (ttm)","N/A"), ">0", 0]

    # Row44
    if incStat.get("Calc_EPSGrowth1Y","N/A") > 10:
        fundamentalScore += 2
        erg["Calc_EPSGrowth1Y"] = [incStat.get("Calc_EPSGrowth1Y","N/A"), ">10", 2]
    else:
        erg["Calc_EPSGrowth1Y"] = [incStat.get("Calc_EPSGrowth1Y","N/A"), ">10", 0]

    # Row45
    if incStat.get("Calc_EPSGrowthHist","N/A") > 10:
        fundamentalScore += 2
        erg["Calc_EPSGrowthHist"] = [incStat.get("Calc_EPSGrowthHist","N/A"), ">10", 2]
    else:
        erg["Calc_EPSGrowthHist"] = [incStat.get("Calc_EPSGrowthHist","N/A"), ">10", 0]

    # Row46
    if cashFlow.get("Free Cash Flow","N/A")[0] > 0:
        fundamentalScore += 1
        erg["Free Cash Flow"] = [cashFlow.get("Free Cash Flow","N/A")[0], ">0", 1]
    else:
        erg["Free Cash Flow"] = [cashFlow.get("Free Cash Flow","N/A")[0], ">0", 0]

    # Row47
    if cashFlow.get("Calc_FCFGrowthHist","N/A") > 10:
        fundamentalScore += 1
        erg["Calc_FCFGrowthHist"] = [cashFlow.get("Calc_FCFGrowthHist","N/A"), ">10", 1]
    else:
        erg["Calc_FCFGrowthHist"] = [cashFlow.get("Calc_FCFGrowthHist","N/A"), ">10", 0]

    # Row48
    if guruFocus.get("Piotroski F-Score","N/A") >= 6:
        fundamentalScore += 1
        erg["Piotroski F-Score"] = [guruFocus.get("Piotroski F-Score","N/A"), ">=6", 1]
    else:
        erg["Piotroski F-Score"] = [guruFocus.get("Piotroski F-Score","N/A"), ">=6", 0]

    # Row49
    if incStat.get("Calc_RevenueGrowth1Y","N/A") > 5:
        fundamentalScore += 1
        erg["Calc_RevenueGrowth1Y"] = [incStat.get("Calc_RevenueGrowth1Y","N/A"), ">5", 1]
    else:
        erg["Calc_RevenueGrowth1Y"] = [incStat.get ("Calc_RevenueGrowth1Y", "N/A"), ">5", 0]

    # Row50
    if incStat.get("Calc_RevenueGrowthHist","N/A") > 5:
        fundamentalScore += 1
        erg["Calc_RevenueGrowthHist"] = [incStat.get("Calc_RevenueGrowthHist","N/A"), ">5", 1]
    else:
        erg["Calc_RevenueGrowthHist"] = [incStat.get("Calc_RevenueGrowthHist","N/A"), ">5", 0]

    # Row51
    if incStat.get("Calc_NetIncomeGrowthHist","N/A") > 10:
        fundamentalScore += 1
        erg["Calc_NetIncomeGrowthHist"] = [incStat.get("Calc_NetIncomeGrowthHist","N/A"), ">10", 1]
    else:
        erg["Calc_NetIncomeGrowthHist"] = [incStat.get("Calc_NetIncomeGrowthHist","N/A"), ">10", 0]

    # Row52
    if incStat.get("Calc_OperatingIncomeGrowthHist","N/A") > 10:
        fundamentalScore += 1
        erg["Calc_OperatingIncomeGrowthHist"] = [incStat.get("Calc_OperatingIncomeGrowthHist","N/A"), ">10", 1]
    else:
        erg["Calc_OperatingIncomeGrowthHist"] = [incStat.get("Calc_OperatingIncomeGrowthHist","N/A"), ">10", 0]

    # Row53
    if incStat.get("Calc_ShareBuybacks","N/A") < 0:
        fundamentalScore += 1
        erg["Calc_ShareBuybacks"] = [incStat.get("Calc_ShareBuybacks","N/A"), "<0", 1]
    else:
        erg["Calc_ShareBuybacks"] = [incStat.get("Calc_ShareBuybacks","N/A"), "<0", 0]

    # Row54
    if statData.get("Total Debt/Equity (mrq)","N/A") <=2:
        fundamentalScore += 1
        erg["Total Debt/Equity (mrq)"] = [statData.get("Total Debt/Equity (mrq)","N/A"), "<=2", 1]
    else:
        erg["Total Debt/Equity (mrq)"] = [statData.get("Total Debt/Equity (mrq)","N/A"), "<=2", 0]

    # Row55
    if guruFocus.get("ROIC","N/A") > 10:
        fundamentalScore += 2
        erg["ROIC"] = [guruFocus.get("ROIC","N/A"), ">10", 2]
    else:
        erg["ROIC"] = [guruFocus.get("ROIC","N/A"), ">10", 0]

    # Row56
    if guruFocus.get("Calc_ROICGrowthHist","N/A") > 10:
        fundamentalScore += 2
        erg["Calc_ROICGrowthHist"] = [guruFocus.get("Calc_ROICGrowthHist","N/A"), ">10", 2]
    else:
        erg["Calc_ROICGrowthHist"] = [guruFocus.get("Calc_ROICGrowthHist","N/A"), ">10", 0]

    # Row36
    if statTable.get("Enterprise Value/EBITDA","N/A")[0] < 15:
        fundamentalScore += 2
        erg["Enterprise Value/EBITDA"] = [statTable.get("Enterprise Value/EBITDA","N/A")[0], "<15", 2]
    else:
        erg["Enterprise Value/EBITDA"] = [statTable.get("Enterprise Value/EBITDA","N/A")[0], "<15", 0]

    # Row57
    if analysis.get("Next Year","N/A")[0] >= 5:
        fundamentalScore += 1
        erg["Next Year Earnings Growth"] = [analysis.get("Next Year","N/A")[0], ">=5", 1]
    else:
        erg["Next Year Earnings Growth"] = [analysis.get("Next Year","N/A")[0], ">=5", 0]

    # Row98
    if analysis.get("Sales Growth (year/est)","N/A")[2] >= 5:
        fundamentalScore += 1
        erg["Sales Growth (year/est)"] = [analysis.get("Sales Growth (year/est)","N/A")[2], ">=5", 1]
    else:
        erg["Sales Growth (year/est)"] = [analysis.get("Sales Growth (year/est)","N/A")[2], ">=5", 0]

    # Row100
    if analysis.get("Next 5 Years (per annum)","N/A")[0] >= 5:
        fundamentalScore += 2
        erg["Next 5 Years (per annum)"] = [analysis.get("Next 5 Years (per annum)","N/A")[0], ">=5", 2]
    else:
        erg["Next 5 Years (per annum)"] = [analysis.get("Next 5 Years (per annum)","N/A")[0], ">=5", 0]

    # Row104
    tmpGrowth = (cashFlow.get ("Calc_FCFGrowthHist", "N/A") \
    + analysis.get("Sales Growth (year/est)","N/A")[2] \
    + analysis.get("Next 5 Years (per annum)","N/A")[0]) / 3
    if tmpGrowth >= 5:
        fundamentalScore += 1
        erg["Avg Growth FCF_EPS_Sales"] = [tmpGrowth, ">=5", 1]
    else:
        erg["Avg Growth FCF_EPS_Sales"] = [tmpGrowth, ">=5", 0]

    # Row108
    if incStat.get("EBIT Drawback","N/A") == 1:
        fundamentalScore += 1
        erg["EBIT Drawback"] = [incStat.get("EBIT Drawback","N/A"), "=1", 1]
    else:
        erg["EBIT Drawback"] = [incStat.get("EBIT Drawback","N/A"), "=1", 1]

    erg["fundamentalScore"] = fundamentalScore
    return (erg)

def calcLevermannScore (stock, out=True, index=None, financeFlag=None, lastEarningsDate=None):
    inpIndex = index
    WAIT = 2
    erg = {}
    if out:
        print ("Calculating Levermann Score for", stock, "...")

    if index == None:
        if ".DE" in stock:
            index = "DAX"
        elif ".AS" in stock:
            index = "AEX25"
        elif ".AX" in stock:
            index = "ASX200"
        elif ".BR" in stock:
            index = "BEL20"
        elif ".CO" in stock:
            index = "EUROSTOXX600"
        elif ".FI" in stock:
            index = "EUROSTOXX600"
        elif ".HE" in stock:
            index = "EUROSTOXX600"
        elif ".HK" in stock:
            index = "HANGSENG"
        elif ".IR" in stock:
            index = "EUROSTOXX600"
        elif ".KS" in stock:
            index = "NIKKEI225"
        elif ".L" in stock:
            index = "FTSE100"
        elif ".LS" in stock:
            index = "EUROSTOXX600"
        elif ".MC" in stock:
            index = "IBEX35"
        elif ".MI" in stock:
            index = "EUROSTOXX600"
        elif ".OL" in stock:
            index = "EUROSTOXX600"
        elif ".PA" in stock:
            index = "CAC40"
        elif ".PR" in stock:
            index = "EUROSTOXX600"
        elif ".SR" in stock:
            index = "TASI"
        elif ".ST" in stock:
            index = "EUROSTOXX600"
        elif ".SW" in stock:
            index = "SMI"
        elif ".T" in stock:
            index = "NIKKEI225"
        elif ".TO" in stock:
            index = "TSX"
        elif ".VI" in stock:
            index = "ATX"
        elif ".VX" in stock:
            index = "SMI"
        else:
            index = "SP500"

    #5 - P/E-Ratio Actual / KGV Aktuell
    # Read summary-data
    summary = read_yahoo_summary(stock)
    if "name" not in summary:
        print(f"Error - Summary data for stock {stock} not found and stopped...")
        return {}
    else:
        if "(" in summary["name"]:
            summary["name"] = summary["name"].split("(")[0].strip()
        name = summary["name"]
        currency = summary["currency"]
        pe_ratio = summary.get("pe_ratio","N/A")

    # Read data
    time.sleep (WAIT)
    profile = read_yahoo_profile (stock)
    time.sleep (WAIT)
    bal_sheet = readYahooBalanceSheet (stock)
    time.sleep (WAIT)
    insstat = readYahooIncomeStatement (stock,calc=True)
    time.sleep (WAIT)
    stat1, stat2 = read_yahoo_statistics (stock)
    time.sleep (WAIT)
    analyst_rating = read_wsj_rating(stock)
    if analyst_rating == {}:
        time.sleep (WAIT)
        analyst_rating2 = read_yahoo_analysis(stock,rating=True)
    time.sleep (WAIT)
    analysis = read_yahoo_analysis(stock)
    time.sleep (WAIT)
    dates_earnings = read_yahoo_earnings_cal (stock)

    #0 - Common Data
    if profile != None:
        sector = profile.get("sector", "N/A")
        industry = profile.get("industry","N/A")
        empl = profile.get("empl","N/A")
    else:
        sector = "N/A"
        industry = "N/A"
        empl = "N/A"

    if financeFlag == None:
        if sector in ["Financial Services"]:
            financeFlag = "Y"
        else:
            financeFlag = "N"

    #2 - EBIT-Margin / EBIT Marge
    insstat.get ("Total Revenue", ["N/A"])
    if "EBIT" not in insstat or financeFlag.upper() == "J":
        ebit = "N/A"
        ebit_marge = "N/A"
    else:
        ebit = insstat.get ("EBIT", None)[0]
        revenue = insstat.get ("Total Revenue", None)[0]
        if ebit != None and revenue not in [None,0]: ebit_marge = round(ebit / revenue * 100,2)
        else: ebit_marge = "N/A"

    #1 - Return On Equity RoE / Eigenkapitalrendite
    tmpNetIncStock = "Not needed for calc"
    tmpCommonStockEqui = "Not needed for calc"
    if "Return on Equity (ttm)" in stat1 and stat1["Return on Equity (ttm)"] != None:
        roe = stat1["Return on Equity (ttm)"]
    else:
        tmpNetIncStock = insstat.get("Net Income Common Stockholders",None)[0]
        tmpCommonStockEqui = bal_sheet.get("Common Stock Equity",None)[0]
        if tmpNetIncStock != None and tmpCommonStockEqui != None:
            roe = round((tmpNetIncStock / tmpCommonStockEqui) * 100,2)
        else:
            roe = "N/A"

    if "Market Cap (intraday)" not in stat2: stat2["Market Cap (intraday)"] = [None]
    marketcap = stat2["Market Cap (intraday)"][0]
    if marketcap == None: marketcap = summary["marketcap"]
    if marketcap in [None,"N/A"]: cap = "N/A"
    else:
        if marketcap < 200000:
            cap = "SmallCap"
            if inpIndex == None and index == "DAX": ind = "SDAX"
        elif marketcap < 5000000:
            cap = "MidCap"
            if inpIndex == None and index == "DAX": ind = "MDAX"
        else: cap = "LargeCap"
    shares_outstanding = stat1.get("Shares Outstanding","N/A")

    if shares_outstanding in ["N/A",None,""]:
        if "Basic Average Shares" in insstat:
            for idx_so, cont_so in enumerate(insstat["Basic Average Shares"]):
                if cont_so != "N/A": break
            shares_outstanding = insstat["Basic Average Shares"][idx_so]
    hist_price_stock = read_yahoo_histprice(stock)

    if index != "TASI": hist_price_index = read_yahoo_histprice(index)
    else:
        today = datetime.today ()
        yback = timedelta (days=375)
        hist_price_index = read_yahoo_histprice (index,today - yback)

    #4 - P/E-Ratio History 5Y / KGV Historisch 5J
    if "Net Income from Continuing & Discontinued Operation" not in insstat: net_income = "N/A"
    if "Breakdown" not in insstat:
        insstat["Breakdown"] = ["N/A"]
    else:
        net_income = insstat.get("Net Income from Continuing & Discontinued Operation")
    count = eps_hist = 0
    net_income_list = []
    net_income_date_list = []
    pe_ratio_hist_list = []
    pe_ratio_hist_dates = []
    if insstat["Breakdown"][0] not in [None,"N/A"] and shares_outstanding not in [None,"N/A"] and net_income not in [None,"N/A"]:
        for idx,cont in enumerate(net_income):
            if cont == "-": continue
            else:
                if insstat["Breakdown"][idx].upper() == "TTM":
                    dt1 = datetime.strftime (datetime.today (), "%Y-%m-%d")
                    tmp_date, tmp_price = read_dayprice (hist_price_stock, dt1, "-")
                    eps_hist += tmp_price / (cont / shares_outstanding)
                    pe_ratio_hist_list.append (str (round (tmp_price / (cont / shares_outstanding), 2)))
                    pe_ratio_hist_dates.append("ttm")
                    net_income_list.append(str(rtt.printNumAbbr(cont)))
                    net_income_date_list.append("ttm")
                else:
                    if cont in [None,"N/A",""]:
                        continue
                    tmp_date, tmp_price = read_dayprice(hist_price_stock,insstat["Breakdown"][idx],"-")
                    eps_hist += tmp_price / (cont / shares_outstanding)
                    pe_ratio_hist_list.append(str(round(tmp_price / (cont / shares_outstanding),2)))
                    pe_ratio_hist_dates.append(insstat["Breakdown"][idx])
                    net_income_list.append(str(rtt.printNumAbbr(cont)))
                    net_income_date_list.append(insstat["Breakdown"][idx])
                count += 1

        pe_ratio_hist = round(eps_hist / count,2)
    else: pe_ratio_hist = "N/A"

    #3 - Equity Ratio / Eigenkaptialquote
    if "Common Stock Equity" not in bal_sheet: bal_sheet["Common Stock Equity"] = ["N/A"]
    if "Breakdown" not in bal_sheet: bal_sheet["Breakdown"] = ["N/A"]
    if bal_sheet["Common Stock Equity"][0] not in ["N/A",None] and bal_sheet["Total Assets"][0] not in ["N/A",None,0]:
        equity = bal_sheet["Common Stock Equity"][0]
        total_assets = bal_sheet["Total Assets"][0]
        eq_ratio = round(equity / total_assets * 100,2)
    else:
        equity = total_assets = eq_ratio = "N/A"

    #6 - Analyst Opinions / Analystenmeinung
    if analyst_rating.get("Rating","N/A") != "N/A":
        rating = analyst_rating["Rating"][0]
        rating_count = analyst_rating["Rating"][2]
    elif analyst_rating2.get("Rating","N/A") != "N/A":
        rating = analyst_rating2["Rating"]
        rating_count = analyst_rating2["No. of Analysts"][0]
    else:
        rating = "N/A"

    #7 Reaction to quarter numbers / Reaktion auf Quartalszahlen
    last_earningsinfo = key = "N/A"
    if lastEarningsDate != None or dates_earnings != {}:
        if lastEarningsDate != None:
            key = datetime.strftime(lastEarningsDate, "%Y-%m-%d")
        else:
            for key in sorted(dates_earnings.keys(), reverse=True):
                if "Header" in key:
                    continue
                if datetime.strptime(key,"%Y-%m-%d") < datetime.today():
                    break
        last_earningsinfo = key

        stock_price_before = read_dayprice (hist_price_stock, key, "+")
        stock_price_before[1] = round (stock_price_before[1], 2)
        dt1 = datetime.strptime (stock_price_before[0], "%Y-%m-%d") + timedelta (days=1)
        dt2 = datetime.strftime (dt1, "%Y-%m-%d")
        stock_price_after = read_dayprice (hist_price_stock, dt2, "+")
        stock_price_after[1] = round (stock_price_after[1], 2)

        index_price_before = read_dayprice (hist_price_index, stock_price_before[0], "+")
        index_price_before[1] = round (index_price_before[1], 2)
        index_price_after = read_dayprice (hist_price_index, dt2, "+")
        index_price_after[1] = round (index_price_after[1], 2)
        stock_reaction = round (((stock_price_after[1] - stock_price_before[1]) / stock_price_before[1]) * 100,
                                2)
        index_reaction = round (((index_price_after[1] - index_price_before[1]) / index_price_before[1]) * 100,
                                2)
        reaction = round (stock_reaction - index_reaction, 2)
    else:
        reaction = stock_reaction = stock_price_before = stock_price_after = "N/A"
        index_reaction = index_price_before = index_price_after = "N/A"
        key = "N/A"

    #8 Profit Revision / Gewinnrevision
    #13 - Profit Growth / Gewinnwachstum
    profitGrowthCalc = False
    if analysis != {}:
        next_year_est_current = analysis["Current Estimate"][3]
        next_year_est_90d_ago = analysis["90 Days Ago"][3]

        if next_year_est_current not in [None,"N/A"] and next_year_est_90d_ago not in [None,"N/A"]:
            profit_revision = round(((next_year_est_current-next_year_est_90d_ago)/next_year_est_90d_ago)*100,2)
        else: profit_revision = "N/A"
        profit_growth_act = analysis["Current Estimate"][2]
        profit_growth_fut = analysis["Current Estimate"][3]

        if profit_growth_act in [None,"N/A"] or profit_growth_fut in [None,"N/A"]:
            profit_growth = "N/A"
        else:
            profit_growth = round(((profit_growth_fut - profit_growth_act) / profit_growth_act)*100,2)
    else:
        profit_revision = "N/A"
        profit_growth = "N/A"
        profit_growth_act = "N/A"
        profit_growth_fut = "N/A"
        next_year_est_current = "N/A"
        next_year_est_90d_ago = "N/A"
        analysis["EPS Trend"] = ["N/A","N/A","N/A","N/A"]
    if profit_growth == "N/A":
        profit_growth = round(insstat.get("Calc_EPSGrowthHist","N/A"),2)
        profitGrowthCalc = True

    #9 Price Change 6month / Kurs Heute vs. Kurs vor 6M
    #10 Price Change 12month / Kurs Heute vs. Kurs vo 1J
    #11 Price Momentum / Kursmomentum Steigend
    dt1 = datetime.strftime (datetime.today(), "%Y-%m-%d")
    dt2 = datetime.today() - timedelta (days=180)
    dt2 = datetime.strftime(dt2, "%Y-%m-%d")
    dt3 = datetime.today() - timedelta (days=360)
    dt3 = datetime.strftime(dt3, "%Y-%m-%d")
    price_today = read_dayprice(hist_price_stock,dt1,"-")
    price_6m_ago = read_dayprice(hist_price_stock,dt2,"+")
    price_1y_ago = read_dayprice(hist_price_stock,dt3,"+")
    change_price_6m = round(((price_today[1]-price_6m_ago[1]) / price_6m_ago[1])*100,2)
    change_price_1y = round(((price_today[1]-price_1y_ago[1]) / price_1y_ago[1])*100,2)

    #12 Dreimonatsreversal
    dt_today = datetime.today()
    m = dt_today.month
    y = dt_today.year
    d = dt_today.day
    dates = []
    for i in range(4):
        m -= 1
        if m == 0:
            y -= 1
            m = 12
        ultimo = calendar.monthrange(y,m)[1]
        dates.append(datetime.strftime(date(y,m,ultimo), "%Y-%m-%d"))
    stock_price = []
    index_price = []
    for i in dates:
        pr1 = read_dayprice(hist_price_stock, i, "-")
        stock_price.append([pr1[0],round(pr1[1],2)])
        pr2 = read_dayprice(hist_price_index, i, "-")
        index_price.append([pr2[0],round(pr2[1],2)])

    stock_change = []
    index_change = []
    for i in range (3, 0, -1):
        if stock_price[i - 1][1] != 0 and index_price[i - 1][1] != 0:
            stock_change.append (round (((stock_price[i][1] - stock_price[i - 1][1]) / stock_price[i - 1][1]) * 100, 2))
            index_change.append (round (((index_price[i][1] - index_price[i - 1][1]) / index_price[i - 1][1]) * 100, 2))
    if stock_change == []:
        stock_change = ["N/A", "N/A", "N/A"]
    if index_change == []:
        index_change = ["N/A", "N/A", "N/A"]

    lm_points = 0
    lm_pointsDict = {}
    #1 - check RoE
    if roe == "N/A": lm_pointsDict["roe"] = 0
    elif roe > 20: lm_pointsDict["roe"] = 1
    elif roe < 10: lm_pointsDict["roe"] = -1
    else: lm_pointsDict["roe"] = 0

    #2 - check ebit_marge
    if financeFlag in ["J","Y"] or ebit_marge == "N/A": lm_pointsDict["ebit_marge"] = 0
    else:
        if ebit_marge > 12 and financeFlag.upper() == "N": lm_pointsDict["ebit_marge"] = 1
        elif ebit_marge < 6 and financeFlag.upper() == "N": lm_pointsDict["ebit_marge"] = -1
        else: lm_pointsDict["ebit_marge"] = 0

    #3 - check eq-ratio
    if eq_ratio == "N/A": lm_pointsDict["eq_ratio"] = 0
    else:
        if financeFlag in ["J","Y"]:
            if eq_ratio > 10: lm_pointsDict["eq_ratio"] = 1
            elif eq_ratio < 5: lm_pointsDict["eq_ratio"] = -1
            else: lm_pointsDict["eq_ratio"] = 0
        else:
            if eq_ratio > 25: lm_pointsDict["eq_ratio"] = 1
            elif eq_ratio < 15: lm_pointsDict["eq_ratio"] = -1
            else: lm_pointsDict["eq_ratio"] = 0

    #4 - check pe-ratio
    if pe_ratio == "N/A": lm_pointsDict["pe_ratio"] = 0
    else:
        if pe_ratio <12 and pe_ratio > 0: lm_pointsDict["pe_ratio"] = 1
        elif pe_ratio >16 or pe_ratio <0: lm_pointsDict["pe_ratio"] = -1
        else: lm_pointsDict["pe_ratio"] = 0

    #5 - check pe-ratio history
    if pe_ratio_hist == "N/A": lm_pointsDict["pe_ratio_hist"] = 0
    else:
        if pe_ratio_hist <12 and pe_ratio_hist > 0: lm_pointsDict["pe_ratio_hist"] = 1
        elif pe_ratio_hist >16 or pe_ratio_hist <0: lm_pointsDict["pe_ratio_hist"] = -1
        else: lm_pointsDict["pe_ratio_hist"] = 0

    #6 - check rating
    if cap == "SmallCap":
        if rating == "N/A": lm_pointsDict["rating"] = 0
        elif rating_count >= 5 and rating <= 2: lm_pointsDict["rating"] = -1
        elif rating_count >= 5 and rating >= 4: lm_pointsDict["rating"] = 1
        elif rating_count < 5 and rating <= 2: lm_pointsDict["rating"] = -1
        elif rating_count < 5 and rating >= 4: lm_pointsDict["rating"] = -1
        else: lm_pointsDict["rating"] = 0
    else:
        if rating == "N/A": lm_pointsDict["rating"] = 0
        elif rating >= 4: lm_pointsDict["rating"] = 1
        elif rating <= 2: lm_pointsDict["rating"] = -1
        else: lm_pointsDict["rating"] = 0

    #7 - check to quarter numbers
    if reaction == "N/A": lm_pointsDict["reaction"] = 0
    else:
        if reaction >1: lm_pointsDict["reaction"] = 1
        elif reaction <-1: lm_pointsDict["reaction"] = -1
        else: lm_pointsDict["reaction"] = 0

    #8 - check profit revision
    if profit_revision == "N/A": lm_pointsDict["profit_revision"] = 0
    else:
        if profit_revision >1: lm_pointsDict["profit_revision"] = 1
        elif profit_revision <-1: lm_pointsDict["profit_revision"] = -1
        else: lm_pointsDict["profit_revision"] = 0

    #9 - change price 6 month
    if change_price_6m >5: lm_pointsDict["change_price_6m"] = 1
    elif change_price_6m <-5: lm_pointsDict["change_price_6m"] = -1
    else: lm_pointsDict["change_price_6m"] = 0

    #10 - change price 1 year
    if change_price_1y >5: lm_pointsDict["change_price_1y"] = 1
    elif change_price_1y <-5: lm_pointsDict["change_price_1y"] = -1
    else: lm_pointsDict["change_price_1y"] = 0

    #11 - price momentum
    if lm_pointsDict["change_price_6m"] == 1 and lm_pointsDict["change_price_1y"] in [0,-1]:
        lm_pointsDict["price_momentum"] = 1
    elif lm_pointsDict["change_price_6m"] == -1 and lm_pointsDict["change_price_1y"] in [0,1]:
        lm_pointsDict["price_momentum"] = -1
    else: lm_pointsDict["price_momentum"] = 0

    #12 month reversal effect
    if cap == "LargeCap":
        if stock_change[2]<index_change[2] and stock_change[1]<index_change[1] and stock_change[0]<index_change[0]:
            lm_pointsDict["3monatsreversal"] = 1
        elif stock_change[2]>index_change[2] and stock_change[1]>index_change[1] and stock_change[0]>index_change[0]:
            lm_pointsDict["3monatsreversal"] = -1
        else: lm_pointsDict["3monatsreversal"] = 0
    else:
        lm_pointsDict["3monatsreversal"] = 0

    ls_vs = []
    if stock_change != [] and index_change != []:
        for i in range (2, -1, -1):
            if stock_change[i] > index_change[i]:
                ls_vs.append (">")
            elif stock_change[i] < index_change[i]:
                ls_vs.append ("<")
            else:
                ls_vs.append ("=")
    else:
        ls_vs = ["N/A", "N/A", "N/A"]

    #13 - profit growth
    if profit_growth == "N/A": lm_pointsDict["profit_growth"] = 0
    else:
        if profit_growth >5: lm_pointsDict["profit_growth"] = 1
        elif profit_growth <-5: lm_pointsDict["profit_growth"] = -1
        else: lm_pointsDict["profit_growth"] = 0

    # print format marketcap
    print_cap = rtt.printNumAbbr(marketcap)

    # overall recommendation levermann full
    lm_sum = 0
    for val in lm_pointsDict.values(): lm_sum += val
    if cap in ["SmallCap", "MidCap"]:
        if lm_sum >= 7:
            rec = "Possible Buy"
        elif lm_sum in [5, 6]:
            rec = "Possible Holding"
        else:
            rec = "Possible Sell"
    else:
        if lm_sum >= 4:
            rec = "Possible Buy"
        elif lm_sum in [3]:
            rec = "Possible Holding"
        else:
            rec = "Possible Sell"

    # overall recommendation levermann light
    lm_sum_light = lm_pointsDict["roe"] + lm_pointsDict["ebit_marge"] + lm_pointsDict["pe_ratio"] \
                   + lm_pointsDict["reaction"] + lm_pointsDict["change_price_6m"]
    # overall recomendation levermann full
    if cap in ["SmallCap","MidCap"]:
        if lm_sum_light >=4: rec_light = "Possible Buy"
        else: rec_light = "Possible Sell"
    else:
        if lm_sum_light >=3: rec_light = "Possible Buy"
        else: rec_light = "Possible Sell"


    erg["name"] = summary["name"]
    erg["ticker"] = stock
    erg["index"] = index
    erg["marketCap"] = print_cap
    erg["currency"] = summary["currency"]
    erg["sector"] = sector
    erg["industry"] = industry
    erg = {**erg, **lm_pointsDict}
    erg["LastEarnings"] = clean_value(last_earningsinfo)
    erg["1roe"] = roe
    erg["2ebitMarge"] = ebit_marge
    erg["3eqRatio"] = eq_ratio
    erg["4peRatioHist"] = pe_ratio_hist
    erg["5peRatio"] = pe_ratio
    erg["6analystRating"] = rating
    erg["7quartalReaction"] = reaction
    erg["8profitRevision"] = profit_revision
    erg["9priceToday6M"] = change_price_6m
    erg["10priceToday1Y"] = change_price_1y
    erg["13profitGrowth"] = profit_growth
    erg["Levermann Score Full"] = lm_sum
    erg["Levermann Score Light"] = lm_sum_light
    erg["Recommendation Full"] = rec
    erg["Recommendation Light"] = rec_light
    erg["Cap"] = cap
    erg["Finanzwert"] = financeFlag

    return erg

if __name__ == '__main__':
    PRINT_KEYS = False
    SUMMARY = False
    PROFILE = False
    STATISTIC = False
    INCSTAT_FAST = False
    INCSTAT_ALL = False
    BALSHEET_FAST = False
    BALSHEET_ALL = False
    CASHFLOW_FAST = False
    CASHFLOW_ALL = False
    ANALYSIS = False
    ANALYSIS_RATING = False
    HISTPRICE_STRING = False
    HISTPRICE_DATETIME = False
    HISTPRIC_DATE = False
    HISTPRIC_DATERANGE = False
    HISTPRIC_CALCS = False
    DAYPRICE = False
    DAYPRICE2 = False
    READ_TASI = False
    RATING_ZACKS = False
    EARNING_CAL = False
    RATING_WSJ = False
    MORNINGSTAR = False
    HIST_DIVIDENDS = False
    HIST_DIVIDENDS_DATE = False
    HIST_SPLITS = False
    IPOS = False
    OPTIONS = False
    INSIDER_TRANS = False
    INVESTING_ECOCAL = False
    CLEAN_VALUE = False
    GURU_FOCUS_FULL = False
    GURU_FOCUS_PARTLY = False
    FINANZ_TECHNICAL_ANALYSIS = False
    CALC_FV = False
    CALC_FUNDAMENTAL_POINTS = False
    CALC_LEVERMANN = True

    stock = "AAPL"
    # stock = "DLR"
    # stock = "%5EIXIC"
    # stock = "%5EBSESN"
    # stock = "OMV.VI"
    # stock = "AARTIDRUGS.NS"
    # stock = "6601.hk"
    stock_ms = "0P000000GY"  #AAPL
    stockFN = "apple-computer-inc"
    # stock_ms = "0P00015BGZ"

    erg = {}
    if SUMMARY: erg = read_yahoo_summary(stock,att=3)
    if PROFILE: erg = read_yahoo_profile(stock)
    if STATISTIC: ergData, ergTable = read_yahoo_statistics(stock,wait=0)
    if INCSTAT_FAST: erg = readYahooIncomeStatement(stock,calc=True)
    if INCSTAT_ALL: erg = read_yahoo_income_statement(stock)
    if BALSHEET_FAST: erg = readYahooBalanceSheet(stock,calc=True)
    if BALSHEET_ALL: erg = read_yahoo_balance_sheet(stock)
    if CASHFLOW_FAST: erg = readYahooCashflow(stock,calc=True)
    if CASHFLOW_ALL: erg = read_yahoo_cashflow(stock)
    if ANALYSIS: erg = read_yahoo_analysis(stock)
    if ANALYSIS_RATING: erg = read_yahoo_analysis(stock,rating=True)
    if HISTPRICE_STRING: erg = read_yahoo_histprice(stock)
    if HISTPRICE_DATETIME: erg = read_yahoo_histprice(stock, keyString=False)
    if HISTPRIC_DATE: erg = read_yahoo_histprice(stock,datetime(2019,1,1))
    if HISTPRIC_DATERANGE: erg = read_yahoo_histprice (stock, datetime(2020,5,15), datetime(2020,5,20))
    if HISTPRIC_CALCS: erg = readYahooPriceCalcs (stock, [5,10,20,30,40,50,200])
    if DAYPRICE: erg = read_dayprice (erg, "2018-12-30", "+")
    if DAYPRICE2: erg = readDayPrice (stock,"2020-05-20")
    if READ_TASI: erg = read_tasi_index(datetime(2020,1,1), out=True)
    if EARNING_CAL: erg = read_yahoo_earnings_cal(stock)
    if RATING_WSJ: erg = read_wsj_rating(stock)
    if MORNINGSTAR: erg = read_morningstars_financials(stock_ms)
    if HIST_DIVIDENDS: erg = read_yahoo_histdividends(stock)
    if HIST_DIVIDENDS_DATE: erg = read_yahoo_histdividends(stock,datetime(2020,1,1))
    if HIST_SPLITS: erg = read_yahoo_histsplits (stock)
    if IPOS: erg = read_ipos(read_from = datetime(2018,12,31), read_to = datetime(2017,1,1))
    if OPTIONS: erg = read_yahoo_options (stock, read_to=datetime(2020,10,2), what="Puts")
    if INSIDER_TRANS: erg = readYahooInsiderTransactions(stock)
    if INVESTING_ECOCAL: erg = read_ecoCal (from_dt=datetime (2020, 5, 15), to_dt=datetime (2020, 5, 15), country="country5", hl=False)
    if GURU_FOCUS_FULL:
        erg = read_gurufocus_data(stock,wait=0.5)
    if GURU_FOCUS_PARTLY:
        erg = read_gurufocus_data (stock, wait=0.5, readOwnerEarnings=False,
                        readGrahamNumber=False,
                        readLynchValue=False,
                        readROIC=False,
                        readSummary=False,
                        readSummarySlow=True,
                        readIntrinsicValue=False)
    if FINANZ_TECHNICAL_ANALYSIS: erg = readInvestingTechnical(stockFN=stockFN,period="1day")
    if CALC_FV: erg = calcFairValue(stock)
    if CALC_FUNDAMENTAL_POINTS: erg = calcFundamentalPoints(stock)
    if CALC_LEVERMANN: erg = calcLevermannScore(stock)

    if STATISTIC:
        for key,val in ergData.items(): print(key,val,type(val))
        for key,val in ergTable.items(): print(key,val)
        if PRINT_KEYS:
            print("\nKeys Data:")
            for key in ergData.keys (): print (key)
            print("\nKeys Table:")
            for key in ergTable.keys (): print (key)
    elif IPOS or DAYPRICE or DAYPRICE2:
        print(erg)
    elif CLEAN_VALUE:
        print('assert clean_value ("4.33B", out="None") == 4330000.0')
        assert clean_value ("4.33B", out="None") == 4330000.0
        print('assert clean_value ("120M", out="None") == 120000.0')
        assert clean_value ("120M", out="None") == 120000.0
        print('assert clean_value ("300T", out="None") == 300000000000.0')
        assert clean_value ("300T", out="None") == 300000000000.0
        print('assert clean_value ("433B", out="None") == 433000000.0')
        assert clean_value ("433B", out="None") == 433000000.0
        print('assert clean_value ("+-54.00%", out="None") == 54.0')
        assert clean_value ("+-54.00%", out="None") == 54.0
        print('assert clean_value ("-54.00%", out="None") == -54.0')
        assert clean_value ("-54.00%", out="None") == -54.0
        print('assert clean_value ("42.749.274.398", dp=",", out="None") == 42749274398')
        assert clean_value ("42.749.274.398", dp=",", out="None") == 42749274398
        print ('assert clean_value ("8.652.094.026,455", dp=",", out="None") == 8652094026.455')
        assert clean_value ("8.652.094.026,455", dp=",", out="None") == 8652094026.455
        print ('assert clean_value ("180,91", dp=",", out="None") == 180.91')
        assert clean_value ("180,91", dp=",", out="None") == 180.91
        print ('assert clean_value ("112.13", out="None") == 112.13')
        assert clean_value ("112.13", out="None") == 112.13
        print ('assert clean_value ("2,954.91", out="None") == 2954.91')
        assert clean_value ("2,954.91", out="None") == 2954.91
        print ('assert clean_value ("nan", out="None") == None')
        assert clean_value ("nan", out="None") == None
        print ('assert clean_value ("Tivoli A/S", out="None") == "Tivoli A/S"')
        assert clean_value ("Tivoli A/S", out="None") == "Tivoli A/S"
        print('assert clean_value("6/30/2020") == "2020-06-30"')
        assert clean_value("6/30/2020") == "2020-06-30"
        print ('assert clean_value ("309.76B",tcorr=True) == 309760000000.0')
        assert clean_value ("309.76B",tcorr=True) == 309760000000.0
        print('assert clean_value("Jun19") == "2019-06-30"')
        assert clean_value("Jun19") == "2019-06-30"
        print ('assert clean_value ("Jun2020") == "2020-06-30"')
        assert clean_value ("Jun2020") == "2020-06-30"
        print ('assert clean_value ("2.34T",tcorr=True) == 2340000000000.0')
        assert clean_value ("2.34T",tcorr=True) == 2340000000000.0
        print ('assert clean_value ("76803.87M",tcorr=True) == 76803870000:')
        assert clean_value ("76803.87M",tcorr=True) == 76803870000.0
        print ('assert clean_value("$72.19") == 72.19')
        assert clean_value("$72.19") == 72.19

    else:
        for key, val in erg.items (): print (f"{key} => {val} {type(val)}")

        if PRINT_KEYS:
            print("\nKeys:")
            for key in erg.keys (): print (key)
