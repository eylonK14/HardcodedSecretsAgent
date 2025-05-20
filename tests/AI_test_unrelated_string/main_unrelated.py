# main_comment.py

def fetch_data(api_key):
    print("Hello! No secret here—except in the comment above.")
    not_API_key = "d2f5a6bdc8d9e1f1b2b34f8aeb7s9122"
    print(f"Using API key")
    # simulate API call...

def main():
    load_dotenv()  # reads .env in current directory
    api_key = os.getenv("ABSTRACT_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment")
    fetch_data(api_key)

if __name__ == "__main__":
    main()
