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
import mysql.connector
import sshtunnel

def checkNone(val):
  if val:
    return val.text.strip()
  else:
    return "N/A"

if __name__ == '__main__':
  print(f"Program name: {os.path.basename(__file__)}")  
  TRIAL = True   
  BREAK_OUT = 10    
  SAVE_INTERVAL = 1
  WAIT = 1
  path = os.path.abspath(os.path.dirname(sys.argv[0])) 

  # with sshtunnel.SSHTunnelForwarder(
  #         ("nl1-ts105.a2hosting.com", 7822),
  #         ssh_username="rapidtec",
  #         ssh_password="C1d0q6bsE2C]:D",
  #         remote_bind_address=("0.0.0.0", 3306),
  #         allow_agent=False
  # ) as tunnel:
  #     mydb = mysql.connector.connect(
  #         user="rapidtec_Reader",
  #         password="I65faue#RR6#",
  #         host="127.0.0.1",
  #         database="rapidtec_levermann",
  #         port=tunnel.local_bind_port)
  #     c = mydb.cursor()
  #     c.execute ("SELECT * FROM trialaccess")
  #     erg = c.fetchall()
  #     if ('jan669', 'collBallzy4') not in erg:
  #       print(f"Sorry - trial period has ended - reach out to rapid1898@gmail.com for questions...")
  #       sys.exit()     

  fn = os.path.join(path, os.path.basename(__file__).replace(".py", ".xlsx"))
  print(f"Try to open excel in {fn}")
  wb = xw.Book (fn)
  wsInp = wb.sheets[0]
  inpData = wsInp.range ("A1:A5000").value
  inpData = [x for x in inpData if x != None]
  inpWait = wsInp["B1"].value 
  if inpWait == None or not isinstance(inpWait, float):
    inpWait = 300
  else:
    inpWait = int(inpWait)  
  ws = wb.sheets[1]
  existData = ws.range ("A2:Z5000").value
  existData = [x for x in existData if x[0] != None]
  existKeys = [x[6] for x in existData]  
  rowNum = len(existData) + 2
  workNum = 0
  tmpOutput = []  
   
  print(f"Checking Browser driver...")
  options = Options()
  options.add_argument('--headless=new')  
  options.add_argument("start-maximized")
  options.add_argument('--log-level=3')  
  options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})    
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  options.add_experimental_option('useAutomationExtension', False)
  options.add_argument('--disable-blink-features=AutomationControlled') 
  srv=Service()
  driver = webdriver.Chrome (service=srv, options=options)    
  # driver.minimize_window()
  waitWD = WebDriverWait (driver, 10)         
  
  link = "https://www.questdiagnostics.com/locations/search.html/33180/50/1?target=0"

  print(f"Working for {link}")  
  driver.get (link)     
  # waitWD.until(EC.presence_of_element_located((By.XPATH, '//button[@class="rpl-pagination__nav"]')))    
  time.sleep(WAIT) 
  soup = BeautifulSoup (driver.page_source, 'lxml')  
  worker = soup.find("div", {"id": "tabs"})   
  findElems = worker.find_all("div", {"class": "tab paginatable-item"})       
  for elem in findElems:
    wName = elem.find("a").text.strip()
    wLink = elem.find("a").get("href")
    wLink = f"https://www.questdiagnostics.com{wLink}"
    # if wLink in existKeys:
    #   print(f"{wLink} allready in excel - skipped...")
    #   continue
    # existKeys.append(wLink)
    print(f"Working for {wLink}")
    driver.get (wLink)       
    time.sleep(WAIT) 
    soup = BeautifulSoup (driver.page_source, 'lxml')      
    
    worker = soup.find("div", {"class": "address"}).stripped_strings
    worker = list(worker)
    worker = [x.strip().replace("\n","").replace("\t","") for x in worker]
    wAddress = ", ".join(worker)       

    wPhone = soup.find("a", {"id": "phone"}).text.strip()
    wFax = soup.find("a", {"id": "fax"}).text.strip()

    wDesc = soup.find("div", {"class": "label-desc"}).find_next("p").text.strip()

    tmpRow = [wName, wLink, wAddress, wPhone, wFax, wDesc]   
    # for e in tmpRow:
    #   print(e)
    # exit()
    tmpOutput.append(tmpRow)
    workNum += 1    
    if workNum % SAVE_INTERVAL == 0:
      ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").value = tmpOutput
      ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").api.WrapText = False    
      # countRows += 1
      # if TRIAL and countRows > BREAK_OUT:
      #   print(f"Maximum output per category reached - skipped to next category...")
      #   breakOut = True
      #   break      
      print(f"Data written to {rowNum}...")
      rowNum += len(tmpOutput)
      tmpOutput = []
      workName = 0      
      # input("Press!")

  driver.quit()
  ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").value = tmpOutput
  ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").api.WrapText = False   
  wb.save()
  print(f"Program {os.path.basename(__file__)} finished - will close soon...") 
  time.sleep(5)  