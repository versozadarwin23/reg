import os
import subprocess
import uuid
import requests
from bs4 import BeautifulSoup
import time
import sys
import random
import string
import openpyxl  # Import openpyxl

# --- Constants ---
MAX_RETRIES = 3
RETRY_DELAY = 2

SUCCESS = "✅"
FAILURE = "❌"
WARNING = "⚠️"
LOADING = "⏳"


# --- Helper Functions ---

def print_box_title():
    cyan = "\033[1;96m"
    reset = "\033[0m"

    title = " Facebook Account Creator "
    width = len(title) + 4  # Padding for box

    print(cyan + "┌" + "─" * (width - 2) + "┐")
    print("│" + " " * (width - 2) + "│")
    print("│ " + title + " │")
    print("│" + " " * (width - 2) + "│")
    print("└" + "─" * (width - 2) + "┘" + reset)

def load_user_agents(file_path="user_agents.txt"):
    """Loads user agents from a specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            user_agents = [line.strip() for line in file if line.strip()]
        if not user_agents:
            return [
                'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]']
        return user_agents
    except FileNotFoundError:
        print(
            f"{FAILURE} Error: User agent file '{file_path}' not found. Please create it with one user agent per line.")
        sys.exit()


def load_names_from_file(file_path):
    """Loads names from a specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            names = [line.strip() for line in file.readlines() if line.strip()]
        if not names:
            print(f"{WARNING} Name file '{file_path}' is empty. Account creation might fail without names.")
        return names
    except FileNotFoundError:
        print(f"{FAILURE} Error: Name file '{file_path}' not found. Please ensure it exists and contains names.")
        sys.exit()


# Load names once globally to avoid re-loading in a loop
MALE_FIRST_NAMES = load_names_from_file("first_name.txt")
FEMALE_FIRST_NAMES = load_names_from_file("first_name.txt")  # Assuming same file for male/female first names
LAST_NAMES = load_names_from_file("last_name.txt")


def get_names(gender):
    """Retrieves random first and last names based on gender."""
    firstname = random.choice(MALE_FIRST_NAMES if gender == 1 else FEMALE_FIRST_NAMES)
    lastname = random.choice(LAST_NAMES)
    return firstname, lastname


def generate_random_phone_number():
    """Generates a random Philippine-like phone number (starting with 9)."""
    # Common Philippine mobile prefixes (e.g., 905, 906, 917, 920, etc.)
    prefixes = ["905", "906", "907", "908", "909", "910", "912", "915", "916", "917", "918", "919", "920", "921", "922",
                "923", "925", "926", "927", "928", "929", "930", "932", "933", "934", "935", "936", "937", "938", "939",
                "942", "943", "945", "946", "947", "948", "949", "950", "951", "953", "954", "955", "956", "961", "963",
                "965", "966", "967", "968", "969", "970", "973", "974", "975", "977", "978", "979", "981", "989", "994",
                "995", "997", "998", "999"]
    return random.choice(prefixes) + str(random.randint(1000000, 9999999))


def generate_random_password(password_base=None):
    """Generates a random password following a specific pattern or a custom base."""
    if password_base and password_base.strip():  # Check if base is provided and not empty
        base = password_base.strip()
    else:
        base = 'Promises'  # Default base if none provided

    six_digit = str(random.randint(100000, 999999))
    password = base + six_digit
    return password


def generate_user_details(gender, password_base=None):
    """
    Generates initial user details (names, birthday, and password).
    """
    firstname, lastname = get_names(gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)

    password = generate_random_password(password_base)
    return firstname, lastname, date, year, month, password


