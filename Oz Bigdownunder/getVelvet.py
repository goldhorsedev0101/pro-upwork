import time
import os, sys
import xlwings as xw
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
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import mysql.connector
import sshtunnel
import string

def col2num(col):
  num = 0
  for c in col:
    if c in string.ascii_letters:
      num = num * 26 + (ord(c.upper()) - ord('A'))
  return num

print(f"Program name: {os.path.basename(__file__)}")  
TRIAL = True   
BREAK_OUT = 10    
SAVE_INTERVAL = 1
WAIT = 1
path = os.path.abspath(os.path.dirname(sys.argv[0])) 

# with sshtunnel.SSHTunnelForwarder(
#         ("nl1-ts105.a2hosting.com", 7822),
#         ssh_username="rapidtec",
#         ssh_password="C1d0q6bsE2C]:D",
#         remote_bind_address=("0.0.0.0", 3306),
#         allow_agent=False
# ) as tunnel:
#     mydb = mysql.connector.connect(
#         user="rapidtec_Reader",
#         password="I65faue#RR6#",
#         host="127.0.0.1",
#         database="rapidtec_levermann",
#         port=tunnel.local_bind_port)
#     c = mydb.cursor()
#     c.execute ("SELECT * FROM trialaccess")
#     erg = c.fetchall()
#     if ('jan669', 'collBallzy4') not in erg:
#       print(f"Sorry - trial period has ended - reach out to rapid1898@gmail.com for questions...")
#       sys.exit()     

fn = os.path.join(path, os.path.basename(__file__).replace(".py", ".xlsx"))
print(f"Try to open excel in {fn}")
wb = xw.Book (fn)
ws = wb.sheets[0]

print(f"Checking Browser driver...")
HEADLESS = True
options = Options()
if HEADLESS:
  options.add_argument('--headless=new')  
  options.add_argument('--window-size=1920x1080')
else:
  options.add_argument("start-maximized")  
options.add_argument('--use-gl=swiftshader')
options.add_argument('--enable-unsafe-webgpu')
options.add_argument('--enable-unsafe-swiftshader')
options.add_argument("--disable-3d-apis")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("start-maximized")
options.add_argument('--log-level=3')  
options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})    
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled') 
srv=Service()
driver = webdriver.Chrome (service=srv, options=options)    
# driver.minimize_window()
waitWD = WebDriverWait (driver, 10)         

outData = []
for pageNr in range(1,100):
  link = f"https://velvet22.com/escorts?page={pageNr}"
  print(f"Working for detail-link: {link}")  
  driver.get (link)     
  # waitWD.until(EC.presence_of_element_located((By.XPATH, '//button[@class="rpl-pagination__nav"]')))    
  time.sleep(WAIT) 
  soup = BeautifulSoup (driver.page_source, 'lxml')  
  worker = soup.find("div", {"id": "profile-card"})   
  findElems = worker.find_all("figure", {"class": "image-container"})  
  findElems = [[x.find("a").get("href")] for x in findElems]
  if len(findElems) == 0:
    break
  outData.extend(findElems)

driver.quit()
ws.range(f"A1:A1000").value = outData
ws.autofit()     
wb.save()
print(f"Program {os.path.basename(__file__)} finished - will close soon...") 
time.sleep(3)  