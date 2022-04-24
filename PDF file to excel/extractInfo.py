import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
import xlwings as xw
import time

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
  existData = [x for x in existData if x[0] != None]

  ws.range(f"A2:K10000").value = None

  fn = "invoice.pdf"
  with open (fn, 'rb') as f:
    pdf = PdfFileReader (f)
    info = pdf.getDocumentInfo ()
    number_of_pages = pdf.getNumPages ()

    content = ""
    for i in range(0, number_of_pages):
      content += pdf.getPage(i).extractText() + "\n"
      listContent = content.split("\n")

  content = content.replace(u"\xa0", " ").strip()
  lines = content.split("\n")
  # lines = [x for x in lines if len(x) > 0]  

  for e in lines:
    print(e)

  for eIDX, eVAL in enumerate(lines):
    if eVAL == "BILL TO":
      tmpName = lines[eIDX + 1]
    if eVAL == "Amount":
      tmpItem = lines[eIDX + 1]
      tmpDesc = []
      tmpDesc.extend(lines[eIDX + 2:eIDX + 5])
      tmpDesc = (", ").join(tmpDesc)
    if eVAL == "Total:":
      tmpPrice = lines[eIDX + 1]      
  
  print(tmpName)
  print(tmpItem)
  print(tmpDesc)
  print(tmpPrice)

  tmpRow = [tmpName, tmpItem, tmpDesc, tmpPrice]    
  ws.range(f"A{rowNum}:K{rowNum}").value = tmpRow
  print(f"{tmpName} written to row {rowNum}...")
  rowNum += 1  

  wb.save()
  input(f"Program finished - pls press <enter> to close the window...") 
  time.sleep(5)   


