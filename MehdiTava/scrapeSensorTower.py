# pyinstaller --onefile --exclude-module matplotlib scrapeAppleAdd.py

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys, os
import xlwings as xw
import re
from fake_useragent import UserAgent
from datetime import datetime, timedelta

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


SAVE_INTERVAL = 5
WAIT = 1
COOLDOWN = 30
FN = "ScrapeSensorTower.xlsx"
path = os.path.abspath(os.path.dirname(sys.argv[0]))
fn = path + "/" + FN
wb = xw.Book (fn)
ws = wb.sheets["Apps"] 
ws2 = wb.sheets["Parameters"] 
ws3 = wb.sheets["Apple Categories"] 
ws4 = wb.sheets["Google Categories"] 

#read parameters
if ws2["B1"].value != None:
  WAIT = float(ws2["B1"].value)

if ws2["B2"].value != None:
  COOLDOWN = int(ws2["B2"].value)

if ws2["B3"].value not in ["",None] and ws2["B3"].value.upper() == "GOOGLE":
  STORE1 = "android"
  STORE2 = "mobile"
  workCategories = ws4.range ("A1:A200").value
  workCategories = [x for x in workCategories if x != None]    
elif ws2["B3"].value not in ["",None] and ws2["B3"].value.upper() == "APPLE":
  STORE1 = "ios"
  STORE2 = "iphone"
  workCategories = ws3.range ("A1:A200").value
  workCategories = [x for x in workCategories if x != None]  
else:
  print(f"Pls provde valid Apple/Google parameter in B3... - program ended...")
  exit()

if ws2["B4"].value not in ["",None]:
  COUNTRY = ws2["B4"].value.lower()
else:
  print(f"Pls provde valid Country parameter in B4... - program ended...")
  exit()

if ws2["B5"].value not in ["",None] and ws2["B5"].value.upper() == "ALL":
  CATEGORY = "ALL"

else:
  CATEGORY = "SELECT"
  workCategories = []
  workCategories = ws2.range ("B8:B200").value
  workCategories = [x for x in workCategories if x != None]

if ws2["B6"].value not in ["",None] and ws2["B6"].value.upper() in ["YES","Y"]:
  OVERWRITE = True
else:
  OVERWRITE = False

existLinks = ws.range ("B2:B100000").value
existLinks = [x for x in existLinks if x != None]
nextFreeRow = len(existLinks) + 2

