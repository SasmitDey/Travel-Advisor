from google import genai
from google.genai import types
import os
from dotenv import load_dotenv


#laoding environment variables
load_dotenv()
openweather_api_key=os.getenv('openweather_api_key')
gemini_api_key=os.getenv('gemini_api_key')




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
print(response.text)