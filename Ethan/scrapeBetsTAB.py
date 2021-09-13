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
  if ws["D1"].value != None:
    WAIT = ws["D1"].value

  # check next free row
  rows = ws.range ("A3:A2000").value
  for idx,cont in enumerate(rows):
      if cont == None:
          nextRow = int(idx+3)
          break 

  ### tab.com I ### 
  WAIT = 1
  link = "https://www.tab.com.au/racing/meetings/tomorrow"  
  print(f"Scrape data from: {link}")

  options = Options()
  options.add_argument('--headless')
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

  # have only to do this cause this popsup in the austrian version - not the australian it seems
  try:
    driver.find_element(By.XPATH, '//button[text()="Select"]').click()    
    print(f"Skip welcome window...") 
  except:
    print(f"Skipping welcome window not necessary / possible...")

  driver.get ("https://www.tab.com.au/") 
  time.sleep (WAIT)
  driver.back()
  time.sleep (WAIT)         
  soup = BeautifulSoup (driver.page_source, 'html.parser')
  time.sleep (WAIT)

  tmpDIVs = soup.find("div", {"class": "_1k65463"})
  tmpDIVs2 = tmpDIVs.find_all("div", {"class": "_1xxbwka"})
  # print(len(tmpDIVs2))
  countRaces = 0
  tmpListRaces = []
  for i,e in enumerate(tmpDIVs2):
    tmpSPANs = e.find_all("a")
    for e2 in tmpSPANs:
      tmpListRaces.append(f"https://www.tab.com.au{e2.get('href')}")

  for e in tmpListRaces:
    track = e.split("/")[5]
    race = e.split("/")[-1]
    racesFinal = []
    print(f"Working on {e}")
    driver.get(e)
    time.sleep (WAIT)  
    try:
      # driver.find_element(By.XPATH, '//button[@class="_128kfdm "]').click()
      driver.find_element(By.XPATH, '//button[@data-testid="tabx-tabs-tab"]').click()      
      print(f"Tipps button pressed...")
    except:
      print(f"No tipps button found - continuing...")
      continue
    soup = BeautifulSoup (driver.page_source, 'html.parser')
    time.sleep (WAIT)  
    # find divs with the 4 tipps / jockeys in it  
    tmpDIVs = soup.find_all("div", {"class": "_1bl97dk"})
    for elem in tmpDIVs:
      # read header of tip
      textTip = elem.find("h1", {"class": "_maswhi"}).text
      # read single jokey / tipps
      tmpDIVs2 = elem.find_all("div", {"class": "_bg6a1o"})
      selection = []
      for elem2 in tmpDIVs2:
        tmpSPAN = elem2.find_all("span")
        nrJokey = tmpSPAN[0].text.replace(".","").replace(" ","").strip()
        selection.append(nrJokey)
      if f"{track} {race} {textTip}" not in racesFinal:
        racesFinal.extend([f"{track} {race} {textTip}",selection])  
        print(f"Writing {track} {race} {textTip} {selection}...")
        ws["A" + str (nextRow)].value = f"TAB {textTip}"
        ws["B" + str (nextRow)].value = datetime.today()
        ws["C" + str (nextRow)].value = track.lower().capitalize()
        ws["D" + str (nextRow)].value = race
        if len(selection) > 0:
          ws["E" + str (nextRow)].value = selection[0]
        if len(selection) > 1:
          ws["F" + str (nextRow)].value = selection[1]
        if len(selection) > 2:
          ws["G" + str (nextRow)].value = selection[2]
        if len(selection) > 3:
          ws["H" + str (nextRow)].value = selection[3]
        if len(selection) > 4:
          ws["H" + str (nextRow)].value = selection[4]
        if len(selection) > 5:
          ws["H" + str (nextRow)].value = selection[5]
      
        nextRow += 1
        if nextRow % SAVE_INTERVAL == 0:
            wb.save (fn)
            # wb.close()
            print ("Saved to disk...")

  for i in racesFinal:
    print(i)