import requests
from bs4 import BeautifulSoup
import time
import random
import string
import os
from datetime import datetime
import re
import sys
import uuid
import hashlib
import subprocess

# IP = {"1-126, 128-191, 192, 99999"} # This variable is unused and incorrectly defined for a range.

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
LIGHT_PINK = "\033[95m"
PINK = "\033[91m"
MAGENTA = "\033[35m"
LIGHT_BLUE = "\033[94m"
PURPLE = "\033[35m"
WHITE = "\033[97m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Constants
BASE_URL_KUKU = "https://m.kuku.lu"
MAX_RETRIES = 3  # Currently unused in all functions, but kept as a constant
RETRY_DELAY = 2  # Currently unused in all functions, but kept as a constant

# Emojis and Symbols
SUCCESS = "✅"
FAILURE = "❌"  # Changed to red X for failure
INFO = "ℹ️"
WARNING = "⚠️"
LOADING = "⏳"


def clear():
    """Clears the terminal screen."""
    os.system('clear')


usernamefile = "email_usernames.txt"  # This variable is unused


def generate_old_android_ua():
    """Generate an old Android user agent."""
    random.seed(datetime.now().timestamp())  # Seed the random generator for diversity

    android_versions = [
        ("4.0.3", "2011"),
        ("4.0.4", "2012"),
        ("4.1.1", "JRO03"),
        ("4.1.2", "JZO54"),
        ("4.2.1", "JOP40"),
        ("4.2.2", "JDQ39"),
        ("4.3", "JSS15"),
        ("4.4.2", "KOT49"),
        ("4.4.3", "KTU84"),
        ("4.4.4", "KTU84Q")
    ]

    devices = [
        ("Galaxy Nexus", "Samsung"),
        ("Nexus S", "Samsung"),
        ("Xperia Z", "Sony"),
        ("Xperia SP", "Sony"),
        ("One M7", "HTC"),
        ("One M8", "HTC"),
        ("Optimus G", "LG"),
        ("G2", "LG"),
        ("Moto X", "Motorola"),
        ("DROID RAZR", "Motorola")
    ]

    android_ver, android_code = random.choice(android_versions)
    device, manufacturer = random.choice(devices)

    build_number = f"{android_code}"
    if android_ver.startswith("4.0"):
        build_number += f".{random.choice(['IMM76', 'GRK39', 'IMM76D'])}"
    else:
        build_number += random.choice(["D", "E", "F"]) + str(random.randint(10, 99))

    chrome_major = random.randint(
        18 if android_ver.startswith("4.0") else 25,
        35 if android_ver.startswith("4.4") else 32
    )
    chrome_build = random.randint(1000, 1999)
    chrome_patch = random.randint(50, 199)

    webkit_base = "534.30" if chrome_major < 25 else "537.36"
    webkit_ver = f"{webkit_base}.{random.randint(1, 99)}" if random.random() > 0.7 else webkit_base

    ua = (
        f"Mozilla/5.0 (Linux; Android {android_ver}; {device} Build/{build_number}) "
        f"AppleWebKit/{webkit_ver} (KHTML, like Gecko) "
        f"Chrome/{chrome_major}.0.{chrome_build}.{chrome_patch} Mobile Safari/{webkit_ver.split('.')[0]}.0"
    )

    return ua


