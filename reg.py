import hashlib
import json
from requests.utils import dict_from_cookiejar
from openpyxl import Workbook, load_workbook
import os
import requests
from bs4 import BeautifulSoup
import time
import random
from zipfile import BadZipFile

COOKIE_DIR = "/storage/emulated/0/cookie"

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
        'accept-encoding': 'gzip, deflate',
        'content-type': 'application/x-www-form-urlencoded',
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

    # Choice input
    while True:
        print("\n\033[94mChoose account identifier:\033[0m")
        print(" [1] Enter Email")
        print(" [2] Use Random Phone Number")
        choice = input("\033[92mYour choice (1 or 2): \033[0m").strip()
        clear_console()
        if choice == '1':
            email_or_phone = input("\033[92mEnter your email:\033[0m ").strip()
            if not email_or_phone:
                print("\033[91m❌ Email cannot be empty.\033[0m")
                continue
            is_phone_choice = False
            break
        elif choice == '2':
            email_or_phone = phone_number
            print(f"\033[92mUsing generated phone number:\033[0m {email_or_phone}")
            is_phone_choice = True
            break
        else:
            print("\033[91m❌ Invalid choice. Please enter 1 or 2.\033[0m")

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

    # Change email if generated with phone
    if is_phone_choice:
        print("\n\033[93m✅ Account created with phone number. Now let's change it to an email.\033[0m")
        while True:
            try:
                new_email = input("\033[92mPlease enter your new email:\033[0m ").strip()
                if not new_email:
                    print("\033[91m❌ Email cannot be empty.\033[0m")
                    continue

                change_email_url = "https://m.facebook.com/changeemail/"
                change_headers = {
                    "User-Agent": headers["User-Agent"],
                    "Accept": "*/*",
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Connection": "keep-alive"
                }

                response = session.get(change_email_url, headers=change_headers, timeout=10)
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

                response = session.post(action_url, headers=change_headers, data=data, timeout=10)
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
    uid = session.cookies.get("c_user")
    profile_id = f'https://www.facebook.com/profile.php?id={uid}'
    filename_xlsx = "/storage/emulated/0/Acc_Created.xlsx"
    filename_txt = "/storage/emulated/0/Acc_created.txt"

    while True:
        if has_access_token_in_xlsx(filename_xlsx, email_or_phone):
            print(f"✅ Account for {email_or_phone} already has access token. Skipping...")
            break

        choice = input("💾 Do you want to save this account? (y/n): ").strip().lower()
        if choice == "n":
            break
        elif choice == "y":
            max_attempts = 3
            attempt = 0
            access_token = ""

            while attempt < max_attempts:
                attempt += 1
                print(f"🔄 Attempt {attempt} to get access token...")
                api_key = "882a8490361da98702bf97a021ddc14d"
                secret = "62f8ce9f74b12f84c123cc23437a4a32"

                params = {
                    "api_key": api_key,
                    "email": uid,
                    "format": "JSON",
                    "generate_session_cookies": 1,
                    "locale": "en_US",
                    "method": "auth.login",
                    "password": used_password,
                    "return_ssl_resources": 1,
                    "v": "1.0"
                }

                sig_str = "".join(f"{key}={params[key]}" for key in sorted(params)) + secret
                params["sig"] = hashlib.md5(sig_str.encode()).hexdigest()

                try:
                    resp = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers, timeout=60)
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

                if access_token.strip():
                    print("✅ Access token acquired.")
                    data_to_save = [full_name, email_or_phone, password, profile_id, access_token]
                    save_to_xlsx(filename_xlsx, data_to_save)
                    save_to_txt(filename_txt, data_to_save)
                    print(f"✅ Account saved | {full_name}")
                    break
                else:
                    print("❌ No access token on this attempt.")

            else:
                print("❌ Failed to get access token after 3 attempts. Account not saved.")
            break

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
    while True:
        clear_console()
        NEMAIN()
