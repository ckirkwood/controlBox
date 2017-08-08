#!/usr/bin/env python

from OSC import OSCServer, OSCClient, OSCMessage
from time import sleep
from threading import Thread
from gpiozero import Button
import unicornhat as unicorn
from dotenv import load_dotenv, find_dotenv
from signal import pause
import colorsys
import os

# set up unicorn hat
unicorn.set_layout(unicorn.PHAT)
unicorn.brightness(0.5)

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

# display the running count of loops on the top row, takes an x value and HSV as inputs
def loop_counter(addr, tags, stuff, source):
    x, h, s, v = stuff
    print stuff
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    unicorn.set_pixel(x, 0, r, g, b)
    unicorn.show()

def clear_counter(addr, tags, stuff, source):
    for x in range(8):
        unicorn.set_pixel(x, 0, 0, 0, 0)    
        unicorn.show()

# send switch status
def switch2_on():
    send_osc('/switch2', 1)

def switch2_off():
    send_osc('/switch2', 0)

# assign server ip and port
server = OSCServer((server_ip, 9090))
send_address = (client_ip, 4559)

c = OSCClient()
c.connect(send_address)

# add message handlers - assign functions to incoming message addresses
server.addMsgHandler("/rgb", rgb)
server.addMsgHandler("/beat", hsv)
server.addMsgHandler("/count", loop_counter)
server.addMsgHandler("/clear", clear_counter)

# start thread
server_thread = Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

#switch1 = Button(19)
switch2 = Button(21)

try: # send message only when switch status changes
    switch2.when_pressed = switch2_on
    switch2.when_released = switch2_off
    pause()

except KeyboardInterrupt:
    print 'losing...' # makes use of the '^C' following keyboard interrupt
    server.close()
