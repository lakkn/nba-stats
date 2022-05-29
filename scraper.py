import requests
from bs4 import BeautifulSoup as bs 
import pandas as pd
from selenium import webdriver

def scrape_mvps():
  years = list(range(1991,2022))
  base_url = 'https://www.basketball-reference.com/awards/awards_{}.html'
  for year in years:
    url = base_url.format(year)
    data = requests.get(url)
    
    with open("mvp/{}.html".format(year), 'w+') as file:
      file.write(data.text)
  mvps = []
  for year in years:
    with open("mvp/{}.html".format(year)) as file:
      page = file.read()
    soup = bs(page, 'html.parser')
    soup.find('tr',class_="over_header").decompose()
    table = soup.find_all(id="mvp")
    mvp_table = pd.read_html(str(table))[0]
    mvp_table["Year"] = year
    mvps.append(mvp_table)
  mvp = pd.concat(mvps)
  mvp.to_csv("mvps.csv")

players = []
for year in range(1991,2022):
  with open("player/{}.html".format(year)) as f:
    page = f.read()
  soup = bs(page, 'html.parser')
  soup.find('tr',class_="thead").decompose()
  table = soup.find_all(id="per_game_stats")
  player_table = pd.read_html(str(table))[0]
  player_table["Year"] = year
  players.append(player_table)
player = pd.concat(players)
player.to_csv("players.csv")