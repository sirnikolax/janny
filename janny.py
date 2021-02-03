"""
Description: This is a virtual assistant program that gets the date, current time,
respond back with a random greeting and returns information about a famous person

Author: Nicolas Ribeiro
Version: 0.1.5
"""

import os # for manage the Watson API_key and URL
import playsound
import random
import speech_recognition as sr
import time
import datetime
import calendar
import json
import requests
import webbrowser
import bs4
import multiprocessing

#Custom import
import chistes

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from newsapi import NewsApiClient
from gtts import gTTS

class Janny:
    """ Janny Core Class"""

    def __init__(self):
        """ Constants for watson """
        self.WATSON_URL  = os.getenv("WATSON_URL")
        self.WATSON_API  = os.getenv("WATSON_API")
        self.JANNY_VOICE = "es-LA_SofiaV3Voice"
        
        """ News API """
        # https://newsapi.org/
        self.NEWS_APIKEY = os.getenv("NEWS_APIKEY")

        # Init news API
        self.newsapi = NewsApiClient(api_key=self.NEWS_APIKEY)

        # Get the last news
        self.top_headlines = self.newsapi.get_top_headlines(
            language='es'
        )

        """ Weather API """
        self.WEATHER_API = os.getenv("WEATHER_API")


        # Set names of the days and moths in spanish
        self.MONTH_NAMES = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Setiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]

        self.DAY_NAMES = [
            "Lunes",
            "Martes",
            "Miercoles",
            "Jueves",
            "Viernes",
            "Sabado",
            "Domingo"
        ]

        #Set Service
        self.authenticator = IAMAuthenticator(self.WATSON_API)
        #TextToSpeech Watson
        self.wtts = TextToSpeechV1(authenticator=self.authenticator)
        # Service URL
        self.wtts.set_service_url(self.WATSON_URL)

    def __normalize_text(self, string):
        """ Normalize the string, replacing á to a """
        self.replace_letters = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
        )

        for a, b in self.replace_letters:
            string = string.replace(a, b)
        return string

    def listening(self):
        
        # Get the microphone input 
        recognizer = sr.Recognizer()
        try: 
            # use the microphone as source for input. 
            with sr.Microphone() as source: 
                # adjust the energy threshold based on the surrounding noise level 
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                #listens for the user's input  
                self.audio = recognizer.listen(source) 
                # Using google to recognize audio
                self.my_text = recognizer.recognize_google(self.audio, language="es-ES")
                self.my_text = self.my_text.lower()
                
                print("Dijiste (Texto normalizado): ", self.__normalize_text(self.my_text))

                return self.__normalize_text(self.my_text)

        except sr.RequestError as e: 
            print("Could not request results; {0}".format(e)) 
            
        except sr.UnknownValueError: 
            print("Error desconocido ocurrio")

    def speak(self, text, voice="pico2wave"):
        """ Make Janny talk! """
        # Generating the random name of a audio_file
        self.random_number = random.randint(1, 100)
        self.audio_name    = 'audio-'+str(self.random_number)+'.mp3'

        if voice == "watson":
            with open(f'./{self.audio_name}', 'wb') as audio_file:
                res = self.wtts.synthesize(text, accept='audio/mp3',  voice=self.JANNY_VOICE).get_result()
                audio_file.write(res.content)
            
            # Play the audio
            playsound.playsound(self.audio_name)
            #Remove the audio
            os.remove(self.audio_name)

        elif voice == "gtts":
            tts = gTTS(text, lang="es-us", tld="com")
            with open(f'./{self.audio_name}', 'wb') as audio_file:
                tts.write_to_fp(audio_file)
            # Play the audio
            playsound.playsound(self.audio_name)
            #Remove the audio
            os.remove(self.audio_name)
        
        elif voice == "pico2wave":
            # Generating the random name of a audio_file
            self.random_number = random.randint(1, 100)
            self.audio_name    = 'audio-'+str(self.random_number)+'.wav'
            
            #Making speak
            os.system(f'pico2wave -l es-ES -w {self.audio_name} "{text}" ')
            
            # Play the audio
            playsound.playsound(self.audio_name)
            #Remove the audio
            os.remove(self.audio_name)

    def wake_word(self, text):
        if text == None:
            return False

        WAKE_WORDS = [
            "yanni",
            "central", 
            "ya ni",
            "yani",
            "janny",
            "jenny",
            "jinny",
            "shani",
            "llani",
            "lla ni"
            ]

        # Start Janny listen
        for phrase in WAKE_WORDS:
            if phrase in text:
                return True
        
        # If the wake word is not found from the loop
        return False

    def get_date(self):
        now         = datetime.datetime.now()
        my_date     = datetime.datetime.today()
        weekday     = now.isoweekday()
        monthNum    = now.month
        dayNum      = now.day
        actual_year = now.year

        return "{weekday} {day} de {month} del {year}".format(
            weekday = self.DAY_NAMES[weekday - 1],
            day     = dayNum,
            month   = self.MONTH_NAMES[monthNum - 1],
            year    = actual_year
        )

    def geeting(self, text):
        
        # Greeting inputs
        GREETING_INPUTS = ["hola", "buen dia", "buenas tardes", "buenas noches"]
        
        # if the users input is a greeting, then return a random response
        if "buenos dias" in text.lower() or "buen dia" in text.lower():
            self.speak("Buen dia señor, espero se encuentre bien.")
        
        if "buenas tardes" in text.lower():
            self.speak("Buenas tardes señor, espero se encuentre bien.")
        
        if "buenas noches" in text.lower():
            self.speak("Buenas noches señor, espero se encuentre bien.")
             # if greeting is not detected, return an empty string
        
        return ''

    def tell_a_joke(self):
        random_joke = random.randint(1, 5)
        print("Este es el valor de random_joke: ", random_joke)
        self.speak(chistes.CHISTES[random_joke])

    def get_hour(self):
        now_time = datetime.datetime.now()
        meridiem = ""

        if now_time.hour >= 12:
            meridiem = "P.M." 
            actual_hour = now_time.hour - 12
        else:
            meridiem = "A.M."
            actual_hour = now_time.hour
        
        # Convert minutes into a proper string
        if now_time.minute < 10:
            actual_minute = '0' + str(now_time.minute)
        else: 
            actual_minute = str(now_time.minute)
        
        return ("Son las {hour}:{minute}{meridiem}".format(
            hour        = actual_hour,
            minute      = actual_minute,
            meridiem    = meridiem
        ))

    def todays_resume(self):

        # Creates a news headers variable
        self.news_headers = ""
        self.sources      = ""
        number_of_notices = 0
        
        # Loop over the headlines and add the headlines to news_headers
        for articles in self.top_headlines['articles']:
            if number_of_notices < 10:
                self.news_headers += articles['title'] + ".\n"
            self.sources += articles['url'] + " \n"
            number_of_notices += 1
        self.speak(f"Este es un resumen del dia {self.get_date()}. {self.get_hour()}. {self.get_weather()}. A continuación, pasaré a decirle los encabezados mas importantes que encontré en la red. \n{self.news_headers}. Estos fueron los encabezados mas importantes a nivel internacional.")
        

    def get_weather(self, city="Montevideo"):
        BASE_URL = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.WEATHER_API}"

        response = requests.get(BASE_URL)
        data = response.json()

        if data['cod'] != "404":
            current_weather = data['main']
            return f"Para el día de hoy, se pronostican {int(current_weather['temp'] - 273.15)} grados con una maxima de {int(current_weather['temp_max'] - 273.15)} grados y una minima de {int(current_weather['temp_min'] - 273.15)} grados. La sensación térmica para el día de hoy es de {int(current_weather['feels_like'] - 273.15)} grados y la humedad anda en torno al {current_weather['humidity']}%."

    def search_on_google(self, query):

        res = requests.get(f"https://google.com/search?q={query}")
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")  
        linkElements = soup.select('a')
        linkToOpen = min(10, len(linkElements))
        webbrowser.open_new("https://www.nicolasribeiro.com")
        for i in range(linkToOpen):
            webbrowser.open("https://google.com{}".format( linkElements[i].get("href") ))

    def open_todays_news(self):
        get_links = self.sources.split(" \n")
        webbrowser.open_new("http://www.nicolasribeiro.com")
        for new_tab in get_links:
            webbrowser.open(new_tab)

    def set_alarm(self, text):
        keywords = ["despertame", "avisame", "pone alarma", "poner alarma", "despertarme"]
        hours    = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "00"]
        meridian = ""

        # Loop over the keywords to find where the command start
        for command in keywords:
            # if the command is in the text, find the command inside the text and save it
            if command in text:
                position_command = text.find(command)
        
        # If the text have inside: 'Por favor', remove those characters
        if "por favor" in text[position_command:]:
            order = text[position_command:-10]
        else:
            order = text[position_command:]
        
        # if the order contains 'mañana tarde noche', meridian will set up with the respective AM, PM
        if "la mañana" in order:
            meridian = "A.M."
        elif "la tarde" in order:
            meridian = "P.M."
        else:
            meridian = "P.M."

        for hour in hours:
            if hour in order:
                hour_position = order.find(hour)

        # checks if the hour have 2 digits
        #Example: pon alarma a las 10 de la tarde == Alarma seteada a las 1 PM
        if order[hour_position:hour_position+1] != " ":
            set_alarm_on = order[hour_position:hour_position+2]


        #check if the order have hour format or not
        if order[hour_position:hour_position+1] != ":" and order[hour_position:hour_position+1] == " ":
            set_alarm_on = order[hour_position:hour_position+1]
        else:
            set_alarm_on = order[hour_position:hour_position+4]
        
        # SETTING THE CLOCK!!
        #print("Alarma configurada a las {} {}".format(set_alarm_on[:2], meridian))
        self.speak("Alarma configurada a las {} {}".format(set_alarm_on[:2], meridian))

        p1 = multiprocessing.Process(target=self.__check_time, args=(set_alarm_on[:2], meridian))
        p1.start()

    def __set_recordatory(self, alarm_hour, meridian):
        now_hour = datetime.datetime.now().hour
        now_meridian = ""

        if now_hour >= 12:
            now_meridian = "P.M."
            now_hour     = now_hour - 12
        else:
            now_meridian = "A.M."


        print("now_hour: ", now_hour)
        print("alarm_hour: ", alarm_hour)
        print("meridian: ", meridian)

        if alarm_hour.strip() == str(now_hour) and meridian.strip() == now_meridian:
            return False
        return True

    def __check_time(self, alarm_hour, meridian):
        
        __boolean_recordatory = self.__set_recordatory(alarm_hour, meridian)
        
        print("Esto es alarm_hour check_time: ", alarm_hour)
        print("Esto es meridian check_time: ", meridian)
        
        
        while __boolean_recordatory:
            print("Aun no es la hora")
            __boolean_recordatory = self.__set_recordatory(alarm_hour, meridian)
            print("Esto es __boolean_recordatoy: ", __boolean_recordatory)
            time.sleep(10)
        
        return __boolean_recordatory



