import csv
import os
import uuid
import requests
from bs4 import BeautifulSoup
import time
import sys
import random
import string

os.system("clear")

custom_password = None  # global variable to store password


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
    if account_type == 1:  # Philippines
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
    return random.choice(phone_formats)


def generate_random_password():
    base = 'Promises'
    symbols = '!@#$%^&*()_+-='
    six_digit = str(random.randint(100000, 999999))
    password = base + six_digit
    return password


def generate_user_details(account_type, gender, password=None):
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    if password is None:
        password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password


custom_password_base = None  # define this globally at top

def create_fbunconfirmed(account_type, usern, gender, password=None):
    global custom_password_base, profile_id, emailsss

    # If no password supplied, handle base password logic
    if password is None:
        if custom_password_base is None:
            inp = input("\033[1;92m😊 Type your password to continue: \033[0m")
            if inp.strip() == '':
                custom_password_base = None
            else:
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
                print('😢 Error No internet connection. Check your Mobile Data or on off Airplane mode.')
                time.sleep(3)
                os.system("clear")

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
                    print(f"Network error turn on off airplane mode")
                    return
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
            "encpass": f"{used_password}",
            "submit": "Sign Up"
        }

        for inp in inputs:
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

        while True:
            try:
                retry_request(action_url, headers, method="post", data=data)
                break
            except:
                pass

        try:
            if "c_user" in session.cookies:
                uid = session.cookies.get("c_user")
                profile_id = 'https://www.facebook.com/profile.php?id=' + uid
            else:
                print("\033[1;91m⚠️ Create Account Failed. Retrying...\033[0m")
                time.sleep(3)
                os.system("clear")
                return

            while True:
                try:
                    # Step 3: Change email
                    change_email_url = "https://m.facebook.com/changeemail/"
                    headerssss = {
                        "sec-ch-ua-platform": '"Android"',
                        "x-requested-with": "XMLHttpRequest",
                        "accept": "*/*",
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
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
                action_url = requests.compat.urljoin(change_email_url, form["action"]) if form.has_attr(
                    "action") else change_email_url
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
                        print('error email')
                        pass

        except Exception as e:
            print("An error occurred:", str(e))
            sys.exit()
        max_retries = 3
        for attempt in range(max_retries):
            try:
                email_response = retry_request(change_email_url, headerssss)
                soup = BeautifulSoup(email_response.text, "html.parser")

                registration_error = soup.find(id="registration-error")
                if registration_error:
                    print("\033[1;91m⚠️ Created account blocked. Try toggling airplane mode or clearing Facebook Lite data.\033[0m")
                    time.sleep(3)
                    os.system("clear")  # Clear terminal screen
                    return  # Retry by looping again (refresh)

                form = soup.find('form', action=lambda x: x and 'checkpoint' in x)
                if form:
                    print("\033[1;91m⚠️ Created account blocked. Try toggling airplane mode or clearing Facebook Lite data.\033[0m")
                    time.sleep(3)
                    os.system("clear")
                    return  # Stop or exit here if needed
                else:
                    break  # Success, no errors, exit loop

            except Exception as e:
                if attempt == max_retries - 1:
                    print("An error occurred after retries:", str(e))
                    sys.exit()

        os.system("clear")
        time.sleep(5)
        print(f"\033[1;92m          Account| Pass | {password} |\033[0m")

        while True:
            try:
                retry_request(action_url, headers, method="post", data=data)
                break
            except:
                print("\033[1;91m⚠️😢 Error: Invalid email. Please use another email.\033[0m")
                time.sleep(3)
                os.system("clear")
                return

    user_input = input(
        "\033[32mType b if the account is blocked, or press Enter if not blocked to continue:\033[0m ")
    if user_input == "b":
        print("\033[1;91m⚠️Creating another account because your account got blocked 😔\033[0m")
        time.sleep(3)
        os.system("clear")
        return
    filename = "/storage/emulated/0/Acc_Created.csv"
    full_name = f"{firstname} {lastname}"
    data_to_save = [full_name, phone_number, used_password, profile_id + '\t']

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

    while True:
        os.system("clear")
        try:
            save_to_csv(filename, data_to_save)
            print(
                f"\033[1;92m✅ Created Account has been saved 😊 {full_name} | {emailsss} | {used_password} |\033[0m")
            time.sleep(3)
            break
        except:
            pass


def NEMAIN():
    os.system("clear")
    max_retries = 5  # Set how many times you want to retry account creation
    attempt = 0
    account_type = 1
    gender = 1
    usern = "ali"

    while attempt < max_retries:
        try:
            create_fbunconfirmed(account_type, usern, gender)
            break  # Break if successful (i.e., didn't return due to failure)
        except Exception as e:
            print(f"\033[1;91m⚠️ Attempt {attempt + 1} failed. Retrying...\033[0m")
            attempt += 1
            time.sleep(2)
            os.system("clear")

    if attempt == max_retries:
        print("\033[1;91m❌ Maximum retries reached. Exiting...\033[0m")


if __name__ == "__main__":
    while True:
        NEMAIN()
