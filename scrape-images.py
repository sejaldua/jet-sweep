import pandas as pd
from bs4 import BeautifulSoup
import requests
pd.options.display.max_columns = None
 
# get URL
page = requests.get("https://www.foxsports.com/nfl/teams")
# scrape webpage
soup = BeautifulSoup(page.content, 'html.parser')
base_url = "https://b.fssta.com/uploads/application/nfl/team-logos/"
divs = soup.findAll('div', class_='image-wrapper')
for div in divs:
    img = div.find('img')['src']
    url_str = img[len(base_url):].split('.')[0]
    with open(f'logos/{url_str}.png', 'wb') as f:
        f.write(requests.get(img).content)