for idxCat, elemCat in enumerate(workCategories):
  
  # tday = datetime.today().date()	
  link = f"https://sensortower.com/{STORE1}/rankings/top/{STORE2}/{COUNTRY}/{elemCat}"
  print(f"Working on category {elemCat} with link {link}...")

  options = Options()
  options.add_argument("--window-size=1920x800")
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-gpu')   
  options.add_experimental_option ('excludeSwitches', ['enable-logging'])      
  options.add_argument('--headless')
  ua = UserAgent()
  userAgent = ua.random
  options.add_argument(f'user-agent={userAgent}')                

  path = os.path.abspath (os.path.dirname (sys.argv[0]))
  if sys.platform == "win32": cd = '/chromedriver.exe'
  elif sys.platform == "linux": cd = '/chromedriver'
  elif sys.platform == "darwin": cd = '/chromedriver'
  driver = webdriver.Chrome (path + cd, options=options)


  driver.get(link)
  time.sleep(WAIT)
  driver.set_window_size(600,1000)
  wait = WebDriverWait(driver, 10)

  tmpElem = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
  tmpElem.click() 

  tmpElem = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Top Grossing']")))
  driver.execute_script('arguments[0].click();', tmpElem)

  # tmpElem = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Top Grossing']")))
  # tmpElem.click() 

  lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
  match=False
  while(match==False):
      lastCount = lenOfPage
      time.sleep(WAIT)
      lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
      if lastCount==lenOfPage:
          match=True

  soup = BeautifulSoup (driver.page_source, 'html.parser')
  tmpLinks = []
  for e in soup.find_all("a"):
    tmpHREF = e.get("href")
    if tmpHREF == None:
      continue
    if tmpHREF[-1] == "/":
      continue
    if "/app/" not in tmpHREF:
      continue
    if f"https://sensortower.com{tmpHREF}" in tmpLinks:
      continue

    tmpLinks.append("https://sensortower.com" + tmpHREF)
  driver.quit()


  # working on apps for one category and country
  for idx,elem in enumerate(tmpLinks): 
    # elem = "https://sensortower.com/android/us/intuit-inc/app/quickbooks-self-employed-mileage-tracker-and-taxes/com.intuit.qbse/overview"

    if elem in existLinks:
      if OVERWRITE:
        rowIDX = existLinks.index(elem) + 2
      else:
        print(f"No overwrite mode - link {elem} allready in excel - skipped...")
        continue
    else:
      rowIDX = nextFreeRow
      nextFreeRow += 1

    print(f"Working on element nr {idx+1} from {len(tmpLinks)} in row {rowIDX} with link {elem}...")    

    while True:
      ua = UserAgent()
      userAgent = ua.random

      options.add_argument(f'user-agent={userAgent}')      
      driver = webdriver.Chrome (path + cd, options=options)      
      driver.get(elem)
      time.sleep(WAIT)  
      driver.set_window_size(1800,1000)
      soup = BeautifulSoup (driver.page_source, 'html.parser')
      tmpElem = soup.find("div", {"class": "app-view-meta-header-container"})
      if tmpElem != None:
        break
      else:
        driver.quit()
        print(f"No data for element - probably cooldown necessary......")
        for i in range (COOLDOWN, 0, -1):  # Delay for 30 seconds - countdown in one row
            sys.stdout.write (str (i) + ' ')  # Countdown output
            sys.stdout.flush ()
            time.sleep (1)
            if i == 1:
                print("\n")        

    tmpElem = tmpElem.findAll("span")
    listMetaHeader = []
    for i in tmpElem:
      i = i.text.strip()
      if len(i) > 0 and "\n" not in i and i not in listMetaHeader:
        listMetaHeader.append(i)    
    appMetaName = listMetaHeader[0]
    if "Category" in listMetaHeader:
      appMetaCat = listMetaHeader[listMetaHeader.index("Category")]
    else:
      appMetaCat = "N/A"
    if "IAP?" in listMetaHeader:
      appMetaIAP = listMetaHeader[listMetaHeader.index("IAP?")]
    else:
      appMetaIAP = "N/A"
    if "Price" in listMetaHeader:
      appMetaPrice = listMetaHeader[listMetaHeader.index("Price")]
    else:
      appMetaPrice = "N/A"
    if "Publisher" in listMetaHeader:
      appMetaPublisher = listMetaHeader[listMetaHeader.index("Publisher")]
    else:
      appMetaPublisher = "N/A"
    if "View in Store" in listMetaHeader:
      appMetaStore = listMetaHeader[listMetaHeader.index("View in Store")]
    else:
      appMetaStore = "N/A"
    if "Country / Region" in listMetaHeader:
      appMetaCountry = listMetaHeader[listMetaHeader.index("Country / Region")]
    else:
      appMetaCountry = "N/A"

    tmpRevDownlDIV = soup.find(id="app-revenue-downloads")
    tmpElem = tmpRevDownlDIV.findAll(["span","h3"])
    listRevDownl= []
    for i in tmpElem:
      i = i.text.strip()
      if "Worldwide" not in i:
        listRevDownl.append(i)
    if "Downloads" in listRevDownl:
      appDownloads = listRevDownl[listRevDownl.index("Downloads")]
    else:
      appDownloads = "N/A"
    if "Revenue" in listRevDownl:
      appRevenue = listRevDownl[listRevDownl.index("Revenue")]
    else:
      appRevenue = "N/A"

    # r = requests.get(elem).text
    # try:
    #   appDownloads = re.findall(r'"downloads":"([^"]*)"', r)[0].strip()
    #   # print(appDownloads)
    #   # print(type(appDownloads))
    #   appDownloads = appDownloads.replace("\u003c","<")
    #   # print(appDownloads)
    #   # print(type(appDownloads))
    # except:
    #   appDownloads = "N/A"
    # try:
    #   appRevenue = re.findall(r'"revenue":"([^"]*)"', r)[0].strip()
    # except:
    #   appRevenue = "N/A"

    tmpElem = soup.find("div", {"class": "visibility-score-body"})
    if tmpElem != None:
      appVisibScore = tmpElem.text.strip()
    else:
      appVisibScore = "N/A"

    tmpRatingDIV = soup.find(id="app-profile-ratings")
    listRating = []
    listSumRating = []  
    if tmpRatingDIV != None:
      tmpElem = tmpRatingDIV.findAll("span", {"class": "rating-count"})
      for i in tmpElem:
        listRating.append(i.text.strip())
      appRating1 = listRating[0]
      appRating2 = listRating[1]
      appRating3 = listRating[2]
      appRating4 = listRating[3]
      appRating5 = listRating[4]

      tmpElem = tmpRatingDIV.find("div", {"class": "current-and-overall-rating-count-container"})
      tmpElem = tmpElem.findAll("span")  
      for i in tmpElem:
        if len(i.text.strip()) > 0:
          listSumRating.append(i.text.strip())
      appRatingCount = listSumRating[1]
    else:
      appRating1 = appRating2 = appRating3 = appRating4 = appRating5 = appRatingCount = "N/A"

    tmpVersionDIV = soup.find(id="app-versions")
    tmpElem = tmpVersionDIV.findAll("td")
    listVersions = []
    for i in tmpElem:
      i = i.text.strip()
      if len(i) > 1:
        listVersions.append(i)

    tmpAboutDIV = soup.find(id="about-app")
    tmpElem = tmpAboutDIV.findAll("td")
    listAbout = []
    for i in tmpElem:
      i = i.text.strip().replace(":","")
      if len(i) > 1:
        listAbout.append(i)
    if "Support URL" in listAbout:
      appSupport = listAbout[listAbout.index("Support URL")]
    else:
      appSupport = "N/A"
    if "Categories" in listAbout:
      appCategories = listAbout[listAbout.index("Categories")].replace("\n\n\n\n"," ")
    else:
      appCategories = "N/A"
    if "Developer Website" in listAbout:
      appDeveloperSite = listAbout[listAbout.index("Developer Website")]
    else:
      appDeveloperSite = "N/A"
    if "Developer Website" in listAbout:
      appDeveloperSite = listAbout[listAbout.index("Developer Website")]
    else:
      appDeveloperSite = "N/A"


    tmpInAppPurchasesDIV = soup.find(id="top-in-app-purchases")    
    if STORE1 == "ios":
      tmpElem = tmpInAppPurchasesDIV.findAll("td")
      listInAppPurchases= []
      for i in tmpElem:
        i = i.text.strip()
        if len(i) > 1:
          listInAppPurchases.append(i)
    else:
      tmpElem = tmpInAppPurchasesDIV.findAll("span")
      listInAppPurchases= []
      for i in tmpElem:
        i = i.text.strip()
        listInAppPurchases.append(i)      

    # print(listMetaHeader)
    # print(listRevDownl)
    # print(appVisibScore) 
    # print(listRating)
    # print(listSumRating)
    # print(listVersions)
    # print(listAbout)
    # print(listInAppPurchases)
    # print(userAgent)
    # print(elem)
    # print("\n")

    ws["A" + str (rowIDX)].value = datetime.today () 
    ws["B" + str (rowIDX)].value = elem
    ws["C" + str (rowIDX)].value = str(listMetaHeader)
    ws["D" + str (rowIDX)].value = str(listRevDownl)
    ws["E" + str (rowIDX)].value = appVisibScore
    ws["F" + str (rowIDX)].value = str(listRating)
    ws["G" + str (rowIDX)].value = appRatingCount
    ws["H" + str (rowIDX)].value = str(listVersions)
    ws["I" + str (rowIDX)].value = str(listAbout)
    ws["J" + str (rowIDX)].value = str(listInAppPurchases)

    if idx % SAVE_INTERVAL == 0:
      wb.save (fn)
      print ("Saved to disk...")

    driver.quit()

















