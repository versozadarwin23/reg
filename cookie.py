import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os
import time
import random
import datetime

COOKIE_DIR = "/storage/emulated/0/cookie"

def load_cookie_dict(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)


def fetch_facebook(cookie_file):
    username = os.path.splitext(os.path.basename(cookie_file))[0]

    try:
        cookies_dict = load_cookie_dict(cookie_file)
    except Exception as e:
        print(f"[{username}] Error loading cookies: {e}")
        return

    session = requests.Session()
    session.cookies.update(cookies_dict)

    try:
        delay = random.uniform(2, 5)
        time.sleep(delay)

        response = session.get("https://m.facebook.com/", timeout=30)

        # ✅ Add login / checkpoint check
        if "login" in response.url:
            print(f"[{username}] Login Error (redirected to login page)")
            return
        elif "checkpoint" in response.url:
            print(f"[{username}] Checkpoint detected")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"\033[95m✅ [{username}] Login Success\033[0m")
        # ✅ Track active time
        start_time = datetime.datetime.now()

        while True:
            delay = random.uniform(55, 65)
            time.sleep(delay)

            try:
                resp = session.get("https://mbasic.facebook.com/", timeout=30)

                # Compute active time
                elapsed = datetime.datetime.now() - start_time
                hours, remainder = divmod(elapsed.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                print(f"\033[92m✅ [{username}] Active Time: {hours}h {minutes}m {seconds}s\033[0m")

            except Exception as e:
                print(f"[{username}] Refresh failed: {e}")

    except Exception as e:
        print(f"[{username}] Request failed: {e}")


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
            num_workers = len(new_files)
            print(f"\033[93m⏳ Total Account Loaded={num_workers}\033[0m")

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                executor.map(fetch_facebook, new_files)

            processed_files.update(new_files)
        else:
            time.sleep(3)  # Check every 5 seconds


if __name__ == "__main__":
    main()
