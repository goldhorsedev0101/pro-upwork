# Read searchwords and locations from excel, search with selenium on indeed.com
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
from urllib.parse import quote


if __name__ == '__main__':
  SAVE_INTERVAL = 5
  WAIT = 3
  path = os.path.abspath(os.path.dirname(sys.argv[0])) 

  fn = os.path.join(path, "dataIndeed.xlsx")
  wb = xw.Book (fn)
  ws = wb.sheets[0]
  wsInp = wb.sheets[1]
  existData = ws.range ("A2:Z5000").value
  existData = [x for x in existData if x[0] != None]
  rowNum = len(existData) + 2
  existLinks = [(x[1], x[2], x[3], x[4], x[5]) for x in existData]
  searchLinks = wsInp.range ("A2:A1000").value
  searchLinks = [x for x in searchLinks if x != None]
  
  if wsInp["D1"].value != None and wsInp["D1"].value in ["J","j","Y","y"]:
    DETAIL_DESC = True
  else:
    DETAIL_DESC = False      

  print(f"Checking Browser driver...")
  os.environ['WDM_LOG_LEVEL'] = '0' 
  ua = UserAgent(verify_ssl=False)
  userAgent = ua.random
  options = Options()
  options.add_argument('--headless')
  options.add_argument("start-maximized")
  options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})    
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  options.add_experimental_option('useAutomationExtension', False)
  options.add_argument('--disable-blink-features=AutomationControlled')
  options.add_argument(f'user-agent={userAgent}')   
  srv=Service(ChromeDriverManager().install())

  for sLink in searchLinks:
    print(f"Working for searchLink {sLink}")
    driver = webdriver.Chrome (service=srv, options=options)   
    waitWebDriver = WebDriverWait (driver, 10)      
    for pageNr in range(0,1000,20):
      if pageNr > 100:
        print(f"Program stopped - in the trial version only the first 5 result sites will be scraped")
        sys.exit()
      workLink = f"{sLink}&start={pageNr}"    
      # driver.minimize_window()        # optional
      print(f"Working for {workLink}")
      # input("Press!")
      driver.get (workLink)       
      driver.execute_script("window.scrollTo(0, 10000)") 
      time.sleep(WAIT) 
      soup = BeautifulSoup (driver.page_source, 'html.parser')       
      tmpDIV = soup.find_all("div", {"class": "slider_item"}) 
      print(f"{len(tmpDIV)} elements found")
      nothingFound = True
      for elem in tmpDIV:
        # print(elem.prettify())
        # input("Press!")
        tmpH2 = elem.find("h2", {"class": "jobTitle"})
        tmpTitle = tmpH2.find("a").text.strip()
        tmpCompany = elem.find("span", {"class": "companyName"}).text.strip()
        tmpLocation = elem.find("div", {"class": "companyLocation"}).text.strip()

        tmpJobType = elem.find("svg", {"aria-label": "Job type"})
        if tmpJobType != None:
          tmpJobType = tmpJobType.parent.text.strip()

        tmpDate = elem.find("span", {"class": "date"}).text.strip()

        checkKey = (tmpTitle, tmpCompany, tmpLocation, tmpJobType, tmpDate)
        if checkKey in existLinks:
          print(f"{tmpTitle} / {tmpCompany} is allready in excel - skipped...")
          continue
        nothingFound = False
        existLinks.append(checkKey)

        # tmpSalary = "N/A"
        # tmpDIV = elem.find("div", {"class": "salary-snippet-container"})
        # if tmpDIV == None:
        #   tmpDIV = elem.find("div", {"class": "metadata estimated-salary-container"})
        # if tmpDIV != None:
        #   tmpSalary = tmpDIV.text.strip()

        # tmpShift = elem.find("svg", {"aria-label": "Shift"})
        # if tmpShift != None:
        #   tmpShift = tmpShift.parent.text.strip()

        tmpSnippet = []
        tmpDIV = elem.find("div", {"class": "job-snippet"})
        tmpLI = tmpDIV.find_all("li")
        for e in tmpLI:
          tmpSnippet.append(e.text.strip())
        tmpSnippet = "\n".join(tmpSnippet)

        tmpLink = tmpH2.find("a").get("href")
        tmpLink = f"https://at.indeed.com{tmpLink}"

        # tmpRow = [workLink, tmpTitle, tmpCompany, tmpLocation, tmpSalary, tmpJobType, 
        #           tmpShift, tmpDate, tmpLink, tmpSnippet]    
        if DETAIL_DESC:
          driver.get (tmpLink)
          time.sleep(WAIT) 
          soup = BeautifulSoup (driver.page_source, 'html.parser')               
          tmpDesc = soup.find("div", {"id": "jobDescriptionText"}).text.strip()
          tmpRow = [workLink, tmpTitle, tmpCompany, tmpLocation, tmpJobType, tmpDate, tmpLink, tmpSnippet, tmpDesc]              
        else:
          tmpRow = [workLink, tmpTitle, tmpCompany, tmpLocation, tmpJobType, tmpDate, tmpLink, tmpSnippet]    
        # for e in tmpRow:
        #   print(e)
        # exit()

        ws.range(f"A{rowNum}:K{rowNum}").value = None
        ws.range(f"A{rowNum}:K{rowNum}").value = tmpRow
        ws.range(f"A{rowNum}:K{rowNum}").api.WrapText = False    
        print(f"{tmpLink} written to row {rowNum}...")
        rowNum += 1
        # input("Press!") 
      if nothingFound:
        break
    driver.quit()
  wb.save()
  print(f"Program finished - pls press <enter> to close the window...") 
  time.sleep(5)   