import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor

def find_ap(combination):
  actual = combination.sort_values("Share", ascending=False).head(5)
  predicted = combination.sort_values("predictions",ascending = False)
  ps = []
  found = 0
  seen = 1
  for index,row in predicted.iterrows():
    if row["Player"] in actual["Player"].values:
      found += 1
      ps.append(found/seen)
    seen += 1
  return sum(ps)/len(ps)


def add_ranks(predictions):
  predictions = predictions.sort_values("Share",ascending=False)
  predictions["Rk"] = list(range(1,predictions.shape[0]+1))
  predictions = predictions.sort_values("predictions",ascending=False)
  predictions["Predicted_Rk"] = list(range(1,predictions.shape[0]+1))
  predictions["Diff"] = predictions["Rk"] - predictions["Predicted_Rk"]
  return predictions


def backtest(stats, model, year, predictors):
  aps = []
  all_predictions = []
  for year in years[5:]:
    train = stats[stats["Year"] < year]
    test = stats[stats["Year"] == year]
    model.fit(train[predictors], train["Share"])
    predictions = model.predict(test[predictors])
    predictions = pd.DataFrame(predictions, columns=["predictions"],index=test.index)
    combination = pd.concat([test[["Player","Share"]],predictions], axis=1)
    combination = add_ranks(combination)
    all_predictions.append(combination)
    aps.append(find_ap(combination))
  return sum(aps)/len(aps), aps, pd.concat(all_predictions)

stats = pd.read_csv("stats.csv")
del stats["Unnamed: 0"]
stats = stats.fillna(0)

predictors = ['Age','G','GS','MP','FG','FGA','FG%','3P','3PA','3P%','2P','2PA','2P%','eFG%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','Year','W','L','W/L%','GB','PS/G','PA/G','SRS']
years = list(range(1991,2022))
reg = Ridge(alpha=.1)


stat_ratios = stats[["PTS","AST","STL","BLK","3P","Year"]].groupby('Year').apply(lambda x: x/x.mean())
stats[['PTS_T','AST_R','STL_R','BLK_R','3P_R']] = stat_ratios[['PTS',"AST","STL","BLK","3P"]]
predictors += ['PTS_T','AST_R','STL_R','BLK_R','3P_R']

stats["NPos"] = stats["Pos"].astype("category").cat.codes
stats["NTm"] = stats["Tm"].astype("category").cat.codes

rf = RandomForestRegressor(n_estimators=500, random_state=1, min_samples_split=5)

mean_ap, aps, all_predictions = backtest(stats, rf, years, predictors)

print(mean_ap)