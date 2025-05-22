# main_log.py
import json
import os
from dotenv import load_dotenv

def fetch_data(api_key):
    print(f"API key in use {api_key}")
    with open("app.log", "a") as log_file:
        log_file.write(f"API key used- {api_key}\n")
        log_file.write("Data fetched successfully\n")

def main():
    # safe API key. all secrets protected, but prints and logs the Key!!
    load_dotenv()
    api_key = os.getenv("VAL")
    if not api_key:
        raise ValueError("API key not found in environment")
    fetch_data(api_key)

if __name__ == "__main__":
    main()
