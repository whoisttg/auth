import requests
import json
import random
import string
import base64
import wmi
import os
import subprocess
import datetime

WEBHOOK = "<YOUR_DISCORD_WEBHOOK>"
ACCESS_TOKEN = "<YOUR_GITHUB_TOKEN>"
REPO = "<YOUR_PRIVATE_REPO>"
AUTHOR = "<REPO_AUTHOR>"

def get_hwid():
    try:
        wmi_obj = wmi.WMI()
        csproduct = wmi_obj.Win32_ComputerSystemProduct()[0]
        hwid = csproduct.UUID
        return hwid
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=40))

def log_info(webhook, key):
    computer_os = subprocess.run('wmic os get Caption', capture_output=True, shell=True).stdout.decode(errors='ignore').strip().splitlines()[2].strip()
    username = os.getenv("UserName")
    hostname = os.getenv("COMPUTERNAME")
    hwid = get_hwid()
    ip = requests.get('https://api.ipify.org').text

    data = {
        "embeds": [
            {
                "title": "Auth",
                "color": 6732278,
                "fields": [
                    {
                        "name": "System Info",
                            "value": f'''💻 **PC Username:** `{username}`\n:desktop: **PC Name:** `{hostname}`\n🌐 **OS:** `{computer_os}`\n\n👀 **IP:** `{ip}`\n🔑 **KEY:** `{key}`\n🔧 **HWID:** `{hwid}`\n\n'''
                    }
                ],
                "footer": {
                    "text": "Auth"
                },
                "thumbnail": {
                    "url": "/your/logo.png"
                }
            }
        ],
        "username": "Auth",
        "avatar_url": "/your/logo.png"
    }

    requests.post(webhook, json=data)

def count(access_token):
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"
    
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        content = response_data['content']
        decoded_content = base64.b64decode(content).decode('utf-8')

        try:
            json_content = json.loads(decoded_content)
            num_keys = len(json_content)
            return num_keys
        except json.JSONDecodeError:
            print("Error parsing JSON content.")
            return None
    else:
        print("Failed to fetch file contents.")
        return None

def prettify(access_token):
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"
  
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        content = response_data['content']
        decoded_content = base64.b64decode(content).decode('utf-8')
        try:
            parsed_content = json.loads(decoded_content)
            prettified_content = json.dumps(parsed_content, indent=4)
        except json.JSONDecodeError:
            print("Error parsing JSON content.")
            return False

        data = {
            "message": "Prettify members.json",
            "content": base64.b64encode(prettified_content.encode()).decode(),
            "sha": response_data['sha']
        }
        update_response = requests.put(url, headers=headers, json=data)
        if update_response.status_code == 200:
            print("members.json prettified and updated successfully.")
            return True
        else:
            print("Failed to update members.json.")
            return False
    else:
        print("Failed to fetch file contents.")
        return False

def update(access_token, new_keys):
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"
    
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        content = base64.b64decode(response_data['content']).decode('utf-8')
        try:
            content_json = json.loads(content)
        except json.JSONDecodeError:
            content_json = {}

        for key in new_keys:
            content_json[key] = {"hwid": "", "uid": "", "date": "", "last": "", "injections": "0"}
        
        updated_content = json.dumps(content_json)
        
        data = {
            "message": "Added new keys",
            "content": base64.b64encode(updated_content.encode()).decode(),
            "sha": response_data['sha']
        }
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200:
            print("Keys added successfully.")
        else:
            print("Failed to add keys.")
    else:
        print("Failed to fetch file contents.")

def reset_hwid(access_token, key):
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"

    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        content = response_data['content']
        decoded_content = base64.b64decode(content).decode('utf-8').strip()
        try:
            json_content = json.loads(decoded_content)
            if key in json_content:
                json_content[key]['hwid'] = ""

                updated_content = json.dumps(json_content, indent=4)
                encoded_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
                
                update_data = {
                    "message": "Reset HWID",
                    "content": encoded_content,
                    "sha": response_data['sha']
                }
                update_url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"
                update_response = requests.put(update_url, headers=headers, json=update_data)
                
                if update_response.status_code == 200:
                    print(f"HWID reset for key '{key}'.")
                else:
                    print("Failed to update file on GitHub.")
            else:
                print(f"Key '{key}' not found.")
        except (json.JSONDecodeError, ValueError) as e:
            print("Error parsing content:", e)
    else:
        print("Failed to fetch file contents.")

def get_member(access_token, key):
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"

    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        content = response_data['content']
        decoded_content = base64.b64decode(content).decode('utf-8').strip()
        try:
            json_content = json.loads(decoded_content)
            if key in json_content:
                member_info = json_content[key]
                print(f"Info for key '{key}':")
                print(json.dumps(member_info, indent=4))
            else:
                print(f"Key '{key}' not found.")
        except (json.JSONDecodeError, ValueError) as e:
            print("Error parsing content:", e)
    else:
        print("Failed to fetch file contents.")

