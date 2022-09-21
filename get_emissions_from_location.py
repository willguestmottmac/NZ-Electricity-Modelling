'''

This script calculates C02 output based off the a location
taking into account the energy spread + transmission line
losses through calculation of the closest node to a location

Author: Will Guest
12/09/2021

'''

import geopandas as gpd
import geopy as gpy
import geopy.distance as distance
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import shapely as shp
from shapely import wkt
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
import haversine as hs
import shapely.wkt
import datetime

# power consumption calcs
daily_power_usage = 2800 #kWh

# input address
address = "Victoria Street &, Federal Street, Auckland CBD, Auckland, New Zealand"

# pull Lat, Long of address
locator = gpy.Nominatim(user_agent="regional_locator_app")
location = locator.geocode(address)

df = pd.DataFrame({'Address': [address],
                   'Latitude': [location.latitude],
                   'Longitude': [location.longitude]})


# Load address as node, and load network nodes
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
nodes = gpd.read_file('data/exports/WORKING_NODES_2.gpkg')


# Get nearest node
def get_nearest_values(row, other_gdf, point_column='geometry', value_column="geometry"):
    """Find the nearest point and return the corresponding value from specified value column."""

    # Create an union of the other GeoDataFrame's geometries:
    other_points = other_gdf["geometry"].unary_union

    # Find the nearest points
    nearest_geoms = nearest_points(row[point_column], other_points)

    # Get corresponding values from the other df
    nearest_data = other_gdf.loc[other_gdf["geometry"] == nearest_geoms[1]]


    return nearest_data

gdf["nearest_loc"] = gdf.apply(get_nearest_values, other_gdf=nodes, point_column="geometry", value_column="id", axis=1)

# Find distance from address to nearest node (Haversine method)
start = str(gdf['geometry'].iloc[0]).replace('POINT (', '').replace(')','').split(' ')
start = (float(start[1]),float(start[0]))

end = str(gdf["nearest_loc"].iloc[0].iloc[0].geometry).replace('POINT (', '').replace(')','').split(' ')
end = (float(end[1]),float(end[0]))

distance = hs.haversine(start,end)

# Get collective power outputs to node
closest_node_id = gdf["nearest_loc"].loc[0].index[0]

# import network distance data
network_od = pd.read_csv('data/exports/test/08_09_2021/network_od.csv')
generation_stations = pd.read_csv('data/exports/test/08_09_2021/generation_stations.csv')

closest_network = network_od[network_od['origin'] == closest_node_id]


# initialize new column
data = {'current_output': [0.00] * len(closest_network)
        , 'description' : ['0'] * len(closest_network)
        , 'location' : ['0'] * len(closest_network)
        , 'island' : ['0'] * len(closest_network)}
current_output = pd.DataFrame(data, columns=['current_output', 'description', 'location', 'island'])

# allocate power losses to closest node
for i in range(len(closest_network)):
    for j in range(len(generation_stations)):
        if closest_network['destination_id'].iloc[i] == generation_stations['id'].iloc[j]:
            current_output['current_output'].iloc[i] = generation_stations['current_output(MW)'].iloc[j]
            current_output['description'].iloc[i] = generation_stations['Name'].iloc[j]
            current_output['location'].iloc[i] = generation_stations['location'].iloc[j]
            current_output['island'].iloc[i] = generation_stations['island'].iloc[j]

# add to closest node
closest_network['current_output(MW)'] = list(current_output['current_output'])
closest_network['description'] = list(current_output['description'])
closest_network['location'] = list(current_output['location'])
closest_network['island'] = list(current_output['island'])

# DRY WEATHER USED
closest_network['total'] =  closest_network['current_output(MW)'] + closest_network['dry_weather_transmission_losses']
closest_network.to_csv('data/exports/test/08_09_2021/closest_network.csv', encoding='utf-8')




# "The average corona losses on several lines ... gave 1 to 20 kW/km in fair weather # (20 - 1)/2 = 10 kW/km
dry_weather_coefficient = 10
#"... In foul-weather, the losses can go up to 300 kW/km # (300 - 20)/2 = 140 kW/km
wet_weather_coefficient = 140

#group by
summary = closest_network.groupby('description')['total'].sum().reset_index()

summary = summary.append({'description' :'transmission_loss','total':(dry_weather_coefficient/1000)*distance}
                         , ignore_index=True)



# calculate time from start
now = datetime.datetime.now()

date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
year_now = date_time[:(len(date_time)-10)]
hour_now = date_time[(len(date_time)-8):]

time_str = year_now + ', ' + generation_stations["time"].iloc[1] + ':00'

time = datetime.datetime.strptime(time_str, '%m/%d/%Y, %H:%M:%S')

start_time_str = year_now + ', ' + '00:00:00'
start_time = datetime.datetime.strptime(start_time_str, '%m/%d/%Y, %H:%M:%S')

total_hours = ((abs(start_time - time).seconds)/3600)

kwh_usage_to_hour = daily_power_usage * (total_hours/24)


# data from https://ecotricity.co.nz/news/carbon-knowledge/
# https://www.volker-quaschning.de/datserv/CO2-spez/index_e.php
# g/Co2e/kwh
emissions_data = {'Wind':[7], 'Hydro':[15], 'Diesel':[267], 'Geothermal':[88], 'Gas': [416], 'Co-Gen': [416], 'Coal':[1073]}
emissions_table = pd.DataFrame(data = emissions_data)


gen_sum = summary['total'].sum()

summary['ratio'] = summary['total']/gen_sum

summary['CO2'] = list([(float(summary['total'].iloc[0])*1000)*float(emissions_data['Co-Gen'][0])
 ,(float(summary['total'].iloc[1])*1000)*float(emissions_data['Diesel'][0])
 ,(float(summary['total'].iloc[2])*1000)*float(emissions_data['Gas'][0])
 ,(float(summary['total'].iloc[3])*1000)*float(emissions_data['Coal'][0])
 ,(float(summary['total'].iloc[4])*1000)*float(emissions_data['Geothermal'][0])
 ,(float(summary['total'].iloc[5])*1000)*float(emissions_data['Hydro'][0])
 ,(float(summary['total'].iloc[6])*1000)*float(emissions_data['Wind'][0])
 ,0])

sum_co2 = (summary['CO2'].sum())*summary['ratio'].iloc[7]
summary['CO2'].iloc[7] = sum_co2


CO2_consumption_g = (kwh_usage_to_hour/gen_sum)*(summary['CO2'].sum())
print('\n')
print('Total Generation: ', round(summary['total'].sum(), 2), ' (MW)')
print('Location: ', address)
print('Distance to nearest node: ', round(distance, 2),  ' Km')
print('As of time: ', time)
print(round((CO2_consumption_g/1000), 2), 'kg of CO2 today')


