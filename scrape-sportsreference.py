import pandas as pd
from bs4 import BeautifulSoup
import requests
pd.options.display.max_columns = None
 
# get URL
page = requests.get("https://www.pro-football-reference.com/years/2024/games.htm")
 
# scrape webpage
soup = BeautifulSoup(page.content, 'html.parser')
 
# grab table values
table = soup.find('table', id="games")
tbody = table.find('tbody')
data = []
for i, row in enumerate(tbody.findAll('tr')):
    if row.find('th').getText().strip() == 'Week':
        continue
    data.append([row.find('th').getText().strip(), *[col.getText().strip() for col in row.findAll('td')]])
df = pd.DataFrame(data, columns = ['Week', 'Day', 'Date', 'Away', 'Away PTS', '@', 'Home', 'Home PTS', 'Time'])

# convert dates to pandas datetime object
df['Date'] = df['Date'].apply(lambda x: pd.to_datetime(f'{x} {"2024" if "January" not in x else "2025"}'))

# remove pre-season games
df = df[~df['Week'].isin(['Pre0', 'Pre1', 'Pre2', 'Pre3'])]

print(f'There are {df.shape[0]} NFL games this season')
df.to_csv('schedule.csv', index=False)