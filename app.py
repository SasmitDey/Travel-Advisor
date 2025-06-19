from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import requests


#laoding environment variables
load_dotenv()
openweather_api_key=os.getenv('openweather_api_key')
gemini_api_key=os.getenv('gemini_api_key')



#initialising gemini model
client=genai.Client(
    api_key=gemini_api_key
)

tools=[]
tools.append(types.Tool(google_search=types.GoogleSearch))

response=client.models.generate_content(
    model='models/gemini-2.5-flash-preview-05-20',
    contents='',
    config=types.GenerateContentConfig(
        tools=tools
    )
)


#getting latitude and longitude from city name (state only supported for usa)
def get_lat_lon(city_name:str):
    url='http://api.openweathermap.org/geo/1.0/direct'
    params={
        'q' : city_name,
        'appid' : openweather_api_key
    }
    req = requests.get(url,params=params)
    response = req.json()
    return response[0]['lat'], response[0]['lon']


def get_forecast(lat:float, lon:float):
    print()