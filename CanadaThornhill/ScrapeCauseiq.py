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
from dotenv import load_dotenv, find_dotenv

SAVE_INTERVAL = 5
WAIT = 3
load_dotenv(find_dotenv()) 
MAIL = os.environ.get("MAIL")
MAILPW = os.environ.get("MAILPW")
FN = "ScrapeCauseiq.xlsx"
path = os.path.abspath(os.path.dirname(sys.argv[0]))
fn = path + "/" + FN
wb = xw.Book (fn)
ws = wb.sheets["Data"]

if ws["D1"].value == None:
  startRevenue = 1
else:
  startRevenue = ws["D1"].value

# read nextfreeRow
listData = ws.range ("A3:A150000").value
for idx,cont in enumerate(listData):
    if cont == None:
        idxRow = int(idx)+3
        break

link = "https://www.causeiq.com/search/organizations/so_4ef5f36d1e427557#list"

options = Options()
options.add_argument('--headless')
options.add_experimental_option ('excludeSwitches', ['enable-logging'])
path = os.path.abspath (os.path.dirname (sys.argv[0]))
cd = '/chromedriver.exe'
driver = webdriver.Chrome (path + cd, options=options)
driver.maximize_window()
driver.get (link)
print(f"Login in...")
driver.find_element_by_xpath ('//*[@id="top"]/div/div[2]/a').click ()
driver.find_element_by_id("id_login").send_keys("rapid1898@gmail.com")
driver.find_element_by_id("id_password").send_keys("12345678")
driver.find_element_by_xpath ('//*[@id="stage_content"]/div/div/div/div[2]/form/button').click ()

# clear all filters
try:
  driver.find_element_by_xpath ('/html/body/div[3]/div[1]/div/div/div[1]/div/div[2]/span[4]/a').click ()
except:
  pass
try:
  driver.find_element_by_xpath ('/html/body/div[3]/div[1]/div/div/div[1]/div/div[2]/span[3]/a').click ()
except:
  pass

# filter types
print(f"Filter types...")
time.sleep(2)
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Types']"))).click()
driver.find_element_by_xpath ('//*[@id="search_filters_new"]/div/div/div[3]/div[2]/div[2]/div[2]/div[2]/div[2]/a/small').click()
driver.find_element_by_xpath ('/html/body/div[10]/div/div/div/div[2]/ul/li[8]/span').click()
driver.find_element_by_xpath ('/html/body/div[10]/div/div/div/div[1]/button').click()
driver.find_element_by_xpath ('//*[@id="search_filters_new"]/div/div/div[3]/div[2]/div[2]/div[2]/button').click()

# filter revenues
print(f"Filter revenues...")
time.sleep(2)
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Total revenues']"))).click()
driver.find_element_by_id("min_val").send_keys(startRevenue)
driver.find_element_by_id("max_val").send_keys(startRevenue)
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search_filters_new"]/div/div[2]/div[3]/div[5]/div[2]/div[2]/button'))).click()


while True:
  print(f"Reading 10 elements...")
  time.sleep(2)
  soup = BeautifulSoup (driver.page_source, 'html.parser')
  table = soup.find_all("div", class_="search-list-item")
  for elem in table:
    title = elem.find("h4")
    title = title.text.strip()

    subinfos = elem.find_all("div", class_="col-sm-6")
    subinfoList = []
    for elem2 in subinfos:
      # print(elem2.prettify())
      elem2 = str(elem2)
      tmpList = elem2.split("</i>")
      for e in tmpList:
        if e[0] == "<":
          continue
        subinfoList.append(e.split("<")[0].strip())

    # write data-row to xlsx
    ws["A" + str (idxRow)].value = title
    ws["B" + str (idxRow)].value = subinfoList[0]
    ws["C" + str (idxRow)].value = subinfoList[1]
    ws["D" + str (idxRow)].value = subinfoList[2]
    ws["E" + str (idxRow)].value = subinfoList[3]
    ws["F" + str (idxRow)].value = subinfoList[4]
    ws["G" + str (idxRow)].value = subinfoList[5]
    # print("\n")
    # print(title)
    # print(subinfoList)
    idxRow += 1

  try:
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-results"]/div[2]/div[11]/ul/li[4]/a'))).click()
  except:
    break