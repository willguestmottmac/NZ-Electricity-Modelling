# NZ-Electricity-Modelling

## get_current_emissions.py
This tool pulls the real-time data of the New Zealand Electricity Generation spread from https://www.transpower.co.nz/power-system-live-data
then based of https://ecotricity.co.nz/news/carbon-knowledge/ calculates the current g/CO2/kWh.

Example output for 21/09/2022 19:56pm
![1](https://user-images.githubusercontent.com/84685671/191448475-12801b7f-59e4-4a48-aa93-4445b62edecb.jpg)


## get_emissions_from_location.py
This tool calculates C02 output based off the a location taking into account the energy spread + transmission linelosses through calculation of the closest node to a location.

Example output:
![2](https://user-images.githubusercontent.com/84685671/191448658-57de62b7-f4e6-436d-8fc9-4ea51508e49d.jpg)


