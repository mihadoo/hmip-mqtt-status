# Report Homematic IP device status over MQTT

This python script is a gateway between Homematic IP Access Point and MQTT which runs "hmip_cli.py --list-devices" once or every X seconds (pass the number of seconds as the only parameter) and reports the status of all Homematic IP devices handled by the Homematic IP Access Point over MQTT. You will have to change the constants in the python script for the correct connection to the MQTT server and the correct location of the hmip_cli.py file.

Make sure that "hmip_cli.py --list-devices" is working from command line before using this python script. You can get hmip_cli.py and instructions how to get it running with the Homematic IP Access Point here:

https://github.com/hahn-th/homematicip-rest-api

This is an example of what is reported over MQTT:

![MQTT Explorer](HMtoMQTT.png?raw=true "MQTT Explorer")
