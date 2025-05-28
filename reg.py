import csv
import os
import uuid
import requests
from bs4 import BeautifulSoup
import time
import sys
import random
import string
import subprocess
import psutil

os.system("clear")

print("\033[1;91m")
print("""
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
<<                                    >>
<<          Auto Reg By Darwin        >>
<<                                    >>
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
""")
print("\033[0m")

time.sleep(2)

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
    phone_formats = [
        f"9{third}{forth}{random_number}",
        f"9{third}{forth}{random_number}",
    ]
    number = random.choice(phone_formats)
    return number

def generate_random_password():
    base = 'Promises'
    symbols = '!@#$%^&*()_+-='
    remaining_length = 3 - len(base)
    if remaining_length > 0:
        mixed_chars = string.digits + symbols
        extra = ''.join(random.choices(mixed_chars, k=remaining_length - 1))
        extra += random.choice(symbols)
        extra = ''.join(random.sample(extra, len(extra)))
    else:
        extra = ''
    six_digit = str(random.randint(100000, 999999))
    password = base + extra + six_digit
    return password

def generate_user_details(account_type, gender):
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password

def create_fbunconfirmed(account_type, usern, gender):
    global uid, profie_link, profile_link, token, profile_id, data_to_save, filename, save_to_csv
    asdf = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    firstname, lastname, date, year, month, phone_number, password = generate_user_details(account_type, gender)

    def check_page_loaded(url, headers):
        while True:
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find("form")
                os.system("clear")
                return form
            except:
                print('😢 error No internet connection. Check your Mobile Data or toggle Airplane mode.')
                time.sleep(3)

    url = "https://limited.facebook.com/reg"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://limited.facebook.com/reg",
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

    while True:
        try:
            session = requests.Session()
            break
        except:
            print('session error')
            pass

    while True:
        form = check_page_loaded(url, headers)
        if form:
            break
        else:
            print("Waiting for form to load...")

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
                else:
                    print(f"Network error turn off and on airplane mode")
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
        data = {
            "firstname": f"{firstname}",
            "lastname": f"{lastname}",
            "birthday_day": f"{date}",
            "birthday_month": f"{month}",
            "birthday_year": f"{year}",
            "reg_email__": f"{phone_number}",
            "sex": f"{gender}",
            "encpass": f"{password}",
            "submit": "Sign Up"
        }

        for inp in inputs:
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

        submit_response = retry_request(action_url, headers, method="post", data=data)
        try:
            if "c_user" in session.cookies:
                uid = session.cookies.get("c_user")
                profile_id = 'https://www.facebook.com/profile.php?id=' + uid
            else:
                print("\033[1;91m⚠️ Create Account Failed. Retrying...\033[0m")
                return
        except Exception as e:
            print("An error occurred:", str(e))
            sys.exit()

    while True:
        try:
            change_email_url = "https://m.facebook.com/changeemail/"
            headerssss = {
                "sec-ch-ua-platform": '"Android"',
                "x-requested-with": "XMLHttpRequest",
                "accept": "*/*",
                'User-Agent': headers['User-Agent'],
                "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                "sec-ch-ua-mobile": "?1",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-encoding": "gzip, deflate,",
                "accept-language": "en-US,en;q=0.9",
                "priority": "u=1, i"
            }
            email_response = retry_request(change_email_url, headerssss)
            soup = BeautifulSoup(email_response.text, "html.parser")
            form = soup.find("form")
            break
        except:
            pass

    if form:
        action_url = requests.compat.urljoin(change_email_url, form["action"]) if form.has_attr("action") else change_email_url
        inputs = form.find_all("input")
        data = {}
        for inp in inputs:
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""
        while True:
            try:
                emailsss = input("Please enter your email: ")
                data["new"] = emailsss
                data["submit"] = "Add"
                break
            except:
                pass

        retry_request(action_url, headers, method="post", data=data)

        def save_to_csv(filename, data):
            while True:
                try:
                    with open(filename, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(data)
                    break
                except Exception as e:
                    print(f"Error saving to {filename}: {e}. Retrying...")

        if "c_user" in session.cookies:
            os.system("clear")
            print(f"\033[1;92m Account Email  | {emailsss}  | Pass  |  {password}  |\033[0m")
        user_input = input("Type b if the account is blocked, or press Enter if not blocked to continue:")
        if user_input == "b":
            print("\033[1;91m⚠️Creating another account because your account got blocked 😔\033[0m")
            time.sleep(3)
            os.system("clear")
            return

        filename = "/storage/emulated/0/Acc_Created.csv"
        full_name = f"{firstname} {lastname}"
        data_to_save = [full_name, phone_number, password, profile_id]
        print(f"\033[1;92m✅ Account created successfully! 😊 {full_name} |  {phone_number} | {password} |\033[0m")
        time.sleep(3)
        os.system("clear")
        while True:
            try:
                save_to_csv(filename, data_to_save)
                print('\033[1;92m✅ Created Account has been saved 😊')
                time.sleep(3)
                break
            except:
                pass

def NEMAIN():
    os.system("clear")
    max_create = 1
    account_type = 1
    gender = 1
    oks = []
    cps = []
    for i in range(max_create):
        usern = "ali"
        result = create_fbunconfirmed(account_type, usern, gender)
        if result:
            oks.append(result)
        else:
            cps.append(result)

# --------------- ADDITIONS: fblogin.py management ---------------

def is_process_running(script_name):
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and script_name in ' '.join(cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def start_fblogin():
    if not is_process_running('fblogin.py'):
        subprocess.Popen(['python', 'fblogin.py'])

# --------------- Main execution loop ---------------
if __name__ == "__main__":
    start_fblogin()  # Ensure fblogin.py runs only once
    while True:
        NEMAIN()
