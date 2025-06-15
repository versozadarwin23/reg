import os
import requests
from bs4 import BeautifulSoup
import time
import csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import re
import json
from requests.utils import dict_from_cookiejar, cookiejar_from_dict

os.system("clear")

# Clone repo once
while True:
    try:
        subprocess.run(["rm", "-rf", "reg"], check=True)
        subprocess.run(["git", "clone", "https://github.com/versozadarwin23/reg.git"], check=True)
        break
    except:
        pass

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
    'Referer': 'https://m.facebook.com/',
    'Content-Type': 'application/x-www-form-urlencoded'
}

windows_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Referer': 'https://m.facebook.com/',
    'Content-Type': 'application/x-www-form-urlencoded'
}

lock = Lock()
success_count = 0
error_count = 0
logged_accounts = set()

def update_status_in_acc_created(username, status):
    with lock:
        with open("/storage/emulated/0/Acc_Created.csv", 'r', newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

        for row in rows:
            account_link = row.get('ACCOUNT LINK', '').strip()
            if account_link.endswith(username):
                row['STATUS'] = status

        with open("/storage/emulated/0/Acc_Created.csv", 'w', newline='', encoding='latin-1') as csvfile:
            fieldnames = rows[0].keys() if rows else ['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'STATUS']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

def keep_alive(name, username, password, account_link):
    global success_count, error_count

    session = requests.Session()
    cookie_file = f"sessions/{username}.json"

    reused_session = False

    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, "r") as f:
                cookies = json.load(f)
            session.cookies = cookiejar_from_dict(cookies)

            home_check = session.get("https://m.facebook.com/home.php", headers=windows_headers, timeout=15)
            if "c_user" in session.cookies:
                with lock:
                    success_count += 1
                uid = session.cookies.get("c_user")
                print(f"\033[92m[✓] {name} Keep-alive OK: {uid} |  (session reused)\033[0m")
                reused_session = True
        except:
            pass

    if not reused_session:
        try:
            login_page = session.get('https://m.facebook.com/login', headers=headers, timeout=60, allow_redirects=True)
            soup = BeautifulSoup(login_page.text, 'html.parser')

            form = soup.find('form', {'id': 'login_form'})
            if not form:
                with lock:
                    error_count += 1
                update_status_in_acc_created(username, 'Login form not found')
                return

            action = form.get('action')
            post_url = 'https://m.facebook.com' + action

            payload = {'email': username, 'pass': password}
            for input_tag in form.find_all('input'):
                name_input = input_tag.get('name')
                value = input_tag.get('value', '')
                if name_input and name_input not in payload:
                    payload[name_input] = value

            response = session.post(post_url, data=payload, headers=headers, timeout=60, allow_redirects=True)

            if "c_user" in session.cookies:
                uid = session.cookies.get("c_user")
                with lock:
                    success_count += 1
                os.makedirs("sessions", exist_ok=True)
                cookies_dict = dict_from_cookiejar(session.cookies)
                cookies_dict['active_time'] = "0m"
                with open(cookie_file, "w") as f:
                    json.dump(cookies_dict, f)
                print(f"\033[92m[✓] {name} Keep-alive OK: {uid} | (login success)\033[0m")
            else:
                with lock:
                    error_count += 1
                update_status_in_acc_created(username, 'Login failed')
                return
        except Exception as e:
            with lock:
                error_count += 1
            update_status_in_acc_created(username, f'Error: {e}')
            return

    start_time = time.time()
    retry_count = 0
    max_retries = 3

    while True:
        try:
            url = 'https://m.facebook.com/home.php'
            response = session.get(url, headers=windows_headers, timeout=10, allow_redirects=True)

            if "c_user" in session.cookies:
                retry_count = 0
                uid = session.cookies.get("c_user")
                elapsed_seconds = time.time() - start_time
                elapsed_minutes = int(elapsed_seconds // 60)
                hours = elapsed_minutes // 60
                minutes = elapsed_minutes % 60
                active_time = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                cookies_dict = dict_from_cookiejar(session.cookies)
                cookies_dict['active_time'] = active_time
                with open(cookie_file, "w") as f:
                    json.dump(cookies_dict, f)

                print(f"\033[92m[✓] {name} Keep-alive OK: {uid} | Active: {active_time}\033[0m")
            else:
                return

        except requests.exceptions.RequestException:
            retry_count += 1
            if retry_count >= max_retries:
                start_time = time.time()
                retry_count = 0

        except:
            pass

        time.sleep(60)

def load_accounts():
    while True:
        try:
            accounts = []
            pattern = re.compile(r'^https://www\.facebook\.com/profile\.php\?id=')

            filepath = "/storage/emulated/0/Acc_Created.csv"

            with open(filepath, newline='', encoding='latin-1') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row.get('NAME', '').strip()
                    account_link = row.get('ACCOUNT LINK', '').strip()
                    password = row.get('PASSWORD', '').strip()
                    if not account_link or not password:
                        continue
                    username = pattern.sub('', account_link)
                    accounts.append([name, username, password, account_link])
            return accounts

        except Exception:
            time.sleep(3)

def main():
    executor = None
    prev_account_count = 0

    while True:
        accounts = load_accounts()
        current_account_count = len(accounts)

        if current_account_count != prev_account_count:
            if executor:
                executor.shutdown(wait=False)
            max_workers = current_account_count if current_account_count > 0 else 1
            executor = ThreadPoolExecutor(max_workers=max_workers)
            prev_account_count = current_account_count

        for name, username, password, account_link in accounts:
            if username not in logged_accounts:
                logged_accounts.add(username)
                executor.submit(keep_alive, name, username, password, account_link)

        time.sleep(60)

if __name__ == "__main__":
    main()
