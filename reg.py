import hashlib
import json
from requests.utils import dict_from_cookiejar
from openpyxl import Workbook, load_workbook
import os
import requests
from bs4 import BeautifulSoup
import time
import random

def print_logo():
    print(r"""
\033[1;96m
  ██████  █████  ██      ██      ███    ███     ███    ███ ███████      █████  ███████ 
 ██      ██   ██ ██      ██      ████  ████     ████  ████ ██          ██   ██ ██      
 ██      ███████ ██      ██      ██ ████ ██     ██ ████ ██ █████       ███████ ███████ 
 ██      ██   ██ ██      ██      ██  ██  ██     ██  ██  ██ ██          ██   ██       ██ 
  ██████ ██   ██ ███████ ███████ ██      ██     ██      ██ ███████     ██   ██ ███████ 

       ██████   █████  ██████  ███████ 
      ██       ██   ██ ██   ██ ██      
      ██   ███ ███████ ██████  █████   
      ██    ██ ██   ██ ██   ██ ██      
       ██████  ██   ██ ██   ██ ███████ 

\033[0m
""")


COOKIE_DIR = "cookie"

def save_to_xlsx(filename, data):
    header_columns = ['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'ACCESS TOKEN']
    while True:
        try:
            if os.path.exists(filename):
                wb = load_workbook(filename)
                ws = wb.active
                if ws.max_row == 0:
                    ws.append(header_columns)
                else:
                    header = [cell.value for cell in ws[1]]
                    if header != header_columns:
                        ws.insert_rows(1)
                        ws.append(header_columns)
            else:
                wb = Workbook()
                ws = wb.active
                ws.append(header_columns)

            ws.append(data)
            wb.save(filename)
            break
        except Exception as e:
            print(f"Error saving to {filename}: {e}. Retrying...")
            time.sleep(1)


def load_names_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def get_names(account_type, gender):
    if account_type == 1:
        male_first_names = load_names_from_file("first_name.txt")
        last_names = load_names_from_file("last_name.txt")
        female_first_names = []
    else:
        male_first_names = []
        female_first_names = load_names_from_file('path_to_female_first_names.txt')
        last_names = load_names_from_file('path_to_last_names.txt')

    firstname = random.choice(male_first_names if gender == 1 else female_first_names)
    lastname = random.choice(last_names)
    return firstname, lastname

def generate_random_phone_number():
    random_number = str(random.randint(1000000, 9999999))
    third = random.randint(0, 4)
    forth = random.randint(1, 7)
    return f"9{third}{forth}{random_number}"

def generate_random_password():
    return 'Promises' + str(random.randint(100000, 999999))

def generate_user_details(account_type, gender, password=None):
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    if password is None:
        password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password


custom_password_base = None

def ensure_cookie_dir():
    if not os.path.exists(COOKIE_DIR):
        os.makedirs(COOKIE_DIR)

def save_cookie_json(cookie_dict):
    ensure_cookie_dir()
    c_user = cookie_dict.get("c_user")
    if not c_user:
        print("❌ ERROR: No 'c_user' in cookie_dict. Cannot save.")
        return
    file_path = os.path.join(COOKIE_DIR, f"{c_user}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cookie_dict, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save cookie: {e}")

def save_session_cookie(session):
    cookie_dict = dict_from_cookiejar(session.cookies)
    save_cookie_json(cookie_dict)

def create_fbunconfirmed(account_type, usern, gender, password=None, session=None):
    global custom_password_base

    if password is None:
        if custom_password_base:
            password = custom_password_base + str(random.randint(100000, 999999))
        else:
            password = generate_random_password()

    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(account_type, gender, password)

    url = "https://m.facebook.com/reg"
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

    if session is None:
        session = requests.Session()

    def get_registration_form():
        while True:
            try:
                response = session.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                form = soup.find("form")
                if form:
                    return form
            except:
                print('😢 No internet. Retrying...')
                time.sleep(3)

    form = get_registration_form()

    os.system("clear")
    email_or_phone = input("\033[92mEnter your email:\033[0m ").strip()

    data = {
        "firstname": firstname,
        "lastname": lastname,
        "birthday_day": str(date),
        "birthday_month": str(month),
        "birthday_year": str(year),
        "reg_email__": email_or_phone,
        "sex": str(gender),
        "encpass": used_password,
        "submit": "Sign Up"
    }

    if form:
        action_url = requests.compat.urljoin(url, form.get("action", url))
        for inp in form.find_all("input"):
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp.get("value", "")

        try:
            response = session.post(action_url, headers=headers, data=data, timeout=15)
        except:
            print("❌ Failed to submit form.")
            return

    if "c_user" not in session.cookies:
        print("\033[1;91m⚠️ Create Account Failed. Try again later.\033[0m")
        return

    print(f"\n\033[92m✅ Email: {email_or_phone} | Pass: {password}\033[0m")

    while True:
        try:
            user_input = input("Type 'b' if blocked, or press Enter to continue: ")
            if user_input.lower() == 'b':
                print("\033[1;91m⚠️ Creating another account because the last one was blocked.\033[0m")
                time.sleep(3)
                os.system("clear")
                return
            break
        except:
            pass

    save_session_cookie(session)
    uid = session.cookies.get("c_user")
    profile_id = f'https://www.facebook.com/profile.php?id={uid}'

    api_key = "882a8490361da98702bf97a021ddc14d"
    secret = "62f8ce9f74b12f84c123cc23437a4a32"

    params = {
        "api_key": api_key,
        "email": email_or_phone,
        "format": "JSON",
        "generate_session_cookies": 1,
        "locale": "en_US",
        "method": "auth.login",
        "password": password,
        "return_ssl_resources": 1,
        "v": "1.0"
    }

    sig_str = "".join(f"{key}={params[key]}" for key in sorted(params)) + secret
    params["sig"] = hashlib.md5(sig_str.encode()).hexdigest()

    access_token = ""
    try:
        resp = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers, timeout=60)
        data = resp.json()
        access_token = data.get("access_token", "")
        if "error_msg" in data:
            print("⚠️ FB API error:", data["error_msg"])
    except Exception as e:
        print("⚠️ Error getting access_token:", e)

    full_name = f"{firstname} {lastname}"
    print(f"\n\033[92m✅ Created Account: {full_name} | Pass: {password}\033[0m")

    filename = "Acc_Created.xlsx"
    data_to_save = [full_name, email_or_phone, password, profile_id, access_token]
    save_to_xlsx(filename, data_to_save)
    print("\n\033[92m✅ Account info saved.\033[0m\n")
    time.sleep(2)
    os.system("clear")

def NEMAIN():
    os.system("clear")
    max_create = 1
    account_type = 1
    gender = 1
    session = requests.Session()

    global custom_password_base
    if custom_password_base is None:
        inp = input("\033[1;92m😊 Type your password: \033[0m").strip()
        custom_password_base = inp if inp else "Promises"

    for _ in range(max_create):
        usern = "ali"
        create_fbunconfirmed(account_type, usern, gender, session=session)


if __name__ == "__main__":
    print_logo()
    time.sleep(3)
    while True:
        try:
            NEMAIN()
        except:
            pass
