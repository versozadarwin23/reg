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

# --- Global Variables ---
# Stores the base for custom passwords if provided by the user
custom_password_base = None
# Stores the Facebook profile ID after successful creation
profile_id = None
# Stores either the generated phone number or the user's email
user_provided_contact_info = None

# --- Constants for Retry Logic and UI Elements ---
MAX_RETRIES = 3  # This is primarily for network requests
RETRY_DELAY = 2

SUCCESS = "✅"
FAILURE = "❌"
INFO = "ℹ️"
WARNING = "⚠️"
LOADING = "⏳"

# --- Helper Functions ---


def load_user_agents(file_path):
    """Loads user agents from a specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            user_agents = [line.strip() for line in file if line.strip()]
        return user_agents
    except FileNotFoundError:
        print(f"{FAILURE} Error: User agent file '{file_path}' not found. Please create it.")
        sys.exit()


def get_random_user_agent(file_path="user_agents.txt"):
    """Returns a random user agent from the loaded list."""
    user_agents = load_user_agents(file_path)
    if not user_agents:
        print(f"{FAILURE} No user agents found in '{file_path}'. Using a default one.")
        return 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]'
    return random.choice(user_agents)


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

    password = password_override if password_override else generate_random_password()
    return firstname, lastname, date, year, month, password


# --- Core Account Creation Logic ---

def create_fbunconfirmed(account_type, usern, gender):
    """
    Attempts to create a Facebook account, handling user input for password
    and contact method (phone/email). Includes internal retries for the same contact info.
    Returns True on success, False on failure after all attempts.
    """
    global custom_password_base, profile_id, user_provided_contact_info

    session = requests.Session()

    def check_page_loaded(url, headers):
        """Attempts to load a page and find the registration form."""
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
        """Retries HTTP requests in case of failure."""
        for attempt in range(MAX_RETRIES):
            try:
                if method == "get":
                    response = session.get(url, headers=headers)
                elif method == "post":
                    response = session.post(url, headers=headers, data=data)

                if response.status_code == 200:
                    return response
                else:
                    print(f"{WARNING} Network error (Status code: {response.status_code}). Retrying... (Attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
            except requests.exceptions.ConnectionError:
                print(f"{FAILURE} Connection error. Check your internet and try again. (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"{FAILURE} An unexpected error occurred during request: {e}. Retrying... (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
        print(f"{FAILURE} Failed to get a successful response after multiple retries.")
        return None

    if custom_password_base is None:
        inp = input(f"\033[1;92m{INFO} Type your custom password (leave blank for random): \033[0m")
        if inp.strip() != '':
            custom_password_base = inp.strip()

    # --- Initial Contact Info Input Logic ---
    if user_provided_contact_info is None:
        initial_contact_choice = None
        while initial_contact_choice not in ['1', '2']:
            os.system("clear")
            print("Choose account input type:")
            print("1. Phone Number (Randomly Generated)")
            print("2. Email Address (You will input it manually)")
            initial_contact_choice = input(f"{INFO} Enter your choice (1 or 2): \033[0m")
            if initial_contact_choice not in ['1', '2']:
                print(f"{WARNING} Invalid choice. Please enter 1 or 2.")
                time.sleep(1)

        if initial_contact_choice == '1':
            user_provided_contact_info = generate_random_phone_number()
        elif initial_contact_choice == '2':
            while True:
                email_input = input(f"{INFO} Please enter the email address you want to use: \033[0m").strip()
                if '@' in email_input and '.' in email_input:
                    user_provided_contact_info = email_input
                    break
                else:
                    print(f"{WARNING} Invalid email format. Please enter a valid email address.")

    # --- Start Account Creation Process ---
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
        return False

    internal_creation_attempts = 0
    max_internal_attempts = 3

    while internal_creation_attempts < max_internal_attempts:
        internal_creation_attempts += 1
        print(f"\n{INFO} Attempting account creation ({internal_creation_attempts}/{max_internal_attempts}) "
              f"with contact info: {user_provided_contact_info}...")

        firstname, lastname, date, year, month, used_password = \
            generate_user_details_initial(account_type, gender, custom_password_base)

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
                # Account successfully created with initial contact info, break internal loop
                break
            else:
                soup_after_reg = BeautifulSoup(reg_response.text, "html.parser")
                registration_error = soup_after_reg.find(id="registration-error")
                checkpoint_form = soup_after_reg.find('form', action=lambda x: x and 'checkpoint' in x)

                if registration_error:
                    error_text = registration_error.get_text(strip=True)
                    print(f"{WARNING} Registration error detected: {error_text}. Trying next internal attempt...")
                elif checkpoint_form:
                    print(f"{WARNING} Account hit a checkpoint immediately. Trying next internal attempt...")
                else:
                    print(f"{WARNING} Create Account Failed: No c_user cookie found and no clear error message. Trying next internal attempt...")

                time.sleep(RETRY_DELAY * 2)
                os.system("clear")

        except Exception as e:
            print(f"{FAILURE} An unexpected error occurred during account verification: {e}. Trying next internal attempt.")
            time.sleep(RETRY_DELAY * 2)
            os.system("clear")

    if not profile_id:
        print(f"{FAILURE} All {max_internal_attempts} internal attempts failed with contact info: {user_provided_contact_info}.")
        return False

    os.system("clear")
    print(f"         Password: {used_password}")

    # --- NEW: Offer to change to email ONLY IF initial contact was a phone number ---
    if initial_contact_choice == '1': # If user initially chose phone number
        try:
            # Step 3: Change email
            change_email_url = "https://m.facebook.com/changeemail/"
            # Use headers defined in the main scope of create_fbunconfirmed
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
                    action_url_email_change = requests.compat.urljoin(change_email_url, form_email_change["action"]) if form_email_change.has_attr("action") else change_email_url
                    inputs_email_change = form_email_change.find_all("input")
                    data_email_change = {}
                    for inp in inputs_email_change:
                        if inp.has_attr("name") and inp["name"] not in data_email_change:
                            data_email_change[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

                    while True:
                        new_email_input = input(f"{INFO} Please enter the NEW email address for this account: \033[0m").strip()
                        if '@' in new_email_input and '.' in new_email_input:
                            data_email_change["new"] = new_email_input
                            data_email_change["submit"] = "Add" # Assuming 'Add' is the submit button name
                            break
                        else:
                            print(f"{WARNING} Invalid email format. Please enter a valid email address.")

                    email_change_post_response = retry_request(action_url_email_change, headers_email_change, method="post", data=data_email_change)
                    if email_change_post_response and "c_user" in session.cookies: # Check if still logged in after post
                        user_provided_contact_info = new_email_input # Update global variable
                        print(f"\033[1;92m{SUCCESS} Email successfully changed to: {user_provided_contact_info}\033[0m")
                    else:
                        print(f"\033[1;91m⚠️😢 Error: Failed to change email. It might be invalid or an issue occurred.\033[0m")
                        # Do not return False here, account is already created, just email change failed.
                else:
                    print(f"{WARNING} Could not find the email change form. Skipping email change.")
        except Exception as e:
            print(f"{FAILURE} An unexpected error occurred during the email change process: {e}")
            # Do not return False here, account is already created, just email change failed.

    user_input_blocked = input(
        f"\033[32m{INFO} Type 'b' if the account is blocked, or press Enter if not blocked to continue:\033[0m ").lower()
    if user_input_blocked == "b":
        print(f"{WARNING} Account marked as blocked. Creating another account.")
        time.sleep(3)
        os.system("clear")
        return False

    filename = "/storage/emulated/0/Acc_Created.csv"
    full_name = f"{firstname} {lastname}"

    data_to_save = [full_name, user_provided_contact_info, used_password, profile_id + '\t', "Live"]

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
    print(f"\033[1;92m{SUCCESS} Created Account has been saved 😊 {full_name} | {user_provided_contact_info} | {used_password} |\033[0m")
    time.sleep(3)
    return True


def NEMAIN():
    """Main function to control the overall account creation flow."""
    os.system("clear")
    max_overall_attempts = 5
    overall_attempt = 0
    account_type = 1
    gender = 1
    usern = "ali"

    global profile_id, user_provided_contact_info, custom_password_base
    profile_id = None
    user_provided_contact_info = None
    custom_password_base = None

    while overall_attempt < max_overall_attempts:
        overall_attempt += 1
        print(f"\n{INFO} Starting overall account creation attempt {overall_attempt}/{max_overall_attempts}...")

        if create_fbunconfirmed(account_type, usern, gender):
            print(f"{SUCCESS} Account creation successful on overall attempt {overall_attempt}!")
            break
        else:
            print(f"{WARNING} Account creation failed on overall attempt {overall_attempt}. Preparing for next overall attempt...")
            os.system("clear")

    if overall_attempt == max_overall_attempts and not profile_id:
        print(f"{FAILURE} Maximum overall creation attempts reached ({max_overall_attempts}). Exiting this run.")


if __name__ == "__main__":
    while True:
        NEMAIN()
