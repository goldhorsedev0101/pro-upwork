FIRST STEPS / PAY ATTENTION:
(see also FAQ on https://www.rapidtech1898.com/htmlFinanztools/en/faqFinanceToolsEN.html)
- Unpack all file contents (program, XLSX templates, readme.txt) in a separate folder.
- Before starting the program, please close the excel sheet - in rare cases there may be conflicts during program execution
- The firewall may have to be activated the first time it is started (click on "OK" or "Allow") - the program obtains data through online scrapping and
therefore needs online access rights
- please do not use any formulas in the yellow input fields

##### Chrome version and chromedriver
They have to match - you can see the current Chrome version at: click on 3 dots at the top right corner of the chrome-windows - click Help -
click About Google Chrome - there you can find the current version of Google Chrome Browser.
Under this link "https://chromedriver.chromium.org/downloads" you can see the available chromedriver versions - please download the 
appropriate chromedriver file in case of problems and save it to the same directory as the program file
See also the description here: https://www.rapidtech1898.com/htmlFinanztools/en/faqFinanceToolsEN#8

Optional parameter for waiting time between scraping:
Cell B1 / D1 - set the number of seconds between the scraping of the bets
(if some error occurs trough scraping try to incread this values - default values are:
SportsBet => 0.5 seconds
TAB => 3 seconds


FAQ - https://www.rapidtech1898.com/htmlFinanztools/en/faqFinanceToolsEN.html

#####Installation and implementation
Unpack all file contents (program, XLSX templates, readme.txt) in a separate folder.

##### Program terminates
Since the data is obtained live from the www, connection problems can sometimes occur - in this case, simply restart the program

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
Please allways include the exact error message from the cmd command line or powershell
