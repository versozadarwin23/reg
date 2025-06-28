import string
from openpyxl import Workbook, load_workbook
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import concurrent.futures
import threading
xlsx_lock = threading.Lock()
console_lock = threading.Lock()
os.system("clear")

ua = [
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; P30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; Moto G Power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 9S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; OnePlus 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; LG G8 ThinQ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; Xperia 5 II) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Pixel 4a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Samsung SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; ASUS_Z01QD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; Vivo V2027) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Oppo A74) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Xiaomi 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; Nokia 7.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; Realme 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Infinix Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Tecno Camon 18) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; ZTE Axon 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; SM-A715F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Google Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; Huawei Mate 20 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; LG V60 ThinQ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Samsung Galaxy A32) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Sony Xperia 1 III) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; Google Pixel 3a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; OnePlus 8T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Redmi K40 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Xiaomi 11 Lite 5G NE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; Moto G7 Power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Samsung SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; P40 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; OnePlus Nord 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; LG Wing) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; Xperia 1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; Asus ROG Phone 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Vivo X70 Pro+) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Oppo Reno6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; Nokia X20) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; Realme 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Infinix Zero X Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; Tecno Pova 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 9; ZTE Blade V2020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/299.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 10; SM-A908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Google Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; SM-G990U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]"
]
def generate_email():
    """Gumawa ng random username para sa harakirimail at bumalik ang email address at url."""
    rchjtrchjb = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    email_address = f"{rchjtrchjb}@harakirimail.com"
    drtyghbj5hgcbv = f"https://harakirimail.com/inbox/{rchjtrchjb}"
    return email_address, drtyghbj5hgcbv

def save_to_txt(filename, data):
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write("|".join(data) + "\n")
    except Exception as e:
        print(f"\033[1;91m❗ Error saving to {filename}: {e}\033[0m")

def save_to_xlsx(filename, data):
    while True:
        with xlsx_lock:
            try:
                if os.path.exists(filename):
                    wb = load_workbook(filename)
                    ws = wb.active
                else:
                    wb = Workbook()
                    ws = wb.active
                    ws.append(["NAME", "USERNAME", "PASSWORD", "ACCOUNT LINK"])
                ws.append(data)
                wb.save(filename)
                break
            except Exception as e:
                print(f"\033[1;91m❗ Error saving to {filename}: {e}. Retrying...\033[0m")
                time.sleep(RETRY_DELAY)

MAX_RETRIES = 3
RETRY_DELAY = 2
SUCCESS = "✅"
FAILURE = "❌"
INFO = "ℹ️"
WARNING = "⚠️"
LOADING = "⏳"

def load_names_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"\033[1;91m❗ Error: Name file not found at {file_path}. Please create it.\033[0m")
        return ["John", "Jane", "Doe", "Smith"]

def get_names(account_type, gender):
    male_first_names_file = "first_name.txt"
    last_names_file = "last_name.txt"

    male_first_names = load_names_from_file(male_first_names_file)
    last_names = load_names_from_file(last_names_file)

    if not male_first_names:
        male_first_names = ["Juan", "Pedro"]
    if not last_names:
        last_names = ["Dela Cruz", "Reyes"]

    firstname = random.choice(male_first_names)
    lastname = random.choice(last_names)
    return firstname, lastname

def generate_random_phone_number():
    random_number = str(random.randint(1000000, 9999999))
    third = random.randint(0, 4)
    forth = random.randint(1, 7)
    return f"9{third}{forth}{random_number}"

def generate_random_password():
    base = "Promises"
    six_digit = str(random.randint(100000, 999999))
    return base + six_digit

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

