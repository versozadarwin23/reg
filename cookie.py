import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os
import time
import random

# 📌 Path where your cookie JSON files are stored
COOKIE_DIR = "/storage/emulated/0/cookie"

# User-Agent (your mobile Facebook Lite style)
USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
    "Chrome/70.0.3538.110 Mobile Safari/537.36 "
    "[FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]"
)


def load_cookie_dict(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)


def fetch_facebook(cookie_file):
    # Extract username from file name
    username = os.path.splitext(os.path.basename(cookie_file))[0]

    try:
        cookies_dict = load_cookie_dict(cookie_file)
    except Exception as e:
        print(f"[{username}] Error loading cookies: {e}")
        return

    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    session.cookies.update(cookies_dict)

    try:
        response = session.get("https://www.facebook.com/", timeout=30)
        time.sleep(random.uniform(2, 5))  # ✅ anti-automation delay

        # ✅ Add login / checkpoint check
        if "login" in response.url:
            print(f"Login Error: {username}")
            return
        elif "checkpoint" in response.url:
            print(f"Checkpoint: {username}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Login Success: {username}")
        os.makedirs("status", exist_ok=True)
        with open(f"status/{username}.html", "w", encoding="utf-8") as file:
            file.write(response.text)

        # ✅ Stay online: keep refreshing every ~1min forever
        while True:
            delay = random.uniform(55, 65)
            time.sleep(delay)
            try:
                resp = session.get("https://www.facebook.com/", timeout=30)
                print(f"[{username}] Refreshed Facebook")
            except Exception as e:
                print(f"[{username}] Refresh failed: {e}")

    except Exception as e:
        pass


def main():
    processed_files = set()

    while True:
        cookie_files = [
            os.path.join(COOKIE_DIR, fname)
            for fname in os.listdir(COOKIE_DIR)
            if fname.endswith(".json")
        ]

        new_files = [f for f in cookie_files if f not in processed_files]

        if new_files:
            print(f"Found {len(new_files)} new cookie files.")
            num_workers = len(new_files)
            print(f"Running with max_workers={num_workers}")

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                executor.map(fetch_facebook, new_files)

            processed_files.update(new_files)
        else:
            print("No new cookie files found.")

        time.sleep(5)  # Check every 5 seconds


if __name__ == "__main__":
    main()
