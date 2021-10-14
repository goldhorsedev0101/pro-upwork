# pyinstaller --onefile --hidden-import pycountry --exclude-module matplotlib scrapeBetsTAB.py
from bs4.element import TemplateString
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sys import platform
import os, sys
import xlwings as xw
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


if __name__ == '__main__':
  SAVE_INTERVAL = 5
  WAIT = 3
  FN = "ScrapeBets.xlsx"
  path = os.path.abspath(os.path.dirname(sys.argv[0]))  
  HEADERS = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }

  fn = path + "/" + FN
  wb = xw.Book (fn)
  ws = wb.sheets["Bets"]

  # check waiting time
  if ws["F1"].value != None:
    WAIT = ws["F1"].value

  # check next free row
  rows = ws.range ("A3:A2000").value
  for idx,cont in enumerate(rows):
      if cont == None:
          nextRow = int(idx+3)
          break 

  ### tab.com I ### 
  WAIT = 1
  link = "https://www.racingandsports.com/form-guide/thoroughbred/australia"  
  print(f"Scrape data from: {link}")

  options = Options()
  # options.add_argument('--headless')
  options.add_experimental_option ('excludeSwitches', ['enable-logging'])
  options.add_argument("start-maximized")
  options.add_argument('window-size=1920x1080')								  
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-gpu')  
  path = os.path.abspath (os.path.dirname (sys.argv[0]))
  if platform == "win32": cd = '/chromedriver.exe'
  elif platform == "linux": cd = '/chromedriver'
  elif platform == "darwin": cd = '/chromedriver'
  driver = webdriver.Chrome (path + cd, options=options)
  driver.get (link)
  time.sleep (WAIT)

  soup = BeautifulSoup (driver.page_source, 'html.parser')
  time.sleep (WAIT)
  tmpA = soup.find_all("a")
  tmpRaces = []
  tday = str(datetime.today().date() + timedelta(days = 1))
  for i in tmpA:
    tmpi = i.get("href") 
    if tmpi != None \
      and "https://www.racingandsports.com/form-guide/thoroughbred/australia/" in tmpi \
      and tmpi[-2] != "R" \
      and tday in tmpi \
      and f"{tmpi}/race-tips" not in tmpRaces:
        tmpRaces.append(f"{tmpi}/race-tips")

  for raceLink in tmpRaces:
    print(f"Working on race: {raceLink}...")
    tmpLocation = raceLink.split("/")[-3].capitalize()
    driver.get (raceLink)
    soup = BeautifulSoup (driver.page_source, 'html.parser')
    tmpRaceNumbers = soup.findAll("div", {'class':['tab-pane', 'meeting-tab']})
    for idxRaceNum, raceNum in enumerate(tmpRaceNumbers):
      ergList = []
      tmpHeaders = raceNum.findAll("input")
      for i in tmpHeaders:
        if [f"RAS {i.get('value')}"] not in ergList:
          ergList.append([f"RAS {i.get('value')}"])
            
      tmpDiv = raceNum.find("tbody")
      tmpRows = tmpDiv.findAll("tr")
      for e in tmpRows:
        tmpTipps = e.findAll("td")
        for i, tipp in enumerate(tmpTipps):
          ergList[i].append(tmpTipps[i].text.strip())

      # write tipps to excel
      for elem in ergList:
        ws["A" + str (nextRow)].value = elem[0]                  
        ws["B" + str (nextRow)].value = datetime.today()
        ws["C" + str (nextRow)].value = tmpLocation
        ws["D" + str (nextRow)].value = idxRaceNum + 1
        if len(elem) > 1:
          ws["E" + str (nextRow)].value = elem[1]
        if len(elem) > 2:
          ws["F" + str (nextRow)].value = elem[2]
        if len(elem) > 3:
          ws["G" + str (nextRow)].value = elem[3]
        nextRow += 1
        if nextRow % SAVE_INTERVAL == 0:
            wb.save (fn)
            # wb.close()
            print ("Saved to disk...")
     

  wb.save (fn)
  # wb.close()
  print ("Saved to disk...")