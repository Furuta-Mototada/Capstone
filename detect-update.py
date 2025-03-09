import requests
import hashlib
import time
import os

# URL to monitor
URL = "https://www.shugiin.go.jp/internet/itdb_gian.nsf/html/gian/menu.htm"
# File to store the previous hash value
HASH_FILE = "page_hash.txt"
# Time interval (in seconds) to check for changes
CHECK_INTERVAL = 60


def get_page_hash(url):
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding  # Handle encoding properly
        page_content = response.text
        # Compute MD5 hash of the page content
        return hashlib.md5(page_content.encode("utf-8")).hexdigest()
    except Exception as e:
        print(f"Error fetching the page: {e}")
        return None


def load_previous_hash(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None


def save_hash(filepath, hash_value):
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(hash_value)


def monitor_website(url, hash_file, interval):
    previous_hash = load_previous_hash(hash_file)
    if previous_hash is None:
        # First run: save the current hash and exit
        print("No previous hash found. Saving current page hash.")
        current_hash = get_page_hash(url)
        if current_hash:
            save_hash(hash_file, current_hash)
        return

    while True:
        current_hash = get_page_hash(url)
        if current_hash is None:
            print("Failed to retrieve page content. Retrying...")
        elif current_hash != previous_hash:
            print("Change detected in the website!")
            save_hash(hash_file, current_hash)
            previous_hash = current_hash
        else:
            print("No change detected.")
        time.sleep(interval)


if __name__ == "__main__":
    monitor_website(URL, HASH_FILE, CHECK_INTERVAL)
