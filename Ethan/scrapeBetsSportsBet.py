# pyinstaller --onefile --hidden-import pycountry --exclude-module matplotlib scrapeBetsSportsBet.py
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
  WAIT = 0.5
  FN = "ScrapeBets.xlsx"
  path = os.path.abspath(os.path.dirname(sys.argv[0]))  
  HEADERS = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }

  fn = path + "/" + FN
  wb = xw.Book (fn)
  ws = wb.sheets["Bets"]

  # check waiting time
  if ws["B1"].value != None:
    WAIT = ws["B1"].value

  # check next free row
  rows = ws.range ("A3:A2000").value
  for idx,cont in enumerate(rows):
      if cont == None:
          nextRow = int(idx+3)
          break
  
  ### sportbet.com ###
  link = "https://www.sportsbet.com.au/racing-schedule/horse-racing"
  page = requests.get (link, headers=HEADERS)
  soup = BeautifulSoup (page.content, "html.parser")
  time.sleep(WAIT)

  ergLinks = []
  tmpHREFs = soup.find_all("a")
  for i,e in enumerate(tmpHREFs):
    e = e.get("href")
    if "horse-racing" in e and "australia-nz" in e:
      ergLinks.append("https://www.sportsbet.com.au" + e)

  ergDetailLinks = []
  for eLinks in ergLinks:
    print(f"Working on place {eLinks}...")
    page = requests.get (eLinks, headers=HEADERS)
    soup = BeautifulSoup (page.content, "html.parser")
    time.sleep(WAIT)
    tmpHREFs = soup.find_all("a")
    for i,e in enumerate(tmpHREFs):
      e = e.get("href")
      if "horse-racing" in e and "australia-nz" in e and len(e.split("/")) == 5:
        ergDetailLinks.append("https://www.sportsbet.com.au" + e)
    # break

  options = Options()
  options.add_argument('--headless')
  options.add_experimental_option ('excludeSwitches', ['enable-logging'])
  options.add_argument("start-maximized")
  path = os.path.abspath (os.path.dirname (sys.argv[0]))

  for eLink in ergDetailLinks:
    print(f"Working on race {eLink}...")
    tmpTrack = eLink.split("/")
    track = tmpTrack[5].capitalize()
    race = tmpTrack[6].split("-")[1]
  
    if platform == "win32": cd = '/chromedriver.exe'
    elif platform == "linux": cd = '/chromedriver'
    elif platform == "darwin": cd = '/chromedriver'
    driver = webdriver.Chrome (path + cd, options=options)
    driver.get (eLink)  # Read link
    time.sleep (WAIT)  # Wait till the full site is loaded
    soup = BeautifulSoup (driver.page_source, 'html.parser')  # Read page with html.parser
    time.sleep (WAIT)  
    selection = soup.find("span", {"data-automation-id": "expert-tips-list"})
    selection = list(selection.text.split(" ")[1].split("-"))
    selection = list(map(int,selection))
    # print(f"DEBUG - {track, race, selection}")
    print(f"Write to excel - {track, race, selection}...")

    ws["A" + str (nextRow)].value = "Sportsbet"
    ws["B" + str (nextRow)].value = datetime.today ()
    ws["C" + str (nextRow)].value = track
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
    
    driver.quit()

    nextRow += 1
    if nextRow % SAVE_INTERVAL == 0:
        wb.save (fn)
        # wb.close()
        print ("Saved to disk...")