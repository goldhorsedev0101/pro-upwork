import requests
import time
import os, sys
import xlwings as xw
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
# from fake_useragent import UserAgent
import mysql.connector

if __name__ == '__main__':
  TRIAL = True    
  WRITE_INTERVAL = 1
  WAIT = 3
  path = os.path.abspath(os.path.dirname(sys.argv[0])) 

  mydb = mysql.connector.connect (host="nl1-ss18.a2hosting.com", user="rapidtec_Reader", passwd="I65faue#RR6#", database="rapidtec_levermann")
  c = mydb.cursor()# c.execute ("SELECT * FROM trialaccess")
  c.execute ("SELECT * FROM trialaccess")
  erg = c.fetchall()
  if ('SarahEllis', 'collLidl') not in erg:
    print(f"Sorry - trial period has ended...")
    sys.exit()     

  fn = os.path.join(path, "dataMajestic.xlsx")
  wb = xw.Book (fn)
  wsInp = wb.sheets[0]
  inpData = wsInp.range ("A1:A5000").value
  inpData = [x for x in inpData if x != None]
  ws = wb.sheets[1]
  existData = ws.range ("A2:Z5000").value
  existData = [x for x in existData if x[0] != None]
  existKeys = [x[9] for x in existData]  
  rowNum = len(existData) + 2
  workNum = 0
  tmpOutput = []  
   
  print(f"Checking Browser driver...")
  os.environ['WDM_LOG'] = '0' 
  # ua = UserAgent(verify_ssl=False2)
  # ua = UserAgent(verify_ssl=False, fallback='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36')
  # userAgent = ua.random
  options = Options()
  options.add_argument('--headless')
  options.add_argument("start-maximized")
  options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})    
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  options.add_experimental_option('useAutomationExtension', False)
  options.add_argument('--disable-blink-features=AutomationControlled')
  # options.add_argument(f'user-agent={userAgent}')   
  srv=Service(ChromeDriverManager().install())
  driver = webdriver.Chrome (service=srv, options=options)    
  # driver.minimize_window()
  waitWD = WebDriverWait (driver, 10)         

  for baseLink in inpData:
    print(f"Working for baselink {baseLink}")
    countRows = 0
    breakOut = False
    for pageNr in range(1,100):
      if breakOut:
        break
      link = f"{baseLink}?pagenumber={pageNr}&paginationtype=10"
      print(f"Working for {link}")  
      driver.get (link)       
      waitWD.until(EC.presence_of_element_located((By.XPATH, '//div[@class="product-list-container"]')))   
      time.sleep(WAIT) 
      soup = BeautifulSoup (driver.page_source, 'html.parser')       
      tmpDIV = soup.find("div", {"class": "product-list-container"})   
      tmpDIV = tmpDIV.find_all("div", {"class": "mb-4 product-item-container"})    
      if len(tmpDIV) == 0:
        break 
      print(f"{len(tmpDIV)} elements found")  
      for elem in tmpDIV:
        wLink = elem.find("a").get("href")
        wLink = f"https://www.majestic.co.uk/{wLink}"
        if wLink in existKeys:
          print(f"{wLink} allready in excel - skipped...")
          continue
        existKeys.append(wLink)
        print(f"Working for {wLink}")       
        driver.get (wLink)       
        time.sleep(WAIT) 
        soup = BeautifulSoup (driver.page_source, 'html.parser')

        wName = soup.find("h1", {"class": "product-info__name"}).text.strip()
        wMajesticBadge = soup.find("span", string=re.compile('Majestic Exclusive'))
        if wMajesticBadge:
          wMajesticBadge = "Y"
        else:
          wMajesticBadge = "N"

        wPrice = soup.find("span", {"class": "product-action__price-text"})
        wPrice = list(wPrice.stripped_strings)[0]
        
        wVar = wRegion = wType = wChar = wABV = wVintage = "N/A"
        worker = soup.find("div", {"class": "product-content__more-content"})  
        worker = worker.find_all("tr")
        for w in worker:
          wTD = w.find_all("td")
          tdText = wTD[0].text.strip()
          tdVal = wTD[1].text.strip()
          if tdText == "Grape":
            wVar = tdVal
          elif tdText == "Country":
            wRegion = tdVal
          elif tdText == "Type":
            wType = tdVal
          elif tdText == "Characteristics":
            wChar = tdVal
          elif tdText == "ABV":
            wABV = tdVal
          elif tdText == "Vintage":
            wVintage = tdVal

        tmpRow = [wName, wVar, wPrice, wRegion, wVintage, wABV, wType, wChar, 
                  wMajesticBadge, wLink, link]    
        # for e in tmpRow:
        #   print(e)
        # exit()
        tmpOutput.append(tmpRow)
        workNum += 1    
        if workNum % WRITE_INTERVAL == 0:
          ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").value = tmpOutput
          ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").api.WrapText = False    
          countRows += 1
          if TRIAL and countRows > 10:
            print(f"Maximum output per category reached - skipped to next category...")
            breakOut = True
            break      
          print(f"Data written to {rowNum}...")
          rowNum += len(tmpOutput)
          tmpOutput = []
          workName = 0      
          # input("Press!")
    
  driver.quit()
  wb.save()
  print(f"Program finished - pls press <enter> to close the window...") 
  time.sleep(5)  