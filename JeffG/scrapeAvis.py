import requests
from bs4 import BeautifulSoup
import os, sys, time
import xlwings as xw
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from random import choice
from selenium import webdriver     
from sys import platform 
from fake_useragent import UserAgent

if __name__ == '__main__':
  WAIT = 1
  FN = "scrapeAvis.xlsx"
  path = os.path.abspath(os.path.dirname(sys.argv[0]))    
  link = f"https://www.avis.com/en/home" 

  nextFreeRow = 2
  fn = path + "/" + FN
  wb = xw.Book (fn)
  ws = wb.sheets["VIE"]

  if platform == "win32": cd = '/chromedriver.exe'
  elif platform == "linux": cd = '/chromedriver'
  elif platform == "darwin": cd = '/chromedriver'
  options = Options()
  ua = UserAgent()
  userAgent = ua.random
  # options.add_argument('--headless')
  options.add_argument("--window-size=1920x1080")
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-gpu')
  options.add_experimental_option ('excludeSwitches', ['enable-logging'])    
  options.add_argument(f'user-agent={userAgent}')        

  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
  }

  driver = webdriver.Chrome (path + cd, options=options)
  driver.get (link)
  time.sleep(WAIT)

  try:
    driver.find_element_by_css_selector("span[aria-label='Close']").click()
    # driver.find_element_by_xpath('//*[@id="resWidgetContainer"]/div/div[2]/div[12]/div[2]/div/div/div/div/div/div[1]/h3/span').click()    
  except:
    pass

  print(f"Read location VIE...")
  driver.find_element_by_id("PicLoc_value").send_keys("VIE") 
  time.sleep(WAIT)
  driver.find_element_by_id("PicLoc_value").click()
  time.sleep(WAIT)
  print(f"Read from date 2021-07-06...")
  driver.find_element_by_id("from").clear()
  time.sleep(WAIT)
  driver.find_element_by_id("from").click()
  time.sleep(WAIT)
  driver.find_element_by_id("from").send_keys("07/06/2021") 
  time.sleep(WAIT)
  print(f"Read to date 2021-07-21...")
  driver.find_element_by_id("to").clear()
  time.sleep(WAIT)
  driver.find_element_by_id("to").click()
  time.sleep(WAIT)
  driver.find_element_by_id("to").send_keys("07/21/2021") 
  time.sleep(WAIT)
  driver.find_element_by_id("res-home-select-car").click()

  time.sleep(WAIT)
  soup = BeautifulSoup (driver.page_source, 'html.parser')
  tmpList = soup.find_all("div", {"class": "available-car-box"})
  print(f"DEBUG TmpList: {len(tmpList)}")

  for elem in tmpList:
    carGroup = elem.find("h3").text.strip()
    
    tmpErg = elem.find("p", {"class": "similar-car"})
    if tmpErg != None:
      similarCar = tmpErg.text.strip()
    else:
      similarCar = "N/A"

    tmpErg = elem.find("p", {"class": "payamntr"})
    if tmpErg != None:
      pricePayNow = tmpErg.text.strip()
    else:    
      pricePayNow = "N/A"

    tmpErg = elem.find("p", {"class": "payamntp"})
    if tmpErg != None:
      pricePayLater = tmpErg.text.strip()
    else:    
      pricePayLater = "N/A"

    tmpErg = elem.find("p", {"class": "res-inputFldFst"})
    if tmpErg != None:
      priceSave = tmpErg.text.strip()
    else:    
      priceSave = "N/A"

    # print(carGroup)
    # print(similarCar)
    # print(pricePayLater)
    # print(pricePayNow)  
    # print(priceSave)

    ws["A" + str (nextFreeRow)].value = "Vienna Airport"
    ws["B" + str (nextFreeRow)].value = "2021-07-06"
    ws["C" + str (nextFreeRow)].value = "2021-07-21"
    ws["D" + str (nextFreeRow)].value = carGroup
    ws["E" + str (nextFreeRow)].value = similarCar
    ws["F" + str (nextFreeRow)].value = pricePayLater
    ws["G" + str (nextFreeRow)].value = pricePayNow
    ws["H" + str (nextFreeRow)].value = priceSave
    print(f"Written Car Group {carGroup} in row {nextFreeRow}...")

    nextFreeRow += 1

  driver.quit()