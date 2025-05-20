# main_hardcoded.py

def fetch_data(api_key):
    # 🤫 Insecure: printing or sending the key as part of a request
    print(f"Using API key: {api_key}")
    # simulate API call...
    # ...

def main():
    # Hardcoded API key (should NEVER be committed to git)
    api_key = "abstract 4f8aeb7c9123d4f5a6b7c8d9e0f1a2b3"
    fetch_data(api_key)

if __name__ == "__main__":
    main()
