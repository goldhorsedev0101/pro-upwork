import sqlite3
import CryptoCrawler as cc

conn = sqlite3.connect("coinsPricesDB.db")	
c = conn.cursor()								=> Create a cursor (for working with the db)
c.execute("""CREATE TABLE coinPrices (					
		attr1 text,
		attr2 text,
		attr3 integer)""")
