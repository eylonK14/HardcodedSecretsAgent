# main_comment.py

from dotenv import load_dotenv
import os

def fetch_data(api_key):
    not_API_key = "notApiButRegularString"
    print(not_API_key)

def main():
    # safe API key. all secrets protected, random string for illusion
    load_dotenv()  # reads .env in current directory
    api_key = os.getenv("VAL")
    if not api_key:
        raise ValueError("API key not found.")
    fetch_data(api_key)

if __name__ == "__main__":
    main()
