import speech_recognition as sr  # import using 'pip install SpeechRecognition'
import os
import sys
import re
import webbrowser
import smtplib
import requests
import subprocess
from pyowm import OWM  # import using 'pip install pyowm'
import youtube_dl  # import using 'pip install youtube-dl'
import urllib
import json
from urllib.request import urlopen
import wikipedia  # import using 'pip install wikipedia'
import random
from time import strftime
import datetime
import pyttsx3  # import using 'pip install pyttsx3'
import wolframalpha  # import using 'pip install wolframalpha'
import shutil
import pyjokes  # import using 'pip install pyjokes'
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs # import using 'pip3 install bs4'
import requests # import using 'pip3 install requests'
import requests # import using 'pip3 install requests'
from playsound import playsound # import using 'pip install playsound==1.2.2' / use earlier version for stability
import multiprocessing # multiprocessing
import keyboard # import using 'pip install keyboard'
from threading import Thread # threading
import pymysql
import googlemaps # import using 'pip install googlemaps'
gmaps = googlemaps.Client(key='<<GOOGLE_MAPS_API_KEY_HERE>>')

# **** remember to run 'pip install pipwin' and then 'pipwin install pyaudio' afterwards ****

from newsapi import NewsApiClient # import NewsAPI client using 'pip install newsapi-python'
import paho.mqtt.client as mqtt   # import MQTT Python client using 'pip install paho-mqtt'
broker = "iotp03g7.mosquitto.local"
port = 8888

# import using 'pip install pycryptodome'
# Reference 1 - Installing PyCryptodome: https://stackoverflow.com/questions/50080459/failed-installing-pycrypto-with-pip
# Reference 2 - AES-256 Implementation: https://medium.com/qvault/aes-256-cipher-python-cryptography-examples-b877b9d2e45e
# Reference 3 - AES-256 Base64 Implementation using PyCryptodome: https://gist.github.com/Frizz925/ac0fb026314807959db5685ac149ed67
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
from base64 import b64encode, b64decode


##############################################
# Check for establishment of MQTT connection #
def on_connect(client, userdata, flags, rc):
    global connected
    connected = True

    # print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    # print("Client has successfully connected. ")


def on_message(client, userdata, message):
    global message_received
    message_received = True

    global mqttVal
    mqttVal = str(message.payload.decode("utf-8"))
    # print("Message Received:", str(message.payload.decode("utf-8")))
    # print("Message Topic:", message.topic)
    # print("Message QoS:", message.qos)
    # print("Message Retain Flag:", message.retain)
##############################################


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning! ")
  
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon! ")  
  
    else:
        speak("Good Evening! ")


def username():
    speak("How should I address you? ")
    uname = captureVoice()
    while uname == "None":
        speak("Sorry, I did not recognize what you just said. Please repeat it again. ")
        uname = captureVoice()
        if uname != "None":
            break

    speak(f"Welcome, {uname}")
     
    speak("How can I help you? ")

    return uname


def captureVoice():
     
    r = sr.Recognizer()
     
    with sr.Microphone() as src:
        r.adjust_for_ambient_noise(src, duration = 1)
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(src)
  
    try:
        print("Recognizing...")   
        query = r.recognize_google(audio, language ='en-sg')
        print(f"User said: {query}\n")
  
    except Exception as e:
        print(e)   
        print("Unable to recognize your voice.") 
        return "None"
     
    return query


