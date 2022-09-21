'''

This script contains the functions for the power scaling calculations

Author: Will Guest
07/09/2021

'''

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

def reorganise(df):
    # Transpose the DataFrame, so that our header contains the account names
    df = df.transpose()

    # Rename the "Breakdown" column to "Date"
    cols = list(df.columns)
    df = df.set_axis(cols, axis='columns', inplace=False)
    return df

# extract data from table
def get_data_index(df, type):
    if type in df.columns:
       data = df[type].iloc[0]
       temp1 = str(data)
       temp2 = temp1[:(len(temp1) - 3)]
       data = int(temp2)
    else:
        data = 'No Data'
    return data

# reformat data for island data
def get_island_data(islands_data):
    count = 0
    for i in range(len(islands_data)):
        count = count + 1
        if islands_data.iloc[i][0] == 'South Island':
            break

    North_Island_raw = islands_data[:(count - 1)]
    North_Island = reorganise(North_Island_raw)
    new_header = North_Island.iloc[0]  # grab the first row for the header
    North_Island = North_Island[1:]  # take the data less the header row
    North_Island.columns = new_header  # set the header row as the df header
    North_Island = North_Island.drop(columns=['North Island'])


    South_Island_raw = islands_data[(count - 1):]
    South_Island = reorganise(South_Island_raw)
    new_header = South_Island.iloc[0]  # grab the first row for the header
    South_Island = South_Island[1:]  # take the data less the header row
    South_Island.columns = new_header  # set the header row as the df header
    South_Island = South_Island.drop(columns=['South Island'])

    return North_Island,South_Island


# get the capacity of each station
def get_capcity(generation_stations):

    # initialize types
    gas = 0
    co_gen = 0
    geothermal = 0
    hydro = 0
    gas_coal = 0
    diesel = 0
    wind = 0

    # find total capacity
    for i in range(len(generation_stations)):

        # gas
        if generation_stations['Name'].iloc[i] == 'gas':
            gas = gas + float(generation_stations['Capacity ('].iloc[i])

        # co_gen
        elif generation_stations['Name'].iloc[i] == 'co_gen':
            co_gen = co_gen + float(generation_stations['Capacity ('].iloc[i])

        # geothermal
        elif generation_stations['Name'].iloc[i] == 'geothermal':
            geothermal = geothermal + float(generation_stations['Capacity ('].iloc[i])

        # hydro
        elif generation_stations['Name'].iloc[i] == 'hydro':
            hydro = hydro + float(generation_stations['Capacity ('].iloc[i])

        # gas_coal
        elif generation_stations['Name'].iloc[i] == 'gas_coal':
            gas_coal = gas_coal + float(generation_stations['Capacity ('].iloc[i])

        # diesel
        elif generation_stations['Name'].iloc[i] == 'diesel':
            diesel = diesel + float(generation_stations['Capacity ('].iloc[i])

        # wind
        elif generation_stations['Name'].iloc[i] == 'wind':
            wind = wind + float(generation_stations['Capacity ('].iloc[i])

    return gas, co_gen, geothermal, hydro, gas_coal, diesel, wind


# get the capacity ratio of each station
def get_capacity_ratio(generation_stations,capacity_list, scaler):

    # initialize new column
    data = {'ratios': [0.00] * len(generation_stations)}
    ratios = pd.DataFrame(data, columns=['ratios'])

    # find total capacity
    for i in range(len(generation_stations)):

        # gas
        if generation_stations['Name'].iloc[i] == 'gas':
            ratios['ratios'].iloc[i] = (float((generation_stations['Capacity ('].iloc[i])/capacity_list[0]))*scaler

        # co_gen
        elif generation_stations['Name'].iloc[i] == 'co_gen':
            ratios['ratios'].iloc[i] = (float((generation_stations['Capacity ('].iloc[i])/capacity_list[1]))*scaler

        # geothermal
        elif generation_stations['Name'].iloc[i] == 'geothermal':
            ratios['ratios'].iloc[i] = (float((generation_stations['Capacity ('].iloc[i])/capacity_list[2]))*scaler

        # hydro
        elif generation_stations['Name'].iloc[i] == 'hydro':
            ratios['ratios'].iloc[i] = (float((generation_stations['Capacity ('].iloc[i]) / capacity_list[3]))*scaler

        # gas_coal
        elif generation_stations['Name'].iloc[i] == 'gas_coal':
            ratios['ratios'].iloc[i] = (float((generation_stations['Capacity ('].iloc[i])/capacity_list[4]))*scaler

        # diesel
        elif generation_stations['Name'].iloc[i] == 'diesel':
            ratios['ratios'].iloc[i] = (float((generation_stations['Capacity ('].iloc[i])/capacity_list[5]))*scaler

        # wind
        elif generation_stations['Name'].iloc[i] == 'wind':
            ratios['ratios'].iloc[i] = (float((generation_stations['Capacity ('].iloc[i])/capacity_list[6]))*scaler

    return ratios['ratios']

def current_gen_output(generation_stations,current_generation):

    # initialize new column
    data = {'current_output': [0.00] * len(generation_stations)}
    current_output = pd.DataFrame(data, columns=['current_output'])

    for i in range(len(generation_stations)):
        # North Island
        if generation_stations["island"].iloc[i] == 'north':
            # gas
            if generation_stations['Name'].iloc[i] == 'gas':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * float(current_generation[0])

            # co_gen
            elif generation_stations['Name'].iloc[i] == 'co_gen':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * float(current_generation[1])

            # geothermal
            elif generation_stations['Name'].iloc[i] == 'geothermal':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * float(current_generation[2])

            # hydro
            elif generation_stations['Name'].iloc[i] == 'hydro':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * (float(current_generation[3]) + float(current_generation[8]))

            # gas_coal
            elif generation_stations['Name'].iloc[i] == 'gas_coal':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * float(current_generation[4])

            # diesel
            elif generation_stations['Name'].iloc[i] == 'diesel':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * float(current_generation[5])

            # wind
            elif generation_stations['Name'].iloc[i] == 'wind':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * (float(current_generation[6]) + float(current_generation[7]))

        # South Island
        if generation_stations["island"].iloc[i] == 'south':
            # wind
            if generation_stations['Name'].iloc[i] == 'wind':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * (float(current_generation[6]) + float(current_generation[7]))

            # hydro
            elif generation_stations['Name'].iloc[i] == 'hydro':
                current_output['current_output'].iloc[i] = generation_stations['ratio'].iloc[i] * (float(current_generation[3]) + float(current_generation[8]))

    return current_output['current_output']

def calc_transmission_loss(network_od,coefficient):

    # initialize new column
    data = {'transmission_loss': [0.00] * len(network_od)}
    transmission_loss = pd.DataFrame(data, columns=['transmission_loss'])

    for i in range(len(transmission_loss)):
        transmission_loss['transmission_loss'].iloc[i] = (network_od["total_distance_km"].iloc[i] * float(coefficient)/1000)

    return transmission_loss['transmission_loss']