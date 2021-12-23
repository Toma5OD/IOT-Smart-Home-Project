import time
import requests
from urllib import request
from urllib.request import urlopen
import ssl
import paho.mqtt.publish as publish
import adafruit_dht
import board

import RPi.GPIO as GPIO

#LED SET UP
def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)

class Thingspeak(object):                       # define a class called Thingspeak

    #API CONNECTION
    def __init__(self, write_api_key = None, read_api_key=None, channel_id=0):

        """

        :param write_key:  takes a string of write api key
        :param timer: can take integer values
        """

        # self.url = 'https://api.thingspeak.com/update?api_key='
        # self.read_url = 'https://api.thingspeak.com/channels/{}/feeds.json?api_key='.format(channel_id)

        self.write_key = write_api_key
        self.channel_id = channel_id
        self.read_api_key = read_api_key

        # Private Var cannot change
        self.__url = 'http://api.thingspeak.com/update?api_key'
        self.__read_url = 'https://api.thingspeak.com/channels/{}/feeds.json?api_key='.format(channel_id)


        self.feild1 = []
        self.feild2 = []
        self.feild3 = []
    
   #POST TO CLOUD
    def post_cloud(self, value1, value2, value3):
        try:
            """
            :param value1: can be interger or float
            :param value2: can be interger or float
            :param value3: can be interger or float
            :return: updated to cloud storage
            """

            URL = self.__url

            KEY = self.write_key

            HEADER = '&field1={}&field2={}&field3={}'.format(str(value1), str(value2), str(value3))

            NEW_URL = str(URL) + "=" + str(KEY) + str(HEADER)
            print(NEW_URL)

            context = ssl._create_unverified_context()

            data = request.urlopen(NEW_URL,context=context)
            print(data)
        except:
            print('could not post to the cloud server ')
    #Read FROM API
    def read_cloud(self, result=2):
        try:
            """
            :param result: how many data you want to fetch accept interger
            :return: Two List which contains Sensor data
            """

            URL_R = self.__read_url
            read_key = self.read_api_key
            header_r = '&results={}'.format(result)

            new_read_url = URL_R + read_key + header_r

            data = requests.get(new_read_url).json()

            field1 = data['feeds']

            for x in field1:
                self.feild1.append(x['field1'])
                self.feild2.append(x['field2'])
                self.feild3.append(x['field3'])

            return self.feild1, self.feild2, self.feild3
        except:
            print('read_cloud failed !!!! ')

#Variables for loops.
sensorDefined=0;
redLedStatus = 0;
allLedStatus = 0;

#Import board data
while sensorDefined ==0:
    
    try:
    
        sensor = adafruit_dht.DHT11(board.D23)
        sensorDefined = 1
        
    except Exception: 
        print("Exception SENSOR SETUP Raised")
        time.sleep(5)
setupGPIO()

