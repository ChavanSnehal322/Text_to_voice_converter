

import os
import flet as ft               # pip install flet
import requests

from murf import Murf           # import class from murf api
# from api_key import API_KEY     # Store api key of Murf.ai from documentation

from dotenv import load_dotenv

# loading API key from .env
load_dotenv()
API_KEY = os.getenv("MURF_API_KEY")  # Making API_KEY is available


# creating API client
client = Murf(api_key = "ap2_6a435a76-9ed5-4579-bce8-6cb0bfc0d33f") 


voices = client.text_to_speech.get_voices()     
# display list of available voices

#for voice in voices:

#    print( "Voice ID: {voice.voice_Id}, Name: {voice.display_name}, Moods: {voice.available_styles} ")

   
# voice feature settings

Voice_Moods = {
    "Justin" :
    {
        "voice_id" : "fr-FR-justine",

        "moods": ['Conversational', 'Promo', 'Calm', 'Sad', 'Angry']
    },

    "Miles": {
        "voice_id" : "en-US-miles",

        "moods" : ['Conversational', 'Promo', 'Sports Commentary', 'Narration', 'Newscast', 'Sad', 'Angry', 'Calm', 'Terrified', 'Inspirational', 'Pirate']
    }, 

    "Natalie": {
        "voice_id" : "en-US-natalie",

        "moods" : [ 'Promo', 'Narration', 'Newscast Formal', 'Meditative','Sad', 'Angry', 'Conversational','Newcast Casual', 'Furious', 'Sorrowful','Terrified', 'Inspirational' ]
    } 


}

# Building actual flet app

def main(page: ft.Page):

    page.title = "AI bot"
    page.padding = 40
    page.bgcolor = "#2295DC"

    # required fields to be displayed on the app page

    # Name of the app
    title = ft.Text("AI bot", size = 50, weight = ft.FontWeight.BOLD, color = "#104BD4")

    # taking input from user to translate the text
    text_input = ft.TextField(

        label = "Enter the text to be translated .. ",
        width = 400,
        bgcolor = "#0C7DDA",
        color = "#FFFFFF",
        border_radius = 16,
        border_color = "#30C4C6"
    )

    #character_selection

    character_selection = ft.Dropdown(

        label = " Select the voice: ",
        options = [ft.dropdown.Option(voice) for voice in Voice_Moods.keys()],
        width = 400,
        bgcolor = "#44ACE4",
        color = "#FFFFFF",
        value = "Justin"
    )
    
    # mood selection

    mood_selection = ft.Dropdown(
        label = " Choose your mood: ",
        width = 400,
        bgcolor = "#44ACE4",
        color = "#FFFFFF"      
    )


    # function to change the available moods for character everytime it is changed from the dropdown

    def update_moods(e = None):
        selected_voice = character_selection.value

        mood_selection.options = [

            ft.dropdown.Option(mood) for mood in Voice_Moods.get(selected_voice, {}).get("moods", [])
        ]

        mood_selection.value = mood_selection.options[0].text if mood_selection.options else None

        page.update()


     # function call
    character_selection.on_change = update_moods
        
    update_moods()


    # speed modulation option ( -50 to +50 limit )

    voice_speed = ft.Slider(
        min = -30, max = 30, value = 0, divisions = 15, label = "{value}%", active_color = "#104BD4"
    )

    #generating AI audio on selection of character_selection

    def generate_audio():

        selected_voice = character_selection.value
        voice_id = Voice_Moods.get(selected_voice,{}).get("voice_id")

        if not text_input.value.strip():
            print("Error!, enter some text .. ")
            return None
        
        try:
            response = client.text_to_speech.generate(
                format = "MP3",
                sample_rate = 48000.0,
                channel_type = "STEREO",
                text = text_input.value,
                voice_id = voice_id,
                style = mood_selection.value,
                pitch = voice_speed.value 
            )

            return response.audio_file if hasattr(response, "audio_file") else None

        except Exception as e:
            print(f" Error: {e}")
            return None
        

    # function to save the audio and play it
    def save_and_play(e):
        
        audio_url = generate_audio() # return ai generated audio file

        if not audio_url:
            print("Error : no audio found ")
            return
        
        try:
            response = requests.get(audio_url, stream = True)

            if response.status_code == 200:
                
                file_path = os.path.abspath("audio.mp3")
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size = 1024):
                        file.write(chunk)

                print(" Audio Saved as:", file_path)
                
                page.overlay.clear()
                page.overlay.append(ft.Audio(src= "audio.mp3", autoplay = True))
                page.update()
                
            else:
                print("Failed to get the audio")

        except Exception as e:
            print( "Error", e)
                



    #enter_button

    Enter_btn = ft.ElevatedButton(
        "Generate speech ",
        bgcolor="#44ACE4",
        color = "#104BD4",

        on_click= save_and_play,

        style = ft.ButtonStyle(shape = ft.RoundedRectangleBorder(radius = 10))
    )


    # UI container to hold the components to be displayed on the page

    input_container = ft.Container(
        
        content = ft.Column(

            controls = [text_input, character_selection, mood_selection, 
                        ft.Text(" Adjust the speed ", size = 20, weight = ft.FontWeight.BOLD, 
                        color = "#104BD4"), 
                        voice_speed, Enter_btn],

            spacing= 16,
            alignment= ft.MainAxisAlignment.CENTER
        ),

        padding= 20,
        border_radius = 25,
        bgcolor= "#0C7DDA",
        shadow = ft.BoxShadow(blur_radius = 12, spread_radius = 3, color = "#30C4C6")

    )

    # adding a new column to page
    page.add(
        ft.Column(
            controls = [title, input_container],
            spacing = 25,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER
        )
    )

    # take the changes and update the page accordingly

    page.update()



    # Run the app
if __name__ == "__main__" :
    # asset_dir to allow access to the directory
    ft.app(target= main, assets_dir= ".")



