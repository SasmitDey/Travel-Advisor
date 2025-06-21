from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import requests
import streamlit as st
import time
import pandas as pd


#laoding environment variables
# load_dotenv()
# openweather_api_key=os.getenv('openweather_api_key')
# gemini_api_key=os.getenv('gemini_api_key')

gemini_api_key=st.secrets["gemini_api_key"]
openweather_api_key=st.secrets["openweather_api_key"]
system_instruction_analysis=st.secrets["model"]["system_instruction_analysis"]
system_instruction_itenary=st.secrets["model"]["system_instruction_itenary"]


# system_instruction_analysis=os.getenv('system_instruction_analysis')



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
            system_instruction=system_instruction_analysis
        )
    )
    for chunk in response:
        yield chunk.text
        time.sleep(0.02)


def get_itenary(city_name:str,num_days:int,fav_activities:list[str]):
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
            system_instruction=system_instruction_itenary
        )
    )
    for chunk in response:
        yield chunk.text
        time.sleep(0.02)









#streamlit app
st.header('🧳 Your Custom Trip Companion')
st.markdown("<hr style='border: 2px solid #333;'>", unsafe_allow_html=True)
st.set_page_config(
    page_title='AI Travel Advisor',
    page_icon='🧳',
    layout='wide',
    initial_sidebar_state="expanded"
)


#sidebar customisation
st.sidebar.header('Trip Details')
with st.form(key="trip_details"):
    city_name = st.sidebar.text_input(
        "Where are you headed?",
        value="New Delhi",
        help="Enter name of the city you want to travel to"
    )


#parameters for model
lat,lon,_,_=get_lat_lon(city_name)
num_days = st.sidebar.slider("How many days?",0,5,2,help="Enter number of days you want to travel for")
activities = st.sidebar.text_input(
    "Things you love to do",
    value="Hiking Surfing Shopping",
    help="Activities should be seperated by space"
)
fav_activities=activities.split(' ')


#write analysis
# st.write_stream(
#     get_analysis(
#         city_name=city_name,
#         num_days=num_days,
#         fav_activities=fav_activities
#     )
# )


map_data = {
    'lat' : [lat],
    'lon' : [lon],
}
map_data_df = pd.DataFrame(map_data)



#button for submitting info
if st.sidebar.button("Submit", type="secondary"):
    st.map(
        map_data_df,
        zoom=12,
        size=0.0,
        height=350
    )
    # st.header("☁Your weather forecast analysis☁")
    st.header("☀️ Weather Outlook for Your Trip")
    with st.spinner(f"Thinking..."):
        st.write_stream(get_analysis(
            city_name=city_name,
            num_days=num_days,
            fav_activities=fav_activities
        ))
    st.markdown("<hr>", unsafe_allow_html=True)
    # st.header("✈Your travel itenary")
    st.header("📅 Your Itinerary")
    with st.spinner(f"Preparing itenary..."):
        st.write_stream(get_itenary(
            city_name=city_name,
            num_days=num_days,
            fav_activities=fav_activities
        ))



#crediting openweather api
st.markdown(
    """
    <style>
    .footer {
        position: absolute;
        bottom: 0;
        right: 10px;
        font-size: 9px;
        color: gray;
    }
    </style>
    <div class="footer">
        Weather data provided by OpenWeather<br>
        https://openweathermap.org/ 
    </div>
    """, 
    unsafe_allow_html=True
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