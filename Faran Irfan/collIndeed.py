import requests
import time
import os, sys
import xlwings as xw
from datetime import datetime, timedelta
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
import mysql.connector
import sshtunnel
from dotenv import load_dotenv
from openai import OpenAI

def checkNone(val):
  if val:
    return val.text.strip()
  else:
    return "N/A"

if __name__ == '__main__':
  print(f"Program name: {os.path.basename(__file__)}")  
  TRIAL = True   
  BREAK_OUT = 10    
  SAVE_INTERVAL = 1
  WAIT = 1
  path = os.path.abspath(os.path.dirname(sys.argv[0])) 
  DETAIL_DESC = True

  with sshtunnel.SSHTunnelForwarder(
          ("nl1-ts105.a2hosting.com", 7822),
          ssh_username="rapidtec",
          ssh_password="C1d0q6bsE2C]:D",
          remote_bind_address=("0.0.0.0", 3306),
          allow_agent=False
  ) as tunnel:
      mydb = mysql.connector.connect(
          user="rapidtec_Reader",
          password="I65faue#RR6#",
          host="127.0.0.1",
          database="rapidtec_levermann",
          port=tunnel.local_bind_port)
      c = mydb.cursor()
      c.execute ("SELECT * FROM trialaccess")
      erg = c.fetchall()
      if ('FaranIrfan', 'collIndeed') not in erg:
        print(f"Sorry - trial period has ended - reach out to rapid1898@gmail.com for questions...")
        sys.exit()     

  print(f"Upload resume file")
  fn = os.path.join(path, ".env")
  load_dotenv(fn) 
  CHATGPT_API_KEY = os.environ.get("CHATGPT_API_KEY")
  client = OpenAI(api_key = CHATGPT_API_KEY)
  fn = os.path.join(path, "resume.docx")
  vector_store = client.beta.vector_stores.create(name="Resume")
  file_paths = [fn]
  file_streams = [open(path, "rb") for path in file_paths]
  file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
  )
  print(file_batch.status)
  print(file_batch.file_counts)

  print(f"Preparing assistant")
  assistant = client.beta.assistants.create(
    name="Document Analyst Assistant",
    instructions= "You are a machine learning researcher, answer questions on the paper. \
    Evaluate how well the paper matches the job description and provide a score from 0 to 100. Do not provide any explanations and output only the score from 0 to 100 and nothing else",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
  )
  assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
  )

  fn = os.path.join(path, "inpIndeed.xlsx")
  print(f"Try to open excel in {fn}")
  wb = xw.Book (fn)
  wsInp = wb.sheets[0]
  inpData = wsInp.range ("B2:B5000").value
  inpData = [x for x in inpData if x != None]
  inpWait = wsInp["B1"].value 
  if inpWait == None or not isinstance(inpWait, float):
    inpWait = 300
  else:
    inpWait = int(inpWait)  
  ws = wb.sheets[1]
  existData = ws.range ("A2:Z50000").value
  existData = [x for x in existData if x[0] != None]
  existLinks = [(x[1], x[2], x[3]) for x in existData]
  rowNum = len(existData) + 2
  workNum = 0
  tmpOutput = []  
   
  print(f"Checking Browser driver...")
  options = Options()
  # options.add_argument('--headless=new')  
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
  
  for idx, baseLink in enumerate(inpData):
    # if TRIAL and idx > 0:
    #   print(f"In the trial-version only the first baselink will be worked on - program stopped...")
    #   sys.exit()
    countRows = 0
    breakOut = False
    for pageNr in range(0, 1000, 20):
      if breakOut:
        break
      # link = f"https://www.orf.at" 
      link = f"{baseLink}&start={pageNr}"  
      # if link in existKeys:
      #   print(f"{link} allready in excel - skipped...")
      #   continue
      # existKeys.append(link)

      print(f"Working for {link}")  
      driver.get (link)    
      driver.execute_script("window.scrollTo(0, 10000)") 
      # input("Press!")

      time.sleep(WAIT) 
      soup = BeautifulSoup (driver.page_source, 'html.parser')       
      tmpDIV = soup.find_all("div", {"class": "slider_item"}) 
      print(f"{len(tmpDIV)} elements found")
      nothingFound = True
      for elem in tmpDIV:
        # print(elem.prettify())
        # input("Press!")
        tmpH2 = elem.find("h2", {"class": "jobTitle"})
        tmpTitle = tmpH2.find("a").text.strip()
        tmpCompany = elem.find("span", {"data-testid": "company-name"}).text.strip()
        tmpLocation = elem.find("div", {"data-testid": "text-location"}).text.strip()

        tmpJobType = elem.find("svg", {"aria-label": "Job type"})
        if tmpJobType != None:
          tmpJobType = tmpJobType.parent.text.strip()

        tmpDate = "N/A"
        worker = elem.find("span", {"data-testid": "myJobsStateDate"})
        if worker:
          tmpDate = worker.text.strip().replace("Posted", "")

        checkKey = (tmpTitle, tmpCompany, tmpLocation)
        if checkKey in existLinks:
          print(f"{tmpTitle} / {tmpCompany} is allready in excel - skipped...")
          continue
        nothingFound = False
        existLinks.append(checkKey)

        # tmpSalary = "N/A"
        # tmpDIV = elem.find("div", {"class": "salary-snippet-container"})
        # if tmpDIV == None:
        #   tmpDIV = elem.find("div", {"class": "metadata estimated-salary-container"})
        # if tmpDIV != None:
        #   tmpSalary = tmpDIV.text.strip()

        # tmpShift = elem.find("svg", {"aria-label": "Shift"})
        # if tmpShift != None:
        #   tmpShift = tmpShift.parent.text.strip()

        tmpSnippet = []
        tmpDIV = elem.find("div", {"class": "jobMetaDataGroup"})
        tmpLI = tmpDIV.find_all("li")
        for e in tmpLI:
          tmpSnippet.append(e.text.strip())
        tmpSnippet = "\n".join(tmpSnippet)

        tmpLink = tmpH2.find("a").get("href")
        tmpLink = f"https://www.indeed.com{tmpLink}"

        # tmpRow = [workLink, tmpTitle, tmpCompany, tmpLocation, tmpSalary, tmpJobType, 
        #           tmpShift, tmpDate, tmpLink, tmpSnippet]    
        if DETAIL_DESC:        
          driver.get (tmpLink)
          print(f"Working on detaillink {tmpLink}")
          time.sleep(WAIT) 
          soup = BeautifulSoup (driver.page_source, 'html.parser')               
          tmpDesc = soup.find("div", {"id": "jobDescriptionText"}).text.strip()
                    
          print(f"Preparing thread")
          thread = client.beta.threads.create()
          print(f"Preparing question")
          results = client.beta.threads.messages.create(
            thread_id = thread.id,
            role = "user",
            content = tmpDesc
          )
          print(f"Running for answer")
          run = client.beta.threads.runs.create (
            thread_id = thread.id,
            assistant_id = assistant.id
          )
          while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve (
              thread_id = thread.id,
              run_id = run.id
            )
          if run.status == "completed":
            results = client.beta.threads.messages.list(
                thread_id=thread.id
            )

          try:
            answer = results.data[0].content[0].text.value
            print(f"The resume is fitting to the job description {answer} out of 100")
          except:
            print(f"No answer found...")
            print(results)
            answer = "N/A"
          tmpRow = [link, tmpTitle, tmpCompany, tmpLocation, tmpDate, tmpLink, tmpSnippet, answer] 
        else:
          tmpRow = [link, tmpTitle, tmpCompany, tmpLocation, tmpDate, tmpLink, tmpSnippet]    
        # for e in tmpRow:
        #   print(e)
        # exit()
        # input("Press")

        tmpOutput.append(tmpRow)
        workNum += 1    
        if workNum % SAVE_INTERVAL == 0:
          ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").value = tmpOutput
          ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").api.WrapText = False    
          # countRows += 1
          # if TRIAL and countRows > BREAK_OUT:
          #   print(f"Maximum output per category reached - skipped to next category...")
          #   breakOut = True
          #   break      
          print(f"Data written to {rowNum}...")
          rowNum += len(tmpOutput)
          tmpOutput = []
          workName = 0      
          # input("Press!")
  
  driver.quit()
  ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").value = tmpOutput
  ws.range(f"A{rowNum}:Z{rowNum + len(tmpOutput)}").api.WrapText = False   
  wb.save()
  print(f"Program {os.path.basename(__file__)} finished - will close soon...") 
  time.sleep(5)  