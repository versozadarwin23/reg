import json
import os
import atexit
import hashlib
from requests.utils import dict_from_cookiejar
from openpyxl import Workbook, load_workbook
import requests
from bs4 import BeautifulSoup
import time
import random
from zipfile import BadZipFile

COOKIE_DIR = "/storage/emulated/0/cookie"
CONFIG_FILE = "/storage/emulated/0/settings.json"

def random_device_model():
    models = [
        "Google-Pixel-7",
        "Google-Pixel-6a",
        "Google-Pixel-5"
    ]
    return random.choice(models)


def random_device_id():
    ids = [
        "15526637-0441-2553-4665-888888888048",
        "26637748-1552-3664-5776-999999999049",
        "37748859-2663-4775-6887-000000000050"
    ]
    return random.choice(ids)


def random_fingerprint():
    fingerprints = [
        "realme/RMX3761/RMX3761:14/UQ1A.240205.004/RMX3761_14_A.13:user/release-keys",
        "motorola/Moto-G73/Moto-G73:13/TP1A.220624.014/20240401:user/release-keys",
        "infinix/X6711/X6711:14/UQ1A.240205.004/X6711-GL-240104V101:user/release-keys"
    ]
    return random.choice(fingerprints)


ua = [
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Google Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; SM-G990U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]"
]

def delete_config_file():
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
        except Exception as e:
            print(f"⚠️ Failed to delete settings file: {e}")

atexit.register(delete_config_file)

