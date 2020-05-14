"""
Core of Janny Assistant 
Build by Nicolas Ribeiro

Janny is a virtual assistant that helps you in your day as a developer with different type of task.

"""
from gtts import gTTS
from time import ctime
import speech_recognition as sr
import webbrowser
import time
import playsound
import os
import random
import chistes


r = sr.Recognizer()


def grabar_audio(pregunta = False):

    with sr.Microphone() as source:

        if pregunta:
            jenny_habla(pregunta)

        audio = r.listen(source)
        try:        
            voz_data = r.recognize_google(audio, language="es-uy")

        except sr.UnknownValueError:
            jenny_habla("Disculpa, no te entendi.")
            jenny( grabar_audio() )

        except sr.RequestError:
            jenny_habla("Error en servidor: Estado fuera de servicio")

        return voz_data

def jenny_habla(text_audio):
    tts = gTTS(text=text_audio, lang='es')
    a = random.randint(1, 1000000)
    archivo_audio = 'audio-'+ str(a) + '.mp3'
    tts.save(archivo_audio)

    playsound.playsound(archivo_audio)
    os.remove(archivo_audio)


def jenny(comando):

    if 'Cómo te llamas' in comando:
        jenny_habla("Me llamo Jenny.")

    if 'Qué día es' in comando:
        jenny_habla(ctime())

    if 'Busca en Google' in comando:
        busqueda = grabar_audio('Que deseas que busque?')
        url = 'https://google.com/search?q='+busqueda
        webbrowser.get().open(url)
        jenny_habla("Esto es lo que encontre sobre "+busqueda)

    if 'Busca en Maps' in comando:
        busqueda = grabar_audio('Que deseas que busque?')
        url = 'https://www.google.com/maps/place/'+busqueda
        webbrowser.get().open(url)
        jenny_habla("Esta es la ubicacion que encontre sobre "+busqueda)

    if 'gracias' in comando:
        jenny_habla("De nada señor")
        exit()

    if 'cuenta un chiste' in comando:
        jenny_habla( chistes.lista[ random.randint(1, 2) ] )


time.sleep(1)

voz_entrada = grabar_audio()

if voz_entrada == 'Jenny':
    jenny_habla('Si?')
    while True:
        voz_entrada = grabar_audio()
        print(voz_entrada)
        jenny(voz_entrada)