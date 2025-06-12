import json
import os, sys
import time
import xlwings as xw

path = os.path.abspath(os.path.dirname(sys.argv[0])) 
fn = os.path.join(path, "sample_json.json")
with open(fn, encoding="UTF-8", errors="ignore") as f:
  inpJSON = f.read()

workDict = json.loads(inpJSON)
worker = workDict["data"]

outData = []
# 20 dicts in list
for r in worker:
  # for k,v in r.items():
  #   print(k,v)
  #   input("Press!")
  # first several attributes are with one entry
  # last attriubte 'statistics' has a list with 77 elements
  R_id = r["id"]
  R_sport_id = r["sport_id"]
  R_country_id = r["country_id"]
  R_venue_id = r["venue_id"]
  R_gender = r["gender"]
  R_name = r["name"]
  R_short_code = r["short_code"]
  R_image_path = r["image_path"]
  R_founded = r["founded"]
  R_type = r["type"]
  R_placeholder = r["placeholder"]
  R_last_played_at = r["last_played_at"]
  stat = r["statistics"]
  for s in stat:
    # first 4 attriubtes are with one entry
    S_id = s["id"]  
    S_team_id = s["team_id"]  
    S_season_id = s["season_id"]  
    S_has_values = s["has_values"]  
    # last attribute "details" has a list with 7 elements
    details = s["details"]
    for d in details:
      D_id = d["id"]  
      D_team_statistic_id = d["team_statistic_id"]  
      D_type_id = d["type_id"]  

      # first 3 attributes are with one entry
      # last attribute "value" has a dict with 3 entires ("all", "home", "away") with 3 attriubtes in it
      value = d["value"]

      if D_type_id == 27254:
        print(value)
        exit()

      V_all_count = V_all_average = V_all_first = V_home_count = V_home_percentage = V_home_average = V_home_first = \
      V_away_count = V_away_percentage = V_away_average = V_away_first = V_0_15_count = V_0_15_percentage = V_15_30_count = \
      V_15_30_percentage = V_30_45_count = V_30_45_percentage = V_45_60_count = V_45_60_percentage = V_60_75_count = \
      V_60_75_percentage = V_75_90_count = V_75_90_percentage = V_Total = V_Scored = V_Missed = V_ConversionRate = V_PlayerID = \
      V_PlayerName = V_Coach = V_CoachAverage = V_Value = V_Rating = V_Over05_MatchCount = V_Over05_MatchPerc = V_Over05_TeamCount = \
      V_Over05_TeamPerc = V_Over15_MatchCount = V_Over15_MatchPerc = V_Over15_TeamCount = V_Over15_TeamPerc = V_Over25_MatchCount = \
      V_Over25_MatchPerc = V_Over25_TeamCount = V_Over25_TeamPerc = V_Over35_MatchCount = V_Over35_MatchPerc = V_Over35_TeamCount = \
      V_Over35_TeamPerc = V_Over45_MatchCount = V_Over45_MatchPerc = V_Over45_TeamCount = V_Over45_TeamPerc = V_Over55_MatchCount = \
      V_Over55_MatchPerc = V_Over55_TeamCount = V_Over55_TeamPerc = V_avg_defender_height = V_avg_midfielder_height = V_avg_goalkeeper_height = \
      V_avg_attacker_height = V_avg_total_height = V_left = V_right = V_unknown = V_most_appearing_players = V_most_substituted_players = \
      most_injured_players = V_fouls_per_card = V_cards_per_foul = scoring_frequency = V_total_minutes_played = V_most_scored_half = \
      V_most_scored_half_goals = V_details_1stHalf_Period = V_details_1stHalf_Total = V_details_2ndHalf_Period = V_details_2ndHalf_Total = \
      V_most_frequent_scoring_minute = V_amount_of_goals = V_total_interceptions = V_interceptions_per_game = V_passes_per_game = V_passes_per_goal = \
      V_passes_per_shot = V_total_passes = "N/A"
      
      if "count" in value:
        V_all_count = value["count"]
      if "average" in value:
        V_all_average = value["average"]
      if "first" in value:
        V_all_first = value["first"]
      if "total" in value:
        V_Total = value["total"]
      if "scored" in value:
        V_Scored = value["scored"]
      if "missed" in value:
        V_Missed = value["missed"]
      if "conversion_rate" in value:
        V_ConversionRate = value["conversion_rate"]
      if "player_id" in value:
        V_PlayerID = value["player_id"]
      if "player_name" in value:
        V_PlayerName = value["player_name"]
      if "coach" in value:
        V_Coach = value["coach"]
      if "coach_average" in value:
        V_CoachAverage = value["coach_average"]
      if "value" in value:
        V_Value = value["value"]
      if "rating" in value:
        V_Value = value["rating"]
      if "avg_defender_height" in value:
        V_avg_defender_height = value["avg_defender_height"]
      if "avg_midfielder_height" in value:
        V_avg_midfielder_height = value["avg_midfielder_height"]
      if "avg_goalkeeper_height" in value:
        V_avg_goalkeeper_height = value["avg_goalkeeper_height"]
      if "avg_attacker_height" in value:
        V_avg_attacker_height = value["avg_attacker_height"]
      if "avg_total_height" in value:
        V_avg_total_height = value["avg_total_height"]
      if "left" in value:
        V_left = value["left"]
      if "right" in value:
        V_right = value["right"]
      if "unknown" in value:
        V_unknown = value["unknown"]
      if "most_appearing_players" in value:
        worker = value["most_appearing_players"]
        worker = [f"{x["player_id"]}: {x["minutes"]}" for x in worker]
        V_most_appearing_players = ", ".join(worker)
      if "most_substituted_players" in value:
        worker = value["most_substituted_players"]
        worker = [f"{x["player_id"]}: {x["in"]}/{x["out"]}/{x["total"]}" for x in worker]
        V_most_substituted_players = ", ".join(worker)
      if "most_injured_players" in value:
        worker = value["most_injured_players"]
        worker = [f"{x["player_id"]}: {x["total"]}" for x in worker]
        V_most_injured_players = ", ".join(worker)
      if "fouls_per_card" in value:
        V_fouls_per_card = value["fouls_per_card"]
      if "cards_per_foul" in value:
        V_cards_per_foul = value["cards_per_foul"]
      if "scoring_frequency" in value:
        V_scoring_frequency = value["scoring_frequency"]
      if "total_minutes_played" in value:
        V_total_minutes_played = value["total_minutes_played"]
      if "most_scored_half" in value:
        V_most_scored_half = value["most_scored_half"]
      if "most_scored_half_goals" in value:
        V_most_scored_half_goals = value["most_scored_half_goals"]
      if "details" in value:
        V_details_1stHalf_Period = value["details"]["1st-half"]["period"]
        V_details_1stHalf_Total = value["details"]["1st-half"]["total"]
        V_details_2ndHalf_Period = value["details"]["2nd-half"]["period"]
        V_details_2ndHalf_Total = value["details"]["2nd-half"]["total"]
      if "most_frequent_scoring_minute" in value:
        V_most_frequent_scoring_minute = value["most_frequent_scoring_minute"]
      if "amount_of_goals" in value:
        V_amount_of_goals = value["amount_of_goals"]
      if "total_interceptions" in value:
        V_total_interceptions = value["total_interceptions"]
      if "interceptions_per_game" in value:
        V_interceptions_per_game = value["interceptions_per_game"]
      if "passes_per_game" in value:
        V_passes_per_game= value["passes_per_game"]
      if "passes_per_goal" in value:
        V_passes_per_goal= value["passes_per_goal"]
      if "passes_per_shot" in value:
        V_passes_per_shot= value["passes_per_shot"]
      if "total_passes" in value:
        V_total_passes = value["total_passes"]

      


      if "over_0_5" in value:
        if "matches" in value["over_0_5"]:
          if "count" in value["over_0_5"]["matches"]:
            V_Over05_MatchCount = value["over_0_5"]["matches"]["count"]
          if "percentage" in value["over_0_5"]["matches"]:
            V_Over05_MatchPerc = value["over_0_5"]["matches"]["percentage"]
        if "team" in value["over_0_5"]:
          if "count" in value["over_0_5"]["team"]:
            V_Over05_TeamCount = value["over_0_5"]["team"]["count"]
          if "percentage" in value["over_0_5"]["team"]:
            V_Over05_TeamPerc = value["over_0_5"]["team"]["percentage"]
      if "over_1_5" in value:
        if "matches" in value["over_1_5"]:
          if "count" in value["over_1_5"]["matches"]:
            V_Over15_MatchCount = value["over_1_5"]["matches"]["count"]
          if "percentage" in value["over_1_5"]["matches"]:
            V_Over15_MatchPerc = value["over_1_5"]["matches"]["percentage"]
        if "team" in value["over_1_5"]:
          if "count" in value["over_1_5"]["team"]:
            V_Over15_TeamCount = value["over_1_5"]["team"]["count"]
          if "percentage" in value["over_1_5"]["team"]:
            V_Over15_TeamPerc = value["over_1_5"]["team"]["percentage"]
      if "over_2_5" in value:
        if "matches" in value["over_2_5"]:
          if "count" in value["over_2_5"]["matches"]:
            V_Over25_MatchCount = value["over_2_5"]["matches"]["count"]
          if "percentage" in value["over_2_5"]["matches"]:
            V_Over25_MatchPerc = value["over_2_5"]["matches"]["percentage"]
        if "team" in value["over_2_5"]:
          if "count" in value["over_2_5"]["team"]:
            V_Over25_TeamCount = value["over_2_5"]["team"]["count"]
          if "percentage" in value["over_2_5"]["team"]:
            V_Over25_TeamPerc = value["over_2_5"]["team"]["percentage"]
      if "over_3_5" in value:
        if "matches" in value["over_3_5"]:
          if "count" in value["over_3_5"]["matches"]:
            V_Over35_MatchCount = value["over_3_5"]["matches"]["count"]
          if "percentage" in value["over_3_5"]["matches"]:
            V_Over35_MatchPerc = value["over_3_5"]["matches"]["percentage"]
        if "team" in value["over_3_5"]:
          if "count" in value["over_3_5"]["team"]:
            V_Over35_TeamCount = value["over_3_5"]["team"]["count"]
          if "percentage" in value["over_3_5"]["team"]:
            V_Over35_TeamPerc = value["over_3_5"]["team"]["percentage"]
      if "over_4_5" in value:
        if "matches" in value["over_4_5"]:
          if "count" in value["over_4_5"]["matches"]:
            V_Over45_MatchCount = value["over_4_5"]["matches"]["count"]
          if "percentage" in value["over_4_5"]["matches"]:
            V_Over45_MatchPerc = value["over_4_5"]["matches"]["percentage"]
        if "team" in value["over_4_5"]:
          if "count" in value["over_4_5"]["team"]:
            V_Over45_TeamCount = value["over_4_5"]["team"]["count"]
          if "percentage" in value["over_4_5"]["team"]:
            V_Over45_TeamPerc = value["over_4_5"]["team"]["percentage"]
      if "over_5_5" in value:
        if "matches" in value["over_5_5"]:
          if "count" in value["over_5_5"]["matches"]:
            V_Over55_MatchCount = value["over_5_5"]["matches"]["count"]
          if "percentage" in value["over_5_5"]["matches"]:
            V_Over55_MatchPerc = value["over_5_5"]["matches"]["percentage"]
        if "team" in value["over_5_5"]:
          if "count" in value["over_5_5"]["team"]:
            V_Over55_TeamCount = value["over_5_5"]["team"]["count"]
          if "percentage" in value["over_5_5"]["team"]:
            V_Over55_TeamPerc = value["over_5_5"]["team"]["percentage"]

      if "0-15" in value:
        if "count" in value["0-15"]:
          V_0_15_count = value["0-15"]["count"]
        if "percentage" in value["0-15"]:
          V_0_15_percentage = value["0-15"]["percentage"]        
      if "15-30" in value:
        if "count" in value["15-30"]:
          V_15_30_count = value["15-30"]["count"]
        if "percentage" in value["15-30"]:
          V_15_30_percentage = value["15-30"]["percentage"]        
      if "30-45" in value:
        if "count" in value["30-45"]:
          V_30_45_count = value["30-45"]["count"]
        if "percentage" in value["30-45"]:
          V_30_45_percentage = value["30-45"]["percentage"]        
      if "45-60" in value:
        if "count" in value["45-60"]:
          V_45_60_count = value["45-60"]["count"]
        if "percentage" in value["45-60"]:
          V_45_60_percentage = value["45-60"]["percentage"]        
      if "60-75" in value:
        if "count" in value["60-75"]:
          V_60_75_count = value["60-75"]["count"]
        if "percentage" in value["60-75"]:
          V_60_75_percentage = value["60-75"]["percentage"]        
      if "75-90" in value:
        if "count" in value["75-90"]:
          V_75_90_count = value["75-90"]["count"]
        if "percentage" in value["75-90"]:
          V_75_90_percentage = value["75-90"]["percentage"]        

      if "all" in value:
        if "count" in value["all"]:
          V_all_count = value["all"]["count"]
        if "average" in value["all"]:
          V_all_average = value["all"]["average"]
        if "first" in value["all"]:
          V_all_first = value["all"]["first"]

      if "home" in value:
        if isinstance(value["home"], int):
          V_home_count = value["home"]
        else:
          if "count" in value["home"]:
            V_home_count = value["home"]["count"]
          if "percentage" in value["home"]:
            V_home_percentage = value["home"]["percentage"]
          if "average" in value["home"]:
            V_home_average = value["home"]["average"]
          if "first" in value["home"]:
            V_home_first = value["home"]["first"]

      if "away" in value:
        if isinstance(value["away"], int):
          V_home_count = value["away"]
        else:
          if "count" in value["away"]:
            V_away_count = value["away"]["count"]
          if "percentage" in value["away"]:
            V_away_percentage = value["away"]["percentage"]
          if "average" in value["away"]:
            V_away_average = value["away"]["average"]
          if "first" in value["away"]:
            V_away_first = value["away"]["first"]

      worker = [R_id, R_sport_id, R_country_id, R_venue_id, R_gender, R_name, R_short_code, R_image_path, R_founded, R_type, R_placeholder, 
                R_last_played_at, S_id, S_team_id, S_season_id, S_has_values, D_id, D_team_statistic_id, D_type_id, V_all_count, V_all_average,
                V_all_first, V_home_count, V_home_percentage, V_home_average, V_home_first, V_away_count, V_away_percentage, V_away_average, V_away_first,
                V_Total, V_0_15_count, V_0_15_percentage, V_15_30_count, V_15_30_percentage, V_30_45_count, V_30_45_percentage, V_45_60_count, V_45_60_percentage,
                V_60_75_count, V_60_75_percentage, V_75_90_count, V_75_90_percentage]
      # if len(outData) % 10 == 0:
      print(f"Working for entry {len(outData)}")
      outData.append(worker)

fn = os.path.join(path, "getData.xlsx")
print(f"Try to open excel in {fn}")
wb = xw.Book (fn)
ws = wb.sheets[0]
ws.range(f"A2:Z50000").value = None
ws.range(f"A2:Z50000").value = outData
ws.autofit()   

wb.save()
print(f"Program {os.path.basename(__file__)} finished - will close soon...") 
time.sleep(3) 