def get_cookies_kuku():
    """Fetch initial cookies from the email service."""
    url = f"{BASE_URL_KUKU}/en.php"
    headers = {
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "upgrade-insecure-requests": "1",
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.google.com/",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=0, i"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.cookies.get_dict()
        else:
            print(f"{RED}{FAILURE} Failed to fetch cookies: {response.status_code}{RESET}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{RED}{FAILURE} Error fetching cookies: {e}{RESET}")
        return None

def generate_email_kuku(cok):
    """Generate a random email using kuku.lu."""
    url = f"{BASE_URL_KUKU}/index.php"
    em = ''.join(random.choices(string.ascii_lowercase, k=18))
    params = {
        "action": "addMailAddrByManual",
        "nopost": "1",
        "by_system": "1",
        "t": str(int(time.time())),
        "csrf_token_check": cok.get("cookie_csrf_token", ""),
        "newdomain": "boxfi.uk",
        "newuser": em,
        "recaptcha_token": "",
        "_": str(int(time.time() * 1000))
    }
    headers = {
        "sec-ch-ua-platform": '"Android"',
        "x-requested-with": "XMLHttpRequest",
        "user-agent": generate_old_android_ua(),
        "accept": "*/*",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?1",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i"
    }

    while True:
        try:
            response = requests.get(url, headers=headers, params=params, cookies=cok)
            if response.status_code == 200:
                if response.text.startswith("OK:"):
                    return response.text.split("OK:")[1].strip()
                else:
                    # Save unexpected HTML response
                    with open("kuku_response_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print(f"{RED}[{GREEN}•{RED}]{RESET} {YELLOW}Unexpected response saved to kuku_response_debug.html{RESET}")
                    time.sleep(15)
            else:
                print(f"{RED}[{GREEN}•{RED}]{RESET} {RED}Non-200 status code: {response.status_code}{RESET}")
                time.sleep(15)
        except requests.exceptions.ConnectionError:
            print(f"{RED}[{GREEN}•{RED}]{RESET} {RED}Connection error. Retrying in 15 seconds...{RESET}")
            time.sleep(15)
        except Exception as e:
            print(f"{RED}[{GREEN}•{RED}]{RESET} {RED}Error: {e}. Retrying in 15 seconds...{RESET}")
            time.sleep(15)


def check_otp_kuku(email, cok, max_attempts=10, delay=3):
    """Check for OTP in the email."""
    url = f"{BASE_URL_KUKU}/recv._ajax.php"
    params = {
        "nopost": "1",
        "csrf_token_check": cok.get("cookie_csrf_token", ""),
        "csrf_subtoken_check": cok.get("csrf_subtoken_check", ""),  # Ensure this is present if needed by kuku.lu
        "_": str(int(time.time() * 1000))
    }
    headers = {
        "sec-ch-ua-platform": '"Android"',
        "x-requested-with": "XMLHttpRequest",
        "User-Agent": 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]',
        "accept": "*/*",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?1",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-encoding": "gzip, deflate",  # Removed trailing comma
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i"
    }

    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=headers, params=params, cookies=cok)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                subject_div = soup.find("div", id=lambda x: x and x.startswith("area_mail_title_"))
                if subject_div:
                    subject_text = subject_div.get_text(strip=True)
                    # Regex to capture 4 to 6 digit OTP, considering variations like FB- XXXXXX or XXXXXX is your code
                    otp_match = re.search(r'(?:FB-[\s]*|is your confirmation code[\s]*|Confirmation Code:\s*)(\d{4,6})',
                                          subject_text, re.IGNORECASE)
                    if otp_match:
                        return otp_match.group(1)
                    else:
                        print(f"{INFO} Attempt {attempt + 1}/{max_attempts}: OTP not found yet for {email}. Retrying in {delay} seconds...{RESET}")
                        time.sleep(delay)
                else:
                    print(f"{INFO} Attempt {attempt + 1}/{max_attempts}: Subject div not found. Retrying in {delay} seconds...{RESET}")
                    time.sleep(delay)
            else:
                print(
                    f"{YELLOW}{INFO} Kuku.lu check OTP response {response.status_code}, retrying in {delay} seconds...{RESET}")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"{RED}[{INFO}]{RESET} {RED}Connection error checking OTP: {e}. Retrying in 15 seconds...{RESET}")
            time.sleep(15)
        except Exception as e:
            print(f"{RED}[{INFO}]{RESET} {RED}Error checking OTP: {e}. Retrying in 15 seconds...{RESET}")
            time.sleep(15)

    return None


def load_names_from_file(file_path):
    """Loads names from a specified file."""
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(
            f"{RED}{FAILURE} Error: Name file '{file_path}' not found. Please ensure it exists in the same directory as the script.{RESET}")
        sys.exit(1)  # Exit the script if critical files are missing


def get_names(account_type, gender):
    """Retrieves random first and last names based on account type and gender."""
    male_first_names = load_names_from_file("first_name.txt")
    last_names = load_names_from_file("last_name.txt")
    female_first_names = load_names_from_file(
        "first_name.txt")  # Assuming same file for female names or change to "female_first_name.txt" if separate

    firstname = random.choice(male_first_names if gender == 1 else female_first_names)
    lastname = random.choice(last_names)
    return firstname, lastname


def generate_random_phone_number():
    """Generate a random Philippine-like phone number (09XX-XXX-XXXX)."""
    # Assuming Philippine mobile number formats starting with 09
    random_prefix_digits = random.choice(["091", "092", "093", "094", "095", "096", "097", "099"])  # Common prefixes
    remaining_digits = ''.join(random.choices(string.digits, k=8))  # 8 more digits
    number = f"{random_prefix_digits}{remaining_digits}"
    return number


def generate_random_password():
    """Generate a random password."""
    length = random.randint(10, 16)  # Password length between 10 and 16 characters
    all_characters = string.ascii_letters + string.digits + "@#$&_!"
    password = ''.join(random.choices(all_characters, k=length))
    return password


def generate_user_details(account_type, gender):
    """Generate random user details."""
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1990, 2005)  # More realistic birth year range for account creation
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    formatted_date = f"{date:02d}-{month:02d}-{year:04d}"  # Not used directly in Facebook reg, but good for tracking
    password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password


