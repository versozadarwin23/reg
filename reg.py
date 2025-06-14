import csv
import os
import uuid
import requests
from bs4 import BeautifulSoup
import time
import sys
import random
import string
import psutil
import subprocess

os.system("clear")

def load_user_agents(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        user_agents = [line.strip() for line in file if line.strip()]
    return user_agents

def get_random_user_agent(file_path):
    user_agents = load_user_agents(file_path)
    return random.choice(user_agents)

MAX_RETRIES = 3
RETRY_DELAY = 2

SUCCESS = "✅"
FAILURE = "✅"
INFO = "✅"
WARNING = "⚠️"
LOADING = "⏳"

def load_names_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

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
    number = f"9{third}{forth}{random_number}"
    return number

def generate_random_password():
    base = 'Promises'
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

def create_fbunconfirmed(account_type, usern, gender, password=None, session=None):
    global custom_password_base, profile_id

    if password is None:
        if custom_password_base is None:
            inp = input("\033[1;92m😊 Type your password to continue: \033[0m")
            if inp.strip():
                custom_password_base = inp.strip()
        if custom_password_base is None:
            password = generate_random_password()
        else:
            six_digit = str(random.randint(100000, 999999))
            password = custom_password_base + six_digit

    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(account_type, gender, password)

    def check_page_loaded(url, headers):
        while True:
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find("form")
                os.system("clear")
                return form
            except:
                print('😢 No internet. Check data or toggle airplane mode.')
                time.sleep(3)

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

    while True:
        form = check_page_loaded(url, headers)
        if form:
            break

    def retry_request(url, headers, method="get", data=None):
        global response
        while True:
            try:
                if method == "get":
                    response = session.get(url, headers=headers)
                elif method == "post":
                    response = session.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    return response
            except requests.exceptions.ConnectionError:
                sys.exit()

    while True:
        try:
            response = retry_request(url, headers)
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")
            break
        except:
            pass

    if form:
        action_url = requests.compat.urljoin(url, form["action"]) if form.has_attr("action") else url
        inputs = form.find_all("input")
        email_or_phone = input("\033[92mEnter your email:\033[0m ")
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

        for inp in inputs:
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

        retry_request(action_url, headers, method="post", data=data)

        if "c_user" not in session.cookies:
            print("\033[1;91m⚠️ Create Account Failed. Try toggling airplane mode or use another email.\033[0m")
            time.sleep(3)
            return

        uid = session.cookies.get("c_user")
        profile_id = f'https://www.facebook.com/profile.php?id={uid}'

        form = soup.find('form', action=lambda x: x and 'checkpoint' in x)
        if form:
            print("\033[1;91m⚠️ Created account blocked. Try toggling airplane mode or clearing Facebook Lite data.\033[0m")
            time.sleep(3)
            os.system("clear")
            return

        os.system("clear")
        print(f"\033[1;92m✅ Account      | Pass: {password}\033[0m")

        user_input = input("Type 'b' if blocked, or press Enter to continue: ")
        if user_input.lower() == 'b':
            print("\033[1;91m⚠️ Creating another account because the last one was blocked.\033[0m")
            time.sleep(3)
            os.system("clear")
            return

        def save_to_csv(filename, data):
            while True:
                try:
                    file_exists = os.path.isfile(filename)
                    with open(filename, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if not file_exists or os.path.getsize(filename) == 0:
                            writer.writerow(['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK'])
                        writer.writerow(data)
                    break
                except Exception as e:
                    print(f"Error saving to {filename}: {e}. Retrying...")

        filename = "/storage/emulated/0/Acc_Created.csv"
        full_name = f"{firstname} {lastname}"
        data_to_save = [full_name, email_or_phone, password, profile_id + '\t']
        save_to_csv(filename, data_to_save)
        print(f"\033[1;92m✅ Account has been saved: {firstname} {lastname} | Pass: {password}\033[0m")
        time.sleep(3)

def NEMAIN(session):
    os.system("clear")
    max_create = 1
    account_type = 1
    gender = 1

    for i in range(max_create):
        usern = "ali"
        create_fbunconfirmed(account_type, usern, gender, session=session)

# ✅ Check if another script is already running
def is_script_running(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and script_name in ' '.join(cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

if __name__ == "__main__":
    session = requests.Session()
    last_session_time = time.time()

    while True:
        current_time = time.time()
        if current_time - last_session_time > 3:
            session.close()
            session = requests.Session()
            last_session_time = current_time

        NEMAIN(session)

        # ✅ Run script2.py only if it's not already running
        if not is_script_running("fblogin.py"):
            subprocess.Popen(["python3", "fblogin.py"])  # or "python" if on Windows
        else:
            print("✅ script2.py is already running.")
