import pymupdf
import pandas
import os
import xlwings as xw
import sys

print(f"Gater all the base data from the pdf")
doc = pymupdf.open("data.pdf")
cat = doc.pdf_catalog()
doc.xref_set_key(cat, "StructTreeRoot", "null")
dataAll = []
for idx, page in enumerate(doc, start=1):
  print(f"Page {idx} out of {len(doc)}")
  tables = page.find_tables()
  for table in tables:
    df = table.to_pandas()
    # nl = df.values.tolist()
    nl = [list(df)]
    nl.extend(df.values.tolist())
    # print(df)
    # print(nl)
    dataAll.extend(nl)
    # print(len(dataAll))
    # input("Press!")

# for r in dataAll[:100]:
#   print(r)
# exit()

outData = []
workRow = False
for r in dataAll:
  if r[0] and r[0].isupper():
    wName = r[0]
    if workRow:
      outData.append(workRow)
      # for elem in outData:
      #   print(elem)
      # input("Press!")
    workRow = [wName, None, None, None, None, None, None]
  for i,e in enumerate(r):
    if e:
      if e.startswith("City"):
        workRow[1] = r[i + 1]
      elif e.startswith("Phone"):
        workRow[4] = r[i + 1]
      elif e.startswith("Email"):
        workRow[5] = r[i + 1]
      elif e.startswith("Updated"):
        workRow[2] = r[i + 1]
      elif e.startswith("Date Added"):
        workRow[2] = r[i + 1]
      elif e.startswith("Website"):
        workRow[3] = r[i + 1]
      elif e.startswith("Notes"):
        workRow[6] = r[i + 1]

path = os.path.abspath(os.path.dirname(sys.argv[0])) 
fn = os.path.join(path, "out.xlsx")
print(f"Try to open excel in {fn}")
wb = xw.Book (fn)
ws = wb.sheets[0]
ws.range(f"A2:G10000").value = None
ws.range(f"A2:G10000").value = outData