def create_fbunconfirmed(account_type, gender):
    """Create a Facebook account using kuku.lu for email and OTP."""

    asdf = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    ua = generate_old_android_ua()
    firstname, lastname, date, year, month, phone_number, password = generate_user_details(account_type, gender)
    # username = firstname + lastname + asdf # This username isn't used for FB registration directly

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
    session = requests.Session()

    def retry_request(url, headers, method="get", data=None, cookies=None):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                if method == "get":
                    response = session.get(url, headers=headers, cookies=cookies)
                elif method == "post":
                    response = session.post(url, headers=headers, data=data, cookies=cookies)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                return response
            except requests.exceptions.ConnectionError:
                print(f"{RED}{FAILURE} Connection error, retrying in {RETRY_DELAY} seconds...{RESET}")
                time.sleep(RETRY_DELAY)
                retries += 1
            except requests.exceptions.Timeout:
                print(f"{RED}{FAILURE} Request timed out, retrying in {RETRY_DELAY} seconds...{RESET}")
                time.sleep(RETRY_DELAY)
                retries += 1
            except requests.exceptions.RequestException as e:
                print(f"{RED}{FAILURE} Request error: {e}, retrying in {RETRY_DELAY} seconds...{RESET}")
                time.sleep(RETRY_DELAY)
                retries += 1
        print(f"{RED}{FAILURE} Max retries reached for {url}. Aborting.{RESET}")
        return None

    # Step 1: Initialize session and get the registration form
    response = retry_request(url, headers)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    form = soup.find("form")

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
            # Facebook often uses 'reg_email__' for phone numbers during initial registration
            "sex": f"{gender}",
            "encpass": f"{password}",
            "submit": "Sign Up"
        }

        for inp in inputs:
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

        time.sleep(2)  # Small delay before submission

        # Step 2: Submit the registration form
        while True:
            submit_response = retry_request(action_url, headers, method="post", data=data)
            if submit_response:
                break
            # If submit_response is None, retry_request failed, we should return
            return None

        uid = session.cookies.get("c_user")
        if not uid:
            # If c_user cookie is not found, registration might have failed or redirected.
            # Look for common error messages or redirection to /checkpoint
            if "checkpoint" in submit_response.url:
                print(f"{RED}{FAILURE} Account hit checkpoint during registration. Skipping.{RESET}")
            else:
                print(
                    f"{RED}{FAILURE} Failed to get user ID after initial registration. Response URL: {submit_response.url}{RESET}")
            return None

    else:
        print(f"{RED}{FAILURE} No registration form found on {url}.{RESET}")
        return None

    # Step 3: Change email - Introduce a retry loop for email change and OTP
    for _ in range(MAX_RETRIES): # Added retry for email change process
        change_email_url = "https://m.facebook.com/changeemail/"
        email_response = retry_request(change_email_url, headers)
        if not email_response:
            continue # Try again if initial request for email change page fails

        soup = BeautifulSoup(email_response.text, "html.parser")
        form = soup.find("form")

        if form:
            action_url = requests.compat.urljoin(change_email_url, form["action"]) if form.has_attr(
                "action") else change_email_url
            inputs = form.find_all("input")
            data = {}
            for inp in inputs:
                if inp.has_attr("name") and inp["name"] not in data:
                    data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

            # Generate email using kuku.lu
            cok = get_cookies_kuku()
            if not cok:
                print(f"{RED}{FAILURE} Failed to get Kuku.lu cookies. Cannot generate email. Retrying email change...{RESET}")
                time.sleep(RETRY_DELAY)
                continue # Try email change again

            email = generate_email_kuku(cok)
            if not email:
                print(f"{RED}{FAILURE} Failed to generate Kuku.lu email. Retrying email change...{RESET}")
                time.sleep(RETRY_DELAY)
                continue # Try email change again

            data["new"] = email
            data["submit"] = "Add"

            # Step 4: Submit email change form
            submit_response = retry_request(action_url, headers, method="post", data=data, cookies=session.cookies)
            if not submit_response:
                print(f"{RED}{FAILURE} Failed to submit email change form. Retrying email change...{RESET}")
                time.sleep(RETRY_DELAY)
                continue # Try email change again

            # Wait for and check OTP
            confirmation_code = check_otp_kuku(email, cok)
            cook = ";".join([f"{key}={value}" for key, value in session.cookies.items()])

            if confirmation_code:
                sys.stdout.write(f'\r\033[K{RESET}  [{GREEN}Successfull{RESET}]: {CYAN}{firstname} {lastname}|{GREEN}{phone_number}|{password}|{confirmation_code}|{email}{RESET}\n')
                sys.stdout.flush()
                # open("/sdcard/Cookie Files.txt", "a").write(f"{uid}|{password}|{confirmation_code}|{cook}|{email}\n") # Uncomment if you want to save cookies
                open("/sdcard/Created Accounts.txt", "a").write(
                    f"{firstname} {lastname}|{phone_number}|{password}|{uid}|{email}\n")
                return {"uid": uid, "password": password, "confirmation_code": confirmation_code, "cookies": cook,
                        "email": email}
            else:
                print(f"{YELLOW}{WARNING} Failed to get OTP for {email}. Account might be unconfirmed. Retrying email change with a new email...{RESET}")
                # The loop will automatically try again if MAX_RETRIES for email change is not exceeded.
                time.sleep(RETRY_DELAY)
                continue # This 'continue' will go to the next iteration of the outer loop for email change.
        else:
            print(f"{RED}{FAILURE} No email change form found on Facebook. Retrying email change...{RESET}")
            time.sleep(RETRY_DELAY)
            continue # Try email change again

    # If all retries for email change and OTP fail
    print(f"{RED}{FAILURE} Exhausted retries for email change and OTP for account associated with UID: {uid}. Account unconfirmed.{RESET}")
    return None # Or return {"uid": uid, "password": password, "email": email, "status": "no_otp"}


