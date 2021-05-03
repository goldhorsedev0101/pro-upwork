###### Files provided:
- modulesAkram.py   => Modules for reading the different sources (Quandl, Benzinga, YahooFinance) 
                    (and other used modules i implemented like connector, yahooSummary, clean_value)
- loadStockDB.py    => Main program for updating the DB
- .env              => Environment-files for secret setting (Qunald API-Key, Benzinga API-Key, DB-Name, DB-Password)
- StocksWork.xlsx	=> Put in the stocks which are should worked on in the column A
                    (other possible way is to directly add some tickers in the stockmain-table in the attribute "ticker")
- dbTables.sql		=> Create statements for creating the database table structure
                    (i used MariaDB version 10.3.24 - instructions: https://mariadb.com/kb/en/installing-mariadb-msi-packages-on-windows/)
                    (and for maintaining the DB i use is HeidiSQL: https://www.heidisql.com/
- requirements.txt  => required modules for working with python
                    (install with pip install requirements.txt)

                    
###### Details loadStockDB.py
Key-Parameters at the top of the __main__ block:
FORCE_TICKERS = []                  => when you put some tickers in the list - only the get forced to work on (rest not)
WORKON_MAIN = True                  => if True: loading the table stockmain
WORKON_FINANCIALS = True            => if True: loading the table stockfinancials
WORKON_DAILYDATA = True             => if True: loading the table stockdailydata
WORKON_PRICES = True                => if True: loading the table stockprices
WORKON_NEWS = True                  => if True: loading the table stocknews
STARTDATE_PRICES = "2010-01-01"     => start-date from which date the prices should be read & loaded
STARTDATE_NEWS = "2021-04-01"       => start-date from which date the news should be read & loaded
MAXCOUNT_NEWS = 100                 => max-counts of news which are read & loaded per stock


###### Details .env
QUANDL_API=     => put in the Quandl-API-Key   
BENZINGA_API=   => put in the Benzinga-API-Key
MYSQL_PW=       => put in the MariaDB / MySQL Password
MYSQL_DBNAME=   => put in the MariaDB / MySQL DB-Name


###### Matching requirements
- open, close,high,low,volume (daily)   => find in table stockprices
- market cap (daily)    => find in table stockdailydata
- day earning release   => find in table stockmain - attribut nextEarningDate
- earning release a miss or not     => not provided as discussed before
- how much profit in a company      => attribut netinc in table stockfinancials
- sector of company                 => attribut sector in table stockmain (also industry and famaindustry maybe interesting / useable)
- is company older than 1 year or not   => attribut older1Year in table stockmain (also see firstPriceDate i the same table)
- ticker    => provided in every table as key
- I also need number of news for each ticker    => can easy selected from the db with: SELECT COUNT(*) FROM stocknews WHERE ticker = "AAPL"
- news in seperate table    => table stocknews
- I want the news before the bell ended, so each day until 4pm EST      => is implemented - parameter limit4PM in module readBenzingaNews
- readlogic in scripts  => implemented for all tables


###### Testing
Tested with all nasdaq-tickers
AAPL	ADBE	ADI	ADP	ADSK	AEP	ALGN	ALXN	AMAT	AMD	AMGN	AMZN	ANSS	ASML	ATVI	AVGO	BIDU	BIIB	BKNG	CDNS	
CDW	CERN	CHKP	CHTR	CMCSA	COST	CPRT	CSCO	CSX	CTAS	CTSH	DLTR	DOCU	DXCM	EA	EBAY	EXC	FAST	FB	FISV	
FOX	FOXA	GILD	GOOG	GOOGL	IDXX	ILMN	INCY	INTC	INTU	ISRG	JD	KDP	KHC	KLAC	LRCX	LULU	MAR	MCHP	MDLZ	
MELI	MNST	MRNA	MRVL	MSFT	MTCH	MU	MXIM	NFLX	NTES	NVDA	NXPI	OKTA	ORLY	PAYX	PCAR	PDD	PEP	PTON	
PYPL	QCOM	REGN	ROST	SBUX	SGEN	SIRI	SNPS	SPLK	SWKS	TCOM	TEAM	TMUS	TSLA	TXN	VRSK	VRSN	VRTX	
WBA	WDAY	XEL	XLNX	ZM


FAQ - also have a look at https://www.rapidtech1898.com/htmlFinanztools/en/faqFinanceToolsEN.html

#####Installation and implementation
Unpack all file contents (program, XLSX templates, readme.txt) in a separate folder.

##### Program terminates
Since the data is obtained live from the www, connection problems can sometimes occur - in this case, simply restart the program
The program is automatically continued with the stock title that was canceled

##### XLS needs to be repaired
Sometimes it can happen that the XLS file has to be repaired (error message in Excel).
To do this, make the repair in excel and save / overwrite the file with the same name

##### XLS blocked by actual user
Delete the respective processes for Excel in the Task Manager (Ctrl-Alt-Del) under Processes

##### Program ends with some ZIP error
Excel sheets are corrupted - it is best to save the Excel sheets again, then the problem should be solved










