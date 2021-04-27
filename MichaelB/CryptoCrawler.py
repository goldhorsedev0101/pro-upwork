# import StockCrawler as sc
# import RapidTechTools as rtt
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
import pandas

def readInitCMB():
    finalListCoins = []
    countReads = 1
    while True:
        print(f"Reading Coins {countReads} iteration - find so far {len(finalListCoins)} coins...")
        tmpListCoins = []
        if countReads == 1:
            link = "https://coinmarketcap.com/"
        else:
            link = f"https://coinmarketcap.com/?page={countReads}"
        page = requests.get (link)
        soup = BeautifulSoup (page.content, "html.parser")
        time.sleep(1)
        tmpTR = soup.find_all("tr")
        for idx, elem in enumerate(tmpTR):
            for idx2, elem2 in enumerate(elem.find_all("td")):
                for idx3, elem3 in enumerate(elem2.find_all("a")):               
                    # print(f"{idx2}: {elem2.text.strip()}")
                    # print(f"{idx2}: {elem2.get('href')}")
                    tmp = elem3.get('href')
                    if "/markets/" not in tmp:
                        tmp = tmp.replace("/","").replace("currencies","").strip()            
                        if tmp not in tmpListCoins and tmp not in finalListCoins:                                                                                                                                                     
                            tmpListCoins.append(tmp)

        if tmpListCoins == []:
            break
        else:
            for elem in tmpListCoins:
                finalListCoins.append(elem)
        countReads += 1
    return(finalListCoins)

def readCurrencyCMC(coin,out=True,att=2):
    """
    Read summary stock data from yahoo
    :param stock: ticker-symbol which should be read
    :param out: when True then output some status informations during program running
    :param att: number of attempts how often the reading should be repeated in case of problems
    :return: dictionary with line per value
    """
    erg = {}
    link = f"https://coinmarketcap.com/currencies/{coin}/"
    if out: print (f"Reading summary web data for {coin} ...")    
    

    attempt = 1
    while attempt < att:
        try:
            page = requests.get (link)
            soup = BeautifulSoup (page.content, "html.parser")
            time.sleep(1)
            tmpTR = soup.find_all("tr")
        except:
            pass
        if tmpTR != None: break
        if out: print ("Read attempt name failed... Try", attempt)
        time.sleep (.5 + attempt)
        attempt += 1 
    if tmpTR == None: return ({})

    tmpSymbol = soup.find("small", class_=re.compile("nameSymbol_"))    
    if tmpSymbol in [None]:
        print(f"Data for coin {coin} not found - skipped...")
        return (erg)
    
    erg["coin"] = coin.capitalize()    
    erg["symbol"] = tmpSymbol.text.strip()

    tmpList = []
    for idx, elem in enumerate(tmpTR):
        tmpTH = elem.find("th")
        tmpTD = elem.find("td")
        # print(tmpTH.text.strip())
        # print(tmpTD.text.strip())

        if tmpTH.text.strip() in ["Price Change24h","Trading Volume24h","Market Cap","Fully Diluted Market Cap"]:
            # print(tmpTH.text.strip())
            # print(tmpTD.text.strip())
            if tmpTD.text.strip() == "No Data":
                erg[tmpTH.text.strip() + " Absolut"] = "N/A"
                erg[tmpTH.text.strip() + " Percent"] = "N/A"
            else:              
                tmpSPAN = tmpTD.find_all("span")    
                erg[tmpTH.text.strip() + " Absolut"] = sc.clean_value(tmpSPAN[0].text.strip())
                if len(tmpSPAN) > 1:
                    erg[tmpTH.text.strip() + " Percent"] = sc.clean_value(tmpSPAN[1].text.strip())
                else: 
                    erg[tmpTH.text.strip() + " Percent"] = "N/A"
                
        elif "All Time High" in tmpTH.text.strip() or "All Time Low" in tmpTH.text.strip():
            tmpSPANKey = tmpTD.find_all("span") 
            tmpSPANValue = tmpTD.find_all("span") 

        elif any(x in tmpTH.text.strip() for x in ["24h Low / 24h High","Yesterday's Low / High","Yesterday's Open / Close",
            "7d Low / 7d High","30d Low / 30d High","90d Low / 90d High","52 Week Low / 52 Week High"]):
            tmpSlashTH = tmpTH.text.strip().split("/")
            tmpSlashTD = tmpTD.text.strip().split("/")
            erg[tmpSlashTH[0].strip()] = sc.clean_value(tmpSlashTD[0].strip())
            if "Yesterday's" in tmpTH.text:
                erg["Yesterday's " + tmpSlashTH[1].strip()] = sc.clean_value(tmpSlashTD[1].strip())
            else:
                erg[tmpSlashTH[1].strip()] = sc.clean_value(tmpSlashTD[1].strip())

        elif any(x in tmpTH.text.strip() for x in ["Circulating Supply","Total Supply","Max Supply"]):
            tmpTickerTD = tmpTD.text.strip().split(" ")[0].strip()
            erg[tmpTH.text.strip()] = sc.clean_value(tmpTickerTD)   

        else:
            if "Price" in tmpTH.text.strip() and "24h" not in tmpTH.text.strip():
                erg["Price"] = sc.clean_value(tmpTD.text.strip())
            elif "ROI" in tmpTH.text.strip():
                erg["ROI"] = sc.clean_value(tmpTD.text.strip())
            elif "Market Rank" in tmpTH.text.strip():
                erg[tmpTH.text.strip()] = sc.clean_value(tmpTD.text.replace("#","").strip())
            else:
                erg[tmpTH.text.strip()] = sc.clean_value(tmpTD.text.strip())

    for key, val in erg.items ():
        if val in ["No Data","No"]:
            erg[key] = "N/A"
    return(erg)

