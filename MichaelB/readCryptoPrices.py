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
conn = sqlite3.connect("coinsTESTPricesDB.db")	

READ_COINPRICES = False
EXCEL = False
ANALYSE = True

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

	filt = (df["datePrice"].isin([dtAct, dt4Weeks, dt10Weeks, dt52Weeks]))
	dfPrice = df[filt].sort_values(by="close")
	dfCoins = cc.readCoinsIDs()
	workCoinsID = dfPrice["id"].unique()
		
	ergFinal = {}
	for coinID in workCoinsID:
		print(f"Working on coin with id {coinID}...")
		filt1 = (dfPrice["id"] == coinID)
		filt2 = (dfPrice["datePrice"] == dtAct)
		workRow = dfPrice[filt1 & filt2]
		workValue = workRow["close"].values[0]
		
		if workValue <= checkPrice:
			filt4W = (dfPrice["datePrice"] == dt4Weeks)
			filt10W = (dfPrice["datePrice"] == dt10Weeks)
			filt52W = (dfPrice["datePrice"] == dt52Weeks)
			# (New-Old)/Old		
			change4W = (dfPrice[filt1 & filt4W]["close"].values[0] - workValue) / workValue
			change10W = (dfPrice[filt1 & filt10W]["close"].values[0] - workValue) / workValue
			change52W = (dfPrice[filt1 & filt52W]["close"].values[0] - workValue) / workValue
			ergFinal[coinID] = [change4W, change10W, change52W]
		
		
	for key, val in ergFinal.items (): print (f"{key} => {val} {type(val)}")  

			


			








	







