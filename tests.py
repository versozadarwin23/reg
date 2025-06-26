import string
from openpyxl import Workbook, load_workbook
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import json

# Clear the console initially for a clean start
os.system("clear")


def generate_email():
    """Gumawa ng random username para sa harakirimail at bumalik ang email address at url."""
    rchjtrchjb = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    email_address = f"{rchjtrchjb}@harakirimail.com"
    drtyghbj5hgcbv = f"https://harakirimail.com/inbox/{rchjtrchjb}"
    return email_address, drtyghbj5hgcbv


def save_to_xlsx(filename, data):
    """I-save ang data sa Excel file."""
    while True:
        try:
            if os.path.exists(filename):
                wb = load_workbook(filename)
                ws = wb.active
            else:
                wb = Workbook()
                ws = wb.active
                # Add headers if it's a new file
                ws.append(["NAME", "USERNAME", "PASSWORD", "ACCOUNT LINK"])
            ws.append(data)
            wb.save(filename)
            break
        except Exception as e:
            print(f"\033[1;91m❗ Error saving to {filename}: {e}. Retrying...\033[0m")
            time.sleep(RETRY_DELAY)  # Wait before retrying

MAX_RETRIES = 3
RETRY_DELAY = 2
SUCCESS = "✅"
FAILURE = "❌"  # Changed to X as per common practice
INFO = "ℹ️"  # Changed to i as per common practice
WARNING = "⚠️"
LOADING = "⏳"


