import os
import requests
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init
import re

# Initialize Colorama
init(autoreset=True)

# Load environment variables from the .env file
load_dotenv()

# API key and host from .env
api_key = os.getenv('RAPIDAPI_KEY')
api_host = os.getenv('RAPIDAPI_HOST')

# Validate environment variables
if not api_key or not api_host:
    print(f"{Fore.RED}Error: Missing RAPIDAPI_KEY or RAPIDAPI_HOST in .env file{Style.RESET_ALL}")
    exit(1)

# Function to print formatted and colored JSON
def print_colored_json(data, level=0):
    indent = "    " * level
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{indent}{Fore.CYAN}{key}{Style.RESET_ALL}:")
                print_colored_json(value, level + 1)
            else:
                print(f"{indent}{Fore.CYAN}{key}{Style.RESET_ALL}: {Fore.YELLOW}{value}{Style.RESET_ALL}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{indent}{Fore.CYAN}[{i}]{Style.RESET_ALL}:")
            print_colored_json(item, level + 1)
    else:
        print(f"{indent}{Fore.YELLOW}{data}{Style.RESET_ALL}")

# Function to validate phone number format
def validate_phone_number(phone_number):
    # Remove all non-digit characters
    cleaned_number = re.sub(r'\D', '', phone_number)
    
    # Check if it's a valid international format (10-15 digits)
    if 10 <= len(cleaned_number) <= 15:
        return cleaned_number
    else:
        return None

# Function to get location data using IP API
def get_location_data(ip_address):
    if not ip_address or ip_address == "N/A":
        return None
    
    location_url = f"http://ip-api.com/json/{ip_address}"
    
    try:
        location_response = requests.get(location_url, timeout=5)
        location_response.raise_for_status()
        return location_response.json()
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Location data error: {e}{Style.RESET_ALL}")
        return None

# Function to query WhatsApp number data
def get_whatsapp_number_info(phone_number):
    url = f"https://{api_host}/number/{phone_number}"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }
    
    try:
        # Make a GET request to the API
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Check for HTTP errors

        # Get response in JSON format
        data = response.json()

        # Print formatted and colored JSON
        print(f"\n{Fore.GREEN}WhatsApp Information:{Style.RESET_ALL}")
        print_colored_json(data)
        
        # Extract IP if available for location data
        ip_address = None
        if isinstance(data, dict):
            # Common fields where IP might be stored
            ip_address = data.get('ip') or data.get('last_ip') or data.get('connected_ip') or "N/A"
        
        # Get and display location data
        print(f"\n{Fore.GREEN}Location Information:{Style.RESET_ALL}")
        location_data = get_location_data(ip_address)
        if location_data:
            print_colored_json(location_data)
        else:
            print(f"{Fore.YELLOW}No location data available for IP: {ip_address}{Style.RESET_ALL}")
    
    except requests.exceptions.HTTPError as http_err:
        print(f"{Fore.RED}HTTP Error: {http_err}{Style.RESET_ALL}")
        if response.status_code == 401:
            print(f"{Fore.RED}Check your API key and host configuration{Style.RESET_ALL}")
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}Request timed out. API might be slow or unavailable.{Style.RESET_ALL}")
    except requests.exceptions.RequestException as req_err:
        print(f"{Fore.RED}Request Error: {req_err}{Style.RESET_ALL}")
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error decoding JSON response.{Style.RESET_ALL}")
    except Exception as err:
        print(f"{Fore.RED}An unexpected error occurred: {err}{Style.RESET_ALL}")

def main():
    # Green banner
    print(Fore.GREEN + """
     __i
    |---|    
    |[_]|    
    |:::|    
    |:::|    
    `\\   \\   
      \\_=_\\ 
    WhatsApp Number Information Lookup
    """ + Style.RESET_ALL)

    number = input("Enter the phone number (with country code): ")
    
    # Validate input
    validated_number = validate_phone_number(number)
    if not validated_number:
        print(f"{Fore.RED}Invalid phone number format. Please enter a valid international number.{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Checking number: {validated_number}{Style.RESET_ALL}")
    
    # Query number data
    get_whatsapp_number_info(validated_number)

if __name__ == "__main__":
    main()