import requests
from fastapi import Request
import os
from Config.config import settings
from datetime import datetime




async def intruder_info(request: Request):
        #intruder_list = []
        client_ip = request.client.host
        headers = request.headers
        user_agent = headers.get("User-Agent")
        mac_address = headers.get("X-MAC-Address")  # Custom header for MAC Address
        location = requests.get(f"https://ipinfo.io/{client_ip}/geo").json()

        intruder_info = {
            "ip_address": client_ip,
            "mac_address": mac_address,
            "user_agent": user_agent,
            "location": location,
        }
        print("intruder info dict: ", intruder_info)
        settings.intruder_list.append(intruder_info)
        print(f"Intruder detected: {intruder_info}")

        return intruder_info


async def log_intruder_info(ip_addr: str, mac_addr: str, user_agent: str, location: str):
    # Get current date to create or append to the log file
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file_name = f"intruder_log_{current_date}.txt"
    log_directory = "security/logs/"

    os.makedirs(log_directory, exist_ok=True)
    
    print("log directory: ", log_directory)
    # Check if the log file exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    
    log_filepath = os.path.join(log_directory, log_file_name)
    

    # Create log entry
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{ip_addr} | {mac_addr} | {user_agent} | {location} | {timestamp}"

    # Check if the log file already exists
    if os.path.exists(log_filepath):
        with open(log_filepath, 'a') as file:
            file.write("================================================================================\n")
            file.write(log_entry + "\n")
    else:
        with open(log_file_name, 'w') as file:
            file.write("IP Addr | Mac Addr | User Agent | location | Timestamp\n")
            file.write(log_entry + "\n")

    return log_filepath




