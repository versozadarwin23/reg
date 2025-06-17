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

os.system("clear")  # Clear only once at start

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
        female_first_names = [] # Ensure this is an empty list if not used
    else:
        male_first_names = [] # Ensure this is an empty list if not used
        female_first_names = load_names_from_file('path_to_female_first_names.txt')
        last_names = load_names_from_file('path_to_last_names.txt')

    # Ensure there are names to choose from
    if gender == 1 and male_first_names:
        firstname = random.choice(male_first_names)
    elif gender != 1 and female_first_names:
        firstname = random.choice(female_first_names)
    else:
        # Handle cases where name lists might be empty for the given gender/type
        firstname = "John" if gender == 1 else "Jane" # Default names
        with lock:
            print(f"{WARNING} No names found for specified gender/account type. Using default.")

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

def generate_user_details(account_type, gender, password=None, current_firstname=None, current_lastname=None):
    if current_firstname and current_lastname:
        firstname = current_firstname
        lastname = current_lastname
    else:
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

def create_fbunconfirmed(account_type, usern, gender, email, retries_left=5, current_password=None, current_firstname=None, current_lastname=None):
    global custom_password_base
    if retries_left == 0:
        with lock:
            print(f"{FAILURE} {email} failed after maximum retries. Skipping.")
        return

    # Generate user details. If this is a retry, keep the same name but generate a new password
    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(
        account_type, gender,
        password=current_password if current_password else generate_random_password(),
        current_firstname=current_firstname,
        current_lastname=current_lastname
    )

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
                print(f"{FAILURE} Failed to load registration form for {email}. Retrying ({retries_left-1} left).")
            # If form not found, it might be a temporary issue or block, retry
            time.sleep(5) # Wait a bit before retrying
            return create_fbunconfirmed(account_type, usern, gender, email, retries_left - 1, generate_random_password(), firstname, lastname)


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

        refresh_url = "https://m.facebook.com/reg"
        refreshed_response = session.get(refresh_url, headers=headers)
        refreshed_soup = BeautifulSoup(refreshed_response.text, "html.parser")

        # Check if checkpointed or blocked
        checkpoint_form = refreshed_soup.find('form', action=lambda x: x and 'checkpoint' in x)
        if checkpoint_form or "checkpoint" in post_response.url.lower():
            with lock:
                print(f"{WARNING} {email_or_phone} hit a checkpoint. Retrying with new password ({retries_left-1} left).")
            time.sleep(2) # Add a delay before retrying
            return create_fbunconfirmed(account_type, usern, gender, email, retries_left - 1, generate_random_password(), firstname, lastname)

        if "c_user" in session.cookies:
            uid = session.cookies.get("c_user")
            profile_id = f"https://www.facebook.com/profile.php?id={uid}"
            full_name = f"{firstname} {lastname}"
            filename = "/storage/emulated/0/Acc_Created.csv"
            data_to_save = [full_name, email_or_phone, used_password, profile_id + '\t']
            save_to_csv(filename, data_to_save)

            with lock:
                msg = f"{SUCCESS} Created: {full_name} | {email_or_phone} | Pass: {used_password}"
                print(msg)
                with open("fb_created_log.txt", "a") as log_file:
                    log_file.write(msg + "\n")
        else:
            with lock:
                print(f"{FAILURE} {email_or_phone} creation failed. Account might be blocked. Retrying ({retries_left-1} left).")
            time.sleep(5) # Wait before retrying
            return create_fbunconfirmed(account_type, usern, gender, email, retries_left - 1, generate_random_password(), firstname, lastname)
    except requests.exceptions.RequestException as e:
        with lock:
            print(f"{FAILURE} Network error during creation for {email}: {e}. Retrying ({retries_left-1} left).")
        time.sleep(5) # Wait before retrying
        return create_fbunconfirmed(account_type, usern, gender, email, retries_left - 1, generate_random_password(), firstname, lastname)
    except Exception as e:
        with lock:
            print(f"{FAILURE} Unexpected error during creation for {email}: {e}. Retrying ({retries_left-1} left).")
        time.sleep(5) # Wait before retrying
        return create_fbunconfirmed(account_type, usern, gender, email, retries_left - 1, generate_random_password(), firstname, lastname)

def threaded_worker(index, account_type, gender, email):
    time.sleep(3 * index)  # delay start
    usern = f"user{index + 1}"
    # The initial call to create_fbunconfirmed starts the retry process with default retries_left
    create_fbunconfirmed(account_type, usern, gender, email)

def main_with_threads():
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

    account_type = 1 # Assuming a fixed account type for simplicity
    gender = 1       # Assuming a fixed gender for simplicity

    # Placeholder for actual file paths. Make sure these files exist.
    # For example, create dummy first_name.txt, last_name.txt, and path_to_female_first_names.txt
    # with some names in them.
    # Example:
    # first_name.txt:
    # John
    # Michael
    # David

    # last_name.txt:
    # Smith
    # Johnson
    # Williams

    # path_to_female_first_names.txt:
    # Mary
    # Susan
    # Linda

    # You might want to pass these paths to get_names or make them global if used broadly.

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(max_create):
            futures.append(executor.submit(threaded_worker, i, account_type, gender, emails[i]))

        for future in futures:
            future.result()

if __name__ == "__main__":
    # Create dummy name files for testing if they don't exist
    if not os.path.exists("first_name.txt"):
        with open("first_name.txt", "w") as f:
            f.write("John\nMichael\nDavid\n")
    if not os.path.exists("last_name.txt"):
        with open("last_name.txt", "w") as f:
            f.write("Smith\nJohnson\nWilliams\n")
    if not os.path.exists("path_to_female_first_names.txt"):
        with open("path_to_female_first_names.txt", "w") as f:
            f.write("Mary\nSusan\nLinda\n")

    main_with_threads()
