import requests
import openmeteo_requests
import requests_cache
import pandas as pd
import os
from retry_requests import retry
import matplotlib.pyplot as plt
import seaborn as sns


#APIs used: 
#Coordinates by name of the city: https://api-ninjas.com/api/geocoding (to get an API key -> https://api-ninjas.com/profile)
#Weather data: https://open-meteo.com/


def city_name():
    city = input('Write down the name of the city: ')
    api_url = 'https://api.api-ninjas.com/v1/geocoding?city={}'.format(city)
    headers = {'X-Api-Key': '3YABZB7wg3eWM0ZXU1wbTg==Ir2rdPdjGPPTWZSz'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == requests.codes.ok:
        data = response.json()
        city_number = 0
        if data == []:
            print('The city with such name was not found.')
            print('Try again!')
            return city_name()
        else:
            if len(data) == 1:
              # Adding the name of the city as a key to a dicitonary and list with longitude and latitude as a corresponding parameter
                city_coordinates[data[0]['name']] = [data[0]['latitude'], data[0]['longitude']]
          
                question = input('Would you like to compare it with another city? ').upper()
                if question in ['YES', 'Y', 'SURE', 'YEP', 'YEA']:
                    return city_name()
                else:
                    return city_coordinates
            print(f'{len(data)} results were found:\n')
            for i, city_found in enumerate(data):
              if 'state' in data[i]:
                print(f"{i+1}. Name: {data[i]['name']}, Country: {data[i]['country']}, State: {data[i]['state']}")
              else:
                print(f"{i+1}. Name: {data[i]['name']}, Country: {data[i]['country']}")
            print()
            question = input('Is the city you meant in the list? ').upper()
            if question not in ['YES', 'Y', 'SURE', 'YEP', 'YEA']:
              return city_name()
            while True:
                while True:
                  try:
                    city_number = int(input('Write down the number that corresponds to your city: '))
                    print()
                    break
                  except ValueError:
                    print('This is an invalid character')
                if city_number in range(1, len(data)+ 1):
                  # Adding the name of the city as a key to a dicitonary and list with longitude and latitude as a corresponding parameter
                    city_coordinates[data[city_number-1]['name']] = [data[city_number-1]['latitude'], data[city_number-1]['longitude']]
                    question = input('Would you like to compare it with another city? ').upper()
                    if question in ['YES', 'Y', 'SURE', 'YEP', 'YEA']:
                        return city_name()
                    else:
                        return city_coordinates
                else:
                    print('The number is out of range')
                    print('Try again')
    else:
        print("Error:", response.status_code, response.text)

def city_coordinates_function():
  while True:
    try: 
      latitude = float(input('Write down the latitude: '))
      longitude = float(input('Write down the longitude: '))
      if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
        print('Latitude should be in range from -90 to 90, and longitude from -180 to 180.')
        print('Try again!\n')
        continue
      break
    except:
      print('You have to write a float number for latitude and longitude.')
      print('Try again!\n')
  city_coordinates[f'Coordinates{len(city_coordinates) + 1}'] = [latitude, longitude]
  question = input('Would you like to compare it with another set of coordinates? ').upper()
  if question in ['YES', 'Y', 'SURE', 'YEP', 'YEA']:
      return city_coordinates_function()
  else:
      return city_coordinates


def storing_results(folder_path):
    os.makedirs(folder_path, exist_ok=True)

    for file_name, fig in plots.items():
        unique_file_name = get_unique_filename(folder_path, file_name)  
        file_path = os.path.join(folder_path, unique_file_name)  
        fig.savefig(file_path, dpi=300, bbox_inches="tight")
        plt.close(fig) 

def get_unique_filename(folder_path, file_name):

    base_name, ext = os.path.splitext(file_name) 
    counter = 1
    unique_file_name = file_name  

    while os.path.exists(os.path.join(folder_path, unique_file_name)):
        unique_file_name = f"{base_name}_{counter}{ext}"
        counter += 1  

    return unique_file_name


city_coordinates = {}

while True:
    try:
        question = int(input('Write down number "1" if you would like to use coordinates, or if you would like to use city name - "2": '))
        if question == 1 or question == 2:
            break  #
        else:
            print('Please enter either "1" or "2"')
    except ValueError:
        print('This is an invalid character')

if question == 2:
  city_name()
else:
   city_coordinates_function()


print(city_coordinates)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

url = "https://archive-api.open-meteo.com/v1/archive"

daily_dataframes = []
for coordinates in city_coordinates.values():
	#print(city_coordinates[0])
	#print(city_coordinates[1])
   
	params = {
		"latitude": coordinates[0],
		"longitude": coordinates[1],
		"start_date": "2023-01-01",
		"end_date": "2024-01-01",
		"daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "rain_sum", "snowfall_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"],
		"wind_speed_unit": "ms",
		"timezone": "Europe/Berlin"
	}
	
 
	responses = openmeteo.weather_api(url, params=params)
	

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	#print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
	#print(f"Elevation {response.Elevation()} m asl")
	#print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
	#print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
	daily_temperature_2m_mean = daily.Variables(2).ValuesAsNumpy()
	daily_sunrise = daily.Variables(3).ValuesAsNumpy()
	daily_sunset = daily.Variables(4).ValuesAsNumpy()
	daily_daylight_duration = daily.Variables(5).ValuesAsNumpy()
	daily_sunshine_duration = daily.Variables(6).ValuesAsNumpy()
	daily_rain_sum = daily.Variables(7).ValuesAsNumpy()
	daily_snowfall_sum = daily.Variables(8).ValuesAsNumpy()
	daily_wind_speed_10m_max = daily.Variables(9).ValuesAsNumpy()
	daily_wind_direction_10m_dominant = daily.Variables(10).ValuesAsNumpy()
	daily_weather_code = daily.Variables(0).ValuesAsNumpy()

	daily_data = {"date": pd.date_range(
		start = pd.to_datetime(daily.Time(), unit = "s"),
		end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min
	daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
	daily_data["sunrise"] = daily_sunrise
	daily_data["sunset"] = daily_sunset
	daily_data["daylight_duration"] = daily_daylight_duration
	daily_data["sunshine_duration"] = daily_sunshine_duration
	daily_data["rain_sum"] = daily_rain_sum
	daily_data["snowfall_sum"] = daily_snowfall_sum
	daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
	daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
	daily_data["weather_code"] = daily_weather_code
  
	daily_dataframes.append(pd.DataFrame(data = daily_data))
  

#==================================================================================================================
#Adjustments/clearing/prepation


#Light rain: Less than 0.5 mm per hour.
#Moderate rain: Greater than 0.5 mm per hour, but less than 4.0 mm per hour.
#Heavy rain: Greater than 4 mm per hour, but less than 8 mm per hour. 	
#Very heavy rain: Greater than 8 mm per hour.

rows = []
for city_number, df in enumerate(daily_dataframes):
    new_row = {'city': list(city_coordinates.keys())[city_number],
               'Negligible': ((df['rain_sum'] < 0.01) | pd.isnull(df['rain_sum'])).sum(),
      				 'Light': ((0.01 <= df['rain_sum']) & (df['rain_sum'] < 0.5)).sum(),
               'Moderate': ((0.5 <= df['rain_sum']) & (df['rain_sum'] < 4.0)).sum(),
               'Heavy': ((4.0 <= df['rain_sum']) & (df['rain_sum']  < 8.0)).sum(),
               'Extreme': (df['rain_sum'] >= 8.0).sum(),
               }
    rows.append(new_row)

raining_df = pd.DataFrame(rows)
raining_df = pd.melt(raining_df, id_vars=['city'], var_name='rain_intensity', value_name='days')


#Light snow: Less then 1.3 cm per hour.
#Moderate snow: Greater than 1.3 cm per hour, but less than 2.5 cm per hour.
#Heavy snow: Greater than 2.5 cm.

rows = []
for city_number, df in enumerate(daily_dataframes):
  new_row = new_row = {'city': list(city_coordinates.keys())[city_number],
               'Negligible': ((df['snowfall_sum'] < .2) | pd.isnull(df['snowfall_sum'])).sum(),
      				 'Light': ((.2 <= df['snowfall_sum']) & (df['snowfall_sum'] < 1.3)).sum(),
               'Moderate': ((1.3 <= df['snowfall_sum']) & (df['snowfall_sum'] < 2.5)).sum(),
               'Heavy': (df['snowfall_sum'] >= 2.5).sum(),
               }
  rows.append(new_row)
  
snowfall_df = pd.DataFrame(rows)
snowfall_df = pd.melt(snowfall_df, id_vars=['city'], var_name='rain_intensity', value_name='days')

#========================================================================================================================
#Plotting 

plots = {}

#Plotting Mean temperatures

sns.set_theme()

fig, ax = plt.subplots(figsize=(10, 6)) 

for city_number, df in enumerate(daily_dataframes):
	ax.plot(df['date'],
          df['temperature_2m_mean'],
          label=f'Mean Temp: {list(city_coordinates.keys())[city_number]}')
 

ax.set_xlabel('Date')
ax.set_ylabel('Temperature (°C)')
ax.legend()
plots["mean_temperature_plot.png"] = fig


#Plotting number of raining days depending on the intensity of the rain. 
fig, ax = plt.subplots(figsize=(12, 15))
bars = sns.barplot(data=raining_df, x='rain_intensity', y='days', hue='city')

for bar in bars.patches:
    height = bar.get_height()
    if height != 0:
        ax.text(bar.get_x() + bar.get_width() / 2, height, int(height), ha='center', va='bottom')

ax.set_ylabel('Number Of Days')
ax.set_xlabel('Rain Intensity')
plots["rain_intensity_plot.png"] = fig


#Plotting number of snowfall days depending on the intensity of the snow. 
fig, ax = plt.subplots(figsize=(10, 6))
bars = sns.barplot(data=snowfall_df, x='rain_intensity', y='days', hue='city')

for bar in bars.patches:
    height = bar.get_height()
    if height != 0:
        ax.text(bar.get_x() + bar.get_width() / 2, height, int(height), ha='center', va='bottom')

ax.set_ylabel('Number Of Days')
ax.set_xlabel('Snowfall Intensity')
plots["snowfall_intensity_plot.png"] = fig



#========================================================================================================================
# Storing the results

storing_resutls = input('Would you like to store the results? Use 1 for yes and 0 otherwise: ')
if storing_resutls == '1':
  folder_path = input('Write down the path to the folder where you would like to store the results: ')
  storing_results(folder_path)