def save_to_xlsx(filename, data):
    """Saves account details to an XLSX file."""
    for _ in range(MAX_RETRIES):
        try:
            # Check if file exists, if not, create a new workbook with headers
            if not os.path.isfile(filename):
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Account Details"
                sheet.append(['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'STATUS'])
            else:
                # Load existing workbook
                workbook = openpyxl.load_workbook(filename)
                sheet = workbook.active

            # Append the new data
            sheet.append(data)
            workbook.save(filename)
            file_manager = 'File Manager or Phone Storage Name Acc_Created.xlsx'
            print(f"\033[1;92m{SUCCESS} Data saved to {file_manager}\033[0m")
            break
        except Exception as e:
            print(f"{FAILURE} Error saving to {filename}: {e}. Retrying... (Attempt {_ + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
    else:
        print(
            f"{FAILURE} Failed to save account details after multiple retries. Please check file permissions or if the file is open.")


# --- Main Account Creation Logic ---

def create_fb_account(password_base_choice, initial_contact_method, provided_email=None):
    """
    Attempts to create a single Facebook account.

    Args:
        password_base_choice (str or None): User-provided password base, or None for random.
        initial_contact_method (str): '1' for phone, '2' for email.
        provided_email (str or None): Email address if initial_contact_method is '2'.

    Returns:
        tuple: (success_status, profile_link, final_contact_info, password_used, full_name)
                success_status is boolean. Others are None if creation fails.
    """
    session = requests.Session()
    current_user_agent = random.choice(load_user_agents())  # Load and pick a user agent

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

    # Nested function for retrying requests with current session and headers
    def retry_request(url, method="get", data=None, extra_headers=None):
        req_headers = headers.copy()
        if extra_headers:
            req_headers.update(extra_headers)

        for attempt in range(MAX_RETRIES):
            try:
                if method == "get":
                    response = session.get(url, headers=req_headers, allow_redirects=True)
                elif method == "post":
                    response = session.post(url, headers=req_headers, data=data, allow_redirects=True)

                if response.status_code == 200:
                    return response
                else:
                    print(
                        f"{WARNING} Network error (Status code: {response.status_code}). Retrying... (Attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
            except requests.exceptions.ConnectionError:
                print(f"{FAILURE} Connection error. Check your internet. (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(
                    f"{FAILURE} An unexpected error occurred during request: {e}. Retrying... (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
        print(f"{FAILURE} Failed to get a successful response after multiple retries.")
        return None

    # Determine initial contact info based on user's choice
    initial_contact_info = ""
    initial_contact_was_phone = False
    if initial_contact_method == '1':  # Phone
        initial_contact_info = generate_random_phone_number()
        initial_contact_was_phone = True
    elif initial_contact_method == '2':  # Email
        initial_contact_info = provided_email  # Use the email passed from main_workflow

    # Generate user details
    # account_type and gender are fixed to 1 for now based on original code
    gender = 1
    firstname, lastname, date, year, month, used_password = generate_user_details(gender, password_base_choice)
    full_name = f"{firstname} {lastname}"

    profile_link = None
    current_contact_info = initial_contact_info  # This will be updated if email changes

    # --- Main Registration Attempt Loop ---
    registration_successful = False
    for attempt in range(MAX_RETRIES):  # Outer loop for major registration attempts
        os.system("clear")
        print(
            f"\033[1;93m{LOADING} Attempting account creation for {full_name}... (Reg attempt {attempt + 1}/{MAX_RETRIES})\n\033[0m")

        url = "https://m.facebook.com/reg"
        reg_page_response = retry_request(url)
        if not reg_page_response:
            print(f"\033[1;91m{WARNING} Failed to load registration page. Trying next attempt.\033[0m")
            continue

        soup = BeautifulSoup(reg_page_response.text, 'html.parser')
        form = soup.find("form", action=True)  # Find form with an action attribute
        if not form:
            print(
                f"{FAILURE} Registration form not found on page. This might indicate a block or page change. Retrying...")
            time.sleep(RETRY_DELAY)
            continue

        action_url = requests.compat.urljoin(url, form["action"])
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
            "reg_email__": initial_contact_info,  # Use the determined initial contact info
        }

        for inp in inputs:
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp.get("value", "")  # Use .get to handle inputs without value

        reg_response = retry_request(action_url, method="post", data=data)

        if not reg_response:
            print(f"{WARNING} Registration POST request failed. Trying next attempt.")
            time.sleep(RETRY_DELAY * 2)
            continue

        if "c_user" in session.cookies:
            uid = session.cookies.get("c_user")
            profile_link = f'https://www.facebook.com/profile.php?id={uid}'
            registration_successful = True
            break  # Exit main registration loop on success
        else:
            soup_after_reg = BeautifulSoup(reg_response.text, "html.parser")
            registration_error_div = soup_after_reg.find(id="registration-error")
            checkpoint_form = soup_after_reg.find('form', action=lambda x: x and 'checkpoint' in x)

            if registration_error_div:
                error_text = registration_error_div.get_text(strip=True)
                print(f"{FAILURE} Registration error: {error_text}")
                # Specific error messages from your initial prompt
                if "registration_error pls enter valid email or number" in error_text.lower():
                    print(
                        f"{WARNING} Contact info appears invalid or blocked. A new one will be generated for next attempt (if phone) or user will be re-prompted (if email).")
                elif "try use another phone number with different info and password" in error_text.lower():
                    print(f"{WARNING} Account details seem to be problematic. Trying with new generated details.")
            elif checkpoint_form:
                print(
                    f"{WARNING} Account hit a checkpoint immediately. This account is likely blocked. Retrying with new details...")
            else:
                print(
                    f"{WARNING} Create Account Failed: No c_user cookie found and no clear error message. Facebook might have blocked the attempt silently. Retrying...")

            time.sleep(RETRY_DELAY * 2)  # Give some time before next retry

    if not registration_successful:
        print(f"{FAILURE} Failed to create account after multiple registration attempts.")
        return False, None, None, None, None  # Indicate overall failure

    # --- Post-Registration (Offer Email Change if Phone was Used) ---
    if initial_contact_was_phone:
        try:
            change_email_url = "https://m.facebook.com/changeemail/"
            # Use specific headers for email change if needed, otherwise default headers are fine
            email_response = retry_request(change_email_url)

            if email_response:
                soup_email_form = BeautifulSoup(email_response.text, "html.parser")
                form_email_change = soup_email_form.find("form", action=True)

                if form_email_change:
                    action_url_email_change = requests.compat.urljoin(change_email_url, form_email_change["action"])
                    data_email_change = {inp["name"]: inp.get("value", "") for inp in
                                         form_email_change.find_all("input") if inp.has_attr("name")}

                    while True:
                        new_email_input = input(f" Type your Email: \033[0m").strip()
                        # Basic email format validation
                        if '@' in new_email_input and '.' in new_email_input and len(new_email_input) > 5:
                            data_email_change["new"] = new_email_input
                            data_email_change["submit"] = "Add"
                            new_email_prompt_successful = True
                            break
                        else:
                            print(
                                f"{WARNING} Invalid email format. Please enter a valid email address or press Enter to skip.")

                    if new_email_prompt_successful:  # Only proceed if user entered a valid email
                        email_change_post_response = retry_request(
                            action_url_email_change,
                            method="post",
                            data=data_email_change
                        )

                        if email_change_post_response and "c_user" in session.cookies:
                            # Check if email actually appears changed on the page or in next request
                            # This is a weak check, a stronger check would be to navigate to settings and parse
                            if new_email_input in email_change_post_response.text:
                                current_contact_info = new_email_input
                        else:
                            print(
                                "\033[1;91m⚠️😢 Error: Failed to change email after post. It might be invalid or an issue occurred.\033[0m")
                else:
                    print(f"{WARNING} Could not find the email change form. Skipping email change.")
            else:
                print(f"{WARNING} Failed to load email change page. Skipping email change.")
        except Exception as e:
            print(f"{FAILURE} An unexpected error occurred during the email change process: {e}")

    os.system("clear")
    print(f"\033[1;92m        Password: {used_password}\033[0m")
    user_input_blocked = input(
        f"\033[32m Type 'b' if the account is blocked, or press Enter if not blocked to continue:\033[0m ").lower().strip()
    if user_input_blocked == "b":
        print(f"{WARNING} Account marked as blocked by user. This account will not be saved.")
        time.sleep(1)
        return False, None, None, None, None  # Indicate user-marked failure

    # Return success and all collected details
    return True, profile_link, current_contact_info, used_password, full_name


# Variables to store user's choices after the first run
_cached_password_choice = None
_cached_initial_contact_method = None
_cached_user_email_for_choice_2 = None


def main_workflow():
    """Main function to control the overall account creation flow."""
    global _cached_password_choice, _cached_initial_contact_method, _cached_user_email_for_choice_2

    os.system("clear")
    max_overall_attempts = 99999

    print_box_title()

    # Get user choices only if they haven't been cached
    if _cached_password_choice is None:
        _cached_password_choice = input(f"\033[1;92m Type Your Password: \033[0m").strip()

    if _cached_initial_contact_method is None:
        while _cached_initial_contact_method not in ['1', '2']:
            os.system("clear")
            print("1. Phone Number)\033[0m")
            print("2. Email Address)\033[0m")
            _cached_initial_contact_method = input(f" Enter your choice (1 or 2): \033[0m").strip()
            if _cached_initial_contact_method not in ['1', '2']:
                print(f"{WARNING} Invalid choice. Please enter 1 or 2.")
                time.sleep(1)

    if _cached_initial_contact_method == '2' and _cached_user_email_for_choice_2 is None:
        while True:
            email_input = input(
                f" Enter the email address to use for registration (e.g., your@email.com): \033[0m").strip()
            if '@' in email_input and '.' in email_input and len(email_input) > 5:
                _cached_user_email_for_choice_2 = email_input
                break
            else:
                print(f"{WARNING} Invalid email format. Please enter a valid email address.")
                time.sleep(1)

    successful_account_created = False
    for overall_attempt in range(1, max_overall_attempts + 1):
        print(
            f"\033[1;93m\n{LOADING} Starting overall account creation attempt {overall_attempt}/{max_overall_attempts}...\033[0m")

        success, profile_id_val, contact_info_val, password_val, full_name_val = create_fb_account(
            _cached_password_choice,
            _cached_initial_contact_method,
            provided_email=_cached_user_email_for_choice_2
        )

        if success:
            output_filename = "/storage/emulated/0/Acc_Created.xlsx"
            data_to_save = [full_name_val, contact_info_val, password_val, profile_id_val]
            save_to_xlsx(output_filename, data_to_save)
            print(
                f"\033[1;92m{SUCCESS} Account created and saved! Details: {full_name_val} | {contact_info_val} | {password_val}\033[0m")
            successful_account_created = True
            time.sleep(3)
            break
        else:
            print(f"{FAILURE} Account creation failed for this attempt. Checking for remaining attempts...")
            time.sleep(2)

    if not successful_account_created:
        print(
            f"{FAILURE} Maximum overall creation attempts ({max_overall_attempts}) reached. No account was successfully created during this run.")


# --- Main Execution Block ---
if __name__ == "__main__":
    # Ensure name files exist, provide basic content if missing
    for filename in ["first_name.txt", "last_name.txt", "user_agents.txt"]:
        if not os.path.exists(filename):
            print(
                f"{WARNING} File '{filename}' not found. Creating a placeholder file. Please populate it with real data.")
            with open(filename, 'w') as f:
                if filename == "first_name.txt":
                    f.write("John\nJane\nMichael\nSarah\n")
                elif filename == "last_name.txt":
                    f.write("Doe\nSmith\nJohnson\nWilliams\n")
                elif filename == "user_agents.txt":
                    f.write(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36\n")
                    f.write(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15\n")
                    f.write(
                        "Mozilla/5.0 (Linux; Android 10; SM-G960F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36\n")

    while True:
        main_workflow()
        print("\n" + "=" * 50)
