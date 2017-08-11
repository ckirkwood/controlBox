#!/usr/bin/env python

from OSC import OSCServer, OSCClient, OSCMessage
from time import sleep
from threading import Thread
from gpiozero import Button
import unicornhat as unicorn
import Adafruit_MCP3008
from dotenv import load_dotenv, find_dotenv
from signal import pause
import colorsys
import os
from subprocess import call

# set up unicorn hat
unicorn.set_layout(unicorn.PHAT)
unicorn.brightness(0.5)

CLK = 11
MISO = 9
MOSI = 10
CS = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


# load environment variables
load_dotenv(find_dotenv())
server_ip = os.environ.get('SERVER_IP')
client_ip = os.environ.get('CLIENT_IP')

# function to send message with multiple values
def send_osc(addr, *stuff):
    msg = OSCMessage()
    msg.setAddress(addr)
    for item in stuff:
        msg.append(item)
    c.send(msg)

### functions to call when osc message received ###
def oscInput(addr, tags, stuff, source):
  print addr, stuff, source

# block colour using all LEDs, takes RGB values as inputs
def rgb(addr, tags, stuff, source):
    r, g, b = stuff
    print(r, g, b)
    unicorn.clear()
    unicorn.set_all(r, g, b)
    unicorn.show()

# block colour leaving the top row clear, takes HSV values as inputs
def hsv(addr, tags, stuff, source):
    h, s, v = stuff
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    print(r, g, b)
    for x in range(8):
        for y in range(1, 4): # leaves the top row clear for loop_counter()
            unicorn.set_pixel(x, y, r, g, b)
            unicorn.show()

def beat(addr, tags, stuff, source):
    x, h, s, v  = stuff
    print stuff
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    unicorn.set_pixel(x, 1, r, g, b)
    unicorn.set_pixel(x+1, 1, r, g, b)
    unicorn.set_pixel(x, 2, r, g, b)
    unicorn.set_pixel(x+1, 2, r, g, b)
    unicorn.set_pixel(x, 3, r, g, b)
    unicorn.set_pixel(x+1, 3, r, g, b)       
    unicorn.show()

# display the running count of loops on the top row, takes an x value and HSV as inputs
def loop_counter(addr, tags, stuff, source):
    x, h, s, v  = stuff
    print stuff
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    unicorn.set_pixel(x, 0, r, g, b)
    unicorn.show()

def clear_counter(addr, tags, stuff, source):
    for x in range(8):
        unicorn.set_pixel(x, 0, 0, 0, 0)    
        unicorn.show()

def clear_all(addr, tags, stuff, source):
    unicorn.clear()
    unicorn.show()

# send switch status
def switch1_on():
    send_osc('/switch1', 1)

def switch1_off():
    send_osc('/switch1', 0)

def switch2_on():
    send_osc('/switch2', 1)

def switch2_off():
    send_osc('/switch2', 0)

def send_pots():
    pot1 = mcp.read_adc(0)
    pot2 = mcp.read_adc(1)
    pot3 = mcp.read_adc(2)
    pot4 = mcp.read_adc(3)
    pot5 = mcp.read_adc(4)
    pot6 = mcp.read_adc(5)
    pot7 = mcp.read_adc(6)
    pot8 = mcp.read_adc(7)
    pots = [pot1, pot2, pot3, pot4, pot5, pot6, pot7, pot8]
    send_osc('/pots', pots)
    print(pots)

# assign server ip and port
server = OSCServer((server_ip, 9090))
send_address = (client_ip, 4559)

c = OSCClient()
c.connect(send_address)

# add message handlers - assign functions to incoming message addresses
server.addMsgHandler("/rgb", rgb)
server.addMsgHandler("/hsv", hsv)
server.addMsgHandler("/beat", beat)
server.addMsgHandler("/count", loop_counter)
server.addMsgHandler("/clear_counter", clear_counter)
server.addMsgHandler("/clear_all", clear_all)


# start thread
server_thread = Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

switch1 = Button(20)
switch2 = Button(21)


try: # send message only when switch status changes
    switch1.when_pressed = switch1_on
    switch1.when_released = switch1_off
    switch2.when_pressed = send_pots
    switch2.when_released = send_pots
    pause()

  

except KeyboardInterrupt:
    print 'losing...' # makes use of the '^C' following keyboard interrupt
    server.close()
