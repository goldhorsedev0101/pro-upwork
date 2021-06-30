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


link = "https://www.causeiq.com/search/organizations/so_4ef5f36d1e427557#list"

options = Options()
# options.add_argument('--headless')
options.add_experimental_option ('excludeSwitches', ['enable-logging'])
path = os.path.abspath (os.path.dirname (sys.argv[0]))
cd = '/chromedriver.exe'
driver = webdriver.Chrome (path + cd, options=options)
driver.get (link)
driver.find_element_by_xpath ('//*[@id="top"]/div/div[2]/a').click ()
driver.find_element_by_id("id_login").send_keys("rapid1898@gmail.com")
driver.find_element_by_id("id_password").send_keys("12345678")
driver.find_element_by_xpath ('//*[@id="stage_content"]/div/div/div/div[2]/form/button').click ()

# element = driver.find_element_by_xpath ('//*[@id="search_filters_new"]/div/div[2]/div[3]/div[5]/div')
# driver.execute_script("arguments[0].setAttribute('class','new-filter-item active')", element)
# driver.find_element_by_xpath ('//*[@id="search_filters_new"]/div/div[2]/div[3]/div[5]/div').click()





                              






