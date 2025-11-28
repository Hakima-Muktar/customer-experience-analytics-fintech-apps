import os
from dotenv import load_dotenv
load_dotenv()
def get_env(key: str, default: str = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        print(f"[WARNING] Environment variable '{key}' not found.")
    return value
if __name__ == "__main__":
    PROXY_URL = get_env("PROXY_URL")
    OUTPUT_FOLDER = get_env("OUTPUT_FOLDER", "./results")
    EMAIL_NOTIFICATION = get_env("EMAIL_NOTIFICATION")

    print("Play Store Scraper Environment Loaded:")
    print(f"PROXY_URL: {PROXY_URL}")
    print(f"OUTPUT_FOLDER: {OUTPUT_FOLDER}")
    print(f"EMAIL_NOTIFICATION: {EMAIL_NOTIFICATION}")
