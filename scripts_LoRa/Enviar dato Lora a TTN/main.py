import socket
import time
import binascii
import pycom
from network import LoRa
import struct
import math as m

from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20 
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE

py = Pysense()
si = SI7006A20(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)
mpPress = MPL3115A2(py,mode=PRESSURE)
mpAlt = MPL3115A2(py,mode=ALTITUDE)

# Disable heartbeat LED
pycom.heartbeat(False)

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region = LoRa.US915)

# create an OTAA authentication parameters
app_eui = binascii.unhexlify('0000000000000000')
app_key = binascii.unhexlify('D29CE7DBF25478258A57B91402CC66A6')

print("DevEUI: %s" % (binascii.hexlify(lora.mac())))
print("AppEUI: %s" % (binascii.hexlify(app_eui)))
print("AppKey: %s" % (binascii.hexlify(app_key)))

#Uncomment for US915 / AU915 & Pygate
for i in range(0,8):
    lora.remove_channel(i)
for i in range(16,65):
    lora.remove_channel(i)
for i in range(66,72):
    lora.remove_channel(i)

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0 )

# wait until the module has joined the network
while not lora.has_joined():
    pycom.rgbled(0x140000)
    time.sleep(2.5)
    pycom.rgbled(0x000000)
    time.sleep(1.0)
    print('Not yet joined...')

print('OTAA joined')
pycom.rgbled(0x001400)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

def leerAcceleration():
    return int(m.sqrt(li.acceleration()[0]**2+li.acceleration()[1]**2+li.acceleration()[2]**2)*100)

def leerTemperature():
    return int(si.temperature()*100)

def leerHumidity():
    return int(si.humidity()*100)

def leerLight():
    return int(m.sqrt(lt.light()[0]**2+lt.light()[1]**2))

def leerPressure():
    return int(mpPress.pressure()*100)

def leerAltitude():
    return int(mpAlt.altitude()*100)

acceleration=leerAcceleration
temperature = leerTemperature
humidity = leerHumidity
light= leerLight
pressure = leerPressure
altitude = leerAltitude

"""
while True:
    s.setblocking(True)
    pycom.rgbled(0x000014)

    tmp=leerAcceleration()
    if tmp==acceleration:
        acceleration=0
    else: 
        acceleration=tmp

    tmp=leerTemperature()
    if tmp==temperature:
        temperature=0
    else: temperature=tmp

    tmp=leerHumidity()
    if tmp==humidity:
        humidity=0
    else: 
        humidity=tmp

    tmp=leerLight()
    if tmp==light:
        light=0
    else: 
        light=tmp

    tmp=leerPressure()
    if tmp==pressure:
        pressure=0
    else: 
        pressure=tmp

    tmp=leerAltitude()
    if tmp==altitude:
        altitude=0
    else: 
        altitude=tmp


    print('\n\nSensor')
    print('Temperature', temperature/100 )
    print('Humidity', humidity/100)
    print('Light', light)
    print('Pressure', pressure/100)
    print('Altitude', altitude/100)
    print('Acceleration', acceleration/100)

    send_data = bytearray(struct.pack('h',temperature)+struct.pack('h',humidity)+struct.pack('h',pressure)+struct.pack('h',altitude)+struct.pack('h',acceleration)+struct.pack('h',light))
      
    print('Sending data (uplink)...')
    s.send(send_data)
    s.setblocking(False)
    print('Data Sent: ', send_data)
    pycom.rgbled(0x001400)
    time.sleep(10)
"""

while True:
    s.setblocking(True)
    pycom.rgbled(0x000014)

    offset=0
    register=0

    tmp=leerAcceleration()
    if tmp!=acceleration:
        acceleration=tmp
        register=register or b'00010000'
        offset=offset+2

    tmp=leerTemperature()
    if tmp!=temperature:
        temperature=tmp
        register=register or b'00000001'
       
    tmp=leerHumidity()
    if tmp!=humidity:
        humidity=tmp
        register=register or b'00000010'
        
    tmp=leerLight()
    if tmp!=light:
        light=tmp
        register=register or b'00100000'
       
    tmp=leerPressure()
    if tmp!=pressure:
        pressure=tmp
        register=register or b'00000100'
        
    tmp=leerAltitude()
    if tmp!=altitude:
        altitude=tmp
        register=register or b'00001000'
        
    register=int(register)
    
    print('\n\nSensor')
    print('Temperature:', temperature/100 )
    print('Humidity:', humidity/100)
    print('Light:', light)
    print('Pressure:', pressure/100)
    print('Altitude:', altitude/100)
    print('Acceleration:', acceleration/100)
    
    send_data = bytearray(struct.pack('h',register)+struct.pack('h',temperature)+struct.pack('h',humidity)+struct.pack('h',pressure)+struct.pack('h',altitude)+struct.pack('h',acceleration)+struct.pack('h',light))
      
    print('Sending data (uplink)...')
    s.send(send_data)
    s.setblocking(False)
    print('Data Sent: ', send_data)
    pycom.rgbled(0x001400)
    time.sleep(10)