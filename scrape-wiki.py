import pandas as pd
from bs4 import BeautifulSoup
import requests
from geopy.distance import geodesic
from lat_lon_parser import parse
pd.options.display.max_columns = None
 
# get URL
page = requests.get("https://en.wikipedia.org/wiki/List_of_current_NFL_stadiums#Map_of_current_stadiums")
 
# scrape webpage
soup = BeautifulSoup(page.content, 'html.parser')
 
table = soup.findAll('table')[1]
tbody = table.find('tbody')
data = []
for i, row in enumerate(tbody.findAll('tr')):
    if i == 0:
        continue
    stadium = row.find('th')
    link = stadium.find('a')['href']
    soup2 = BeautifulSoup(requests.get(f'https://en.wikipedia.org{link}').content, 'html.parser')
    loc = soup2.find('span', class_='geo-dms')
    lat = parse(loc.find('span', class_='latitude').getText())
    lng = parse(loc.find('span', class_='longitude').getText())
    data.append([row.find('th').getText().strip(), lat, lng, *[col.getText().strip() for col in row.findAll('td')]])

COLUMNS = ['Stadium', 'Latitude', 'Longitude', 'Blank', 'Capacity', 'City', 'Surface', 'Roof Type', 'Team', 'Opened', 'Ref']
df = pd.DataFrame(data, columns = COLUMNS)
df = df[[col for col in df.columns if col not in ['Blank', 'Ref']]]
df['Team Name'] = df['Team'].apply(lambda x: x.split(' ')[-1])
df.to_csv('arena_info.csv')
