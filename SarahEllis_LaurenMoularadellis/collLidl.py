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
  WAIT = 5
  path = os.path.abspath(os.path.dirname(sys.argv[0])) 

  mydb = mysql.connector.connect (host="nl1-ss18.a2hosting.com", user="rapidtec_Reader", passwd="I65faue#RR6#", database="rapidtec_levermann")
  c = mydb.cursor()# c.execute ("SELECT * FROM trialaccess")
  c.execute ("SELECT * FROM trialaccess")
  erg = c.fetchall()
  if ('SarahEllis', 'collLidl') not in erg:
    print(f"Sorry - trial period has ended...")
    sys.exit()     

  fn = os.path.join(path, "dataLidl.xlsx")
  wb = xw.Book (fn)
  wsInp = wb.sheets[0]
  inpData = wsInp.range ("A1:A5000").value
  inpData = [x for x in inpData if x != None]
  ws = wb.sheets[1]
  existData = ws.range ("A2:Z5000").value
  existData = [x for x in existData if x[0] != None]
  existKeys = [x[7] for x in existData]  
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
  
  listVar = ["Cabernet Sauvignon", "Merlot", "Pinot Noir", "Syrah", "Shiraz", "Zinfandel", 
              "Sangiovese", "Tempranillo", "Malbec", "Grenache", "Chardonnay", "Sauvignon Blanc",
              "Riesling", "Pinot Grigio", "Pinot Gris", "Gewürztraminer", "Chenin Blanc", 
              "Viognier", "Marsanne", "Roussanne", "Semillon", "Muscat", "Moscato"]

  for link in inpData:
    countRows = 0
    # link = f"https://www.lidl.co.uk/our-wine-range/white-wine" 
    print(f"Working for {link}")  
    driver.get (link)       
    waitWD.until(EC.presence_of_element_located((By.XPATH, '//footer[@class="nuc-o-footer"]')))   
    time.sleep(WAIT) 
    soup = BeautifulSoup (driver.page_source, 'html.parser')       
    # tmpDIV = soup.find("div", {"class": "tblresults"})   
    tmpDIV = soup.find_all("article", {"class": "ret-o-card"})     
    print(f"{len(tmpDIV)} elements found")  
    for elem in tmpDIV:
      wLink = elem.find("a").get("href")
      wLink = f"https://www.lidl.co.uk{wLink}"
      if wLink in existKeys:
        print(f"{wLink} allready in excel - skipped...")
        continue
      existKeys.append(wLink)
      print(f"Working for {wLink}")
      wName = elem.find("h3", {"class": "ret-o-card__headline"}).text.strip()
      wName = wName.split()
      wName = [x for x in wName if x != "" if not x.strip().isdigit()]
      wName = " ".join(wName)

      wFormat = "N/A"
      worker = elem.find("p", {"class": "ret-o-card__content"})
      if worker != None:
        wFormat = worker.text.strip()
        
      driver.get (wLink)       
      time.sleep(WAIT) 
      soup = BeautifulSoup (driver.page_source, 'html.parser')
      wPrice = soup.find("span", {"class": "pricebox__price"}).text.strip()

      wRegion = wVintage = wABV = "N/A"
      worker = soup.find("article", {"class": "textbody"})  
      worker = worker.find_all("li")
      for w in worker:
        w2 = list(w.stripped_strings)
        w2 = [x.strip() for x in w2]
        if w2[0] == "Region:":
          wRegion = w2[1]
        elif w2[0] == "Vintage:":
          wVintage = w2[1]
        elif w2[0] == "ABV:":
          wABV = w2[1]

      wVar = "N/A"
      for v in listVar:
        if v in wName:
          wVar = v
          # wName = wName.replace(v, "")
          # wName = wName.split()
          # wName = [x for x in wName if x != ""]
          # wName = " ".join(wName)

      tmpRow = [wName, wVar, wFormat, wPrice, wRegion, wVintage, wABV, wLink, link]    
      # for e in tmpRow:
      #   print(e)
      # exit()
      tmpOutput.append(tmpRow)
      workNum += 1    
      if workNum % WRITE_INTERVAL == 0:
        ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").value = tmpOutput
        ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").api.WrapText = False    
        countRows += 1
        if TRIAL and countRows > 5:
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