def load_names_from_file(file_path):
    """I-load ang mga pangalan mula sa file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"\033[1;91m❗ Error: Name file not found at {file_path}. Please create it.\033[0m")
        # Provide more generic default names as a fallback if files are completely missing
        return ["John", "Jane", "Doe", "Smith"]


def get_names(account_type, gender):
    """Kumuha ng random firstname at lastname mula sa files.
    account_type is currently not fully utilized, selection is based on gender.
    """
    male_first_names_file = "first_name.txt"
    last_names_file = "last_name.txt"

    male_first_names = load_names_from_file(male_first_names_file)
    last_names = load_names_from_file(last_names_file)

    # Ensure there are names to choose from, even if files are empty
    if not male_first_names:
        male_first_names = ["Juan", "Pedro"]
    if not last_names:
        last_names = ["Dela Cruz", "Reyes"]

    # Fix: Complete the conditional expression for firstname
    # This line was previously missing the 'else' part and had an extra closing parenthesis.
    firstname = random.choice(male_first_names)
    lastname = random.choice(last_names)
    return firstname, lastname


def generate_random_phone_number():
    """Gumawa ng random phone number."""
    random_number = str(random.randint(1000000, 9999999))
    third = random.randint(0, 4)
    forth = random.randint(1, 7)
    return f"9{third}{forth}{random_number}"


def generate_random_password():
    """Gumawa ng random password."""
    base = "Promises"
    six_digit = str(random.randint(100000, 999999))
    return base + six_digit


def generate_user_details(account_type, gender, password=None):
    """Kumuha ng user details kasama ang pangalan, kaarawan, password at phone number."""
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    if password is None:
        password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password


custom_password_base = None  # Global variable to store custom password base


def create_fbunconfirmed(account_type, gender, password=None, session=None):
    """Gumawa ng Facebook unconfirmed account."""
    global custom_password_base, profile_id

    # Clear screen at the beginning of each account creation attempt for a fresh display
    os.system("clear")
    print(f"{LOADING} Starting account creation process...")

    email_address, drtyghbj5hgcbv = generate_email()

    # Generate password using custom base if set, otherwise use random
    if password is None:
        if custom_password_base:
            six_digit = str(random.randint(100000, 999999))
            password = custom_password_base + six_digit
        else:
            password = generate_random_password()

    # Get user details with the determined password
    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(account_type, gender,
                                                                                                password)

    def check_page_loaded(url, headers):
        """Hintayin ang page na magkaroon ng form."""
        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = requests.get(url, timeout=30, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find("form")
                if form:
                    return form
                else:
                    print(f"{WARNING} Form not found on {url}, retrying...")
            except requests.exceptions.RequestException as e:
                print(f"{FAILURE} No internet or connection issue: {e}. Retrying in {RETRY_DELAY} seconds...")
            except Exception as e:
                print(f"{FAILURE} An unexpected error occurred: {e}. Retrying in {RETRY_DELAY} seconds...")

            time.sleep(RETRY_DELAY)
            retries += 1
        print(f"{FAILURE} Failed to load page and find form after {MAX_RETRIES} retries.")
        return None

    url = "https://m.facebook.com/reg"
    # User-Agent is dynamically fetched now
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

    form = check_page_loaded(url, headers)
    if not form:
        print(f"\033[1;91m{FAILURE} Could not load registration page or find form. Aborting current attempt.\033[0m")
        return  # Exit if the page couldn't be loaded properly

    # Re-fetch the page to get the form with all current inputs, important for dynamic fields
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")
            if form:
                break
        except requests.exceptions.RequestException as e:
            print(f"\033[1;91m{FAILURE} Error fetching form: {e}. Retrying...\033[0m")
        except Exception as e:
            print(f"\033[1;91m{FAILURE} An unexpected error occurred while fetching form: {e}. Retrying...\033[0m")
        time.sleep(RETRY_DELAY)
        retries += 1

    if not form:
        print(f"\033[1;91m{FAILURE} Failed to get registration form after retries. Aborting.\033[0m")
        return

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

    print(f"{LOADING} Submitting registration data...")
    try:
        response = session.post(action_url, headers=headers, data=data, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"\033[1;91m{FAILURE} Network error during submission: {e}. Cannot complete account creation.\033[0m")
        return
    except Exception as e:
        print(
            f"\033[1;91m{FAILURE} An unexpected error occurred during submission: {e}. Cannot complete account creation.\033[0m")
        return

    if "c_user" not in session.cookies:
        print(
            "\033[1;91m⚠️ Create Account Failed. No c_user cookie found. Try toggling airplane mode or use another email.\033[0m")
        time.sleep(3)
        return

    uid = session.cookies.get("c_user")
    profile_id = f'https://www.facebook.com/profile.php?id={uid}'

    # Save cookies
    cookie_dir = "/storage/emulated/0/cookie"  # This path is specific to Android environments (e.g., Termux)
    os.makedirs(cookie_dir, exist_ok=True)
    cookie_file = os.path.join(cookie_dir, f"{uid}.json")
    cookie_names = ["c_user", "datr", "fr", "noscript", "sb", "xs"]
    cookies_data = {name: session.cookies.get(name, "") for name in cookie_names}
    try:
        with open(cookie_file, "w") as f:
            json.dump(cookies_data, f, indent=4)
    except IOError as e:
        print(f"\033[1;91m{FAILURE} Error saving cookies: {e}\033[0m")

    # Check for checkpoint (blocked account)
    soup = BeautifulSoup(response.text, "html.parser")  # Use the soup from the post response
    form_checkpoint = soup.find('form', action=lambda x: x and 'checkpoint' in x)
    if form_checkpoint:
        print("\033[1;91m⚠️ Created account blocked. Try toggling airplane mode or clearing Facebook Lite data.\033[0m")
        time.sleep(3)
        # No os.system("clear") here to keep previous success message
        return  # Return to allow NEMAIN to try again

    # Attempt to get confirmation code from Harakirimail
    jbkj = None
    retries = 0
    while retries < MAX_RETRIES * 5:  # Give more time for email
        try:
            dtryvghjuijhn = requests.get(drtyghbj5hgcbv, timeout=30)
            dtryvghjuijhn.raise_for_status()  # Check for HTTP errors
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
            print(f"\033[1;91m{FAILURE} Error fetching email: {e}. Retrying...\033[0m")
        except Exception as e:
            print(f"\033[1;91m{FAILURE} An unexpected error occurred while processing email: {e}. Retrying...\033[0m")

        time.sleep(5)
        retries += 1

    if not jbkj:
        print(
            f"\033[1;91m{FAILURE} Failed to get confirmation code after multiple attempts. Account might be unconfirmed.\033[0m")
        # Still proceed to save the account, but mark it as unconfirmed if needed.
        # For now, just print the message and continue.

    # Print success details - these will now persist
    print('\n' * 2)  # Add some spacing
    print(f"\033[1;92m{SUCCESS}       Email: | {email_address} |\033[0m")
    print(f"\033[1;92m{SUCCESS}       Pass: | {password} |\033[0m")
    print(f"\033[1;92m{SUCCESS}       Code: | {jbkj if jbkj else 'N/A (Code not found)'}\033[0m")
    print(f"\033[1;92m{SUCCESS}       Profile Link: | {profile_id} |\033[0m")
    print('\n' * 2)  # Add some spacing

    # User input to check for blocked status before continuing
    while True:
        try:
            user_input = input("Type 'b' if blocked, or press Enter to continue: ").strip().lower()
            if user_input == 'b':
                print("\033[1;91m⚠️ User indicated account was blocked. Moving to next account attempt.\033[0m")
                time.sleep(2)
                # No os.system("clear") here to keep previous success message
                return  # Return to indicate this account was effectively blocked
            break
        except Exception as e:
            print(f"\033[1;91m{FAILURE} Error during user input: {e}. Please try again.\033[0m")

    filename = "/storage/emulated/0/Acc_Created.xlsx"
    full_name = f"{firstname} {lastname}"
    data_to_save = [full_name, email_address, password, profile_id]
    save_to_xlsx(filename, data_to_save)
    # IMPORTANT: Removed os.system("clear") here to allow prints to stay on screen.


def NEMAIN():
    os.system("clear")  # Clear screen at the start of NEMAIN
    print("\033[1;36m======================================\033[0m")
    print("\033[1;36m  Facebook Unconfirmed Account Creator\033[0m")
    print("\033[1;36m======================================\033[0m\n")

    global custom_password_base
    if custom_password_base is None:
        inp = input("Enter custom password base (e.g., 'Promises', leave blank for default 'Promises'): ").strip()
        custom_password_base = inp if inp else "Promises"

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

    # Fixed account type and gender for now, as per original code
    account_type = 1  # 1 for male, check get_names logic for others
    gender = 1  # 1 for male, 2 for female (if female_first_names.txt is used)

    for i in range(max_create):
        print(f"\n\033[1;33m--- Creating Account {i + 1} of {max_create} ---\033[0m")
        # usern is not used in create_fbunconfirmed, so removing it from args
        create_fbunconfirmed(account_type, gender, session=requests.Session())
        if i < max_create - 1:  # Add a clear separator between attempts
            print("\n" * 2)  # Add a couple of empty lines for visual separation
            print("\033[1;36m-----------------------------------------\033[0m")
            print("\033[1;36m      Starting next account creation     \033[0m")
            print("\033[1;36m-----------------------------------------\033[0m")
            time.sleep(1)  # Small pause before clearing for the next attempt

    print("\n\033[1;92m======================================\033[0m")
    print("\033[1;92m        Account Creation Finished!      \033[0m")
    print("\033[1;92m======================================\033[0m")


if __name__ == "__main__":
    NEMAIN()