def get_uid(access_token):
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"

    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        content = response_data['content']
        decoded_content = base64.b64decode(content).decode('utf-8').strip()

        try:
            json_content = json.loads(decoded_content)
            uids = [int(member['uid']) for member in json_content.values() if member.get('uid') and member['uid'].isdigit()]
            last_uid = max(uids) if uids else 0
            new_uid = last_uid + 1
            return new_uid
        except (json.JSONDecodeError, ValueError) as e:
            print("Error parsing content:", e)
            return None
    else:
        print("Failed to fetch file contents.")
        return None

def check_key(access_token, key):
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"

    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        content = response_data['content']
        decoded_content = base64.b64decode(content).decode('utf-8').strip()
        try:
            json_content = json.loads(decoded_content)
            if key in json_content:
                if json_content[key]["uid"] == "":
                    new_uid = get_uid(access_token)
                    if new_uid is not None:
                        json_content[key]["uid"] = str(new_uid)
                        json_content[key]["date"] = str(datetime.datetime.now())
                    else:
                        print("Failed to get UID.")
                else:
                    print("UID already set for this key.")

                if json_content[key]["hwid"] != "":
                    if json_content[key]["hwid"] == get_hwid():
                        json_content[key]["last"] = str(datetime.datetime.now())
                        json_content[key]["injections"] = str(int(json_content[key]["injections"]) + 1)
                        print("Valid HWID.")
                    else:
                        print("Invalid HWID.")
                else:
                    json_content[key]["hwid"] = get_hwid()
                    json_content[key]["injections"] = str(int(json_content[key]["injections"]) + 1)
                    json_content[key]["last"] = str(datetime.datetime.now())
                data = {
                    "message": "Set HWID and UID",
                    "content": base64.b64encode(json.dumps(json_content).encode()).decode(),
                    "sha": response_data['sha']
                }
                update_response = requests.put(url, headers=headers, json=data)
                if update_response.status_code != 200:
                    print("Failed to update members.json.")
            else:
                print("Invalid key.")
        except json.JSONDecodeError as e:
            print("Error parsing content:", e)
    else:
        print("Failed to fetch file contents.")

def check_hwid(access_token):
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"

    headers = {
        "Authorization": f"token {access_token}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    user_hwid = get_hwid()

    if "content" in data:
        members_json = data["content"]
        members_json = base64.b64decode(members_json).decode("utf-8")
        members_data = json.loads(members_json)

        for key, value in members_data.items():
            if value.get("hwid") == user_hwid:
                return key

    return None

def return_value(access_token, val, key):
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/members.json"

    headers = {
        "Authorization": f"token {access_token}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if "content" in data:
        members_json = data["content"]
        members_json = base64.b64decode(members_json).decode("utf-8")
        members_data = json.loads(members_json)

        for i, value in members_data.items():
            if i == key:
                return value.get(val)
            
    return None

def ban_hwid(access_token, hwid, reason):
    banned_data = {hwid: {"time": str(datetime.datetime.now()), "reason": reason}}
    json_content = json.dumps(banned_data, indent=4)

    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/banned.json"

    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data['sha']

        existing_content = base64.b64decode(file_data['content']).decode('utf-8')
        existing_data = json.loads(existing_content)
        existing_data.update(banned_data)
        updated_content = json.dumps(existing_data, indent=4)

        data = {
            "message": f"Ban HWID: {hwid}",
            "content": base64.b64encode(updated_content.encode()).decode(),
            "sha": sha
        }

        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"HWID '{hwid}' banned successfully.")
        else:
            print("Failed to ban HWID.")
    else:
        print("Failed to fetch file contents.")

def is_hwid_banned(access_token, hwid):
    url = f"https://api.github.com/repos/{AUTHOR}/{REPO}/contents/data/banned.json"

    headers = {
        "Authorization": f"token {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        banned_json = json.loads(base64.b64decode(file_data['content']).decode('utf-8'))

        if hwid in banned_json:
            banned_time = banned_json[hwid]
            print(f"HWID '{hwid}' was banned at: {banned_time}")
            return True
        else:
            print(f"HWID '{hwid}' is not banned.")
            return False
    else:
        print("Failed to fetch file contents.")
        return False

if __name__ == "__main__":

    # THIS IS THE ADMIN PANEL, ADD NECESSARY FUNCTIONS TO ANOTHER FILE


    #key = input("Enter key: ")
    #log_info(WEBHOOK, key)
    #reset_hwid(ACCESS_TOKEN, key)

    #get_member(ACCESS_TOKEN, key)

    #check_key(ACCESS_TOKEN, key)

    #print(get_uid(ACCESS_TOKEN))

    num_keys = 500
    new_keys = [generate_key() for _ in range(num_keys)]
    update(ACCESS_TOKEN, new_keys)

    print(f"Total keys: {count(ACCESS_TOKEN)}")
    #print(f"Last uid: {get_uid(ACCESS_TOKEN)}")

    #hwid = input("Enter HWID: ")
    #reason = input("Enter Reason: ")
    #is_hwid_banned(ACCESS_TOKEN, hwid)
    #ban_hwid(ACCESS_TOKEN, hwid, reason)

    prettify(ACCESS_TOKEN)