def NEMAIN():
    os.system("clear")
    try:
        while True:
            max_create_input = input(f"{YELLOW}{INFO}   HOW MANY ACCOUNTS? (1-500, 0=exit): {RESET}")
            if not max_create_input.isdigit():
                print(f"{RED}{FAILURE} Invalid input. Please enter a number.{RESET}")
                continue

            max_create = int(max_create_input)

            if max_create == 0:
                print(f"{CYAN}{INFO}   Exiting...{RESET}")
                break
            elif 1 <= max_create <= 500:
                print(f"{YELLOW}{INFO}   1. Philippine Account {RESET}")
                print(f"{YELLOW}{INFO}   2. Mix Account{CYAN}  (Not Available) {RESET}")
                account_type_input = input(f"{INFO}   Select Option: {GREEN}{RESET}")
                if not account_type_input.isdigit():
                    print(f"{RED}{FAILURE} Invalid input. Please enter a number.{RESET}")
                    continue

                account_type = int(account_type_input)
                if account_type not in [1, 2]:
                    print(f"{CYAN}{FAILURE} Invalid option selected. Please choose 1 or 2.{RESET}")
                    continue
                if account_type == 2:
                    print(
                        f"{CYAN}{FAILURE} Mix Account option is not available yet. Please select Philippine Account.{RESET}")
                    continue

                gender_input = input(f"{YELLOW}{INFO}   Gender (1: Male, 2: Female): {RESET}")
                if not gender_input.isdigit():
                    print(f"{RED}{FAILURE} Invalid input. Please enter a number.{RESET}")
                    continue

                gender = int(gender_input)
                if gender not in [1, 2]:
                    print(f"{CYAN}{FAILURE} Try again (1: Male, 2: Female){RESET}")
                    continue

                os.system("clear")
                oks = []
                cps = []
                print(f"{BLUE}{LOADING} Starting account creation...{RESET}")
                for i in range(max_create):
                    sys.stdout.write(
                        f'\r  \33[38;5;37m[\x1b[38;5;46mCreating Please wait...\33[38;5;37m]\033[1;97m-\33[38;5;37m[\033[1;97m{i + 1}/{max_create}\33[38;5;37m]\033[1;97m-\33[38;5;37m[\x1b[38;5;46mOK\33[38;5;160m/\x1b[38;5;208mFAIL\33[38;5;37m]\033[1;97m-\33[38;5;37m[\x1b[38;5;46m{len(oks)}\33[38;5;160m/\x1b[38;5;208m{len(cps)}\33[38;5;37m]{RESET}')
                    sys.stdout.flush()

                    result = create_fbunconfirmed(account_type, gender)

                    if result:
                        oks.append(result)
                    else:
                        cps.append("Failed Account")  # Append a string to indicate failure

                print(f"\n{BLUE}{INFO}   Batch creation completed{RESET}")
                print(f"{GREEN}{SUCCESS} Successfully Created: {len(oks)}{RESET}")
                print(f"{RED}{FAILURE} Failed to Create: {len(cps)}{RESET}")

            else:
                print(f"{CYAN}{FAILURE} Invalid input (1-500 only){RESET}")
    except ValueError:
        print(f"{RED}{FAILURE} Please enter a valid number.{RESET}")
    except KeyboardInterrupt:
        print(f"{RED}{FAILURE} \n[!] Interrupted by user.{RESET}")
    finally:
        print(f"{RED}{INFO} Exiting...{RESET}")
        exit()

# Run the main function
if __name__ == "__main__":
    NEMAIN()
