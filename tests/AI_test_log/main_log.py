# main_log.py
import json
import os

def fetch_data(api_key):
    # Insecure: printing the secret to console
    print(f"API key in use: {api_key}")
    # Insecure: writing the secret into a log file
    with open("app.log", "a") as log_file:
        log_file.write(f"API key used: {api_key}\n")
        log_file.write("Data fetched successfully\n")

def main():
    load_dotenv()  # reads .env in current directory
    api_key = os.getenv("ABSTRACT_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment")
    fetch_data(api_key)

if __name__ == "__main__":
    main()
