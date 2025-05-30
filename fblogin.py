import requests
from bs4 import BeautifulSoup
import time
import csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import re

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

def record_success(name, username, password, account_link, status):
    with lock:
        with open('login_results.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'STATUS'])
            writer.writerow({
                'NAME': name,
                'USERNAME': username,
                'PASSWORD': password,
                'ACCOUNT LINK': account_link,
                'STATUS': status
            })

def record_error(name, username, password, account_link, status):
    with lock:
        with open('login_errors.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'STATUS'])
            writer.writerow({
                'NAME': name,
                'USERNAME': username,
                'PASSWORD': password,
                'ACCOUNT LINK': account_link,
                'STATUS': status
            })

def keep_alive(name, username, password, account_link):
    global success_count, error_count

    session = requests.Session()
    try:
        login_page = session.get('https://m.facebook.com/login', headers=headers, timeout=10, allow_redirects=True)
        soup = BeautifulSoup(login_page.text, 'html.parser')

        form = soup.find('form', {'id': 'login_form'})
        if not form:
            print(f"[❌] [{name}] Login form not found.")
            with lock:
                error_count += 1
            record_error(name, username, password, account_link, 'Login form not found')
            return

        action = form.get('action')
        post_url = 'https://m.facebook.com' + action

        payload = {'email': username, 'pass': password}
        for input_tag in form.find_all('input'):
            name_input = input_tag.get('name')
            value = input_tag.get('value', '')
            if name_input and name_input not in payload:
                payload[name_input] = value

        response = session.post(post_url, data=payload, headers=headers, timeout=10, allow_redirects=True)

        if "c_user" in session.cookies:
            uid = session.cookies.get("c_user")
            with lock:
                success_count += 1
            record_success(name, username, password, account_link, f'SUCCESS (UID: {uid})')
        else:
            print(f"[❌] {name} Login failed.")
            with lock:
                error_count += 1
            record_error(name, username, password, account_link, 'Login failed')
            return
    except Exception as e:
        print(f"[⚠️] [{name}] Login error: {e}")
        with lock:
            error_count += 1
        record_error(name, username, password, account_link, f'Error: {e}')
        return

    start_time = time.time()

    while True:
        try:
            url = 'https://m.facebook.com/home.php'
            response = session.get(url, headers=windows_headers, timeout=10, allow_redirects=True)

            if "c_user" in session.cookies:
                uid = session.cookies.get("c_user")
                elapsed_seconds = time.time() - start_time
                elapsed_minutes = int(elapsed_seconds // 60)
                hours = elapsed_minutes // 60
                minutes = elapsed_minutes % 60
                active_time = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                profile_link = f'https://www.facebook.com/profile.php?id={uid}'
                print(f"[💓] {name} Keep-alive OK: {profile_link} | Active: {active_time}")
            else:
                print(f"[❌] [{name}] Session expired.")
                return
        except Exception as e:
            print(f"[⚠️] [{name}] Keep-alive error: {e}")

        time.sleep(60)

def load_accounts():
    while True:
        try:
            accounts = []
            pattern = re.compile(r'^https://www\.facebook\.com/profile\.php\?id=')
            with open("/storage/emulated/0/Acc_Created.csv", newline='', encoding='latin-1') as csvfile:
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
        except Exception as e:
            time.sleep(3)
            os.system("clear")
            print(f"Error loading accounts: {e}. Retrying...")

def main():
    # Initialize CSV files with headers
    with open('login_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'STATUS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    with open('login_errors.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'STATUS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

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
            print(f"[🔄] Restarted ThreadPoolExecutor with max_workers={max_workers}")

        for name, username, password, account_link in accounts:
            if username not in logged_accounts:
                logged_accounts.add(username)
                executor.submit(keep_alive, name, username, password, account_link)
                print(f"[➕] New account added and keep-alive started: {name}, {username}, {password}, {account_link}")

        time.sleep(60)

if __name__ == "__main__":
    main()
