import os, sys
import xlwings as xw

path = os.path.abspath(os.path.dirname(sys.argv[0])) 
fn = os.path.join(path, "Farm.xlsx")
print(f"Try to open excel in {fn}")
wb = xw.Book (fn)
wsInp = wb.sheets[0]
inpFarms = wsInp.range ("A2:A10000").value
inpFarms = list(set(inpFarms))
inpFarms = [x for x in inpFarms if x]
dictFarms = {x: [0,0,0,0,0,0] for x in inpFarms}
# for k,v in dictFarms.items():
#   print(k,v)
# exit()

fn = os.path.join(path, "Plot.xlsx")
print(f"Try to open excel in {fn}")
wb = xw.Book (fn)
wsInp = wb.sheets[0]
inpPlot = wsInp.range ("A2:T10000").value
inpPlot = [x for x in inpPlot if x[0] != None]

for idxRow, row in enumerate(inpPlot, start=2):
  print(idxRow)
  wFarmerCode = row[2]
  wAutoFieldAcr = row[6]
  wFieldSize = row[10]
  wNumMainCropTrees = row[16]
  wNumMainCropProd = row[17]
  wYieldEstimate = row[18]
  wTotalMain = row[19]
  if wFarmerCode in dictFarms:
    dictFarms[wFarmerCode][0] += float(wAutoFieldAcr)
    dictFarms[wFarmerCode][1] += float(wFieldSize)
    if wNumMainCropTrees:
      dictFarms[wFarmerCode][2] += wNumMainCropTrees
    if wNumMainCropProd:
      dictFarms[wFarmerCode][3] += wNumMainCropProd   
    if wYieldEstimate:
      dictFarms[wFarmerCode][4] += float(wYieldEstimate)
    if wTotalMain:
      dictFarms[wFarmerCode][5] += float(wTotalMain)

outData = []
for k,v in dictFarms.items():
  workRow = [k]
  workRow.extend(v)
  outData.append(workRow)
fn = os.path.join(path, "Output.xlsx")
print(f"Try to open excel in {fn}")
wb = xw.Book (fn)
wsOut = wb.sheets[0]
wsOut.range(f"A2:G1000").value = outData