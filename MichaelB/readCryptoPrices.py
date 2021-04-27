import sqlite3
import CryptoCrawler as cc
from datetime import datetime, timedelta
from datetime import date
import pandas as pd

START_DATE = "2017-01-01"
TDAY = str(datetime.today().date())
conn = sqlite3.connect("coinsPricesDB.db")	

READ_COINPRICES = False
EXCEL = True

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






	







