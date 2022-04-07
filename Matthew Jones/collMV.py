from bs4.element import TemplateString
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from sys import platform
import os, sys
import xlwings as xw
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

if __name__ == '__main__':
  SAVE_INTERVAL = 5
  WAIT = 3
  FN = "data.xlsx"
  path = os.path.abspath(os.path.dirname(sys.argv[0]))  
  rowNum = 2

  fn = path + "/" + FN
  wb = xw.Book (fn)
  ws = wb.sheets[0]
  existData = ws.range ("A2:Z5000").value
  existMatchLinks = [x[10] for x in existData if x[0] != None]
  rowNum = len(existMatchLinks) + 2   
   
  print(f"Checking chromedriver...")
  os.environ['WDM_LOG_LEVEL'] = '0' 
  ua = UserAgent()
  userAgent = ua.random
  options = Options()
  options.add_argument('--headless')
  options.add_experimental_option ('excludeSwitches', ['enable-logging'])
  options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})    
  options.add_argument("--disable-infobars")
  options.add_argument("--disable-extensions")  
  options.add_argument("start-maximized")
  options.add_argument('window-size=1920x1080')								  
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-gpu')  
  options.add_argument(f'user-agent={userAgent}') 	
  srv=Service(ChromeDriverManager().install())
  try:      # try it with automatic download
    driver = webdriver.Chrome (service=srv, options=options)    
  except:   # if not possible use manual download from the chromedriver
    path = os.path.abspath (os.path.dirname (sys.argv[0]))
    if platform == "win32": cd = '/chromedriver.exe'
    elif platform == "linux": cd = '/chromedriver'
    elif platform == "darwin": cd = '/chromedriver'
    srv=Service(path + cd)
    driver = webdriver.Chrome (service=srv, options=options)        
  waitWebDriver = WebDriverWait (driver, 10)         
  
  listLeagues = ["https://www.transfermarkt.co.uk/premier-league/startseite/wettbewerb/GB1",
                "https://www.transfermarkt.co.uk/a-league-men/startseite/wettbewerb/AUS1"
                ]
  listYears = ["2020","2021"]

  for league in listLeagues:
    for year in listYears:
      link = f"{league}/plus/?saison_id={year}"
      tmpLeague = link.split("/")[3]
      tmpSeason = f"{year}/{str(int(year)+1)}"
      print(f"Working for {tmpLeague} with link {link}...")

      # driver.minimize_window()        # optional
      driver.get (link)       
      time.sleep(WAIT) 
      soup = BeautifulSoup (driver.page_source, 'html.parser')  
      tmpID = soup.find("div", {"id": "yw1"}) 
      tmpBODY = tmpID.find("tbody")
      tmpTR = tmpBODY.find_all("tr")
      for idx, elem in enumerate(tmpTR):
        tmpLink = elem.find("a").get("href")
        tmpLink = f"https://www.transfermarkt.co.uk{tmpLink}"
        tmpLink = tmpLink.replace("startseite","spielplandatum")
        print(f"Working for link {tmpLink}...")   
        driver.get (tmpLink)  
        time.sleep(WAIT) 
        soup = BeautifulSoup (driver.page_source, 'html.parser')     
        tmpName = soup.find("h1").text.strip()
        tmpDIV = soup.find("div", {"class": "responsive-table"}) 
        tmpTBODY = tmpDIV.find("tbody")
        tmpTR = tmpTBODY.find_all("tr")
        tmpComp = None
        for elemTR in tmpTR:
          classInfo = elemTR.get("style")
          if classInfo == None:
            tmpComp = elemTR.text.strip()
          else:
            tmpTD = elemTR.find_all("td")
            tmpRound = tmpTD[0].text.strip()
            tmpDate = tmpTD[1].text.strip()
            tmpTime = tmpTD[2].text.strip()
            tmpVenue = tmpTD[3].text.strip()
            tmpOpponent = tmpTD[6].find("a").get("title")
            tmpResult = tmpTD[9].text.strip()
            tmpMatchLink = tmpTD[9].find("a").get("href")
            tmpMatchLink = f"https://www.transfermarkt.co.uk{tmpMatchLink}"
            
            if tmpMatchLink in existMatchLinks:
              print(f"{tmpMatchLink} allready in excel - skipped...")
              continue
            existMatchLinks.append(tmpMatchLink)        
            print(f"Working on MatchLink: {tmpMatchLink}")
            
            tmpMV1 = tmpMV2 = linkLineUps = None
            TMPWAIT = WAIT          
            while True and TMPWAIT < 5:          
              driver.get (tmpMatchLink)  
              time.sleep(TMPWAIT) 
              soup = BeautifulSoup (driver.page_source, 'html.parser') 
              tmpLI = soup.find("li", {"id": "line-ups"})
              if tmpLI != None:
                break
              else:
                TMPWAIT += 1
                print(f"Reading again with increased waiting time {TMPWAIT}...")                                                       
            if tmpLI != None:       
              linkLineUps = tmpLI.find("a").get("href")
              linkLineUps = f"https://www.transfermarkt.co.uk{linkLineUps}"
              print(f"Working on LineUps: {linkLineUps}...")         
              TMPWAIT = WAIT
              while True:          
                driver.get (linkLineUps)         
                time.sleep(TMPWAIT) 
                soup = BeautifulSoup (driver.page_source, 'html.parser')
                tmpDIV = soup.find_all("div", {"class": "table-footer"}) 
                if len(tmpDIV) > 0:
                  break
                else:
                  TMPWAIT += 1
                  print(f"Reading again with increased waiting time {TMPWAIT}...")                       
              tmpMV1 = tmpDIV[0].find_all("td")[3].text.strip().replace("Total MV:","").strip()
              tmpMV2 = tmpDIV[1].find_all("td")[3].text.strip().replace("Total MV:","").strip()

            if tmpVenue == "A":
              tmpHomeTeam = tmpOpponent
              tmpAwayTeam = tmpName
            elif tmpVenue == "H":
              tmpHomeTeam = tmpName
              tmpAwayTeam = tmpOpponent
            else:
              print(f"Stop Working - tmpVenue wrong with: {tmpVenue}")
              exit()

            # print(tmpName)
            # print(tmpRound)
            # print(tmpDate)
            # print(tmpTime)
            # print(tmpVenue)
            # print(tmpOpponent)
            # print(tmpResult)
            # print(tmpMV1)
            # print(tmpMV2)   
            # print(tmpLink)
            # print(linkLineUps)

            tmpRow = [tmpSeason, tmpDate, tmpTime, tmpLeague, tmpComp, tmpHomeTeam, 
                      tmpAwayTeam, tmpMV1, tmpMV2, tmpLink, tmpMatchLink, linkLineUps]  
            print(tmpRow)
            # if tmpRow[:5] in existMatches:
            #   print(f"{tmpRow[:5]} allready in existMatches - skipped...")
            #   continue
            # else:
            #   existMatches.append(tmpRow[:5])
            ws.range(f"A{rowNum}:L{rowNum}").value = None
            ws.range(f"A{rowNum}:L{rowNum}").value = tmpRow
            print(f"{link} written to row {rowNum}...")
            rowNum += 1

            # input("Press!")     

    wb.save()