def create_fbunconfirmed(account_num, account_type, gender, password=None, session=None):
    agent = random.choice(ua)
    global custom_password_base
    os.system("clear")
    email_address, drtyghbj5hgcbv = generate_email()
    if password is None:
        if custom_password_base:
            six_digit = str(random.randint(100000, 999999))
            password = custom_password_base + six_digit
        else:
            password = generate_random_password()

    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(account_type, gender, password)

    def check_page_loaded(url, headers, current_session):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = current_session.get(url, timeout=30, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find("form")
                if form:
                    return form
                else:
                    print(f"{WARNING} Form not found on {url}, retrying... (Account #{account_num})")
            except requests.exceptions.RequestException as e:
                print(f"{FAILURE} No internet or connection issue: {e}. Retrying in {RETRY_DELAY} seconds... (Account #{account_num})")
            except Exception as e:
                print(f"{FAILURE} An unexpected error occurred: {e}. Retrying in {RETRY_DELAY} seconds... (Account #{account_num})")

            time.sleep(RETRY_DELAY)
            retries += 1
        print(f"{FAILURE} Failed to load page and find form after {MAX_RETRIES} retries. (Account #{account_num})")
        return None

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
        'User-Agent': agent,
    }
    if session is None:
        session = requests.Session()

    form = check_page_loaded(url, headers, session)
    if not form:
        print(f"\033[1;91m{FAILURE} Could not load registration page or find form. Aborting attempt for account #{account_num}.\033[0m")
        return "FAILED_PAGE_LOAD"

    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")
            if form:
                break
        except requests.exceptions.RequestException as e:
            print(f"\033[1;91m{FAILURE} Error fetching form: {e}. Retrying... (Account #{account_num})\033[0m")
        except Exception as e:
            print(f"\033[1;91m{FAILURE} An unexpected error occurred while fetching form: {e}. Retrying... (Account #{account_num})\033[0m")
        time.sleep(RETRY_DELAY)
        retries += 1

    if not form:
        print(f"\033[1;91m{FAILURE} Failed to get registration form after retries. Aborting attempt for account #{account_num}.\033[0m")
        return "FAILED_FORM_FETCH"

    action_url = requests.compat.urljoin(url, form["action"]) if form.has_attr("action") else url
    inputs = form.find_all("input")
    data = {
        "firstname": firstname,
        "lastname": lastname,
        "birthday_day": str(date),
        "birthday_month": str(month),
        "birthday_year": str(year),
        "reg_email__": email_address,
        "sex": str(gender),
        "encpass": used_password,
        "submit": "Sign Up"
    }

    for inp in inputs:
        if inp.has_attr("name") and inp["name"] not in data:
            data[inp["name"]] = inp.get("value", "")

    try:
        response = session.post(action_url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"\033[1;91m{FAILURE} Network error during submission: {e}. Cannot complete account creation for account #{account_num}.\033[0m")
        return "FAILED_SUBMISSION_NETWORK"
    except Exception as e:
        print(f"\033[1;91m{FAILURE} An unexpected error occurred during submission: {e}. Cannot complete account creation for account #{account_num}.\033[0m")
        return "FAILED_SUBMISSION_UNEXPECTED"

    with open(f"status.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    if "c_user" not in session.cookies:
        print(f"\033[1;91m⚠️ Create Account Failed for account #{account_num}. No c_user cookie found. Try toggling airplane mode or use another email.\033[0m")
        time.sleep(3)
        return "FAILED_NO_C_USER"

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
        print(f"\033[1;91m{FAILURE} Error saving cookies for account #{account_num}: {e}\033[0m")

    soup = BeautifulSoup(response.text, "html.parser")
    form_checkpoint = soup.find('form', action=lambda x: x and 'checkpoint' in x)
    if form_checkpoint:
        print(f"\033[1;91m⚠️ Created account #{account_num} blocked. Try toggling airplane mode or clearing Facebook Lite data.\033[0m")
        time.sleep(3)
        return "BLOCKED"

    jbkj = None
    retries = 0
    while retries < MAX_RETRIES * 5:
        try:
            dtryvghjuijhn = requests.get(drtyghbj5hgcbv, timeout=30)
            dtryvghjuijhn.raise_for_status()
            soup_mail = BeautifulSoup(dtryvghjuijhn.text, "html.parser")
            table = soup_mail.find("table", class_="table table-hover table-striped")
            if table:
                subject_link = table.find("tbody", id="mail_list_body").find("a")
                if subject_link:
                    subject_div = subject_link.find("div")
                    if subject_div:
                        subject = subject_div.get_text(strip=True)
                        if "is your confirmation code" in subject:
                            jbkj = subject.replace(" is your confirmation code", "")
                            if jbkj:
                                break
        except requests.exceptions.RequestException as e:
            print(f"\033[1;91m{FAILURE} Error fetching email for account #{account_num}: {e}. Retrying...\033[0m")
        except Exception as e:
            print(f"\033[1;91m{FAILURE} An unexpected error occurred while processing email for account #{account_num}: {e}. Retrying...\033[0m")

        time.sleep(5)
        retries += 1

    if not jbkj:
        print(f"\033[1;91m{FAILURE} Failed to get confirmation code for account #{account_num} after multiple attempts. Account might be unconfirmed.\033[0m")

    print('\n')

    full_name = f"{firstname} {lastname}"
    data_to_save = [full_name, email_address, password, profile_id]

    with console_lock:
        print("\n\033[1;96m======================================\033[0m")
        print(f"\033[1;92m✅     Email: | {email_address} |\033[0m")
        print(f"\033[1;92m✅     Pass:  | {password} |\033[0m")
        print(f"\033[1;92m✅     Code:  | {jbkj if jbkj else 'N/A (Code not found)'}\033[0m")
        print("\033[1;96m======================================\033[0m\n")

        while True:
            choice = input("💾 Do you want to save this account? (y/n): ").strip().lower()
            if choice in ["y", "n"]:
                break
            print("❗ Please enter y or n.")

        if choice == "y":
            filename_xlsx = "/storage/emulated/0/Acc_Created.xlsx"
            filename_txt = "/storage/emulated/0/Acc_created.txt"
            save_to_xlsx(filename_xlsx, data_to_save)
            save_to_txt(filename_txt, data_to_save)
        else:
            print("\033[1;93m⚠️  Account not saved.\033[0m")

    return "SUCCESS"


def NEMAIN():
    os.system("clear")
    print("\033[1;36m======================================\033[0m")
    print("\033[1;36m  Facebook By: Dars Account Creator\033[0m")
    print("\033[1;36m        (Parallel Edition)            \033[0m")
    print("\033[1;36m======================================\033[0m\n")

    global custom_password_base
    if custom_password_base is None:
        inp = 'Promises@'
        custom_password_base = inp if inp else "Promises@"

    while True:
        try:
            max_create_input = input("Enter the maximum number of accounts to create: ").strip()
            max_create = int(max_create_input)
            if max_create <= 0:
                print("\033[1;91m❗ Please enter a positive number.\033[0m")
            else:
                break
        except ValueError:
            print("\033[1;91m❗ Invalid input. Please enter a number.\033[0m")

    account_type = 1
    gender = 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(max_create):
            time.sleep(3)
            future = executor.submit(create_fbunconfirmed, i + 1, account_type, gender, None, requests.Session())
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result == "SUCCESS":
                    pass
                else:
                    print(f"\033[1;91m{WARNING} An account creation task finished with status: {result}.\033[0m")
            except Exception as exc:
                print(f"\033[1;91m{FAILURE} An account generation task generated an exception: {exc}\033[0m")

    print("\n\033[1;92m======================================\033[0m")
    print("\033[1;92m        Account Creation Finished!      \033[0m")
    print("\033[1;92m======================================\033[0m")

if __name__ == "__main__":
    NEMAIN()
