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

SAVE_INTERVAL = 5
WAIT = 2
startRow = 2
FN = "ScrapeAppStore.xlsx"
path = os.path.abspath(os.path.dirname(sys.argv[0]))
fn = path + "/" + FN
wb = xw.Book (fn)
ws = wb.sheets["Apps"] 
ws2 = wb.sheets["Parameters"] 
# read stocks for working on
maxRow = 10000
workAppLinks = ws.range ("F2:F10000").value
workAppLinks = [x for x in workAppLinks if x != None]

#read parameters
if ws2["D1"].value != None:
    startRow = int(ws2["D1"].value)   
if ws2["F1"].value != None:
    WAIT = ws2["F1"].value

idxStock = 2

options = Options()
# options.add_argument('--headless')
options.add_experimental_option ('excludeSwitches', ['enable-logging'])
path = os.path.abspath (os.path.dirname (sys.argv[0]))
if sys.platform == "win32": cd = '/chromedriver.exe'
elif sys.platform == "linux": cd = '/chromedriver'
elif sys.platform == "darwin": cd = '/chromedriver'
driver = webdriver.Chrome (path + cd, options=options)

for idx,appLink in enumerate(workAppLinks):
  if idxStock < startRow:
    idxStock += 1
    continue
  if ws["F" + str (idxStock)].value != appLink:
    print(f"Error - work stopped - working app-link \n{appLink}\n is not ident with value in F{idxStock}\n{ws['F' + str (idxStock)].value}")
    break

  appLink = appLink.split("?")[0]
  print (f"Working on {appLink} in row {idxStock}...")
  link = appLink

  headers = {
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
  }

  # read ranknumber / rankcategory
  tries = 0
  while tries < 1000:    

    print(f"DEBUG Link: {link}")

    driver.get (link)
    soup = BeautifulSoup (driver.page_source, 'html.parser')

    # page = requests.get (link)
    # soup = BeautifulSoup (page.content, "html.parser")

    # print(soup)
    # print(len(soup))
    # exit()

    erg = soup.find("header")
    if erg:
      break
    else:
      print(f"No header found re-read - try {tries}...")    
      tries += 1


  erg2 = erg.find_all("li")
  for e in erg2:
    tmpText = e.text.strip()
    if "#" in tmpText and "in" in tmpText:
      rankNumber = int(tmpText.split(" ")[0].replace("#","").strip())
      rankCategory = tmpText.split(" ")[-1].strip()
      break
  # print(f"DEBUG RankNumber: {rankNumber}")
  # print(f"DEBUG RankCategory: {rankCategory}")
  ws["AK" + str (idxStock)].value = rankNumber
  ws["AL" + str (idxStock)].value = rankCategory

  # Check if in-app purchases are on the page
  inAppPurchase = True
  erg = soup.find("dt", string="In-App Purchases")
  if erg == None:
    inAppPurchase = False

  # read In-App-Purchases
  if inAppPurchase == True:
    ws["V" + str (idxStock)].value = "YES"

    # options = Options()
    # options.add_argument('--headless')
    # options.add_experimental_option ('excludeSwitches', ['enable-logging'])
    # path = os.path.abspath (os.path.dirname (sys.argv[0]))
    # if sys.platform == "win32": cd = '/chromedriver.exe'
    # elif sys.platform == "linux": cd = '/chromedriver'
    # elif sys.platform == "darwin": cd = '/chromedriver'
    # driver = webdriver.Chrome (path + cd, options=options)
    # driver.get (link)
    # time.sleep (WAIT)

    # WebDriverWait wait = new WebDriverWait(driver, waitTime);
    # wait.until(ExpectedConditions.elementToBeClickable(locator));
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ember140"]/div/section[7]/div[1]/dl/div[9]/dd/ol/div/button'))).click() 
    try:
      driver.find_element_by_xpath ('/html/body/div[4]/div/main/div[2]/div/section[7]/div[1]/dl/div[9]/dd/ol/div/button').click ()
    except:
      # idxStock += 1
      # print("No In-App Purchase Info found - skipped...")
      # continue
      pass
    # driver.find_element_by_xpath ('//*[@id="ember140"]/div/section[7]/div[1]/dl/div[9]/dd/ol/div/button').click ()
    time.sleep (WAIT)
    soup = BeautifulSoup (driver.page_source, 'html.parser')  # Read page with html.parser
    time.sleep (WAIT)
    driver.quit ()
    # page = requests.get (link)
    # soup = BeautifulSoup (page.content, "html.parser")

    erg = soup.find("dt", string="In-App Purchases")
    erg2 = erg.find_parent("div")
    erg3 = erg2.find_all("li")
    ergList = []
    for i in erg3:
      if i.text not in ["",None]:
        ergList.append(i.text.strip())

    maxPrice = 0
    minPrice = 9999999999
    for idx,elem in enumerate(ergList):
      tmpPrice = float(elem.split("\n")[1].replace("$","".strip()))
      if tmpPrice < minPrice:
        minPrice = tmpPrice
      if tmpPrice > maxPrice:
        maxPrice = tmpPrice
      ergList[idx] = elem.replace("\n", ":")

    # print(f"DEBUG ErgList: {ergList}")
    # print(f"DEBUG Min: {minPrice}")
    # print(f"DEBUG Max: {maxPrice}")

    ergString = ', '.join(ergList)
    ws["AH" + str (idxStock)].value = minPrice
    ws["AI" + str (idxStock)].value = maxPrice
    ws["AJ" + str (idxStock)].value = ergString
  else:
    ws["V" + str (idxStock)].value = ""

  idxStock += 1
  if idxStock % SAVE_INTERVAL == 0:
    wb.save (fn)
    print ("Saved to disk...")

wb.save (fn)
print ("Saved to disk...")