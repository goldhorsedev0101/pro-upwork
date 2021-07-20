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

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


SAVE_INTERVAL = 5
WAIT = 10
COOLDOWN = 60
startRow = 2
FN = "ScrapeSensorTower.xlsx"
path = os.path.abspath(os.path.dirname(sys.argv[0]))
fn = path + "/" + FN
wb = xw.Book (fn)
ws = wb.sheets["Apps"] 
ws2 = wb.sheets["Parameters"] 
# read stocks for working on
maxRow = 100000#
workCategories = ws.range ("B6:B200").value
workCategories = [x for x in workCategories if x != None]

#read parameters
if ws2["B1"].value != None:
  WAIT = int(ws2["B1"].value)

if ws2["B2"].value not in ["",None] and ws2["B2"].value.upper() == "GOOGLE":
  STORE = "GOOGLE"
elif ws2["B2"].value not in ["",None] and ws2["B2"].value.upper() == "APPLE":
  STORE = "APPLE"
else:
  print(f"Pls provde valid Apple/Google parameter in B2... - program ended...")
  exit()

if ws2["B3"].value not in ["",None]:
  COUNTRY = ws2["B3"].value.lower()
else:
  print(f"Pls provde valid Country parameter in B3... - program ended...")
  exit()

if ws2["B4"].value not in ["",None] and ws2["B2"].value.upper() == "ALL":
  CATEGORY = "ALL"
else:
  CATEGORY = "SELECT"

idxStock = 2

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


link = "https://sensortower.com/ios/rankings/top/iphone/us/games?date=2021-07-12"
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

print(len(tmpLinks))

for idx,elem in enumerate(tmpLinks):
  # page = requests.get (elem, headers=HEADERS)
  # soup = BeautifulSoup (page.content, "html.parser")
  # tmpElem = soup.find("div", {"class": "info-item category-item"})
  # tmpElem = soup.find_all("div", class_="info-item category-item")
  # print(tmpElem)

  # elem = "https://sensortower.com/ios/us/disney/app/espn-live-sports-scores/317469184/overview"


  print(f"Working on element {idx+1} with link {elem}...")
  
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

  r = requests.get(elem).text
  try:
    appDownloads = re.findall(r'"downloads":"([^"]*)"', r)[0].strip()
    appDownloads = str(appDownloads).replace("\u003c","<")
  except:
    appDownloads = "N/A"
  try:
    appRevenue = re.findall(r'"revenue":"([^"]*)"', r)[0].strip()
  except:
    appRevenue = "N/A"

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

    tmpElem = tmpRatingDIV.find("div", {"class": "current-and-overall-rating-count-container"})
    tmpElem = tmpElem.findAll("span")  
    for i in tmpElem:
      if len(i.text.strip()) > 0:
        listSumRating.append(i.text.strip())

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
    i = i.text.strip()
    if len(i) > 1:
      listAbout.append(i)

  tmpInAppPurchasesDIV = soup.find(id="top-in-app-purchases")
  tmpElem = tmpInAppPurchasesDIV.findAll("td")
  listInAppPurchases= []
  for i in tmpElem:
    i = i.text.strip()
    if len(i) > 1:
      listInAppPurchases.append(i)

  # print(appCategory)
  # print(appIAP)
  # print(appPrice)
  # print(appPublisher)
  # print(appStore)
  # print(appCountry)  
  print(listMetaHeader)
  print(appDownloads)
  print(appRevenue)   
  print(appVisibScore) 
  print(listRating)
  print(listSumRating)
  print(listVersions)
  print(listAbout)
  print(listInAppPurchases)
  print(userAgent)
  print(elem)
  print("\n")

  driver.quit()

