#OUTPUT TO MHR SIMULATED LIGHTS
while True:       
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        preLed = msg=requests.get("https://thingspeak.com/channels/1614323/field/3")
        led = msg.json()['feeds'][-1]['field3']        
        
        #ALL LIGHTS OFF
        if int(led) == 1 and temperature < 16 and humidity >= 61:
            GPIO.output(12, GPIO.LOW) #ORANGE OFF
            GPIO.output(16, GPIO.LOW) #RED OFF
            GPIO.output(18, GPIO.LOW) #GREEN OFF
        #GREEN LIGHT ON
        elif int(led) == 1 and temperature >= 16 and temperature <=17 and humidity >= 61:
            GPIO.output(12, GPIO.LOW)  
            GPIO.output(16, GPIO.LOW)  
            GPIO.output(18, GPIO.HIGH) #GREEN ON
        #ORANGE LIGHT ON
        elif int(led) == 1 and temperature >= 18 and temperature <=21 and humidity >= 61:
            GPIO.output(12, GPIO.HIGH) #ORANGE ON
            GPIO.output(16, GPIO.LOW)  
            GPIO.output(18, GPIO.LOW)
        #RED LIGHT ON
        elif int(led) == 1 and temperature >= 22 and temperature <=24 and humidity >= 61:
            GPIO.output(12, GPIO.LOW)  
            GPIO.output(16, GPIO.HIGH) #RED ON
            GPIO.output(18, GPIO.LOW) 
        #RED FLASHING LIGHT ON
        elif int(led) == 1 and temperature >= 25 and humidity >= 61:
            #FLASHING RED LIGHT
            if(redLedStatus==0):
                GPIO.output(16, GPIO.HIGH) #RED OFF
                redLedStatus=1
            else:
                redLedStatus=0
                GPIO.output(16, GPIO.LOW) #RED OFF
        #ORANGE LIGHT + GREEN LIGHT ON
        elif int(led) == 1 and temperature < 16 and humidity <= 60:
            GPIO.output(12, GPIO.HIGH)  #ORANGE ON
            GPIO.output(16, GPIO.LOW)  
            GPIO.output(18, GPIO.HIGH) #GREEN ON
        #RED LIGHT + GREEN LIGHT ON
        elif int(led) == 1 and temperature >= 16 and temperature <=17 and humidity <= 60:
            GPIO.output(12, GPIO.LOW) 
            GPIO.output(16, GPIO.HIGH) #RED ON
            GPIO.output(18, GPIO.HIGH) #GREEN ON
        #RED LIGHT + ORANGE LIGHT ON
        elif int(led) == 1 and temperature >= 18 and temperature <=21 and humidity <= 60:
            GPIO.output(12, GPIO.HIGH) #ORANGE ON 
            GPIO.output(16, GPIO.HIGH) #RED ON
            GPIO.output(18, GPIO.LOW) 
        #ALL LIGHTS ON!
        elif int(led) == 1 and temperature >= 22 and temperature <=23 and humidity <= 60:
            GPIO.output(12, GPIO.HIGH) #ORANGE ON 
            GPIO.output(16, GPIO.HIGH) #RED ON
            GPIO.output(18, GPIO.HIGH) #GREEN ON
        #ALL LIGHTS FLASHING
        elif int(led) == 1 and temperature >= 24 and humidity <= 60:
            #ALL LIGHTS FLASHING
            if(allLedStatus==0):
                GPIO.output(12, GPIO.HIGH) #ORANGE ON 
                GPIO.output(16, GPIO.HIGH) #RED ON
                GPIO.output(18, GPIO.HIGH) #GREEN ON
                redLedStatus=1
            else:
                allLedStatus=0
                GPIO.output(12, GPIO.HIGH) #ORANGE ON 
                GPIO.output(16, GPIO.HIGH) #RED ON
                GPIO.output(18, GPIO.HIGH) #GREEN ON
        elif int(led) == 0:
            GPIO.output(12, GPIO.LOW) #ORANGE OFF
            GPIO.output(16, GPIO.LOW) #RED OFF
            GPIO.output(18, GPIO.LOW) #GREEN OFF
        # if temperature <= 20:
        #     GPIO.output(16, GPIO.HIGH)
        # if temperature <=24:
        #     GPIO.output(18, GPIO.HIGH)      
        # GPIO.output(12, GPIO.LOW)  #ORANGE
        # GPIO.output(16, GPIO.LOW)  #RED  
    
        # if led == '1':
        #     GPIO.output(12, GPIO.HIGH)
        #     GPIO.output(16, GPIO.HIGH)
        #     GPIO.output(18, GPIO.HIGH)   
        # else:
        #     GPIO.output(12, GPIO.LOW)
        #     GPIO.output(16, GPIO.LOW)
        #     GPIO.output(18, GPIO.LOW)
                    
        msg=requests.get("https://thingspeak.com/channels/1614323/field/3")
        msg=msg.json()['feeds'][-1]['field3']
        print("\nField1 (TEMPERATURE): "+str(temperature)+"\n""\nField2 (HUMIDITY): "+str(humidity)+"\n""\nField3 (MHRV ON OFF): "+str(msg)+"\n\n")
        
    except Exception: 
        print("Exception SENSOR READING Raised")
        time.sleep(5)
        
   #POST DATA
        
  
    w_key = 'RDXAI962UDTWPFKL'
    r_key = 'HSEDQ40Z666MKUE4'
    channel_id = 1614323
    
    ob = Thingspeak(write_api_key=w_key, read_api_key=r_key, channel_id=channel_id)
    ob.post_cloud(value1=temperature,value2=humidity,value3=led)
    time.sleep(5)
    