def readHistPriceCMC(coin,out=True,wait=.5):
    erg = {}
    link = f"https://coinmarketcap.com/currencies/{coin}/historical-data/"
    if out: print (f"Reading price data for {coin} ...")    
    erg["coin"] = coin.capitalize()    
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument('window-size=1920x1080')
    options.add_argument('--headless')
    options.add_experimental_option ('excludeSwitches', ['enable-logging'])
    path = os.path.abspath (os.path.dirname (sys.argv[0]))

    if platform == "win32": cd = '/chromedriver.exe'
    elif platform == "linux": cd = '/chromedriver_linux'
    elif platform == "darwin": cd = '/chromedriver'
    driver = webdriver.Chrome (path + cd, options=options)
    driver.get (link)
    time.sleep (wait)
    element = driver.find_element_by_xpath ('//*[@id="__next"]/div/div[2]/div/div[3]/div/div/div[1]/span/button')
    time.sleep (wait)
    webdriver.ActionChains(driver).move_to_element(element ).click(element ).perform()
    time.sleep (wait)

    driver.find_element_by_xpath ('//*[@id="tippy-24"]/div/div[1]/div/div/div[1]/div[2]/ul/li[5]').click()

    time.sleep (wait)
    driver.find_element_by_xpath ('//*[@id="tippy-24"]/div/div[1]/div/div/div[2]/span/button').click()
    time.sleep (wait)

    tmpListElements = []
    soup = BeautifulSoup (driver.page_source, 'html.parser')
    tmpTR = soup.find_all("tr")

    for idx, elem in enumerate(tmpTR):
        for idx2, elem2 in enumerate(elem.find_all("td")):
            tmpListElements.append(elem2.text.strip())

    for i,e in enumerate(tmpListElements):
        if i % 7 == 0:
            tmpDate = datetime.strptime(e, "%b %d, %Y")
            tmpDate = datetime.strftime(tmpDate, "%Y-%m-%d")
            erg[tmpDate] = tmpListElements[i+1:i+7]

    for key, val in erg.items ():
        if key == "coin":
            continue
        tmpVal = val
        for elemIDX, elem in enumerate(tmpVal):
            tmpVal[elemIDX] = sc.clean_value(elem)
        erg[key] = tmpVal

    return (erg)

def readHistPriceCMCapi(coinID,out=True,start="2017-01-01",end="2021-04-27",output="df"):
    # output="df" for dataframe, output="dict" for dictionary
    erg = {}
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")

    startISO = int(datetime.fromisoformat(str(start)).timestamp())
    endISO = int(datetime.fromisoformat(str(end)).timestamp())

    # coinID = "1,1027,1839,52,825,2010,74,6636,7083,2"
    # coinID = "2010,74,6636,7083,2"
    # coinID = "1,1027,1839,52,825"
    
    link = f"https://web-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical?id={coinID}&convert=USD&time_start={startISO}&time_end={endISO}"      
    response = requests.get(link).json()   
    erg = response["data"]
    listFinal = []
    # loop trough individual coin
    for key, val in response["data"].items():
        if out: print (f"Reading price data for {val['symbol']} ...")          
        id = val["id"]
        name = val["name"]
        symbol = val["symbol"]
        # loop trough individual price per day
        for elem in val["quotes"]: 
            ergDict = {}
            ergDict["id"] = val["id"]
            ergDict["name"] = val["name"]
            ergDict["symbol"] = val["symbol"]
            tmpDate = elem["time_open"][:10]
            ergDict["datePrice"] = datetime.strptime(tmpDate, "%Y-%m-%d")
            ergDictQuote = elem["quote"]["USD"]
            ergDict = {**ergDict, **ergDictQuote}

            listFinal.append(ergDict)
  
    df = pandas.DataFrame(listFinal)        
    # df = pandas.DataFrame([q["quote"]["USD"] for q in response["data"]["quotes"]])
    # df['timestamp'] = pandas.to_datetime(df['timestamp']).apply(lambda x: x.date())
    # df = df.set_index("timestamp")    
    if output == "df":
        return(df)
    else:   
        erg = df.T.to_dict('list')
        return (erg)

def readCoinsIDs():
    link = f"https://web-api.coinmarketcap.com/v1/cryptocurrency/map?sort=cmc_rank"
    response = requests.get(link).json()
    dataErg = response["data"]
    return dataErg


if __name__ == '__main__':
    SUMMARY = False
    HISTPRICE = False
    HISTPRICE_API_DICT = False
    HISTPRICE_API_DF = True
    READCOINS_API = False
    COIN_INIT = False

    coin = "bitcoin"
    # coin = "venus-bnb"
    # coin = "istanbul-basaksehir-fan-token"
    # coin = "bitcoin-cash"
    # coin = "ethereum"
    # coin = "funfair"

    erg = {}
    ergList = []
    if SUMMARY: erg = readCurrencyCMB(coin)
    if HISTPRICE: erg = readHistPriceCMB(coin)
    if HISTPRICE_API_DICT: erg = readHistPriceCMCapi(1,output="dict")
    if HISTPRICE_API_DF: erg = readHistPriceCMCapi(1)
    if COIN_INIT: ergList = readInitCMB()
    if READCOINS_API: erg = readCoinsIDs()

    if COIN_INIT:
        for i,e in enumerate(ergList):
            print(f"{i+1}: {e}")
    elif READCOINS_API:
        for i in erg:
            print(i)
    elif HISTPRICE_API_DF:
        print(erg)
    else:
        for key, val in erg.items (): print (f"{key} => {val} {type(val)}")  