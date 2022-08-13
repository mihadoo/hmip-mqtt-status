# hmip-mqtt-status
Report Homematic IP device status over MQTT

This python script runs "hmip_cli.py --list-devices" every 60 seconds and reports the status of all Homematic IP devices handled by the Homematic IP Bridge over MQTT. You will have to change the constants in the python script for the correct connection to the MQTT server and the correct location of the hmip_cli.py file.

Make sure that "hmip_cli.py --list-devices" is working from command line before using the python script. You can get hmip_cli.py and instructions how to get it running with the Homematic IP Bridge here:

https://github.com/hahn-th/homematicip-rest-api