if __name__ == "__main__":
    # Creating Janny
    assistant = Janny()

    while True:

        text_from_mic   = assistant.listening()
        #text_from_mic   = "central, resumen"
        
        if (assistant.wake_word(text_from_mic) == True):

            # Greeting before the start
            assistant.geeting(text_from_mic)

            if "dia es" in text_from_mic:
                assistant.speak(assistant.get_date())
            
            if "hora es" in text_from_mic:
                assistant.speak(assistant.get_hour())

            if "un chiste" in text_from_mic:
                assistant.tell_a_joke()

            if "resumen" in text_from_mic:
                assistant.todays_resume()
                assistant.speak("¿Deseas que abra las noticias en una nueva ventana?")
                answer = assistant.listening()

                if "Error" in answer:
                    pass

                if "si" in answer:
                    assistant.open_todays_news()
                else:
                    assistant.speak("De acuerdo, cualquier otra cosa solo pídalo.")

            if "gracias" in text_from_mic:
                assistant.speak("Es un placer ayudarlo, cualquier cosa estoy a las ordenes.")

            if "busca" in text_from_mic or "busqueda" in text_from_mic:
                assistant.speak("Digame que desea que le busque")
                searching = assistant.listening()
                if searching == None:
                    searching = assistant.listening()

                assistant.search_on_google(searching)
                assistant.speak(f"Esto es lo que encontre sobre lo que me pedistes sobre {searching}...")

            if "estas ahi" in text_from_mic:
                assistant.speak("Siempre estoy presente")

            if "poner alarma" in text_from_mic or "avisame" in text_from_mic or "despertame" in text_from_mic or "despertarme" in text_from_mic:
                assistant.set_alarm(text_from_mic)

            if "noticias de hoy" in text_from_mic:
                assistant.open_todays_news()