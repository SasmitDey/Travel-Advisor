from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import requests
import streamlit as st
import time


#laoding environment variables
load_dotenv()
openweather_api_key=os.getenv('openweather_api_key')
gemini_api_key=os.getenv('gemini_api_key')
# system_instruction_analysis=os.getenv('system_instruction_analysis')
system_instruction_analysis="You are given a weather forecast for a number of days which is also\
provided for a city in json format.\
You are to give a travel advisory for ONLY that many number of days\
by analysing the data. Focus on overall days and not the time.\
You are also provided a list of some activities the traveller likes. Integrate\
these activities into your analysis. If the weather is good or bad for a particular activity from the list\
inform the traveller of the same.\
Do this in about 200 words in a blog post style. Nothing else.\
Ensure it is in a human readable language and looks like it is written by a human. Do not write \
words like 'analysis' and use more human words like 'thoughts'.\
DO NOT USE ANY UNRELATED SPECIAL CHARACTERS LIKE ASTERISKS (*) OR DOUBLE ASTERISKS (**).\
For time format, use the local time of the place provided.\
Finally, write a conclusion style final analysis paragraph in 100 words max.\
End off in a friendly note."



weather_data_attribution="Weather data provided by OpenWeather\n\
Hyperlink to our website https://openweathermap.org/ "

#initialising gemini model
client=genai.Client(
    api_key=gemini_api_key
)

tools=[]
tools.append(types.Tool(google_search=types.GoogleSearch))

# response=client.models.generate_content(
#     model='models/gemini-2.5-flash-preview-05-20',
#     contents='',
#     config=types.GenerateContentConfig(
#         tools=tools
#     )
# )
def get_image_url(city_name:str):
    response = client.models.generate_content(
        model='models/gemini-2.5-flash-preview-05-20',
        contents=f"Give one url for a high quality image about {city_name}. \
            Give only the url for an IMAGE, not a website, and nothing else.\
            Image link should be from unsplash",
        config=types.GenerateContentConfig(
            tools=tools,
        )
    )
    url=response.text
    return url


#getting latitude and longitude from city name (state only supported for usa)
def get_lat_lon(city_name:str):     #returns lat,long,cityName and country
    url='http://api.openweathermap.org/geo/1.0/direct'
    params={
        'q' : city_name,
        'appid' : openweather_api_key
    }
    req = requests.get(url,params=params)
    response = req.json()
    return response[0]['lat'], response[0]['lon'],response[0]['name'],response[0]['country']



def get_forecast(city_name:str):
    url='https://api.openweathermap.org/data/2.5/forecast'
    lat,lon,_,_=get_lat_lon(city_name)
    params={
        'lat':lat,
        'lon':lon,
        'appid':openweather_api_key,
        'units':'metric',
        'lang':'us_en'
    }
    req = requests.get(url,params=params)
    response = req.json()
    return response


def get_analysis(city_name:str,num_days:int,fav_activities:list[str]):
    _,_,city,country=get_lat_lon(city_name)
    response = client.models.generate_content_stream(
        model='models/gemini-2.5-flash-preview-05-20',
        contents=f"\
            Forecast data: {get_forecast(city_name)}\
            City Name: {city}\
            Country Code: {country}\
            Number of days: {num_days}\
            Favorite activities: {fav_activities}",
        config=types.GenerateContentConfig(
            tools=tools,
            # system_instruction=os.getenv('system_instruction_analysis')
            system_instruction=system_instruction_analysis
        )
    )
    for chunk in response:
        yield chunk.text
        time.sleep(0.02)



#streamlit app
st.header('🧳 AI POWERED TRAVEL ADVISOR')
st.set_page_config(
    page_title='AI Travel Advisor',
    page_icon='🧳',
    layout='wide'
)

st.sidebar.header('Your data')

city_name = st.sidebar.text_input(
    "City Name",
    value="New Delhi",
    help="Enter name of the city you want to travel to"
)

num_days = st.sidebar.slider("Number of days",0,5,2,help="Enter number of days you want to travel for")
activities = st.sidebar.text_input(
    "Favorite activities",
    value="Hiking Surfing Shopping...",
    help="Activities should be seperated by space."
)
fav_activities=activities.split(' ')


#write analysis
st.write_stream(
    get_analysis(
        city_name=city_name,
        num_days=num_days,
        fav_activities=fav_activities
    )
)



#chat feature not important - can remove
# with st.chat_message("user"):
#     chat = client.chats.create(
#         model="'models/gemini-2.5-flash-preview-05-20"
#     )
#     prompt = st.chat_input(placeholder="Your message",
#                   accept_file=False,
#                   width="stretch")
#     if prompt:
#         st.write(f"User: {prompt}")
#         response = chat.send_message(prompt)
#         st.write(response.text)




#work on implementing image
# img_url=get_image_url('new delhi')
# st.write(img_url)
# st.image(img_url)