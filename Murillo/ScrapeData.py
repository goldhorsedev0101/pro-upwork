import RapidTechTools as rtt
import YahooCrawler as yc
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import sys, os
from selenium.webdriver.chrome.options import Options
from sys import platform
from datetime import datetime, timedelta
from datetime import date
from selenium.common.exceptions import NoSuchElementException
import os
import xlwings as xw
import time
import sys
from icecream import ic

def readStocktwits(stock,out=True,att=10):
    """
    Read summary stock data from yahoo
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :param att: number of attempts how often the reading should be repeated in case of problems
    :return: dictionary with line per value
    """
    erg = {}

    link = "https://stocktwits.com/symbol/" + stock
    if out: print (f"Reading web data from stocktwits for {stock}")
    erg["symbol"] = stock

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
            # time.sleep (1)
            soup = BeautifulSoup (driver.page_source, 'html.parser')  # Read page with html.parser
            # time.sleep (1)
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

    # price = soup.find ("span", attrs={"class": "st_3OTz8Ec"})  # Read specific class
    # time.sleep (1)
    # erg["price"] = yc.clean_value(price.text)

    sentiment = soup.find_all ("div", attrs={"class": "st_21nJvQl st_2h5TkHM st_8u0ePN3 st_2mehCkH"})  # Read specific class
    # time.sleep (1)
    detaiList = ["Price Perc","Sentiment Perc","Message Volume Perc"]
    for idx,cont in enumerate(sentiment):
        erg[detaiList[idx]] = yc.clean_value(cont.text)

    # deviation = soup.find ("span", attrs={"class": "st_3E7muvq st_8u0ePN3 st_3kXJm4P st_2KQW5_v st_37VuZWc"})
    # time.sleep (1)
    # erg["deviation1"] = yc.clean_value(deviation.text.split(" (")[0].strip())
    # erg["deviation2"] = yc.clean_value(deviation.text.split(" (")[1].replace("%)","").strip())

    # detaiListIndex = ["Dow","SP500","Nasdaq"]
    # time.sleep (2)
    # indizes = soup.find_all ("span", attrs={"lib_2H63hKL lib_2WawZPB lib_hYxgIpE lib_1TQ25j6"})
    # time.sleep (2)
    # # print(f"DEBUG: Len of Index {len(indizes)}")
    # for idx in range(3):
    #     # print(f"DEBUG: {idx}")
    #     # print(f"DEBUG: {indizes[idx].text}")
    #     erg[detaiListIndex[idx]] = yc.clean_value(indizes[idx].text)

    return(erg)

if __name__ == '__main__':
    SAVE_INTERVAL = 5
    SLEEP = 1
    START_TICKER = ""
    FN = "ScrapeData.xlsx"
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    fn = path + "/" + FN
    wb = xw.Book (fn)
    ws = wb.sheets["Stocks"]

    l_stocks = ws.range ("A2:A10000").value
    workStocks = []
    for idx,cont in enumerate(l_stocks):
        if cont == "Ticker":
            continue
        if cont == None:
            break
        else:
            workStocks.append(cont)
    # print(f"DEBUG: {workStocks}")
    idxStock = 3
    dayChgPercSP500 = yc.read_yahoo_summary ("%5EGSPC")["daychange_perc"]
    dayChgPercDow30 = yc.read_yahoo_summary ("%5EDJI")["daychange_perc"]
    dayChgPercNasdaq = yc.read_yahoo_summary ("%5EIXIC")["daychange_perc"]

    for idx, stock in enumerate (workStocks):
        summary = yc.read_yahoo_summary (stock)
        analysis = yc.read_yahoo_analysis (stock)
        transactions = yc.readYahooInsiderTransactions (stock)
        statData, statTable = yc.read_yahoo_statistics(stock,wait=0)
        stockTwits = readStocktwits(stock)
        tmpName = rtt.check_element_dict ("name", summary, "N/A", -1)
        if "(" in tmpName: tmpName = tmpName.split ("(")[0].strip ()
        if tmpName == "N/A" or summary == {}:
            continue
        ws["B" + str (idxStock)].value = tmpName
        ws["C" + str (idxStock)].value = rtt.check_element_dict ("currency", summary, "N/A", -1)
        ws["D" + str (idxStock)].value = stockTwits["Price Perc"]
        ws["E" + str (idxStock)].value = stockTwits["Sentiment Perc"]
        ws["F" + str (idxStock)].value = stockTwits["Message Volume Perc"]
        ws["G" + str (idxStock)].value = rtt.check_element_dict ("price", summary, "N/A", -1)
        ws["H" + str (idxStock)].value = rtt.check_element_dict ("daychange_abs", summary, "N/A", -1)
        ws["I" + str (idxStock)].value = rtt.check_element_dict ("daychange_perc", summary, "N/A", -1)
        ws["J" + str (idxStock)].value = dayChgPercDow30
        ws["K" + str (idxStock)].value = dayChgPercSP500
        ws["L" + str (idxStock)].value = dayChgPercNasdaq
        ws["M" + str (idxStock)].value = rtt.check_element_dict ("vol", summary, "N/A", -1)
        ws["N" + str (idxStock)].value = rtt.check_element_dict ("avg_vol", summary, "N/A", -1)
        ws["O" + str (idxStock)].value = rtt.check_element_dict ("Next Year", analysis, "N/A", 0)
        ws["P" + str (idxStock)].value = rtt.check_element_dict ("Next 5 Years (per annum)", analysis, "N/A", 0)
        ws["Q" + str (idxStock)].value = rtt.check_element_dict ("Past 5 Years (per annum)", analysis, "N/A", 0)
        ws["R" + str (idxStock)].value = rtt.check_element_dict ("Purchases Shares", transactions, "N/A", -1)
        ws["S" + str (idxStock)].value = rtt.check_element_dict ("Purchases Trans", transactions, "N/A", -1)
        ws["T" + str (idxStock)].value = rtt.check_element_dict ("Sales Shares", transactions, "N/A", -1)
        ws["U" + str (idxStock)].value = rtt.check_element_dict ("Sales Trans", transactions, "N/A", -1)
        ws["V" + str (idxStock)].value = rtt.check_element_dict ("Total Cash (mrq)", statData, "N/A", -1)
        ws["W" + str (idxStock)].value = rtt.check_element_dict ("Total Debt (mrq)", statData, "N/A", -1)

        idxStock += 1

        if idxStock % 5 == 0:
            wb.save (fn)
            # wb.close()
            print ("Saved to disk...")

# stock="AAPL"
# stock="CAT"
# stock="FB"
# erg = readStocktwits(stock)
# for key, val in erg.items (): print (key, val, type(val))
