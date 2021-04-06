import StockCrawler as sc
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

def readCurrencyCMB(coin,out=True,att=2):
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
    erg["coin"] = coin.capitalize()

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

if __name__ == '__main__':
    SUMMARY = True
    COIN_INIT = False

    coin = "bitcoin"
    # coin = "venus-bnb"
    # coin = "istanbul-basaksehir-fan-token"

    erg = {}
    ergList = []
    if SUMMARY: erg = readCurrencyCMB(coin)
    if COIN_INIT: ergList = readInitCMB()

    if SUMMARY:
        for key, val in erg.items (): print (f"{key} => {val} {type(val)}")
    if COIN_INIT:
        for i,e in enumerate(ergList):
            print(f"{i+1}: {e}")