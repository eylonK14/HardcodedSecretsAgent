
from api_called import send_api_key
from random_called import send_other_str

def main():
    # Hardcoded API key (should NEVER be committed to git)
    api_key = "abstract 4f8aeb7c9123d4f5a6b7c8d9e0f1a2b3"
    safeStr = "safe string"
    send_api_key(api_key)
    send_other_str(safeStr)

if __name__ == "__main__":
    print('Hardcoded test')
    main()
