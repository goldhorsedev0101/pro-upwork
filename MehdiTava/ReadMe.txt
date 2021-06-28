FIRST STEPS / PAY ATTENTION:
(see also FAQ on https://www.rapidtech1898.com/htmlFinanztools/en/faqFinanceToolsEN.html)

##### Installation and implementation
- Unpack all file contents (program, XLSX templates, readme.txt) in a separate folder.
- for the Apple-Store use ScrapeAppStore.xlsx and the 2 programs (scrapeAppStorePRG1.exe and scrapeAppStorePRG2.exe)
- for the Google Store use ScrapeGoogleStore.xlsx and the program scrapeGoogleStore.exe
- in the worksheets "Collection All" and "Category All" you see all possible Collections / Categories from Apple / Google
- Control and input parameters are entered in the worksheet "Parameters"
- Outputs of the results in the worksheet "Apps"
- Before starting the program, please close the excel sheet
- The firewall may have to be activated the first time it is started (click on "OK" or "Allow") - the program obtains data through online scrapping and
therefore needs online access rights


##### Chrome version and chromedriver
They have to match - you can see the current Chrome version at: click on 3 dots at the top right corner of the chrome-windows - klick Help -
klick About Google Chrome - there you can find the current version of Google Chrome Browser.
Under this link "https://chromedriver.chromium.org/downloads" you can see the available chromedriver versions - please download the 
appropriate chromedriver file in case of problems and save it to the same directory as the program file
see FAQ: https://www.rapidtech1898.com/htmlFinanztools/faqFinanceTools.html#8


PARAMETERS ScrapeAppStore.xlsx / ScrapeGoogleStore.xlsx
In the parameters workhsheet starting with row 4 you can enter collection / category combinatons you want to scrape
Or you enter collections and categories in the corresponding worksheets (Collection, Category) and all possible combinations will be build automatically
Cell B1: if "y" or "yes" all combinations will be build for the worksheets collection and category - otherwise only the combinatons from the worksheet parameters starting
from row 4 will be taken for scraping




Common FAQ - https://www.rapidtech1898.com/htmlFinanztools/en/faqFinanceToolsEN.html

#####Installation and implementation
Unpack all file contents (program, XLSX templates, readme.txt) in a separate folder.

##### Program terminates
Since the data is obtained live from the www, connection problems can sometimes occur - in this case, simply restart the program
The program is automatically continued with the stock title that was canceled

##### Program terminates - error message is only (too) short visible
If the program is started from Windows Explorer and aborts due to an error (e.g. web access error), the error message is
only visible for a short time and the cmd Command Line window is closed immediately. In order to see the error message, the program 
must be started from cmd Command Line.

##### XLS needs to be repaired
Sometimes it can happen that the XLS file has to be repaired (error message in Excel).
To do this, make the repair in excel and save / overwrite the file with the same name

##### XLS blocked by actual user
Delete the respective processes for Excel in the Task Manager (Ctrl-Alt-Del) under Processes

##### Program ends with some ZIP error
Excel sheets are corrupted - it is best to save the Excel sheets again, then the problem should be solved

##### In case of other problems
If there are any problems or bugs please feel free to contact me at rapid1898@gmail.com
Please always include the ticker symbol and if possible the exact error message from the cmd command line or powershell
