import time
import pexpect
import subprocess
import requests
from math import pow
import pprint
import json


#--------- Bluetooth Exeption Class
class bluetoothException(Exception):
    pass

#---*9631------


#--------- Data Trasnmitter Between Wrapper And Server
class data_transmitter():
    server_address = "http://127.0.0.1:3000/beacons/"
    server_port = 3000
    url = server_address

    def send_data(self , data):
        try :
            #TODO : make a proper request based on api provided by the server
            requests.post(url=data_transmitter.url ,data = data)
        except Exception as e :
            print(e)

    def fetch_beacons_mac_address(self):
        try:
            # TODO : make a proper request based on api provided by the server
            addrs = requests.get(url=data_transmitter.url)
        except Exception as e:
            print(e)
        else :
            return addrs

#---------


#--------- Wrapper Class
class wrapper():

    def __init__(self):
        out = subprocess.check_output("rfkill unblock bluetooth", shell=True)
        self.child = pexpect.spawn("bluetoothctl", echo=False)
        self.setup()

    #initial setup
    def setup(self):
        self.run_command("discoverable on")
        self.run_command("scan on")

    #fetch the beacon information from the server
    def fetch_beacon_addrs(self):
        #TODO : get the addresses from the server and their position
        #in case of test
        devices = [{"mac_address" : "DC:78:C7:F3:AD:51" , "x" : 0 , "y":0}]
        return devices
        pass

    #run a command
    def run_command(self , command , sleepTime = 0):
        self.child.send(command + "\n")
        time.sleep(sleepTime)
        result = self.child.expect(["bluetooth" , pexpect.EOF])

        if result :
            raise bluetoothException("Failure happened " + command)

        return self.child.before.split("\r\n")

    #start scanning
    def start_scan(self):
        try :
            output = self.run_command("scan on")
        except bluetoothException as e:
            print(e)
            return None

    #parse device prime info
    def parse_device_prime_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2]
                    }

        return device

    #get all the available devices in the environment
    def get_available_devices(self):
        try:
            result = self.run_command("devices")
        except bluetoothException as e:
            print(e)
        else :
            available_devices  = []
            for r in result:
                device = self.parse_device_prime_info(r)
                if (device):
                    available_devices.append(device)

            return available_devices

    #filter beacons from other bluetooth devices
    def filter_beacons(self):
        all_dev = self.get_available_devices()
        fetched_beacons_addr = self.fetch_beacon_addrs()
        available_beacons = []
        #find the available beacons
        for dev in all_dev:
            for beacon in fetched_beacons_addr:
                #compare the available mac_addresses with fetched mac_addresses from server
                if(beacon["mac_address"] == dev["mac_address"]):
                    #store the filtered one
                    available_beacons.append(dev)
        return available_beacons

    #get information from available beacons
    def get_beacons_info(self):
        available_beacons = self.filter_beacons()
        online_beacons_info = []
        for dev in available_beacons:
            beacon_information = self.get_beacon_detailed_info(dev["mac_address"])
            if(beacon_information["RSSI"] is not  None):
                online_beacons_info.append(beacon_information)

        return online_beacons_info

    #parse the info of a bluetooth beacon
    def parse_beacon_info(self, info_string):
        device = {}
        attribute_list = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)
        if string_valid:
            try:
                #parse the string
                #first item in the array is the device address and the last one is "]" which has no use
                for i in range(1 , len(info_string) - 1):
                    pair = info_string[i].split(":")

                    #TODO : please refactor codes below !!!
                    #from here(welcome to block of doom) [
                    key = pair[0].replace(" " , "").strip()
                    value = pair[1].replace(" " , "").strip()
                    if(key == "RSSI"):
                        attribute_list["{}".format(key)] = int(value)
                    else :
                        attribute_list["{}".format(key)] = value
                    #] -> TODO : refactor this block of code for god sake

                pass
            except ValueError:
                pass
            else :
                return attribute_list

    #get the info of a device provided its name
    def get_beacon_detailed_info(self, device_addr):
        command = "info {}".format(device_addr)
        try :
            raw_info = self.run_command(command)
        except bluetoothException as e:
            print(e)
        else:
            info = self.parse_beacon_info(raw_info)
            info["mac_address"] = device_addr
            return info

    #calculate the distance using the rssi
    def calculate_distance(self , rssi , txpower = -65):
        #TODO : ask if it is right or not to use a hard coded transmit power
        if (rssi == 0):
            return -1.0
        ratio = rssi * 1.0 / txpower
        if (ratio < 1.0) :
            return pow(ratio, 10)
        else:
            distance = (0.89976) * pow(ratio, 7.7095) + 0.111;
        return distance

#---------


if __name__ == "__main__" :
    # print("intiating")
    # pp = pprint.PrettyPrinter(indent=4)
    # wrapper = wrapper()
    # print("scanning")
    # for i in range(1 , 10):
    #     print(i)
    #     time.sleep(0.1)
    # print("getting available devices")
    # dev_list = wrapper.get_beacons_info()
    # counter = 0
    # for dev_info in dev_list :
    #     print(">>>> Result #{} <<<<".format(counter))
    #     pp.pprint(dev_info)
    #     print("Estimated distance : {} meters".format(wrapper.calculate_distance((dev_info["RSSI"]))))
    #     print("--------------------")
    #     counter = counter + 1

    print("fetch data from server")
    transmitter = data_transmitter()
    r = transmitter.fetch_beacons_mac_address()
    print(str(r.content))