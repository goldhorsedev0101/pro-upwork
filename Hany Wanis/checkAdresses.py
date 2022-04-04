from itertools import count
from dotenv import load_dotenv, find_dotenv
import os
import sys
from serpapi import GoogleSearch
import xlwings as xw
import mpu
import json

if __name__ == '__main__':
  load_dotenv(find_dotenv()) 
  SERP_API = os.environ.get("SERP_API")  

  SAVE_INTERVAL = 10
  FN = "input.xlsx"
  path = os.path.abspath(os.path.dirname(sys.argv[0]))
  rowNum = 2
  fn = path + "/" + FN
  wb = xw.Book (fn)
  ws1 = wb.sheets[0]
  inpData = ws1.range("A2:D10000").value
  inpData = [x for x in inpData if x[0] != None]
  searchLoc = ws1.range("E1:T1").value

  existAddr = {}
  for rowNum, rowCont in enumerate(inpData, start=2):
    searchAddress = rowCont[3]
    if searchAddress not in existAddr:
      # get coordinates for address
      print(f"Searching for {searchAddress}...")
      params = {
        "engine": "google_maps",
        "q": searchAddress,
        # "ll": "@40.7455096,-74.0083012,15.1z",
        "type": "search",
        "api_key": "cc0af3110697954d1224ee22769f89a4d0753083697755551bde6520c9feb190"
      }
      search = GoogleSearch(params)
      res = search.get_dict()
      print(json.dumps(res, indent=2, sort_keys=True))
      addrLat1 = res["place_results"]["gps_coordinates"]["latitude"]
      addrLong1 = res["place_results"]["gps_coordinates"]["longitude"]
      
      tmpLocRow = []
      for searchLocIDX, searchLoc in enumerate(searchLoc):
        print(f"Searching for locatons: {searchLoc}...")
        params = {
          "engine": "google_maps",
          "q": searchLoc,
          "ll": f"@{addrLat1},{addrLong1},21z",
          "type": "search",
          "api_key": SERP_API
        }
        search = GoogleSearch(params)
        res = search.get_dict()
        countLoc = 0
        for resElem in res["local_results"]:
          print(json.dumps(resElem, indent=2, sort_keys=True))
          locLat1 = resElem["gps_coordinates"]["latitude"]
          locLong1 = resElem["gps_coordinates"]["longitude"]
          distLoc = mpu.haversine_distance((addrLat1, addrLong1), (locLat1, locLong1))
          # print(distLoc)
          # input("Press!")
          if distLoc < 1:
            countLoc += 1
        tmpLocRow.append(countLoc)
        print(countLoc)  
      existAddr[searchAddress] = tmpLocRow
    else:
      tmpLocRow = existAddr[searchAddress]

    ws1.range(f"E{rowNum}:T{rowNum}").value = tmpLocRow
    input("Press!")