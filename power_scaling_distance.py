'''

This script calculates the weight related to the power consumption
including transmission losses from transpower data

Author: Will Guest
07/09/2021

'''

import pandas as pd
import lxml
import geopandas as gpd
import branca
from string import Template as Templ
import power_scaling_functions as psf


# Pull Transpower Data from https://www.transpower.co.nz/power-system-live-data
table_transpower = pd.read_html('https://www.transpower.co.nz/power-system-live-data')
islands_data = table_transpower[1]

# https://en.wikipedia.org/wiki/Electricity_sector_in_New_Zealand
# Installed capacity (MW) in New Zealand, 31 December 2020
capacity_2021 = 9448


# get island data
North_Island, South_Island = psf.get_island_data(islands_data)

# Get data

# North Island
north_wind = psf.get_data_index(North_Island, 'Wind')
north_hydro = psf.get_data_index(North_Island, 'Hydro')
north_geothermal = psf.get_data_index(North_Island, 'Geothermal')
north_gas_coal = psf.get_data_index(North_Island, 'Gas/Coal')
north_gas = psf.get_data_index(North_Island, 'Gas')
north_diesel_oil = psf.get_data_index(North_Island, 'Diesel/Oil')
north_co_gen = psf.get_data_index(North_Island, 'Co-Gen')

# South Island
south_wind = psf.get_data_index(South_Island, 'Wind')
south_hydro = psf.get_data_index(South_Island, 'Hydro')

# totals
gen_north_total = north_wind + north_hydro + north_geothermal + north_gas_coal + north_gas + north_diesel_oil + north_co_gen
gen_south_total = south_wind + south_hydro
gen_total = gen_north_total + gen_south_total
time = islands_data.columns[1]


# generation stations power requirements
nodes = gpd.read_file('data/exports/WORKING_NODES_2.gpkg')
generation_stations = nodes[nodes['location'] != 'line']

# get total capacities for each type from station data
gas_cap, co_gen_cap, geothermal_cap, hydro_cap, gas_coal_cap, diesel_cap, wind_cap = psf.get_capcity(generation_stations)
total_capacity = int(gas_cap + co_gen_cap + geothermal_cap + hydro_cap + gas_coal_cap + diesel_cap + wind_cap)

# recalibrate total capacities to Installed capacity (MW) in New Zealand, 31 December 2020
# https://en.wikipedia.org/wiki/Electricity_sector_in_New_Zealand
print(total_capacity)
print(capacity_2021)
print(gen_total)

'''
Installed capacity (MW) in New Zealand, 31 December 2020

Fuel	        Capacity	%
Hydroelectric	5,400	    57%
Gas	            1,245	    13%
Geothermal	    991	        10%
Wind	        689	        7%
Coal/gas	    500	        5%
Cogen	        398	        4%
Diesel	        191	        2%
Other	        34	        <1%
Total	        9,448	    -
'''

# get total ratios for each site
'''
capacity_list = [((gas_cap*1245)/gas_cap)
    , ((co_gen_cap*398)/co_gen_cap)
    , ((geothermal_cap*991)/geothermal_cap)
    , ((hydro_cap*5400)/hydro_cap)
    , ((gas_coal_cap*500)/gas_coal_cap)
    , ((diesel_cap*191)/diesel_cap)
    , ((wind_cap*689)/wind_cap)]
'''
capacity_list = [gas_cap, co_gen_cap, geothermal_cap, hydro_cap, gas_coal_cap, diesel_cap, wind_cap]

scaler = 1 #(capacity_2021/total_capacity)

generation_stations["ratio"] = list(psf.get_capacity_ratio(generation_stations,capacity_list, scaler))

print(generation_stations["ratio"].sum())

# get current transpower calc time and add to generation_stations
generation_stations["time"] = time[(len(time) - 5):]


# assign current power output to each node
current_generation_list = [north_gas, north_co_gen, north_geothermal, north_hydro, north_gas_coal, north_diesel_oil, north_wind, south_wind, south_hydro]
generation_stations["current_output(MW)"] = list(psf.current_gen_output(generation_stations,current_generation_list))


print(generation_stations["current_output(MW)"].sum())

# import network distance data
network_od = pd.read_csv('data/exports/total_distance_matrix.csv')

node_min = network_od["origin"].iloc[0]
node_max = network_od["origin"].iloc[len(network_od["origin"])-1]


#https://www.linkedin.com/pulse/corona-concept-formulae-ahsan-mahmood/
# account for corona losses

# "The average corona losses on several lines ... gave 1 to 20 kW/km in fair weather # (20 - 1)/2 = 10 kW/km
dry_weather_coefficient = 10
#"... In foul-weather, the losses can go up to 300 kW/km # (300 - 20)/2 = 140 kW/km
wet_weather_coefficient = 140

# add to network transmission power losses (MW)
network_od["dry_weather_transmission_losses"] = list(psf.calc_transmission_loss(network_od,dry_weather_coefficient))
network_od["wet_weather_transmission_losses"] = list(psf.calc_transmission_loss(network_od,wet_weather_coefficient))

network_od.to_csv('data/exports/test/08_09_2021/network_od.csv', encoding='utf-8')
generation_stations.to_csv('data/exports/test/08_09_2021/generation_stations.csv', encoding='utf-8')


