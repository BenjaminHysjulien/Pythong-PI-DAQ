import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import queue
import urllib
import datetime
from gpiozero import OutputDevice
from time import sleep
from serial import Serial
import csv
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import sys
import math
import csv
import os.path
from os import path
from math import log
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22,GPIO.OUT)
time.sleep(1)
sleep_time = 1
wait_write = 60

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4



flagButton = False

#set up i2c ports
i2c = busio.I2C(board.SCL, board.SDA)

#Create the ADC object with correct ports.
adc1 = ADS.ADS1115(i2c, address=0x48) #For addressing pulled to gound. Default addressing.

#Setup all four channels. 
chan0_0x49 = AnalogIn(adc1, ADS.P0);  
chan1_0x49 = AnalogIn(adc1, ADS.P1);
chan2_0x49 = AnalogIn(adc1, ADS.P2); 
chan3_0x49 = AnalogIn(adc1, ADS.P3);

#declare FIFO for buffer. One for each channel
qtime = queue.Queue()
q0 = queue.Queue()
q1 = queue.Queue()
q2 = queue.Queue()
q3 = queue.Queue()
timer_check = 0
write_data = False
date = "myDate" + ".csv"
def csvwriter_func(q0, q1, qtime):
    ts = datetime.datetime.now().timestamp()
    readableTime = datetime.datetime.fromtimestamp(ts).isoformat()
    date = readableTime.split('T')
    index = 0
    data_dict = {"Time Stamp":[], "Humidity":[], "Temp":[]};
    while not q0.empty():
        str_temp = qtime.get()
        str_temp = str_temp.split('T')
        str_temp = str_temp[1].split('.')
        data_dict["Time Stamp"].append(str_temp[0])
        data_dict["Humidity"].append(q0.get())
        data_dict["Temp"].append(q1.get())
    print(data_dict)
    if not os.path.exists("data_log_" + date[0] + ".csv"):
        with open("data_log_" + date[0] + ".csv", 'w') as csv_file:
            field_names = ['Time Stamp', 'Humidity', 'Temp']
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(data_dict.keys())
            csv_writer.writerows(zip(*data_dict.values()))
    else:
        with open("data_log_" + date[0] + ".csv", 'a') as csv_file:
            field_names = ['Time Stamp', 'Humidity', 'Temp']
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(zip(*data_dict.values()))
            
        
LED_flag = False;
     
#start main module 
while(True):
  # with Serial('/dev/ttys0', 9800) as s:
        a = 8.54942E-04
        b = 2.57305E-04
        c = 1.65368E-07
        #read value in.
        #convert value to meaningful data.
        #display data to terminal.
        #transmit data
        
        ts = datetime.datetime.now().timestamp()
        readableTime = datetime.datetime.fromtimestamp(ts).isoformat()
        print(readableTime)
        qtime.put(readableTime)
        if(LED_flag == False):
            GPIO.output(22,GPIO.HIGH)
            LED_flag = True
        else:
            GPIO.output(22,GPIO.LOW)
            LED_flag = False
        #print("Humidity Raw: "+"{:>5}\t{:>5.3f}".format(chan0_0x49.value, chan0_0x49.voltage))
        hum = round((0.0375 * (chan0_0x49.voltage)*1000 - 37.7),2); 
        q0.put(hum)
        print("Humidity: ", hum)
        vol = chan1_0x49.voltage
        #Calculate resistance of a NTC temp sensor 
        r2 = 10000*vol/(5.2-vol)
        e = 2.71828
        temp = round(1/(a+b*math.log(r2,e)+c*math.log(r2,e)*log(r2,e)*log(r2,e))-273.15,2)
        print ("Temperature: ", temp, "*C")
        q1.put(temp)
        print("\n")

        timer_check += 1 
        sleep(sleep_time)
        if timer_check == wait_write:
            write_data = True
            timer_check = 0
        else:
            write_data = False
        if write_data:
            csvwriter_func(q0, q1, qtime)
            
            
        