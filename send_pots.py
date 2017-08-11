#!/usr/bin/env python

import OSC
import time
import Adafruit_MCP3008
from dotenv import load_dotenv, find_dotenv
import os

# retrieve environment variables
load_dotenv(find_dotenv())
client_ip = os.environ.get('CLIENT_IP')

# set IP and port of device running Sonic Pi
send_address = (client_ip, 4559)

# Initialize the OSC client.
c = OSC.OSCClient()
c.connect(send_address)

# Define pins used by MCP3008
CLK = 11
MISO = 9
MOSI = 10
CS = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# create a function to send multiple arguments
def send_osc(addr, *stuff):
    msg = OSC.OSCMessage()
    msg.setAddress(addr)
    for item in stuff:
        msg.append(item)
    c.send(msg)

# function to read ADC values and send them to Sonic PI
def pot_value():
    while True:
	1 = (((mcp.read_adc(0) - 0) * (128 - 0)) / (1023 - 0)) + 0
	2 = (((mcp.read_adc(1) - 0) * (128 - 0)) / (1023 - 0)) + 0
	3 = (((mcp.read_adc(2) - 0) * (128 - 0)) / (1023 - 0)) + 0
    	4 = (((mcp.read_adc(3) - 0) * (128 - 0)) / (1023 - 0)) + 0
        5 = (((mcp.read_adc(4) - 0) * (128 - 0)) / (1023 - 0)) + 0
        6 = (((mcp.read_adc(5) - 0) * (128 - 0)) / (1023 - 0)) + 0
        7 = (((mcp.read_adc(6) - 0) * (128 - 0)) / (1023 - 0)) + 0
        8 = (((mcp.read_adc(7) - 0) * (128 - 0)) / (1023 - 0)) + 0
        pots = [1, 2, 3, 4, 5, 6, 7, 8]
        send_osc('/pots', pots)

# call function on a loop
try:
    while True:
        pot_value()
        time.sleep(0.1)

# clean exit
except KeyboardInterrupt:
    print 'Closing...'
