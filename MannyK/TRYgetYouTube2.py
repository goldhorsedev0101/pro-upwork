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

  with sshtunnel.SSHTunnelForwarder(
          ("nl1-ts105.a2hosting.com", 7822),
          ssh_username="rapidtec",
          ssh_password="C1d0q6bsE2C]:D",
          remote_bind_address=("127.0.0.1", 3306),
          local_bind_address=("0.0.0.0", 3306)
  ) as tunnel:
      mydb = mysql.connector.connect(
          user="rapidtec_Reader",
          password="I65faue#RR6#",
          host="127.0.0.1",
          database="rapidtec_levermann",
          port="3306")
      c = mydb.cursor()
      c.execute ("SELECT * FROM trialaccess")
      erg = c.fetchall()
      if ('MannyK', 'getYouTube') not in erg:
        print(f"Sorry - trial period has ended...")
        sys.exit()     

  fn = os.path.join(path, os.path.basename(__file__).replace(".py", ".xlsx"))
  print(f"Try to open excel in {fn}")
  wb = xw.Book (fn)
  ws = wb.sheets[0]
  inpData = ws.range ("A2:C5000").value
  inpData = [x for x in inpData if x[0] != None]
  # inpWait = wsInp["B1"].value 
  # if inpWait == None or not isinstance(inpWait, float):
  #   inpWait = 300
  # else:
  #   inpWait = int(inpWait)  
  # ws = wb.sheets[1]
  # existData = ws.range ("A2:Z5000").value
  # existData = [x for x in existData if x[0] != None]
  # existKeys = [x[6] for x in existData]  
  # rowNum = len(existData) + 2
  # workNum = 0
  # tmpOutput = []  
   
  print(f"Checking Browser driver...")
  options = Options()
  # options.add_argument('--headless=new')  
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

  link = "https://www.youtube.com/"
  driver.get (link)  
  input(f"Pls signup to your google accoutn and press a key...")
  for rowNum, row in enumerate(inpData, start=2):
    if row[1] != None:
      continue
    link = row[0]
    # link = "https://www.youtube.com/user/BesY24"
    driver.get (link)  
    # if firstRun:
    #   try:
    #     driver.find_element(By.XPATH,'(//button[@aria-label="Accept all"])[1]').click()       
    #   except:
    #     pass
    #   try:
    #     driver.find_element(By.XPATH,'(//button[@aria-label="Alle akzeptieren"])[1]').click()       
    #   except:
    #     pass
      
      # firstRun = False
    time.sleep(WAIT) 

    waitWD.until(EC.element_to_be_clickable((By.XPATH, '//yt-attributed-string[@id="more"]'))).click()     
    time.sleep(WAIT) 
    soup = BeautifulSoup (driver.page_source, 'lxml')  
    worker = soup.find("div", {"id": "links-section"})
    worker = worker.find_all("div", {"class": "yt-channel-external-link-view-model-wiz__container"})       
    linkList = []
    for w in worker:
      wName = w.find_next("span").text.strip()
      wLink = w.find_next("a").text.strip()
      wLink = f"https://{wLink}"
      linkList.append(f"{wName}: {wLink}")
    wAboutLink = ", ".join(linkList)

    waitWD.until(EC.element_to_be_clickable((By.XPATH, '//td[@id="view-email-button-container"]//button'))).click()  
    waitWD.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@title='reCAPTCHA']")))          
    waitWD.until(EC.element_to_be_clickable((By.XPATH, '//span[@id="recaptcha-anchor"]'))).click()  
    # driver.execute_script("arguments[0].click();", waitWD.until(EC.element_to_be_clickable((By.XPATH, '//span[@id="recaptcha-anchor"]'))))    
    driver.switch_to.default_content()  
    time.sleep(WAIT) 
    waitWD.until(EC.element_to_be_clickable((By.XPATH, '//button[@id="submit-btn"]'))).click()  
    time.sleep(WAIT)

    input("Press!")


    worker = soup.find("div", {"id": "additional-info-container"})
    worker = worker.find_next("table")
    worker = worker.find_all("td")
    worker = [x.text.strip() for x in worker]
    worker = [x for x in worker if x and not x.startswith("Sign in")]
    wChannelDetails = ", ".join(worker)

    tmpRow = [wAboutLink, wChannelDetails]   
    for e in tmpRow:
      print(e)
    exit()

    ws.range(f"B{rowNum}:C{rowNum}").value = tmpRow
    ws.range(f"A{rowNum}:Z{rowNum}").api.WrapText = False    
    print(f"Data written to {rowNum}...")
    # input("Press!")
  
  driver.quit()
  wb.save()
  print(f"Program {os.path.basename(__file__)} finished - will close soon...") 
  time.sleep(5)  