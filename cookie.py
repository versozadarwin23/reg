import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os
import time
import random
import datetime
os.system("clear")
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

        if "login" in response.url:
            print(f"[{username}] Login Error (redirected to login page)")
            return
        elif "checkpoint" in response.url:
            print(f"[{username}] Checkpoint detected")
            return

        print(f"\033[95m✅ [{username}] Login Success\033[0m")
        start_time = datetime.datetime.now()

        while True:
            delay = random.uniform(55, 65)
            time.sleep(delay)

            try:
                resp = session.get("https://mbasic.facebook.com/", timeout=30)
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

    with ThreadPoolExecutor(max_workers=50) as executor:
        while True:
            cookie_files = [
                os.path.join(COOKIE_DIR, fname)
                for fname in os.listdir(COOKIE_DIR)
                if fname.endswith(".json")
            ]

            new_files = [f for f in cookie_files if f not in processed_files]

            for new_file in new_files:
                print(f"\033[94m✅ New Account Added: {os.path.basename(new_file)}\033[0m")
                executor.submit(fetch_facebook, new_file)
                processed_files.add(new_file)

            time.sleep(3)


if __name__ == "__main__":
    main()
