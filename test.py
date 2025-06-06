import csv
import os
import uuid
import requests
from bs4 import BeautifulSoup
import time
import sys
import random
import string
from concurrent.futures import ThreadPoolExecutor
import threading

os.system("clear")

# GLOBALS
SUCCESS = "✅"
FAILURE = "❌"
INFO = "ℹ️"
WARNING = "⚠️"
LOADING = "⏳"
custom_password_base = None
lock = threading.Lock()

def load_user_agents(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        user_agents = [line.strip() for line in file if line.strip()]
    return user_agents

def get_random_user_agent(file_path):
    user_agents = load_user_agents(file_path)
    return random.choice(user_agents)

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
    return f"9{third}{forth}{random_number}"

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

def create_fbunconfirmed(account_type, usern, gender, password=None, email=None):
    global custom_password_base
    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(account_type, gender, password)

    url = "https://m.facebook.com/reg"
    headers = {
        "User-Agent": 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
        "Referer": "https://m.facebook.com/reg",
        "X-FB-Connection-Type": "MOBILE.LTE",
        "X-FB-Connection-Quality": "EXCELLENT",
        "X-FB-Net-HNI": "51502",
        "X-FB-SIM-HNI": "51502",
        "X-FB-HTTP-Engine": "Liger",
        'accept-encoding': 'gzip, deflate',
        'content-type': 'application/x-www-form-urlencoded',
    }

    session = requests.Session()

    try:
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        form = soup.find("form")
        if not form:
            with lock:
                print(f"{FAILURE} Failed to load registration form.")
            return

        action_url = requests.compat.urljoin(url, form["action"]) if form.has_attr("action") else url
        inputs = form.find_all("input")

        email_or_phone = email
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

        post_response = session.post(action_url, headers=headers, data=data)
        if "c_user" in session.cookies:
            uid = session.cookies.get("c_user")
            profile_id = f"https://www.facebook.com/profile.php?id={uid}"
            filename = "/storage/emulated/0/Acc_Created.csv"
            full_name = f"{firstname} {lastname}"
            data_to_save = [full_name, email_or_phone, used_password, profile_id + '\t']

            with lock:
                save_to_csv(filename, data_to_save)
                print(f"{SUCCESS} Created: {full_name} | {email_or_phone} | Pass: {used_password}")
        else:
            with lock:
                print(f"{FAILURE} ❌ Failed or checkpointed. Email: {email_or_phone}")

    except Exception as e:
        with lock:
            print(f"{FAILURE} Exception: {str(e)}")

def threaded_worker(index, account_type, gender, email):
    time.sleep(3 * (index + 1))  # Delay start: worker 1 waits 3 sec, worker 2 waits 6 sec ...
    usern = f"user{index + 1}"   # username count starts at 1
    with lock:
        print(f"{INFO} Starting worker {index + 1} with email {email}...")
    create_fbunconfirmed(account_type, usern, gender, email=email)

def main_with_threads():
    os.system("clear")
    try:
        max_create = int(input("🔢 Enter number of accounts to create: "))
        max_workers = int(input("🧵 Enter max workers (threads): "))
    except ValueError:
        print(f"{FAILURE} Invalid input.")
        return

    emails = []
    for i in range(max_create):
        email = input(f"📧 Enter email for account #{i + 1}: ")
        emails.append(email.strip())

    account_type = 1
    gender = 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(max_create):
            futures.append(executor.submit(threaded_worker, i, account_type, gender, emails[i]))

        for future in futures:
            future.result()

if __name__ == "__main__":
    main_with_threads()
