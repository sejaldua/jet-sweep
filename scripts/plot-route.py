import pandas as pd
import folium
import matplotlib.pyplot as plt

arena_df = pd.read_csv('../inputs/arena_info.csv')
abbrev_df = pd.read_csv('../inputs/abbreviations.csv')
arena_df = pd.merge(left=arena_df, right=abbrev_df, left_on='Team', right_on='Franchise')
arena_df.loc[len(arena_df)] = ['Home', 40.7590, -73.9761, '', '', '', '', 'Home', 'Home', 'Home', 'Home', 'Home', 'Home']

avg_location = arena_df[['Latitude', 'Longitude']].mean()
m = folium.Map(location=avg_location, zoom_start=4)

data = []
df = pd.read_csv('../outputs/solved_route.csv').set_index('Unnamed: 0')
dates = df.max(axis=1).unique()
dates = sorted([pd.to_datetime(x) for x in dates])
for d in dates:
    date_str = str(d)[:10]
    for idx, row in df.iterrows():
        for col in df.columns:
            if row[col] == date_str:
                data.append([d, col, idx])
route_df = pd.DataFrame(data, columns = ['Date', 'Source', 'Destination'])
route_df = pd.merge(left=route_df, right=arena_df[['Team', 'Commonly Used Abbreviations', 'Latitude', 'Longitude']], 
                    left_on='Source', right_on='Commonly Used Abbreviations')
route_df = pd.merge(left=route_df, right=arena_df[['Team', 'Commonly Used Abbreviations', 'Latitude', 'Longitude']], 
                    left_on='Destination', right_on='Commonly Used Abbreviations')
route_df.to_csv('final_route.csv', index=False)

# find the corresponding subset of the NFL schedule that we will be attending
schedule = pd.read_csv('../inputs/schedule.csv')
schedule['Date'] = pd.to_datetime(schedule['Date'])
sked_subset = pd.merge(left=route_df, right=schedule, left_on=['Date', 'Commonly Used Abbreviations_y'], right_on=['Date', 'Home Abbrev'])
sked_subset.to_csv('../outputs/itinerary.csv', index=False)

for idx, row in route_df.iterrows():
    # marker for current stop
    marker = folium.Marker(location=(row['Latitude_x'], row['Longitude_x']),
                           tooltip=f"{row['Team_x']}\n\n{row['Date']}")
    # line for the route segment connecting current to next stop
    line = folium.PolyLine(
        locations=[(row['Latitude_x'], row['Longitude_x']), 
                   (row['Latitude_y'], row['Longitude_y'])],
        tooltip=f"{row['Team_x']} >>> {row['Team_y']}",
    )
    # add elements to the map
    marker.add_to(m)
    line.add_to(m)

m.save("../outputs/map.html")