import sqlite3
import CryptoCrawler as cc
from datetime import datetime, timedelta
from datetime import date
import pandas as pd
import os
import sys
import xlwings as xw

START_DATE = "2017-01-01"
TDAY = str(datetime.today().date())
conn = sqlite3.connect("coinsPricesDB.db")	

READ_COINPRICES = False
EXCEL = False
CSV_OUTPUT = True
ANALYSE = False

coinsRank = cc.readCoinsIDs()
countCoin = 0
countInfo = 5
coinSearch = ""

if READ_COINPRICES:
	finalPriceDF = pd.DataFrame()
	for idx, coin in enumerate(coinsRank):
		if coinSearch == "":
			coinSearch = str(coin["id"])
		else:
			coinSearch = coinSearch + "," + str(coin["id"])
		countCoin += 1		
		if countCoin % 5 == 0 or idx == len(coinsRank)-1:	
			print(f"Reading prices for {countInfo} coins...")
			countInfo += 5
			ergDF = cc.readHistPriceCMCapi(coinSearch,out=True,start=START_DATE,end=TDAY,output="df")
			finalPriceDF = finalPriceDF.append(ergDF, ignore_index=True)
			ergDF.to_sql('coinPrices', conn, if_exists='append', index=False)
			countCoin = 0
			coinSearch = ""
			print(finalPriceDF)
			print(finalPriceDF["name"].unique())
			input()
	conn.commit()
	conn.close()

if EXCEL:
	df = pd.read_sql_query("SELECT * FROM coinPrices", conn)	
	conn.commit()
	conn.close()

	filt = df["symbol"].isin(["LTC","BTC","ETG","AUG","BNB","XRP","ADA","DOGE","DOT","XLM"])
	df = df[filt]

	with pd.ExcelWriter("example.xlsx") as writer:		
		df.to_excel(writer, sheet_name="coinPrices")		

if CSV_OUTPUT:
	print(f"Reading price data from db...")
	df = pd.read_sql_query("SELECT * FROM coinPrices", conn)	
	conn.commit()
	conn.close()

	# filt = df["symbol"].isin(["LTC","BTC","ETG","AUG","BNB","XRP","ADA","DOGE","DOT","XLM"])
	# df = df[filt]

	# split in several csvs with max rows
	splitLen = 1000000
	for idx in range(0,len(df),splitLen):
		print(f"Writing CSV-File Part {int(idx/splitLen+1)}...")
		dfTemp = df.iloc[idx:idx+splitLen]
		dfTemp.to_csv(f"coinPrices{int(idx/splitLen+1)}.csv", sep=';')

if ANALYSE:
	df = pd.read_sql_query("SELECT * FROM coinPrices", conn)	
	df["datePrice"] = df["datePrice"].apply(lambda x: x[:10])
	conn.commit()
	conn.close()

	FN = "AnalyseExcel.xlsx"
	path = os.path.abspath(os.path.dirname(sys.argv[0]))
	fn = path + "/" + FN
	wb = xw.Book (fn)
	ws = wb.sheets["Input"]
	ws2 = wb.sheets["Output"]

	checkDate = ws["B1"].value
	checkPrice = ws["B2"].value

	dtAct = datetime.strftime(checkDate, "%Y-%m-%d")
	dt4Weeks = datetime.strftime((checkDate + timedelta(days=28)), "%Y-%m-%d")     
	dt10Weeks = datetime.strftime(checkDate + timedelta(days=70), "%Y-%m-%d")     
	dt52Weeks = datetime.strftime(checkDate + timedelta(days=365), "%Y-%m-%d")     
	coinDF = cc.readCoinsIDs()

	filt = (df["datePrice"].isin([dtAct, dt4Weeks, dt10Weeks, dt52Weeks]))
	dfPrice = df[filt].sort_values(by="close")
	dfCoins = cc.readCoinsIDs()
	workCoinsID = dfPrice["id"].unique()
		
	ergFinal = {}
	for coinID in workCoinsID:
		print(f"Working on coin with id {coinID}...")
		filtID = (coinDF["id"] == coinID)
		workRow = coinDF[filtID]
		tmpRank = workRow["rank"].values[0]
		tmpName = workRow["name"].values[0]
		tmpSymbol = workRow["symbol"].values[0]

		filt1 = (dfPrice["id"] == coinID)
		filt2 = (dfPrice["datePrice"] == dtAct)
		workRow = dfPrice[filt1 & filt2]

		if workRow.empty:
			continue
		else:
			workValue = workRow["close"].values[0]
		
		if workValue <= checkPrice:
			priceFlag = "less"
		else:
			priceFlag = "greater"

		filt4W = (dfPrice["datePrice"] == dt4Weeks)
		filt10W = (dfPrice["datePrice"] == dt10Weeks)
		filt52W = (dfPrice["datePrice"] == dt52Weeks)
		if dfPrice[filt1 & filt4W]["close"].empty or dfPrice[filt1 & filt10W]["close"].empty or dfPrice[filt1 & filt52W]["close"].empty:
			continue

		# (New-Old)/Old	
		change4W = (dfPrice[filt1 & filt4W]["close"].values[0] - workValue) / workValue
		change10W = (dfPrice[filt1 & filt10W]["close"].values[0] - workValue) / workValue
		change52W = (dfPrice[filt1 & filt52W]["close"].values[0] - workValue) / workValue
		ergFinal[coinID] = [priceFlag, tmpRank, tmpName, tmpSymbol, change4W, change10W, change52W]

	# calculate deviatons
	changeSum = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
	changeCount = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
	for key, val in ergFinal.items ():

		print(val)

		if val[0] == "less":
			for i in range(3):
				changeSum [0][i] += val[4+i]
				changeCount [0][i] += 1		
		if val[0] == "greater":
			for i in range(3):
				changeSum [1][i] += val[4+i]
				changeCount [1][i] += 1	
		if val[0] == "less" and val[1] <= 100:
			for i in range(3):
				changeSum [2][i] += val[4+i]
				changeCount [2][i] += 1				
		if val[0] == "greater" and val[1] <= 100:
			for i in range(3):
				changeSum [3][i] += val[4+i]
				changeCount [3][i] += 1	
		if val[0] == "less" and val[1] >= 101 and val[1] <= 300:
			for i in range(3):
				changeSum [4][i] += val[4+i]
				changeCount [4][i] += 1				
		if val[0] == "greater" and val[1] >= 101 and val[1] <= 300:
			for i in range(3):
				changeSum [5][i] += val[4+i]
				changeCount [5][i] += 1	
		if val[0] == "less" and (301 <= val[1] <= 600):
			for i in range(3):
				changeSum [6][i] += val[4+i]
				changeCount [6][i] += 1				
		if val[0] == "greater" and (301 <= val[1] <= 600):
			for i in range(3):
				changeSum [7][i] += val[4+i]
				changeCount [7][i] += 1	

	print(f"SumList: {changeSum}")
	print(f"CountList: {changeCount}")
	deviationFinal = []
	for idx,elem in enumerate(changeSum):
		tmpList = []
		for idx2,elem2 in enumerate(elem):
			if changeCount[idx][idx2] != 0:
				tmpList.append(elem2 / changeCount[idx][idx2])
			else:
				tmpList.append(0)
		deviationFinal.append(tmpList)
	print(f"DeviationList: {deviationFinal}")

	# write results to excel
	ws2["B1"].value = checkDate
	ws2["D1"].value = checkPrice
	ws2["B3"].value = dt4Weeks
	ws2["C3"].value = dt10Weeks
	ws2["D3"].value = dt52Weeks
	ws2.range("B4:D11").value = deviationFinal
			


			








	