def get_weather_data(url):
    session = requests.Session()
    session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    session.headers['Accept-Language'] = "en-US,en;q=0.5"
    session.headers['Content-Language'] = "en-US,en;q=0.5"
    html = session.get(url)
    # create a new soup
    soup = bs(html.text, "html.parser")

    # store all results on this dictionary
    result = {}
    # extract region
    result['region'] = soup.find("div", attrs={"id": "wob_loc"}).text
    # extract temperature now
    result['temp_now'] = soup.find("span", attrs={"id": "wob_tm"}).text
    # get the day and hour now
    result['dayhour'] = soup.find("div", attrs={"id": "wob_dts"}).text
    # get the actual weather
    result['weather_now'] = soup.find("span", attrs={"id": "wob_dc"}).text

    # get the precipitation
    result['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text
    # get the % of humidity
    result['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
    # extract the wind
    result['wind'] = soup.find("span", attrs={"id": "wob_ws"}).text

    # get next few days' weather
    next_days = []
    days = soup.find("div", attrs={"id": "wob_dp"})
    for day in days.findAll("div", attrs={"class": "wob_df"}):
        # extract the name of the day
        day_name = day.findAll("div")[0].attrs['aria-label']
        # get weather status for that day
        weather = day.find("img").attrs["alt"]
        temp = day.findAll("span", {"class": "wob_t"})
        # maximum temperature in Celsius, use temp[1].text if you want fahrenheit
        max_temp = temp[0].text
        # minimum temperature in Celsius, use temp[3].text if you want fahrenheit
        min_temp = temp[2].text
        next_days.append({"name": day_name, "weather": weather, "max_temp": max_temp, "min_temp": min_temp})
    # append to result
    result['next_days'] = next_days
    return result


def generatePrivateKey(secret):
    # Generate random salt to comply with NIST's recommendation of minimum salt length of 32-bytes
    # Reference: https://levelup.gitconnected.com/python-salting-your-password-hashes-3eb8ccb707f9?gi=7c9c34f6ed0f
    salt = os.urandom(32)
    kdf = PBKDF2(secret, salt, 64, 1000)
    key = kdf[:32]

    return key


def getPrivateKey(privateKeyPath):
    # Reference: https://www.kite.com/python/answers/how-to-read-bytes-from-a-binary-file-in-python
    with open(privateKeyPath, 'rb') as f:
        privateKey = f.read()

    return privateKey


def encryptData(note, privateKeyPath):
##### Encrypt #####
    privateKey = getPrivateKey(privateKeyPath)
    raw = pad(note).encode('utf8')    # Reference: https://stackoverflow.com/questions/50302827/object-type-class-str-cannot-be-passed-to-c-code-virtual-environment
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(privateKey, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw))


def decryptData(ciphertext, privateKeyPath):
##### Decrypt #####
    privateKey = getPrivateKey(privateKeyPath)
    enc = b64decode(ciphertext)
    iv = enc[:16]
    cipher = AES.new(privateKey, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))


wakeWord = "vanessa"
message_received = ""
mqttVal = ""


