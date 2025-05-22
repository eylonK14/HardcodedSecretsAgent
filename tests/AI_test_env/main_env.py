# main_env.py
import os
from dotenv import load_dotenv

def fetch_data(api_key):
    print(f"Using API key")

def main():
    load_dotenv()  # reads .env in current directory
    api_key = os.getenv("ABSTRACT_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment")
    fetch_data(api_key)

if __name__ == "__main__":
    main()
