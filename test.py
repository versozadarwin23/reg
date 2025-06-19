import csv
import os
import subprocess
import uuid
import requests
from bs4 import BeautifulSoup
import time
import sys
import random
import string

os.system("clear")

# Refresh session function
def refresh_session(session, url="https://m.facebook.com/home.php", headers=None, retries=3):
    print(f"\n🔄 Refreshing session {retries} times...\n")
    for i in range(retries):
        try:
            response = session.get(url, headers=headers)
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Refresh {i + 1} failed: {e}")


custom_password_base = None
profile_id = None
user_provided_contact_info = None
initial_contact_choice_global = None

MAX_RETRIES = 3  # This is primarily for network requests
RETRY_DELAY = 2

SUCCESS = "✅"
FAILURE = "❌"
WARNING = "⚠️"
LOADING = "⏳"

def load_user_agents(file_path):
    """Loads user agents from a specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            user_agents = [line.strip() for line in file if line.strip()]
        return user_agents
    except FileNotFoundError:
        print(f"{FAILURE} Error: User agent file '{file_path}' not found. Please create it.")
        sys.exit()

def load_names_from_file(file_path):
    """Loads names from a specified file."""
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"{FAILURE} Error: Name file '{file_path}' not found. Please ensure it exists.")
        sys.exit()


def get_names(account_type, gender):
    """Retrieves random first and last names based on account type and gender."""
    male_first_names = load_names_from_file("first_name.txt")
    last_names = load_names_from_file("last_name.txt")

    female_first_names = load_names_from_file("first_name.txt")

    firstname = random.choice(male_first_names if gender == 1 else female_first_names)
    lastname = random.choice(last_names)
    return firstname, lastname


def generate_random_phone_number():
    """Generates a random Philippine-like phone number."""
    random_number = str(random.randint(1000000, 9999999))
    third = random.randint(0, 4)
    forth = random.randint(1, 7)
    phone_formats = [
        f"9{third}{forth}{random_number}",
    ]
    return random.choice(phone_formats)


def generate_random_password():
    """Generates a random password following a specific pattern."""
    base = 'Promises'
    six_digit = str(random.randint(100000, 999999))
    password = base + six_digit
    return password


def generate_user_details_initial(account_type, gender, password_override=None):
    """
    Generates initial user details (names, birthday, and password).
    Contact info is handled separately in create_fbunconfirmed.
    """
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)

    if password_override:
        # If a custom password base is provided, append a random 6-digit number
        six_digit = str(random.randint(100000, 999999))
        password = password_override + six_digit
    else:
        password = generate_random_password()
    return firstname, lastname, date, year, month, password


def create_fbunconfirmed(account_type, usern, gender):
    global custom_password_base, profile_id, user_provided_contact_info, initial_contact_choice_global
    session = requests.Session()
    def check_page_loaded(url, headers):
        for _ in range(MAX_RETRIES):
            try:
                response = session.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find("form")
                os.system("clear")
                return form
            except requests.exceptions.ConnectionError:
                print(f'{FAILURE} Error: No internet connection. Check your Mobile Data or toggle Airplane mode.')
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"{FAILURE} An error occurred while checking page: {e}")
                time.sleep(RETRY_DELAY)
        print(f"{FAILURE} Failed to load page after multiple retries.")
        return None

    def retry_request(url, headers, method="get", data=None):
        for attempt in range(MAX_RETRIES):
            try:
                if method == "get":
                    response = session.get(url, headers=headers)
                elif method == "post":
                    response = session.post(url, headers=headers, data=data)

                if response.status_code == 200:
                    return response
                else:
                    print(
                        f"{WARNING} Network error (Status code: {response.status_code}). Retrying... (Attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
            except requests.exceptions.ConnectionError:
                print(
                    f"{FAILURE} Connection error. Check your internet and try again. (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(
                    f"{FAILURE} An unexpected error occurred during request: {e}. Retrying... (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
        print(f"{FAILURE} Failed to get a successful response after multiple retries.")
        return None

    if custom_password_base is None:
        inp = input(f"\033[1;92m Type your password: \033[0m")
        if inp.strip() != '':
            custom_password_base = inp.strip()

    if initial_contact_choice_global is None:
        while initial_contact_choice_global not in ['1', '2']:
            os.system("clear")
            print("Choose account input type: Choose 1 if option 2 is getting blocked, or Choose 2 if option 1 is getting blocked.\033[0m")
            print("1. Phone Number\033[0m")
            print("2. Email Address\033[0m")
            initial_contact_choice_global = input(f" Enter your choice (1 or 2): \033[0m")
            if initial_contact_choice_global not in ['1', '2']:
                print(f"{WARNING} Invalid choice. Please enter 1 or 2.")
                time.sleep(1)

    if initial_contact_choice_global == '1':
        user_provided_contact_info = generate_random_phone_number()
    elif initial_contact_choice_global == '2':
        while True:
            email_input = input(f" Type your Email:  \033[0m").strip()
            if '@' in email_input and '.' in email_input:
                user_provided_contact_info = email_input
                break
            else:
                print(f"{WARNING} Invalid email format. Please enter a valid email address.")

    initial_contact_was_phone = (initial_contact_choice_global == '1')

    while True:
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
            "User-Agent": 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
        }

        form = check_page_loaded(url, headers)
        if not form:
            print(f"{FAILURE} Initial registration form not found. Cannot proceed with this account creation attempt.")
            continue  # Retry from the top

        internal_creation_attempts = 0
        max_internal_attempts = 5

        while internal_creation_attempts < max_internal_attempts:
            internal_creation_attempts += 1
            print(
                f"\033[92m\nPlease wait, I'm trying to skip the checkpoint block ({internal_creation_attempts}/{max_internal_attempts})\033[0m")

            firstname, lastname, date, year, month, used_password = generate_user_details_initial(account_type, gender,
                                                                                                  custom_password_base)

            action_url = requests.compat.urljoin(url, form["action"]) if form.has_attr("action") else url
            inputs = form.find_all("input")

            data = {
                "firstname": firstname,
                "lastname": lastname,
                "birthday_day": str(date),
                "birthday_month": str(month),
                "birthday_year": str(year),
                "sex": str(gender),
                "encpass": used_password,
                "submit": "Sign Up",
                "reg_email__": user_provided_contact_info,
            }

            for inp in inputs:
                if inp.has_attr("name") and inp["name"] not in data:
                    data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

            reg_response = retry_request(action_url, headers, method="post", data=data)
            if not reg_response:
                print(f"{WARNING} Registration post failed. Trying next internal attempt.")
                time.sleep(RETRY_DELAY * 2)
                continue

            try:
                if "c_user" in session.cookies:
                    uid = session.cookies.get("c_user")
                    profile_id = f'https://www.facebook.com/profile.php?id={uid}'
                    print(f"{SUCCESS} Account created successfully: {profile_id}")
                    break  # Exit internal loop
                else:
                    soup_after_reg = BeautifulSoup(reg_response.text, "html.parser")
                    registration_error = soup_after_reg.find(id="registration-error")
                    checkpoint_form = soup_after_reg.find('form', action=lambda x: x and 'checkpoint' in x)

                    if registration_error:
                        error_text = registration_error.get_text(strip=True)
                        print(f"{FAILURE} Registration error: {error_text}")
                    elif checkpoint_form:
                        print(f"{WARNING} Account hit a checkpoint immediately. Trying next internal attempt...")
                    else:
                        print(f"{WARNING} Create Account Failed: No c_user cookie found and no clear error message. Trying next internal attempt...")

                    # 🔄 Refresh session before retry
                    refresh_session(session, headers=headers, retries=3)

                    time.sleep(RETRY_DELAY * 2)
                    os.system("clear")

            except Exception as e:
                print(
                    f"{FAILURE} An unexpected error occurred during account verification: {e}. Trying next internal attempt.")
                time.sleep(RETRY_DELAY * 2)
                os.system("clear")

        # Exit outer while loop if successful
        if "c_user" in session.cookies:
            break

    if not profile_id:
        print(
            f"{FAILURE} All {max_internal_attempts} internal attempts failed")
        return False

    os.system("clear")

    # --- NEW: Offer to change to email ONLY IF initial contact was a phone number ---
    if initial_contact_was_phone:  # Check the stored value
        try:
            # Step 3: Change email
            change_email_url = "https://m.facebook.com/changeemail/"
            headers_email_change = {
                "sec-ch-ua-platform": '"Android"',
                "x-requested-with": "XMLHttpRequest",
                "accept": "*/*",
                "User-Agent": 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
                "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                "sec-ch-ua-mobile": "?1",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-encoding": "gzip, deflate,",
                "accept-language": "en-US,en;q=0.9",
                "priority": "u=1, i"
            }

            email_response = retry_request(change_email_url, headers_email_change)
            if not email_response:
                print(f"{WARNING} Failed to load email change page. Skipping email change.")
            else:
                soup_email_form = BeautifulSoup(email_response.text, "html.parser")
                form_email_change = soup_email_form.find("form")

                if form_email_change:
                    action_url_email_change = requests.compat.urljoin(
                        change_email_url,
                        form_email_change["action"] if form_email_change.has_attr("action") else change_email_url
                    )
                    inputs_email_change = form_email_change.find_all("input")
                    data_email_change = {}

                    for inp in inputs_email_change:
                        if inp.has_attr("name") and inp["name"] not in data_email_change:
                            data_email_change[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

                    while True:
                        new_email_input = input(f" Type your Email:  \033[0m").strip()
                        if '@' in new_email_input and '.' in new_email_input:
                            data_email_change["new"] = new_email_input
                            data_email_change["submit"] = "Add"
                            break
                        else:
                            print(f"{WARNING} Invalid email format. Please enter a valid email address.")

                    email_change_post_response = retry_request(
                        action_url_email_change,
                        headers_email_change,
                        method="post",
                        data=data_email_change
                    )

                    if email_change_post_response and "c_user" in session.cookies:
                        user_provided_contact_info = new_email_input
                    else:
                        print(
                            "\033[1;91m⚠️😢 Error: Failed to change email. It might be invalid or an issue occurred.\033[0m")
                else:
                    print(f"{WARNING} Could not find the email change form. Skipping email change.")
        except Exception as e:
            print(f"{FAILURE} An unexpected error occurred during the email change process: {e}")

    os.system("clear")
    print(f"          Password: {used_password}")
    user_input_blocked = input(
        f"\033[32m Type 'b' if the account is blocked, or press Enter if not blocked to continue:\033[0m ").lower()
    if user_input_blocked == "b":
        print(f"{WARNING} Account marked as blocked. Creating another account.")
        time.sleep(3)
        os.system("clear")
        return False

    filename = "/storage/emulated/0/Acc_Created.csv"
    full_name = f"{firstname} {lastname}"

    data_to_save = [full_name, user_provided_contact_info, used_password, profile_id]

    def save_to_csv(filename, data):
        """Saves account details to a CSV file."""
        for _ in range(MAX_RETRIES):
            try:
                file_exists = os.path.isfile(filename)
                with open(filename, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if not file_exists or os.path.getsize(filename) == 0:
                        writer.writerow(['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'STATUS'])
                    writer.writerow(data)
                break
            except Exception as e:
                print(f"{FAILURE} Error saving to {filename}: {e}. Retrying... (Attempt {_ + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
        else:
            print(f"{FAILURE} Failed to save account details after multiple retries. Please check file permissions.")

    save_to_csv(filename, data_to_save)
    print(
        f"\033[1;92m{SUCCESS} Created Account has been saved 😊 {full_name} | {user_provided_contact_info} | {used_password} |\033[0m")
    time.sleep(3)

    # user_provided_contact_info is NOT reset here because initial_contact_choice_global handles persistence
    return True


def NEMAIN():
    """Main function to control the overall account creation flow."""
    os.system("clear")
    max_overall_attempts = 5
    overall_attempt = 0

    # Declare global variables here that will be modified in this function
    global profile_id, custom_password_base, user_provided_contact_info, initial_contact_choice_global

    # The custom_password_base and initial_contact_choice_global are NOT reset here,
    # so they persist across multiple account creation attempts within the same run of NEMAIN.

    while overall_attempt < max_overall_attempts:
        overall_attempt += 1
        # profile_id is reset for each new account creation attempt
        profile_id = None
        # user_provided_contact_info is set within create_fbunconfirmed based on initial_contact_choice_global
        # For 'email' choice, it will prompt for a new email each time if you want unique emails per account.
        # For 'phone' choice, it will generate a new random phone number each time.

        account_type = 1
        gender = 1
        usern = "ali"

        if create_fbunconfirmed(account_type, usern, gender):
            break  # Stop if an account is successfully created
        else:
            print(
                f"{WARNING} Account creation failed on overall attempt {overall_attempt}. Preparing for next overall attempt...")
            time.sleep(2)  # Give a small pause before clearing
            os.system("clear")

    if overall_attempt == max_overall_attempts and not profile_id:
        print(f"{FAILURE} Maximum overall creation attempts reached ({max_overall_attempts}). Exiting this run.")


if __name__ == "__main__":
    while True:
        NEMAIN()