######################## MAIN PROGRAM ########################
if __name__ == '__main__':
    clear = lambda: os.system('cls')

    # Get the full path to the file containing the alarm set off time
    alarmPath = os.path.abspath("alarm.txt")

    # Get the full path to the files containing the user's name and private key used
    unamePath = os.path.abspath("uname.txt")
    privateKeyPath = os.path.abspath("private.txt")
    allNotes = ""

    ########## ENCRYPTION & DECRYPTION OF DATA ##########
    BLOCK_SIZE = 16
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    secret = "ep0403_group7" # Using a static secret value
    ########## ENCRYPTION & DECRYPTION OF DATA ##########
     
    # The function will clean any command before execution of this python file
    clear()

    wishMe()

    while True:
        message_received = ""
        mqttVal = ""

        with open(alarmPath, 'r') as f:
            alarm = f.read()
        if alarm == datetime.now().strftime("%I:%M %p"):
            print("========== ALARM ACTIVATED =========\n              " + datetime.now().strftime("%I:%M %p")+ "\n\n          ((  (__I__)  ))\n            .'_....._'.\n           / / .12 . \ \ \n          | | '  |  ' | |\n          | | 9  /  3 | |\n           \ \ '.6.' / /\n            '.`-...-'.'\n             /'-- --'\ \n")
            speak("Alarm Activated")

            client = mqtt.Client()  # Create new instance
            client.on_connect = on_connect
            client.on_message = on_message

            client.username_pw_set(username='david',password='1qwer$#@!')

            #print("Connecting to MQTT broker...")
            client.connect(broker, port)  # Connect to broker
            client.loop_start()  # Start the loop

            ### MQTT Publish ###
            client.publish("house/livingroom/buzzer","1")
            
            ## DEBUG
            print("Sending MQTT...")
            
            # Stop Buzzer after 5 seconds
            time.sleep(5)  # Wait for 5 seconds
            client.publish("house/livingroom/buzzer","0")
            client.loop_stop()  # Stop the loop
            print("========== ALARM DEACTIVATED =========")
            speak("Alarm Deactivated")



        # Try to grab the user's name from the file 'uname.txt' in the current working directory
        try:
            with open(unamePath, 'r') as f:
                uname = f.read()
        
        # If the file does not exist, create the file and write the user's name, based on what he/she has said
        except FileNotFoundError:
            uname = username()
            with open(unamePath, 'w+') as f:
                f.write(uname)

        # Try to grab the private key from the file 'privateKey.txt' in the current working directory
        try:
            with open(privateKeyPath, 'rb') as f:
                privateKey = f.read()

        # If the file does not exist, create the file and write the private key
        except FileNotFoundError:
            privateKey = generatePrivateKey(secret)
            with open(privateKeyPath, 'wb+') as f:
                print(privateKey)
                f.write(privateKey)


        # All the commands said by the user will be stored in the 'query' variable and converted to lower case
        query = captureVoice().lower()

        # User needs to specify the wake word in order to get the virtual assistant to perform tasks
        # if query == wakeWord:
        # print(wakeWord)
        # print(query)

        if wakeWord in query:
            print("Yes?")
            speak("Yes?")

            query = captureVoice().lower()

            if 'wikipedia' in query:
                speak('Searching Wikipedia...')
                query = query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences = 3)
                speak("According to Wikipedia")
                print(results)
                speak(results)
    
    
            elif 'what time is it' in query:
                # strTime = datetime.datetime.now().strftime("%H:%M:%S")
                strTime = datetime.now().strftime("%I:%M %p")
                speak(f"It is currently {strTime}")
    
    
            elif 'how are you' in query:
                speak("I am fine, thank you")
                

            elif 'joke' in query:
                speak(pyjokes.get_joke())
                
            
            elif 'alarm' in query:
                while True:
                    print("When do you need the alarm to ring?")
                    speak("When do you need the alarm to ring?")
                    requestedTime = captureVoice()
                    try:
                        duration = int(re.search(r'\d+', requestedTime).group())
                    except:
                        requestedTime = "failed"
                    if 'hour' in requestedTime:
                        sum = timedelta(hours=duration)
                        currentTime = datetime.now()
                        timetoring = currentTime + sum
                        speak("Alarm set to ring in " + str(duration) + " hours")
                        print("Alarm set to ring in " + str(duration) + " hour(s).\n")
                        f = open("alarm.txt", "w")
                        f.write(timetoring.strftime("%I:%M %p"))
                        f.close()
                        break
                    elif 'minute' in requestedTime:
                        sum = timedelta(minutes=duration)
                        currentTime = datetime.now()
                        timetoring = currentTime + sum
                        speak("Alarm set to ring in " + str(duration) + " minutes.")
                        print("Alarm set to ring in " + str(duration) + " minute(s).\n")
                        f = open("alarm.txt", "w")
                        f.write(timetoring.strftime("%I:%M %p"))
                        f.close()
                        break
                    elif 'second' in requestedTime:
                        sum = timedelta(seconds=duration)
                        currentTime = datetime.now()
                        timetoring = currentTime + sum
                        speak("Alarm set to ring in " + str(duration) + " seconds.")
                        print("Alarm set to ring in " + str(duration) + " second(s).\n")
                        #speak("Alarm set to ring in " + str(duration) + " seconds at approximately " + str(timetoring))
                        #print("Alarm set to ring in " + str(duration) + " seconds at approximately " + str(timetoring) + "\n")
                        f = open("alarm.txt", "w")
                        f.write(timetoring.strftime("%I:%M %p"))
                        f.close()
                        break
                    else:
                        print("Sorry. I did not get that. For example, set an alarm by saying, Ring in 15 minutes.")
                        speak("Sorry. I did not get that. For example, set an alarm by saying, Ring in 15 minutes.")
                        continue


            elif 'song' in query: # CTRL + C to stop playing
                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                ### MQTT Code to get all song list
                #client.publish("user/songs/to-node-red", "*") # Request all available songs from song list
                #client.subscribe("user/songs/from-node-red") # Get all available songs from song list

                ### Get Path of Song
                print("What song would you like to listen to?")
                speak("What song would you like to listen to?")
                song_request = captureVoice()
                client.publish("user/songs/to-node-red", song_request)
                client.subscribe("user/songs/from-node-red")

                while message_received != True:
                    time.sleep(0.2)

                songInfo = mqttVal

                songInfoJSON = json.loads(mqttVal)
                songInfoBeautified = json.dumps(songInfoJSON, indent = 2)

                # print(f"Got song? --> {len(songInfoJSON)}")

                if len(songInfoJSON) == 0:
                    print("That song is not available. ")
                    speak("That song is not available. ")

                else:
                    ## DEBUG ##
                    print(songInfoBeautified)
                    ## DEBUG ##

                    print(f"Playing song: {songInfoJSON[0]['name']}")
                    speak(f"Playing song: {songInfoJSON[0]['name']}")

                    playsound(songInfoJSON[0]["path"])


            elif "news" in query:
                newsapi = NewsApiClient(api_key='<<NEWS_API_KEY_HERE>>')

                # Display all the categories available from NewsAPI Python library
                print("What are you interested in?\n1. Business\n2. Entertainment\n3. General\n4. Health\n5. Science\n6. Technology\n")
                speak("What type of news are you interested in? Business? Entertainment? General? Health? Science or Technology? ")

                while True:
                    newsKeyword = captureVoice()
                    if newsKeyword == "business" or newsKeyword == "entertainment" or newsKeyword == "general" or newsKeyword == "health" or newsKeyword == "science" or newsKeyword == "technology":
                        break
                    elif newsKeyword == "None":
                        print("Sorry, please try again.")
                        speak("Sorry, please try again.")
                        continue
                    else:
                        print("Sorry, that category is unsupported. Please try a supported category, namely Business, Entertainment, General, Health, Science or Technology")
                        speak("Sorry, that category is unsupported. Please try a supported category, namely Business, Entertainment, General, Health, Science or Technology")
                        continue

                top_headlines = newsapi.get_top_headlines(
                    category=newsKeyword,
                    language='en',
                    country='sg'
                )

                ###### Grab all articles related to the news keyword, within a specified time range
                # all_articles = newsapi.get_everything(q=newsKeyword,
                #     #sources='bbc-news,the-verge',
                #     #domains='bbc.co.uk,techcrunch.com',
                #     from_param='2021-12-06',
                #     to='2021-12-31',
                #     language='en',
                #     sort_by='relevancy',
                #     page=1
                # )

                print(f"The following are some of the latest news regarding the keyword {newsKeyword}.")
                speak(f"The following are some of the latest news regarding the keyword {newsKeyword}.")

                headlines = top_headlines['articles']
                i = 1

                for item in top_headlines['articles']:
                    print(str(i) + '. ' + item['title'] + '\n')
                    print(item['description'] + '\n')
                    speak(str(i) + '. ' + item['title'] + '\n')
                    i += 1
            
            elif "turn on the lights" in query:
                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                ### MQTT Publish ###
                print("Switching on the lights...")
                speak("Switching on the lights...")

                client.publish("house/livingroom/lights-1","1")
                time.sleep(2)  # Wait for 2 seconds
                client.loop_stop()  # Stop the loop

                print("Lights are on.")
                speak("Lights are on.")

            elif "turn off the lights" in query:
                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                ### MQTT Publish ###
                print("Switching off the lights...")
                speak("Switching off the lights...")

                client.publish("house/livingroom/lights-1","0")
                time.sleep(2)  # Wait for 2 seconds
                client.loop_stop()  # Stop the loop

                print("Lights are off.")
                speak("Lights are off.")


            elif "dim" and "lights" in query:
                print("Choose your mode:\n1. Normal Mode\n2. Sleep Mode")
                speak("Say 1 for normal mode dimming, and 2 for sleep mode dimming.")
                dimMode = captureVoice()

                if dimMode == "one" or dimMode == "1":
                    dimVal = "40"
                    
                elif dimMode == "two" or dimMode == "2":
                    dimVal = "10"

                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                ### MQTT Publish ###
                print("Dimming the lights...")
                speak("Dimming the lights...")

                client.publish("house/livingroom/lights-pwm-1", dimVal)
                time.sleep(2)  # Wait for 2 seconds
                client.loop_stop()  # Stop the loop

                print("Lights are dimmed.")
                speak("Lights are dimmed.")


            elif "don't listen" in query or "stop listening" in query:
                speak("For how long you want me to stop listening for commands?")
                a = int(captureVoice())
                speak("Understood.")
                time.sleep(a)
                print(a)

            
            elif "write a note" in query:
                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                print("What should I write?")
                speak("What should I write?")
                note = captureVoice()

                print("What should I categorise this as?")
                speak("What should I categorise this as?")
                category = captureVoice()

                ## MQTT Publish (Sending Notes)
                print("Publishing to MQTT topic 'user/notes/to-node-red'... ")
                # speak("Publishing to MQTT topic 'user/notes/to-node-red'")
                print("Processing your note...")

                noteJSON = {
                    "note":encryptData(note, privateKeyPath).decode(), 
                    "category":category
                }

                # print(noteJSON)

                noteJSONDump = json.dumps(noteJSON)

                client.publish("user/notes/to-node-red", noteJSONDump)
                time.sleep(2)  # Wait for 2 seconds
                # client.loop_stop() # Stop the loop

                print("Your note has been written.")
                speak("Your note has been written.")


            elif "show me my notes" in query:
                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                ## MQTT Subscribe (Receiving Notes)
                # Useful Link to View JSON Data: http://jsonviewer.stack.hu/
                # Reference: https://www.journaldev.com/33302/python-pretty-print-json
                # Reference: https://www.geeksforgeeks.org/json-pretty-print-using-python/
                # Reference: https://stackoverflow.com/questions/37897834/return-data-on-message-in-python-paho-mqtt
                # Reference: http://www.steves-internet-guide.com/receiving-messages-mqtt-python-client/
                # Reference: https://www.youtube.com/watch?v=j24FBa49cVs

                print("Subscribing to MQTT topic 'user/notes/from-node-red'... ")
                # speak("Subscribing to MQTT topic 'user/notes/from-node-red'")
                client.publish("user/notes/get", "yes")  # Node-RED will wait for a 'yes' in 'user/notes/get' before sending all notes from MySQL DB
                client.subscribe("user/notes/from-node-red")  # Get all notes from MySQL DB through Node-RED via MQTT

                while message_received != True:
                    time.sleep(0.2)

                allNotesJSON = json.loads(mqttVal)
                allNotesBeautified = json.dumps(allNotesJSON, indent = 2)

                # print(len(allNotesJSON))

                if len(allNotesJSON) == 0:
                    speak("You do not have any notes. ")

                else:
                    print("Showing your notes")
                    speak("Showing your notes")
                    print("\n")
                    
                    # Reference: https://www.kite.com/python/answers/how-to-convert-bytes-to-a-string-in-python
                    for itemNo in range(0, len(allNotesJSON)):
                        print(f"Item Number: {itemNo + 1}")
                        print(f"Category: {allNotesJSON[itemNo]['category']}")
                        print(f"Description: {decryptData(allNotesJSON[itemNo]['item'], privateKeyPath).decode()}")
                        print("\n")
                        speak(decryptData(allNotesJSON[itemNo]['item'], privateKeyPath).decode())

    
            elif "weather" in query:
                # Google Open weather website
                # to get API of Open weather
                api_key = "<<OPEN_WEATHER_API_KEY_HERE>>"
                base_url = "http://api.openweathermap.org/data/2.5/forecast?"
                print("State your city name. ")
                speak("State your city name")
                city_name = captureVoice()
                print("Reporting the weather for " + str(city_name))
                speak("Reporting the weather for " + str(city_name))

                complete_url = base_url + "q=" + city_name + "&appid=" + api_key + "&units=metric"
                response = requests.get(complete_url)
                x = response.json()
                
                if x["cod"] == "404" and x["cod"] == "401":
                    speak(" City Not Found ")
                else:
                    URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather+"
                    URL += city_name
                    data = get_weather_data(URL)

                    count = 0
                    while count < 3:
                        w = x["list"][count]
                        y = w["main"]
                        min_temp = str(y["temp_min"])
                        max_temp = str(y["temp_max"])
                        humiditylevel = str(y["humidity"])
                        cloudiness = str(w["clouds"]["all"])
                        windspeed = str(w["wind"]["speed"])
                        z = w["weather"]
                        weather_description = z[0]["description"]
                        if count == 0:
                            print("="*40 + " Today " + "="*40)
                            print("Max Temperature: ", max_temp, "°C\nMin Temperature: ", min_temp, "°C\nState: ", weather_description, "\nHumidity:", humiditylevel, "%\nCloudiness:", cloudiness, "%\nChance of Rain: ", data["precipitation"],"\nWind Speed: ", windspeed, "m/s\n")
                            speak("Today's weather will be " + weather_description + " with temperatures reaching a high of " + max_temp + "degree celsius and a low of " + min_temp + "degree celsius.")
                            speak("Humidity level is at " + humiditylevel + " percent and Cloudiness at " + cloudiness + " percent, with wind speeds up to " + windspeed + "meters per second.")
                            speak("Chances of rain is at " + str(data["precipitation"]))
                        elif count == 1:
                            print("="*40 + " Tomorrow " + "="*40)
                            print("Max Temperature: ", max_temp, "°C\nMin Temperature: ", min_temp, "°C\nState: ", weather_description, "\nHumidity:", humiditylevel, "%\nCloudiness: ", cloudiness,"%\nWind Speed: ", windspeed, "m/s\n")
                            speak("Tomorrow's weather will be " + weather_description + " with temperatures reaching a high of " + max_temp + "degree celsius and a low of " + min_temp + "degree celsius.")
                            speak("Humidity level is at " + humiditylevel + " percent and Cloudiness at " + cloudiness + " percent, with wind speeds up to " + windspeed + "meters per second.")
                        else:
                            print("="*40 + " The day after tomorrow " + "="*40)
                            print("Max Temperature: ", max_temp, "°C\nMin Temperature: ", min_temp, "°C\nState: ", weather_description, "\nHumidity:", humiditylevel, "%\nCloudiness: ", cloudiness,"%\nWind Speed: ", windspeed, "m/s\n")
                            speak("The day after tomorrow's weather will be " + weather_description + " with temperatures reaching a high of " + max_temp + "degree celsius and a low of " + min_temp + "degree celsius.")
                            speak("Humidity level is at " + humiditylevel + " percent and Cloudiness at " + cloudiness + " percent, with wind speeds up to " + windspeed + "meters per second.")
                        count += 1


            elif "distance" in query:
                speak("Set your origin. ")
                print("Origin: \n")
                origin_location = captureVoice()
                speak("Set your destination. ")
                print("Destination: \n")
                destination_location = captureVoice()
                
                data = gmaps.distance_matrix(
                    origin_location,
                    destination_location,
                    departure_time=datetime.now() + timedelta(minutes=10) # Set to depart in 10 minutes
                )

                distance = data["rows"][0]["elements"][0]["distance"]["text"]

                print("Distance between",origin_location,"and",destination_location,"is:",distance)
                speak("The distance between" + origin_location + "and," + destination_location + "is:" + distance)
                

            elif "directions" in query:
                speak("Set your origin. ")
                print("Origin: \n")
                origin_location = captureVoice()

                speak("Set your destination. ")
                print("Destination: \n")
                destination_location = captureVoice()

                speak("State your mode of transport. Driving, public transport, or walking. ")
                print("Mode of Transport: \n")
                transportMode = captureVoice()

                if transportMode == "driving":
                    mode = "driving"

                elif transportMode == "public transport":
                    mode = "transit"

                elif transportMode == "walking":
                    mode = "walking"

                origin = gmaps.geocode(origin_location) # Retreive coordinates from string location
                destination = gmaps.geocode(destination_location) # Retreive coordinates from string location

                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                # print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                destinationJSON = json.dumps(destination)

                client.publish("user/dashboard/maps", destinationJSON)

                directions_result = gmaps.directions(
                    origin[0]["formatted_address"],
                    destination[0]["formatted_address"],
                    mode=mode, # Can get from query
                    arrival_time=datetime.now() + timedelta(minutes=0.5)
                )
                x = directions_result[0]['legs'][0]['steps']
                length = len(x)
                i = 0
                route_map = ''
                while i < length:
                    route_map += str(i+1)
                    route_map += '. '
                    route_map += x[i]['html_instructions']
                    route_map += '\n'
                    i += 1
                print("========== Directions ==========")
                soup = bs(route_map,features="html.parser")
                print(soup.get_text()) # Display all direction routes
                speak(soup.get_text())
            

            elif "current temperature" in query:
                client = mqtt.Client()  # Create new instance
                client.on_connect = on_connect
                client.on_message = on_message

                client.username_pw_set(username='david',password='1qwer$#@!')

                print("Connecting to MQTT broker...")
                client.connect(broker, port)  # Connect to broker
                client.loop_start()  # Start the loop

                client.publish("house/livingroom/dht-query", "1") # Get latest temperature

                client.subscribe("house/livingroom/dht-get")

                while message_received != True:
                    time.sleep(0.2)

                print(f"Current Temperature: {mqttVal} degrees Celsius ")
                speak("The current temperature is" + mqttVal + "degrees Celsius.")


            elif "bye-bye" in query:
                speak(f"See you some time soon, {uname}")
                exit()
    

            # elif "" in query:
                # For adding more commands