def save_user_choice(key, value):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    data[key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_user_choice(key):
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get(key)
        except:
            return None

def clear_console():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except:
        pass

def save_to_txt(filename, data):
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write("|".join(data) + "\n")
    except Exception as e:
        print(f"\033[1;91m❗ Error saving to {filename}: {e}\033[0m")

def has_access_token_in_xlsx(filename, email_address):
    if not os.path.exists(filename):
        return False

    try:
        wb = load_workbook(filename)
    except BadZipFile:
        print(f"\033[91m⚠️ Corrupted XLSX detected at {filename}. Skipping access token check.\033[0m")
        return False

    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        saved_email = row[1]
        saved_access_token = row[4]
        if saved_email == email_address and saved_access_token and saved_access_token.strip():
            return True
    return False

def save_to_xlsx(filename, data):
    header_columns = ['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'ACCESS TOKEN']

    while True:
        try:
            if os.path.exists(filename):
                try:
                    wb = load_workbook(filename)
                    ws = wb.active
                except BadZipFile:
                    print(f"\033[91m⚠️ Corrupted XLSX detected at {filename}. Recreating file...\033[0m")
                    os.remove(filename)
                    wb = Workbook()
                    ws = wb.active
                    ws.append(header_columns)
            else:
                wb = Workbook()
                ws = wb.active
                ws.append(header_columns)

            # Ensure header is correct
            header = [cell.value for cell in ws[1]]
            if header != header_columns:
                ws.delete_rows(1)
                ws.insert_rows(1)
                ws.append(header_columns)

            # Check if row already exists
            existing_rows = [tuple(row) for row in ws.iter_rows(min_row=2, values_only=True)]
            if tuple(data) not in existing_rows:
                ws.append(data)

            wb.save(filename)
            break
        except Exception as e:
            print(f"❗ Error saving to {filename}: {e}. Retrying in 1 second...")
            time.sleep(1)

def load_names_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def get_names(account_type, gender):
    firstnames = load_names_from_file("first_name.txt")
    last_names = load_names_from_file("last_name.txt")
    firstname = random.choice(firstnames)
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
    firstname, lastname, date, year, month, phone_number, password = None, None, None, None, None, None, None
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
    agent = random.choice(ua)

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
        "Accept-Language": "en-US,en;q=0.9",
        "X-FB-Connection-Type": "mobile.LTE",
        "X-FB-Device": random_device_model(),
        "X-FB-Device-ID": random_device_id(),
        "X-FB-Fingerprint": random_fingerprint(),
        "X-FB-Connection-Quality": "EXCELLENT",
        "X-FB-Net-HNI": "51502",
        "X-FB-SIM-HNI": "51502",
        "X-FB-HTTP-Engine": "Liger",
        'x-fb-connection-type': 'Unknown',
        'accept-encoding': 'gzip, deflate',
        'content-type': 'application/x-www-form-urlencoded',
        'x-fb-http-engine': 'Liger',
        'User-Agent': agent,
    }

    if session is None:
        session = requests.Session()

    def get_registration_form():
        while True:
            try:
                response = session.get(url, headers=headers, timeout=60)
                soup = BeautifulSoup(response.text, "html.parser")
                form = soup.find("form")
                if form:
                    return form, response.text # Return response.text here
            except:
                print('\033[1;91m😢 Failed to connect to network on off airplane mode...\033[0m')
                time.sleep(3)

    form, initial_response_text = get_registration_form() # Get initial response text

    # Choice input with saved preference
    choice = load_user_choice("reg_choice")

    if choice is None:
        while True:
            print("\n\033[94mChoose an option that doesn’t get blocked:\033[0m")
            print(" [1] Enter Email")
            print(" [2] Use Random Phone Number")
            choice = input("\033[92mYour choice (1 or 2): \033[0m").strip()
            clear_console()
            if choice in ['1', '2']:
                save_user_choice("reg_choice", choice)
                break
            else:
                print("\033[91m❌ Invalid choice. Please enter 1 or 2.\033[0m")
    else:
        pass

    if choice == '1':
        while True:
            email_or_phone = input("\033[92mEnter your email:\033[0m ").strip()
            if email_or_phone:
                break
            print("\033[91m❌ Email cannot be empty.\033[0m")
        is_phone_choice = False
    else:  # choice == '2'
        email_or_phone = phone_number
        print(f"\033[92mUsing generated phone number:\033[0m {email_or_phone}")
        is_phone_choice = True

    data = {
        "firstname": firstname,
        "lastname": lastname,
        "birthday_day": str(date),
        "birthday_month": str(month),
        "birthday_year": str(year),
        "reg_email__": email_or_phone,
        "sex": str(gender),
        "encpass": password,
        "submit": "Sign Up"
    }

    if form:
        action_url = requests.compat.urljoin(url, form.get("action", url))
        for inp in form.find_all("input"):
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp.get("value", "")

        while True:
            try:
                response = session.post(action_url, headers=headers, data=data, timeout=60)
                break
            except:
                pass


    if "c_user" not in session.cookies:
        print(f"\033[1;91m⚠️ Create Account Failed No c_user cookie found. Try toggling airplane mode or use another email.\033[0m")
        time.sleep(3)
        return "FAILED_NO_C_USER"

    # Change email if generated with phone
    if is_phone_choice:
        print("\n\033[93m✅ Account created with phone number. Now let's change it to an email.\033[0m")
        while True:
            try:
                new_email = input("\033[92mPlease enter your new email:\033[0m ").strip()
                if not new_email:
                    print("\033[91m❌ Email cannot be empty.\033[0m")
                    continue

                if "c_user" not in session.cookies:
                    return

                change_email_url = "https://m.facebook.com/changeemail/"
                while True:
                    try:
                        response = session.get(change_email_url, headers=headers, timeout=60)
                        break
                    except:
                        pass
                soup = BeautifulSoup(response.text, "html.parser")
                form = soup.find("form")

                if not form:
                    print("\033[91m❌ Could not load email change form. Skipping.\033[0m")
                    break

                action_url = requests.compat.urljoin(change_email_url, form.get("action", change_email_url))
                data = {}
                for inp in form.find_all("input"):
                    if inp.has_attr("name"):
                        data[inp["name"]] = inp.get("value", "")

                data["new"] = new_email
                data["submit"] = "Add"

                while True:
                    try:
                        response = session.post(action_url, headers=headers, data=data, timeout=60)
                        break
                    except:
                        pass

                if "email" in response.text.lower():
                    print("\033[92m✅ Email change submitted successfully!\033[0m")
                else:
                    print("\033[91m⚠️ Email change may not have succeeded. Check your account manually.\033[0m")

                email_or_phone = new_email
                break
            except Exception as e:
                print(f"\033[91m❌ Error changing email: {e}\033[0m")
                time.sleep(2)
    full_name = f"{firstname} {lastname}"
    print(f"\033[92m✅ | Account | Pass | {password}\033[0m")
    print(f"\033[92m✅ | info | {full_name}\033[0m")

    uid = session.cookies.get("c_user")
    profile_id = f'https://www.facebook.com/profile.php?id={uid}'
    filename_xlsx = "/storage/emulated/0/Acc_Created.xlsx"
    filename_txt = "/storage/emulated/0/Acc_created.txt"

    while True:
        if has_access_token_in_xlsx(filename_xlsx, email_or_phone):
            break

        choice = input("💾 Do you want to save this account? (y/n): ").strip().lower()
        if choice == "":
            choice = "y"
            uid = session.cookies.get("c_user")
            profile_id = f'https://www.facebook.com/profile.php?id={uid}'

            cookie_dir = "/storage/emulated/0/cookie"
            os.makedirs(cookie_dir, exist_ok=True)
            cookie_file = os.path.join(cookie_dir, f"{uid}.json")
            cookie_names = ["c_user", "datr", "fr", "noscript", "sb", "xs"]
            cookies_data = {name: session.cookies.get(name, "") for name in cookie_names}
            try:
                with open(cookie_file, "w") as f:
                    json.dump(cookies_data, f, indent=4)
            except IOError as e:
                pass

        if choice == "n":
            break
        elif choice == "y":
            # proceed with save logic here

            while True:
                print(f"🔄 Trying to get access token...")
                api_key = "882a8490361da98702bf97a021ddc14d"
                secret = "62f8ce9f74b12f84c123cc23437a4a32"

                params = {
                    "api_key": api_key,
                    "email": uid,
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

                try:
                    resp = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers,
                                        timeout=60)
                    try:
                        data = resp.json()
                    except json.JSONDecodeError:
                        print("❌ Failed to parse Facebook API JSON response.")
                        continue
                    access_token = data.get("access_token", "")
                    if "error_title" in data:
                        print(data["error_title"])
                except Exception as error_title:
                    print(error_title)
                    access_token = ""

                if access_token.strip():
                    print("✅ Access token acquired.")
                    data_to_save = [full_name, email_or_phone, password, profile_id, access_token]
                    save_to_xlsx(filename_xlsx, data_to_save)
                    save_to_txt(filename_txt, data_to_save)
                    print(f"✅ Account saved | {full_name}")
                    cookie_dir = "/storage/emulated/0/cookie"
                    os.makedirs(cookie_dir, exist_ok=True)
                    cookie_file = os.path.join(cookie_dir, f"{uid}.json")
                    cookie_names = ["c_user", "datr", "fr", "noscript", "sb", "xs"]
                    cookies_data = {name: session.cookies.get(name, "") for name in cookie_names}
                    try:
                        with open(cookie_file, "w") as f:
                            json.dump(cookies_data, f, indent=4)
                    except IOError as e:
                        pass
                    break
                else:
                    print("❌ No access token on this attempt.")
                    airplane_mode = input("✈️ Plss ON OFF Airplane mode (y/n): ").strip().lower()
                    if airplane_mode == "y":
                        cookie_dir = "/storage/emulated/0/cookie"
                        os.makedirs(cookie_dir, exist_ok=True)
                        cookie_file = os.path.join(cookie_dir, f"{uid}.json")
                        cookie_names = ["c_user", "datr", "fr", "noscript", "sb", "xs"]
                        cookies_data = {name: session.cookies.get(name, "") for name in cookie_names}
                        try:
                            with open(cookie_file, "w") as f:
                                json.dump(cookies_data, f, indent=4)
                        except:
                            pass
                        print("⚠️ Please turn on airplane mode now, then off to continue.")
                        input()
                    else:
                        print("ℹ️ Skipping airplane mode toggle.")
    # Check for logout link after successful registration or email change
    if response and response.text:
        soup = BeautifulSoup(response.text, "html.parser")
        logout_link = soup.find("a", href=lambda href: href and "/logout.php" in href)
        if logout_link:
            logout_url = requests.compat.urljoin("https://m.facebook.com/", logout_link["href"])
            # print(f"\033[94mFound logout link: {logout_url}\033[0m")
            try:
                # print("Attempting to log out...")
                session.get(logout_url, headers=headers, timeout=30)
                print("\033[92m✅ Successfully logged out.\033[0m")
            except Exception as e:
                pass
                # print(f"\033[91m❌ Failed to log out: {e}\033[0m")


def NEMAIN():
    clear_console()
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
    clear_console()
    if os.path.exists("settings.json"):
        os.remove("settings.json")
    while True:
        clear_console()
        NEMAIN()
