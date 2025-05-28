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

def record_result(section, text):
    with lock:
        with open('login_results.txt', 'a') as f:
            f.write(f"[{section}] {text}\n")

def keep_alive(email, password):
    global success_count, error_count

    session = requests.Session()
    try:
        login_page = session.get('https://m.facebook.com/login', headers=headers, timeout=10, allow_redirects=True)
        soup = BeautifulSoup(login_page.text, 'html.parser')

        form = soup.find('form', {'id': 'login_form'})
        if not form:
            with lock:
                error_count += 1
            record_result("ERROR", f"{email}\tLogin form not found.")
            return

        action = form.get('action')
        post_url = 'https://m.facebook.com' + action

        payload = {'email': email, 'pass': password}
        for input_tag in form.find_all('input'):
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            if name and name not in payload:
                payload[name] = value

        response = session.post(post_url, data=payload, headers=headers, timeout=10, allow_redirects=True)

        if "c_user" in session.cookies:
            uid = session.cookies.get("c_user")
            with lock:
                success_count += 1
            record_result("SUCCESS", f"{email}\t{uid}")
        else:
            with lock:
                error_count += 1
            record_result("ERROR", f"{email}\tLogin failed.")
            return
    except Exception as e:
        with lock:
            error_count += 1
        record_result("ERROR", f"{email}\tError: {e}")
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
            else:
                return
        except Exception as e:
            pass
        time.sleep(60)

def load_accounts():
    while True:
        try:
            accounts = []
            pattern = re.compile(r'^https://www\.facebook\.com/profile\.php\?id=')
            with open('Acc_Created.csv', newline='', encoding='latin-1') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    username = row.get('ACCOUNT LINK', '').strip()
                    password = row.get('PASSWORD', '').strip()
                    if not username or not password:
                        continue
                    # Remove URL prefix if present
                    username = pattern.sub('', username)
                    accounts.append([username, password])
            break
        except:
            pass

def main():
    with open('login_results.txt', 'w') as f:
        f.write("=== LOGIN SUCCESS ===\n")
        f.write("=== LOGIN ERRORS ===\n")

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

        for email, password in accounts:
            if email not in logged_accounts:
                logged_accounts.add(email)
                executor.submit(keep_alive, email, password)

        time.sleep(60)

if __name__ == "__main__":
    main()
