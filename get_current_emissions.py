
'''

This script calculates the generation spread New Zealand

Author: Will Guest
12/09/2021

'''

import pandas as pd

#-------------------------------------------------------------------------------------------------------------------------------------------------------
############### Pull data from Transpower

table_transpower = pd.read_html('https://www.transpower.co.nz/power-system-live-data')
islands_data = table_transpower[1]
islands_data.columns = ["Source", "Power"]

#-------------------------------------------------------------------------------------------------------------------------------------------------------
############# Function to extract data from table

def get_data_index(df, type):
    try:
        data = df["Power"].iloc[df[df["Source"] == type].index[0]]
        data = int(data[:(len(data) - 3)])
    except:
        data = -1
    return data

#-------------------------------------------------------------------------------------------------------------------------------------------------------
############# Pull values from tables

# Get data
wind = get_data_index(islands_data, 'Wind')
hydro = get_data_index(islands_data, 'Hydro')
geothermal = get_data_index(islands_data, 'Geothermal')
gas_coal = get_data_index(islands_data, 'Coal')
gas = get_data_index(islands_data, 'Gas')
diesel_oil = get_data_index(islands_data, 'Liquid')
co_gen = get_data_index(islands_data, 'Co-Gen')
battery = get_data_index(islands_data, 'Battery')

total = wind + hydro + geothermal + gas_coal + gas + diesel_oil + co_gen + battery

wind_percent = (wind/total)*100
hydro_percent = (hydro/total)*100
geothermal_percent = (geothermal/total)*100
gas_coal_percent = (gas_coal/total)*100
gas_percent = (gas/total)*100
diesel_oil_percent = (diesel_oil/total)*100
co_gen_percent = (co_gen/total)*100
battery_percent = (battery/total)*100

# print results
print('\n')
print("Wind :", wind, " MW,", " this accounts for ", round(wind_percent,2), "% of power generated")
print("Hydro :", hydro," MW,", " this accounts for ", round(hydro_percent,2), "% of power generated")
print("Geothermal :", geothermal, " MW,", " this accounts for ", round(geothermal_percent,2), "% of power generated")
print("Gas/Coal :", gas_coal," MW,", " this accounts for ", round(gas_coal_percent,2), "% of power generated")
print("Gas :", gas," MW,", " this accounts for ", round(gas_percent,2), "% of power generated")
print("Diesel/Oil :", diesel_oil," MW,", " this accounts for ", round(diesel_oil_percent,2), "% of power generated")
print("Co-Gen :", co_gen," MW,", " this accounts for ", round(co_gen_percent,2), "% of power generated")
print("Battery :", battery," MW,", " this accounts for ", round(battery_percent,2), "% of power generated")

#-------------------------------------------------------------------------------------------------------------------------------------------------------
############# Create table of g/CO2e/kWh

# data from https://ecotricity.co.nz/news/carbon-knowledge/
emissions_data = {'Wind':[7], 'Hydro':[15], 'Solar':[0], 'Geothermal':[99], 'Gas': [404], 'Co-Gen': [707], 'Coal':[921]}
emissions_table = pd.DataFrame(data = emissions_data)


#-------------------------------------------------------------------------------------------------------------------------------------------------------

############# Calculate emissions

weighted_ave = ((wind_percent/100)*emissions_table['Wind']) + ((hydro_percent/100)*emissions_table['Hydro']) + ((geothermal_percent/100)*emissions_table['Geothermal']) + ((gas_percent/100)*emissions_table['Gas']) + ((co_gen_percent/100)*emissions_table['Co-Gen'])

print('\n')
print(round(float(weighted_ave),1), "g/CO2/kWh currently")











