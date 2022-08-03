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
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from dotenv import load_dotenv, find_dotenv

if __name__ == '__main__':
  SAVE_INTERVAL = 5
  WAIT = 3
  path = os.path.abspath(os.path.dirname(sys.argv[0])) 
  rowNum = 2

  load_dotenv(os.path.join(os.getcwd(), ".env")) 
  TIKTOK_USER = os.environ.get("TIKTOK_USER")
  TIKTOK_PW = os.environ.get("TIKTOK_PW")

  fn = os.path.join(path, "data.xlsx")
  wb = xw.Book (fn)
  ws = wb.sheets[0]
  existData = ws.range ("A2:Z5000").value
  existData = [x for x in existData if x[0] != None]
   
  print(f"Checking Browser driver...")
  os.environ['WDM_LOG_LEVEL'] = '0' 
  ua = UserAgent()
  userAgent = ua.random
  options = Options()
  # options.add_argument('--headless')
  options.add_argument("start-maximized")
  options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})    
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  options.add_experimental_option('useAutomationExtension', False)
  options.add_argument('--disable-blink-features=AutomationControlled')
  options.add_argument(f'user-agent={userAgent}')   
  srv=Service(ChromeDriverManager().install())
  driver = webdriver.Chrome (service=srv, options=options)    
  waitWebDriver = WebDriverWait (driver, 10)         
  
  link = f"https://www.tiktok.com/login/phone-or-email/email" 
  # driver.minimize_window()        # optional
  driver.get (link)       
  waitWebDriver.until(EC.presence_of_element_located((By.XPATH,"//input[@name='username']"))) \
    .send_keys(TIKTOK_USER)
  waitWebDriver.until(EC.presence_of_element_located((By.XPATH,"//input[@type='password']"))) \
    .send_keys(TIKTOK_PW)
  waitWebDriver.until(EC.element_to_be_clickable( \
    (By.XPATH, "//button[@type='submit']"))).click()   
   
  time.sleep(5000) 


  soup = BeautifulSoup (driver.page_source, 'html.parser')       

  for idx,elem in enumerate(lElems):
    # working with selenium-elements on page
    driver.find_element(By.XPATH,"//button[@id= 'gdpr-modal-agree']").click()  
    # time.sleep(WAIT)    

    waitWebDriver.until(EC.presence_of_element_located((By.XPATH,"//input[@name='email']"))) \
      .send_keys("email")
    waitWebDriver.until(EC.presence_of_element_located((By.XPATH,"//input[@name='passwort']"))) \
      .send_keys("pw")
    waitWebDriver.until(EC.element_to_be_clickable( \
      (By.XPATH, "//button[@type='submit']"))).click()     

    waitWebDriver.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='sportName tennis']")))   
    waitWebDriver.until(EC.presence_of_element_located( \
      (By.XPATH, "//input[@class='_31SfF']"))).send_keys("XYZ" + u'\ue007')
    
    try:
      waitWebDriver.until(EC.presence_of_element_located((By.XPATH,"//textarea[@id='reply']"))) \
        .send_keys("XYZ")    
    except TimeoutException as ex:
      print(f"Element for sending the message not found - skipped...")
      continue

    driver.execute_script("window.scrollTo(0, 10000)")               
  
    # getting some data with requests
    ua = UserAgent()
    userAgent = ua.random
    HEADERS = {"User-Agent": userAgent}
    page = requests.get (link, headers=HEADERS)
    soup = BeautifulSoup (page.content, "html.parser")

    # working with beautiful soap to get data
    tmpDIV = soup.find("div", {"id": "line"})   
    tmpDIV = soup.find_all("div", {"class": "main"})                
    tmpSPAN = soup.find("span", string=" Geburtsdatum: ")    
    tmpDIV = soup.find("div", class_=re.compile("RacePage_raceInfoContainer"))         
    tmpA = tmpDIV.find_all("a")   
    link = tmpA[0].get("href")
    soup.select("div.class1.class2") 
    soup.find("button", string="In-App Purchases")  
    soup.find("dt", string=re.compile("Industry"))  
    print(repr(link))
  
    # writing back data using xlwings
    tmpRow = [link, a, b, c, d()()()]    
    ws.range(f"A{rowNum}:K{rowNum}").value = None
    ws.range(f"A{rowNum}:K{rowNum}").value = tmpRow
    ws.range(f"A{rowNum}:K{rowNum}").api.WrapText = False    
    print(f"{link} written to row {rowNum}...")
    rowNum += 1
    input("Press!")
  
  driver.quit()
  wb.save()
  print(f"Program finished - pls press <enter> to close the window...") 
  time.sleep(5)   