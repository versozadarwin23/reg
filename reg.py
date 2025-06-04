import csv
import os
import uuid
import requests
from bs4 import BeautifulSoup
import time
import sys
import random

os.system("clear")

def load_user_agents(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        user_agents = [line.strip() for line in file if line.strip()]
    return user_agents

def get_random_user_agent(file_path):
    user_agents = load_user_agents(file_path)
    return random.choice(user_agents)

# Example usage:

MAX_RETRIES = 3
RETRY_DELAY = 2
# ANSI color codes

# Emojis and Symbols
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
        # Load male and last names from file (ensure correct file paths)
        male_first_names = load_names_from_file("first_name.txt")
        last_names = load_names_from_file("last_name.txt")
        female_first_names = []  # Female names not used for this account type
    else:  # Other account type
        male_first_names = []  # Not used
        female_first_names = load_names_from_file('path_to_female_first_names.txt')
        last_names = load_names_from_file('path_to_last_names.txt')

    # Select first name based on gender
    firstname = random.choice(male_first_names if gender == 1 else female_first_names)
    lastname = random.choice(last_names)

    return firstname, lastname


def generate_random_phone_number():
    """Generate a random phone number."""
    random_number = str(random.randint(1000000, 9999999))
    third = random.randint(0, 4)
    forth = random.randint(1, 7)
    phone_formats = [
        f"9{third}{forth}{random_number}",
        f"9{third}{forth}{random_number}",
    ]
    number = random.choice(phone_formats)

    return number


import random
import string

def generate_random_password():
    base = 'Promises'  # fixed part
    symbols = '!@#$%^&*()_+-='
    remaining_length = 3 - len(base)

    # Ensure at least one symbol is included (only if base is short enough, which it's not)
    if remaining_length > 0:
        mixed_chars = string.digits + symbols
        extra = ''.join(random.choices(mixed_chars, k=remaining_length - 1))
        extra += random.choice(symbols)  # ensure at least one symbol
        extra = ''.join(random.sample(extra, len(extra)))  # shuffle extra chars
    else:
        extra = ''

    six_digit = str(random.randint(100000, 999999))  # random 6-digit number
    password = base + extra + six_digit
    return password



def generate_user_details(account_type, gender):
    """Generate random user details."""
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password


def create_fbunconfirmed(account_type, usern, gender):
    """Create a Facebook account using kuku.lu for email and OTP."""

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

    url = "https://m.facebook.com/reg"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        # "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://m.facebook.com/reg",
        "Connection": "keep-alive",
        "X-FB-Connection-Type": "MOBILE.LTE",
        "X-FB-Connection-Quality": "EXCELLENT",
        "X-FB-Net-HNI": "51502",  # Smart PH
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
            print('seasion error')
            pass

    # # Save entire page as HTML
    # with open('confirmation_page.html', 'w', encoding='utf-8') as f:
    #     f.write(soup.prettify())
    # print("Saved HTML successfully.")
    # Polling loop
    while True:
        form = check_page_loaded(url, headers)
        if form:
            break  # Exit loop if form is found
        else:
            print("Waiting for form to load...")

    # Retry request function
    def retry_request(url, headers, method="get", data=None):
        global response
        while True:
            try:
                if method == "get":
                    response = session.get(url, headers=headers)
                elif method == "post":
                    response = session.post(url, headers=headers, data=data)
                # Check for successful response
                if response.status_code == 200:
                    return response
                else:
                    print(f"Network error turn of and on airplane mode")
            except requests.exceptions.ConnectionError:
                sys.exit()  # exit if not logged in

    while True:
        try:
            response = retry_request(url, headers)
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")
            # # Save entire page as HTML
            # with open('confirmation_page.html', 'w', encoding='utf-8') as f:
            #     f.write(soup.prettify())
            # print("Saved HTML successfully.")
            break
        except:
            pass

    if form:
        action_url = requests.compat.urljoin(url, form["action"]) if form.has_attr("action") else url
        inputs = form.find_all("input")
        email_or_phone = input("\033[92mEnter your email:\033[0m ")
        data = {
            "firstname": f"{firstname}",
            "lastname": f"{lastname}",
            "birthday_day": f"{date}",
            "birthday_month": f"{month}",
            "birthday_year": f"{year}",
            "reg_email__": email_or_phone,
            "sex": f"{gender}",
            "encpass": f"{password}",
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
                return  # exit the function so NEMAIN() can call again
        except Exception as e:
            print("An error occurred:", str(e))
            sys.exit()

        def save_to_csv(filename, data):
            while True:
                try:
                    file_exists = os.path.isfile(filename)
                    with open(filename, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        # If the file is new or empty, write headers first
                        if not file_exists or os.path.getsize(filename) == 0:
                            writer.writerow(['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK'])
                        writer.writerow(data)
                    break  # success!
                except Exception as e:
                    print(f"Error saving to {filename}: {e}. Retrying...")

        # Start of the block
        if "c_user" in session.cookies:
            # 🟢 New: Check a URL using the active session
            check_url = "https://m.facebook.com/changeemail/"  # Example: check settings page
            try:
                resp = session.get(check_url, headers=headers)
                if resp.status_code == 200:
                    # Do something with resp.text if you want to scrape
                    pass
                else:
                    # Handle failed status code if needed
                    pass
            except Exception as e:
                # Handle exceptions if needed
                pass

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    form = soup.find('form', action=lambda x: x and 'checkpoint' in x)
                    if form:
                        print("\033[1;91m⚠️ Created account blocked try on off airplane mode % clear data facebook lite\033[0m")
                        time.sleep(3)
                        os.system("clear")
                        return
                    else:
                        if attempt == max_retries - 1:
                            form = None
                except Exception:
                    if attempt == max_retries - 1:
                        form = None

            os.system("clear")
            print(f"\033[1;92m Account Email {email_or_phone} |{password}| \033[0m")
            # Process the result

        user_input = input("Type b if the account is blocked, or press Enter if not blocked to continue:")
        if user_input == "b":
            print("\033[1;91m⚠️Creating another account because your account got blocked 😔\033[0m")
            time.sleep(3)
            os.system("clear")
            return

        # Otherwise, proceed
        filename = "/storage/emulated/0/Acc_Created.csv"
        full_name = f"{firstname} {lastname}"
        data_to_save = [full_name, email_or_phone, password, profile_id+'\t']
        print(f"\033[1;92m✅ Account created successfully! 😊 {full_name} |  Pass | {password} |\033[0m")
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
        usern = "ali"  # Replace with actual username logic
        result = create_fbunconfirmed(account_type, usern, gender)

        if result:
            oks.append(result)
        else:
            cps.append(result)

# Instead of directly calling NEMAIN(), wrap it in a loop
if __name__ == "__main__":
    while True:
        NEMAIN()
