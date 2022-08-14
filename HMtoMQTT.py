#!/usr/bin/env python

# runs "hmip_cli.py --list-devices" every X seconds and reports device status over MQTT
# pass the number of seconds as the first parameter, if not it will only run once

import datetime, time
from datetime import datetime
from datetime import timedelta
import signal
import atexit
import sys
import traceback
import time
import os
import paho.mqtt.client as mqtt
import socket
import subprocess

global client
global MQTTtopic

MQTTtopic = "bridge/location/homematic/"
MQTTServer = "192.168.218.21"
MQTTUsername = "username"
MQTTPassword = "password"
HMShellFile = "python /home/openhabian/.local/bin/hmip_cli.py --list-devices --config_file /home/openhabian/config.ini"

def sigint_handler(signal, frame):
    print('Keyboard interrupt')
    client.publish(MQTTtopic + "status", "stopped")
    sys.exit(0)

def handle_exit():
    print("Killed")
    client.publish(MQTTtopic + "status", "stopped")

def on_connect_handler(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        print("MQTT connected OK Returned code=",rc)
    else:
        print("MQTT bad connection Returned code=",rc)

def on_disconnect_handler(client, userdata, rc):
    if rc != 0:
        print("MQTT disconnected: "  +str(rc))
    client.connected_flag=False

def on_log_handler(client, userdata, level, buf):
    print("log: ",buf)

def GetRepeatSeconds():
    if len(sys.argv) < 2:
        return(0)
    try:
        return(int(sys.argv[1]))
    except ValueError:
        return(0)

def ProcessHMDevice(id, data):
    i = data.find("(")
    if i <= 0:
        print("ERROR: ( not found in " + d)
        return
    j = data.find(")")
    if j <= 0:
        print("ERROR: ) not found in " + d)
        return
    d = data[:i]
    v = data[i+1:j]
    print("Publishing: " + id + " " + d + " " + v)
    client.publish(MQTTtopic + id + "/" + d, v)

def ProcessHMLine(line):
    i = line.find(" ")
    if i <= 1:
        print("ERROR: ID not found in " + line)
        return
    id = line[0:i]
    print("ID: " + id)
    j = line.find("(")
    if j <= 1:
        print("ERROR: First ( not found in " + line)
        return
    while j >= 0 and (line[j] != " "):
        j = j-1
    if j < 0:
        print("ERROR: First space before ( not found in " + line)
        return
    device = line[i:j]
    print("Device: " + device)
    client.publish(MQTTtopic + id + "/device", device)
    data = line[j+1:].split(" ")
    for d in data:
        ProcessHMDevice(id, d)

print("Starting script")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
myip = s.getsockname()[0]
print("My IP Address is " + myip)

client = mqtt.Client(client_id=MQTTtopic.replace('/','_'))
client.username_pw_set(MQTTUsername, MQTTPassword)
client.on_log=on_log_handler
client.on_connect=on_connect_handler
client.on_disconnect=on_disconnect_handler
client.connected_flag=False
print("Connecting to mqtt")

while not client.connected_flag:
    try:
        client.connect(MQTTServer)
        break
    except:
        print("Error connecting to mqtt daemon, retrying in 5 seconds")
        time.sleep(5)

print("Connected to mqtt")
client.loop_start()
print("Loop started")
atexit.register(handle_exit)
signal.signal(signal.SIGTERM, sigint_handler)
signal.signal(signal.SIGINT, sigint_handler)
client.publish(MQTTtopic + "status", "running")
client.publish(MQTTtopic + "ip", myip)

lastreadtime = datetime.utcnow() - timedelta(days=1)

while 1:
    # body of the loop ...
    # Fill a string with date, humidity and temperature
    try:
        stream = os.popen(HMShellFile)
        lines = stream.readlines()
#        print(lines)
        if len(lines) >= 1:
            for line in lines:
                ProcessHMLine(line.strip())

    except BaseException as ex:
        # Get current system exception
        ex_type, ex_value, ex_traceback = sys.exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" %ex_value)
        print("Stack trace : %s" %stack_trace)

    rsecs = GetRepeatSeconds()
    if rsecs > 0:
        time.sleep(rsecs)
    else:
        break

print("Stopping script")


client.publish(MQTTtopic + "status", "stopped")
client.disconnect()
client.loop_stop()
