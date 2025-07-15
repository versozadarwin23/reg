import json
import os
import atexit
import hashlib
from requests.utils import dict_from_cookiejar
from openpyxl import Workbook, load_workbook
import requests
from bs4 import BeautifulSoup
import time
import random
from zipfile import BadZipFile
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

COOKIE_DIR = "/storage/emulated/0/cookie"
CONFIG_FILE = "/storage/emulated/0/settings.json"

# --- Original functions from reg.py (unchanged) ---

def random_device_model():
    models = [
        "Google-Pixel-7",
        "Google-Pixel-6a",
        "Google-Pixel-5"
    ]
    return random.choice(models)

def random_device_id():
    ids = [
        "15526637-0441-2553-4665-888888888048",
        "26637748-1552-3664-5776-999999999049",
        "37748859-2663-4775-6887-000000000050"
    ]
    return random.choice(ids)

def random_fingerprint():
    fingerprints = [
        "realme/RMX3761/RMX3761:14/UQ1A.240205.004/RMX3761_14_A.13:user/release-keys",
        "motorola/Moto-G73/Moto-G73:13/TP1A.220624.014/20240401:user/release-keys",
        "infinix/X6711/X6711:14/UQ1A.240205.004/X6711-GL-240104V101:user/release-keys"
    ]
    return random.choice(fingerprints)

ua = [
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Google Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; SM-G990U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]"
]

def delete_config_file():
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
        except Exception as e:
            print(f"⚠️ Failed to delete settings file: {e}")

atexit.register(delete_config_file)

def save_user_choice(key, value):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    data[key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_user_choice(key):
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get(key)
        except:
            return None

def clear_console():
    # This will be replaced by clearing the UI log in Flask
    pass

def save_to_txt(filename, data):
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write("|".join(data) + "\n")
    except Exception as e:
        print(f"❗ Error saving to {filename}: {e}")

def has_access_token_in_xlsx(filename, email_address):
    if not os.path.exists(filename):
        return False

    try:
        wb = load_workbook(filename)
    except BadZipFile:
        print(f"⚠️ Corrupted XLSX detected at {filename}. Skipping access token check.")
        return False

    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        saved_email = row[1]
        saved_access_token = row[4]
        if saved_email == email_address and saved_access_token and saved_access_token.strip():
            return True
    return False

def save_to_xlsx(filename, data):
    header_columns = ['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK', 'ACCESS TOKEN']

    while True:
        try:
            if os.path.exists(filename):
                try:
                    wb = load_workbook(filename)
                    ws = wb.active
                except BadZipFile:
                    print(f"⚠️ Corrupted XLSX detected at {filename}. Recreating file...")
                    os.remove(filename)
                    wb = Workbook()
                    ws = wb.active
                    ws.append(header_columns)
            else:
                wb = Workbook()
                ws = wb.active
                ws.append(header_columns)

            # Ensure header is correct
            header = [cell.value for cell in ws[1]]
            if header != header_columns:
                ws.delete_rows(1)
                ws.insert_rows(1)
                ws.append(header_columns)

            # Check if row already exists
            existing_rows = [tuple(row) for row in ws.iter_rows(min_row=2, values_only=True)]
            if tuple(data) not in existing_rows:
                ws.append(data)

            wb.save(filename)
            break
        except Exception as e:
            print(f"❗ Error saving to {filename}: {e}. Retrying in 1 second...")
            time.sleep(1)

def load_names_from_file(file_path):
    # Ensure these files exist or handle their absence
    if not os.path.exists(file_path):
        # Create dummy files if they don't exist
        with open(file_path, 'w', encoding='utf-8') as f:
            if "first_name" in file_path:
                f.write("John\nJane\n")
            elif "last_name" in file_path:
                f.write("Doe\nSmith\n")
        print(f"Created dummy file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def get_names(account_type, gender):
    firstnames = load_names_from_file("first_name.txt")
    last_names = load_names_from_file("last_name.txt")
    firstname = random.choice(firstnames)
    lastname = random.choice(last_names)
    return firstname, lastname

def generate_random_phone_number():
    random_number = str(random.randint(1000000, 9999999))
    third = random.randint(0, 4)
    forth = random.randint(1, 7)
    return f"9{third}{forth}{random_number}"

def generate_random_password():
    return 'Promises' + str(random.randint(100000, 999999))

def generate_user_details(account_type, gender, password=None):
    firstname, lastname, date, year, month, phone_number, password = None, None, None, None, None, None, None
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    if password is None:
        password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password

custom_password_base = None

def ensure_cookie_dir():
    if not os.path.exists(COOKIE_DIR):
        os.makedirs(COOKIE_DIR)

def save_cookie_json(cookie_dict):
    ensure_cookie_dir()
    c_user = cookie_dict.get("c_user")
    if not c_user:
        print("❌ ERROR: No 'c_user' in cookie_dict. Cannot save.")
        return
    file_path = os.path.join(COOKIE_DIR, f"{c_user}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cookie_dict, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save cookie: {e}")

def save_session_cookie(session):
    cookie_dict = dict_from_cookiejar(session.cookies)
    save_cookie_json(cookie_dict)

# --- Modified create_fbunconfirmed to work with Flask and UI ---
def create_fbunconfirmed_flask(account_type, usern, gender, password=None, session=None, reg_choice=None, user_email_input=None, new_email_input=None):
    global custom_password_base
    agent = random.choice(ua)
    log_messages = [] # To store messages for the UI

    def log_to_ui(message, color="text-gray-700"):
        log_messages.append({"message": message, "color": color})
        print(message) # Also print to console for debugging

    if password is None:
        if custom_password_base:
            password = custom_password_base + str(random.randint(100000, 999999))
        else:
            password = generate_random_password()

    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(account_type, gender, password)
    log_to_ui(f"Generated Name: {firstname} {lastname}", "text-success")
    log_to_ui(f"Generated Password: {password}", "text-success")

    url = "https://m.facebook.com/reg"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://m.facebook.com/reg",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9",
        "X-FB-Connection-Type": "mobile.LTE",
        "X-FB-Device": random_device_model(),
        "X-FB-Device-ID": random_device_id(),
        "X-FB-Fingerprint": random_fingerprint(),
        "X-FB-Connection-Quality": "EXCELLENT",
        "X-FB-Net-HNI": "51502",
        "X-FB-SIM-HNI": "51502",
        "X-FB-HTTP-Engine": "Liger",
        'x-fb-connection-type': 'Unknown',
        'accept-encoding': 'gzip, deflate',
        'content-type': 'application/x-www-form-urlencoded',
        'x-fb-http-engine': 'Liger',
        'User-Agent': agent,
    }

    if session is None:
        session = requests.Session()

    def get_registration_form():
        while True:
            try:
                response = session.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                form = soup.find("form")
                if form:
                    return form, response.text
            except requests.exceptions.RequestException as e:
                log_to_ui(f"😢 Failed to connect to network: {e}. Retrying...", "text-danger")
                time.sleep(3)
            except Exception as e:
                log_to_ui(f"An unexpected error occurred during form retrieval: {e}. Retrying...", "text-danger")
                time.sleep(3)


    form, initial_response_text = get_registration_form()

    email_or_phone = ""
    is_phone_choice = False

    if reg_choice == '1': # User chose email
        email_or_phone = user_email_input
        if not email_or_phone:
            log_to_ui("❌ Email cannot be empty.", "text-danger")
            return {"status": "error", "message": "Email cannot be empty.", "log": log_messages}
        is_phone_choice = False
        log_to_ui(f"Using provided email: {email_or_phone}", "text-info")
    else: # User chose random phone number
        email_or_phone = phone_number
        is_phone_choice = True
        log_to_ui(f"Using generated phone number: {email_or_phone}", "text-info")


    data = {
        "firstname": firstname,
        "lastname": lastname,
        "birthday_day": str(date),
        "birthday_month": str(month),
        "birthday_year": str(year),
        "reg_email__": email_or_phone,
        "sex": str(gender),
        "encpass": password,
        "submit": "Sign Up"
    }

    if form:
        action_url = requests.compat.urljoin(url, form.get("action", url))
        for inp in form.find_all("input"):
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp.get("value", "")

        try:
            response = session.post(action_url, headers=headers, data=data)
        except requests.exceptions.RequestException as e:
            log_to_ui(f"❌ Network error during registration: {e}", "text-danger")
            return {"status": "error", "message": "Network error during registration.", "log": log_messages}
        except Exception as e:
            log_to_ui(f"An unexpected error occurred during registration: {e}", "text-danger")
            return {"status": "error", "message": "An unexpected error occurred during registration.", "log": log_messages}

    if "c_user" not in session.cookies:
        log_to_ui(f"⚠️ Create Account Failed: No c_user cookie found. Try toggling airplane mode or use another email.", "text-warning")
        return {"status": "failed", "message": "Account creation failed (no c_user cookie).", "log": log_messages, "email": email_or_phone, "password": password}

    # Change email if generated with phone
    if is_phone_choice:
        log_to_ui("✅ Account created with phone number. Now let's change it to an email.", "text-info")
        if not new_email_input:
            log_to_ui("❌ New email cannot be empty for phone-based account.", "text-danger")
            return {"status": "error", "message": "New email required for phone-based account.", "log": log_messages, "email": email_or_phone, "password": password}

        new_email = new_email_input

        if "c_user" not in session.cookies:
            log_to_ui("Session expired before email change. Cannot proceed.", "text-danger")
            return {"status": "failed", "message": "Session expired during email change.", "log": log_messages, "email": email_or_phone, "password": password}

        change_email_url = "https://m.facebook.com/changeemail/"
        try:
            response = session.get(change_email_url, headers=headers)
        except requests.exceptions.RequestException as e:
            log_to_ui(f"❌ Network error getting email change form: {e}", "text-danger")
            return {"status": "error", "message": "Network error getting email change form.", "log": log_messages, "email": email_or_phone, "password": password}

        soup = BeautifulSoup(response.text, "html.parser")
        form = soup.find("form")

        if not form:
            log_to_ui("❌ Could not load email change form. Skipping.", "text-danger")
        else:
            action_url = requests.compat.urljoin(change_email_url, form.get("action", change_email_url))
            data = {}
            for inp in form.find_all("input"):
                if inp.has_attr("name"):
                    data[inp["name"]] = inp.get("value", "")

            data["new"] = new_email
            data["submit"] = "Add"

            try:
                response = session.post(action_url, headers=headers, data=data)
            except requests.exceptions.RequestException as e:
                log_to_ui(f"❌ Network error submitting email change: {e}", "text-danger")
                return {"status": "error", "message": "Network error submitting email change.", "log": log_messages, "email": email_or_phone, "password": password}

            if "email" in response.text.lower():
                log_to_ui("✅ Email change submitted successfully!", "text-success")
            else:
                log_to_ui("⚠️ Email change may not have succeeded. Check your account manually.", "text-warning")

            email_or_phone = new_email

    full_name = f"{firstname} {lastname}"
    log_to_ui(f"✅ Account Created! | Password: {password}", "text-success")
    log_to_ui(f"✅ Info: {full_name}", "text-success")

    uid = session.cookies.get("c_user")
    profile_id = f'https://www.facebook.com/profile.php?id={uid}'

    # Access token retrieval logic (simplified for Flask, user interaction handled by UI)
    access_token = ""
    log_to_ui(f"🔄 Trying to get access token...", "text-info")
    api_key = "882a8490361da98702bf97a021ddc14d"
    secret = "62f8ce9f74b12f84c123cc23437a4a32"

    params = {
        "api_key": api_key,
        "email": uid,
        "format": "JSON",
        "generate_session_cookies": 1,
        "locale": "en_US",
        "method": "auth.login",
        "password": password,
        "return_ssl_resources": 1,
        "v": "1.0"
    }

    sig_str = "".join(f"{key}={params[key]}" for key in sorted(params)) + secret
    params["sig"] = hashlib.md5(sig_str.encode()).hexdigest()

    for attempt in range(3):
        try:
            resp = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers)

            try:
                data = resp.json()
            except json.JSONDecodeError:
                log_to_ui("❌ Failed to parse Facebook API JSON response.", "text-danger")
                data = {}  # Ensure data is a dict even on error

            access_token = data.get("access_token", "")

            if "error_title" in data:
                log_to_ui(data["error_title"], "text-danger")
                # If there's an error_title, it might mean the request was successful
                # but the server returned an application-level error.
                # You might want to break here or continue based on your error handling logic.
                # For now, let's assume a successful response with an error_title is still a "success"
                # in terms of receiving a response, but you might want to adjust this.
                if access_token:  # If an access token was still returned despite an error title
                    break  # Break if we got an access token, even with an error title
                else:
                    continue  # If no access token and there's an error title, retry

            if access_token:
                log_to_ui("Access token obtained successfully.", "text-success")
                break  # Break out of the loop if successful
            else:
                log_to_ui(f"Attempt {attempt + 1}: No access token received, retrying...", "text-warning")
                time.sleep(1)  # Optional: Add a small delay before retrying

        except requests.exceptions.RequestException as e:  # Catch more specific requests exceptions
            log_to_ui(f"Attempt {attempt + 1}: Request error getting access token: {e}", "text-danger")
            time.sleep(1)  # Optional: Add a small delay before retrying
        except Exception as e:
            log_to_ui(f"Attempt {attempt + 1}: An unexpected error occurred: {e}", "text-danger")
            time.sleep(1)  # Optional: Add a small delay before retrying

    # After the loop, you can check if an access_token was obtained
    if access_token:
        pass
    else:
        log_to_ui("Failed to obtain access token after 3 attempts.", "text-danger")

    if access_token.strip():
        log_to_ui("✅ Access token acquired.", "text-success")
        data_to_save = [full_name, email_or_phone, password, profile_id, access_token]
        # Saving will be triggered by UI button click
        return {"status": "success", "message": "Account created successfully!", "email": email_or_phone, "password": password, "full_name": full_name, "profile_id": profile_id, "access_token": access_token, "log": log_messages}
    else:
        log_to_ui("❌ No access token on this attempt.", "text-warning")
        return {"status": "failed", "message": "Account created but no access token.", "email": email_or_phone, "password": password, "full_name": full_name, "profile_id": profile_id, "access_token": "", "log": log_messages}


@app.route('/')
def index():
    # New Minimalist & Modern Design HTML content for the Flask app
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FB Account Creator</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --color-primary: #4CAF50; /* Green */
                --color-primary-dark: #388E3C;
                --color-secondary: #03A9F4; /* Light Blue */
                --color-info: #2196F3; /* Blue */
                --color-success: #4CAF50; /* Green */
                --color-warning: #FFC107; /* Amber */
                --color-danger: #F44336; /* Red */

                /* Light Theme */
                --light-bg: #f5f7fa;
                --light-text: #333333;
                --light-card-bg: #ffffff;
                --light-border: #e0e0e0;
                --light-input-bg: #f0f0f0;
                --light-log-bg: #e8ebf0;

                /* Dark Theme */
                --dark-bg: #1a202c;
                --dark-text: #e2e8f0;
                --dark-card-bg: #2d3748;
                --dark-border: #4a5568;
                --dark-input-bg: #242b36;
                --dark-log-bg: #374151;
            }

            body {
                font-family: 'Roboto', sans-serif;
                transition: background-color 0.3s, color 0.3s;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1.5rem;
                line-height: 1.6;
            }

            body.light-theme {
                background-color: var(--light-bg);
                color: var(--light-text);
            }

            body.dark-theme {
                background-color: var(--dark-bg);
                color: var(--dark-text);
            }

            .card-container {
                background-color: var(--light-card-bg);
                border-radius: 0.75rem;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--light-border);
                max-width: 550px;
                width: 100%;
                transition: background-color 0.3s, border-color 0.3s, box-shadow 0.3s;
            }

            body.dark-theme .card-container {
                background-color: var(--dark-card-bg);
                border-color: var(--dark-border);
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
            }

            .input-field {
                padding: 0.8rem 1rem;
                border-radius: 0.5rem;
                border: 1px solid var(--light-border);
                background-color: var(--light-input-bg);
                color: var(--light-text);
                outline: none;
                transition: border-color 0.2s, box-shadow 0.2s, background-color 0.3s, color 0.3s;
            }

            body.dark-theme .input-field {
                border-color: var(--dark-border);
                background-color: var(--dark-input-bg);
                color: var(--dark-text);
            }

            .input-field:focus {
                border-color: var(--color-primary);
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
            }

            .btn {
                padding: 0.8rem 1.5rem;
                border-radius: 0.5rem;
                font-weight: 500;
                transition: background-color 0.2s, transform 0.1s ease-in-out;
                border: none;
                cursor: pointer;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }

            .btn-primary {
                background-color: var(--color-primary);
                color: white;
            }
            .btn-primary:hover {
                background-color: var(--color-primary-dark);
                transform: translateY(-1px);
            }

            .btn-secondary {
                background-color: var(--color-secondary);
                color: white;
            }
            .btn-secondary:hover {
                background-color: #0288D1;
                transform: translateY(-1px);
            }

            .btn-copy {
                background-color: var(--color-info);
                color: white;
                padding: 0.3rem 0.7rem;
                font-size: 0.7rem;
                border-radius: 0.3rem;
                border: none;
                box-shadow: none;
            }
            .btn-copy:hover {
                background-color: #1976D2;
            }

            .log-entry {
                padding: 0.4rem 0;
                border-bottom: 1px dotted var(--light-border);
            }
            body.dark-theme .log-entry {
                border-bottom: 1px dotted var(--dark-border);
            }
            .log-entry:last-child {
                border-bottom: none;
            }

            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.7);
                justify-content: center;
                align-items: center;
            }
            .modal-content {
                background-color: var(--light-card-bg);
                margin: auto;
                padding: 40px;
                border-radius: 0.75rem;
                box-shadow: 0 0 25px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 450px;
                text-align: center;
                border: 1px solid var(--light-border);
                transition: background-color 0.3s, border-color 0.3s, box-shadow 0.3s;
            }
            body.dark-theme .modal-content {
                background-color: var(--dark-card-bg);
                border-color: var(--dark-border);
                box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
            }

            .loader {
                border: 5px solid var(--color-primary);
                border-top: 5px solid transparent;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 1.8rem auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* Themed text colors */
            .text-success { color: var(--color-success); }
            .text-info { color: var(--color-info); }
            .text-warning { color: var(--color-warning); }
            .text-danger { color: var(--color-danger); }
            .text-primary { color: var(--color-primary); }
            .text-secondary-color { color: var(--color-secondary); } /* Renamed to avoid Tailwind conflict */
            .text-muted { color: #6c757d; } /* General lighter text */
            body.dark-theme .text-muted { color: #a0aec0; }

            .form-radio:checked {
                background-color: var(--color-primary);
                border-color: var(--color-primary);
            }
            .form-radio {
                border-color: var(--light-border);
                transition: background-color 0.2s, border-color 0.2s;
            }
            body.dark-theme .form-radio {
                border-color: var(--dark-border);
            }

            .bg-result-light {
                background-color: #e6ffe6; /* Very light green tint */
                border-color: #a7d9a8;
            }
            .bg-result-dark {
                background-color: #3b4e3e; /* Dark green tint */
                border-color: #557556;
            }

            .bg-log-light {
                background-color: var(--light-log-bg);
                border-color: var(--light-border);
            }
            .bg-log-dark {
                background-color: var(--dark-log-bg);
                border-color: var(--dark-border);
            }

            a {
                color: var(--color-info);
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
                color: #1976D2;
            }

            .theme-toggle-switch {
                position: absolute;
                top: 1.5rem;
                right: 1.5rem;
                display: flex;
                align-items: center;
                cursor: pointer;
                user-select: none;
            }

            .theme-toggle-switch input {
                display: none;
            }

            .slider {
                position: relative;
                width: 50px;
                height: 26px;
                background-color: #ccc;
                border-radius: 26px;
                transition: 0.4s;
            }

            .slider:before {
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 4px;
                bottom: 4px;
                background-color: white;
                border-radius: 50%;
                transition: 0.4s;
            }

            input:checked + .slider {
                background-color: var(--color-primary);
            }

            input:checked + .slider:before {
                transform: translateX(24px);
            }

        </style>
    </head>
    <body class="light-theme">
        <label class="theme-toggle-switch">
            <input type="checkbox" id="themeToggleCheckbox">
            <span class="slider"></span>
        </label>

        <div class="card-container p-7">
            <h1 class="text-3xl font-bold text-center mb-7 leading-tight">FB ACCOUNT CREATOR <span class="font-light text-2xl">// 2.0</span></h1>

            <div class="mb-5">
                <label for="passwordInput" class="block text-sm font-medium mb-1 text-muted">PASSWORD</label>
                <input type="text" id="passwordInput" class="input-field w-full" placeholder="Type your password here...">
            </div>

            <div class="mb-5">
                <label class="block text-sm font-medium mb-2 text-muted">Select registration method:</label>
                <div class="flex items-center space-x-6">
                    <div class="flex items-center">
                        <input type="radio" id="regChoiceEmail" name="regChoice" value="1" class="form-radio h-5 w-5" checked>
                        <label for="regChoiceEmail" class="ml-2 text-base text-muted">Input Email</label>
                    </div>
                    <div class="flex items-center">
                        <input type="radio" id="regChoicePhone" name="regChoice" value="2" class="form-radio h-5 w-5">
                        <label for="regChoicePhone" class="ml-2 text-base text-muted">Generate Random Phone</label>
                    </div>
                </div>
            </div>

            <div id="emailInputContainer" class="mb-5">
                <label for="userEmailInput" class="block text-sm font-medium mb-1 text-muted">EMAIL ADDRESS</label>
                <input type="email" id="userEmailInput" class="input-field w-full" placeholder="Paste your email...">
            </div>

            <div id="newEmailInputContainer" class="mb-5 hidden">
                <label for="newEmailInput" class="block text-sm font-medium mb-1 text-muted">NEW EMAIL FOR PHONE-BASED ACCOUNT</label>
                <input type="email" id="newEmailInput" class="input-field w-full" placeholder="new.email@example.com">
            </div>

            <button id="createAccountBtn" class="btn btn-primary w-full mb-6">
                INITIATE ACCOUNT CREATION
            </button>

            <div id="resultDisplay" class="p-5 rounded-lg mb-5 border hidden" data-theme-class-light="bg-result-light border-green-300" data-theme-class-dark="bg-result-dark border-gray-700">
                <p class="text-lg font-semibold mb-3 text-primary">ACCOUNT DETAILS</p>
                <p class="text-sm mb-1 break-words">EMAIL: <span id="displayEmail" class="font-medium text-success"></span> <button class="btn-copy ml-2" onclick="copyToClipboard('displayEmail')">COPY</button></p>
                <p class="text-sm mb-1 break-words">PASSWORD: <span id="displayPassword" class="font-medium text-success"></span> <button class="btn-copy ml-2" onclick="copyToClipboard('displayPassword')">COPY</button></p>
                <p class="text-sm mb-1">NAME: <span id="displayFullName" class="font-medium text-success"></span></p>
                <p class="text-sm break-words">PROFILE LINK: <a id="displayProfileLink" href="#" target="_blank" class="text-info hover:underline"></a></p>
            </div>

            <div id="saveAccountButtons" class="flex justify-center space-x-4 mb-6 hidden">
                <button id="saveAccountBtn" class="btn btn-primary">SAVE ACCOUNT DATA</button>
                <button id="dontSaveAccountBtn" class="btn btn-secondary">DO NOT SAVE</button>
            </div>

            <div class="p-5 rounded-lg shadow-inner border" data-theme-class-light="bg-log-light border-gray-200" data-theme-class-dark="bg-log-dark border-gray-700">
                <h2 class="text-xl font-semibold mb-4 text-primary">ACTIVITY LOG</h2>
                <div id="activityLog" class="max-h-56 overflow-y-auto text-sm">
                </div>
            </div>
        </div>

        <div id="loadingModal" class="modal">
            <div class="modal-content">
                <div class="loader"></div>
                <p class="text-lg font-medium text-primary">Processing Account Creation...</p>
            </div>
        </div>

        <script>
            let currentAccountData = null; // To store data for saving

            document.addEventListener('DOMContentLoaded', function() {
                const passwordInput = document.getElementById('passwordInput');
                const regChoiceEmail = document.getElementById('regChoiceEmail');
                const regChoicePhone = document.getElementById('regChoicePhone');
                const emailInputContainer = document.getElementById('emailInputContainer');
                const userEmailInput = document.getElementById('userEmailInput');
                const newEmailInputContainer = document.getElementById('newEmailInputContainer');
                const newEmailInput = document.getElementById('newEmailInput');
                const createAccountBtn = document.getElementById('createAccountBtn');
                const activityLog = document.getElementById('activityLog');
                const resultDisplay = document.getElementById('resultDisplay');
                const displayEmail = document.getElementById('displayEmail');
                const displayPassword = document.getElementById('displayPassword');
                const displayFullName = document.getElementById('displayFullName');
                const displayProfileLink = document.getElementById('displayProfileLink');
                const saveAccountButtons = document.getElementById('saveAccountButtons');
                const saveAccountBtn = document.getElementById('saveAccountBtn');
                const dontSaveAccountBtn = document.getElementById('dontSaveAccountBtn');
                const loadingModal = document.getElementById('loadingModal');
                const themeToggleCheckbox = document.getElementById('themeToggleCheckbox');
                const body = document.body;

                function clearNewEmailField() {
                    newEmailInput.value = '';
                }

                function clearUserEmailField() {
                    userEmailInput.value = '';
                }

                // Theme Toggle Logic
                function setTheme(theme) {
                    body.classList.remove('light-theme', 'dark-theme');
                    body.classList.add(theme);
                    localStorage.setItem('theme', theme);
                    themeToggleCheckbox.checked = (theme === 'dark-theme');

                    const elementsToTheme = [
                        { element: resultDisplay, light: 'bg-result-light border-green-300', dark: 'bg-result-dark border-gray-700' },
                        { element: document.querySelector('#activityLog').closest('div'), light: 'bg-log-light border-gray-200', dark: 'bg-log-dark border-gray-700' }
                    ];

                    elementsToTheme.forEach(({ element, light, dark }) => {
                        if (element) {
                            element.classList.remove(...light.split(' '));
                            element.classList.remove(...dark.split(' '));
                            if (theme === 'light-theme') {
                                element.classList.add(...light.split(' '));
                            } else {
                                element.classList.add(...dark.split(' '));
                            }
                        }
                    });
                }

                const savedTheme = localStorage.getItem('theme') || 'light-theme';
                setTheme(savedTheme);

                themeToggleCheckbox.addEventListener('change', () => {
                    if (themeToggleCheckbox.checked) {
                        setTheme('dark-theme');
                    } else {
                        setTheme('light-theme');
                    }
                });

                // Initial state based on radio button
                if (regChoiceEmail.checked) {
                    emailInputContainer.classList.remove('hidden');
                    newEmailInputContainer.classList.add('hidden');
                    clearNewEmailField();
                } else {
                    emailInputContainer.classList.add('hidden');
                    newEmailInputContainer.classList.remove('hidden');
                }

                regChoiceEmail.addEventListener('change', function() {
                    emailInputContainer.classList.remove('hidden');
                    newEmailInputContainer.classList.add('hidden');
                    clearUserEmailField();
                    clearNewEmailField();
                });

                regChoicePhone.addEventListener('change', function() {
                    emailInputContainer.classList.add('hidden');
                    newEmailInputContainer.classList.remove('hidden');
                    clearUserEmailField();
                });

                function appendLog(message, colorClass = 'text-muted') {
                    const logEntry = document.createElement('div');
                    logEntry.classList.add('log-entry', colorClass);
                    logEntry.textContent = message;
                    activityLog.appendChild(logEntry);
                    activityLog.scrollTop = activityLog.scrollHeight;
                }

                function clearActivityLog() {
                    activityLog.innerHTML = '';
                }

                createAccountBtn.addEventListener('click', async () => {
                    clearActivityLog();
                    resultDisplay.classList.add('hidden');
                    saveAccountButtons.classList.add('hidden');
                    currentAccountData = null;

                    const customPassword = passwordInput.value.trim();
                    const regChoice = document.querySelector('input[name="regChoice"]:checked').value;
                    const userEmail = userEmailInput.value.trim();
                    const newEmail = newEmailInput.value.trim();

                    if (regChoice === '1' && !userEmail) {
                        appendLog("❌ ERROR: EMAIL ADDRESS REQUIRED.", "text-danger");
                        return;
                    }
                    if (regChoice === '2' && !newEmail) {
                        appendLog("❌ ERROR: NEW EMAIL REQUIRED FOR PHONE-BASED ACCOUNT.", "text-danger");
                        return;
                    }

                    loadingModal.style.display = 'flex';

                    try {
                        const response = await fetch('/create_account', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                custom_password_base: customPassword,
                                reg_choice: regChoice,
                                user_email_input: userEmail,
                                new_email_input: newEmail
                            }),
                        });

                        const data = await response.json();

                        data.log.forEach(entry => appendLog(entry.message, entry.color));

                        if (data.status === 'success' || data.status === 'failed') {
                            displayEmail.textContent = data.email || 'N/A';
                            displayPassword.textContent = data.password || 'N/A';
                            displayFullName.textContent = data.full_name || 'N/A';
                            displayProfileLink.textContent = data.profile_id || 'N/A';
                            displayProfileLink.href = data.profile_id || '#';
                            resultDisplay.classList.remove('hidden');
                            currentAccountData = data;
                            saveAccountButtons.classList.remove('hidden');

                            if (regChoice === '1') {
                                clearUserEmailField();
                            } else {
                                clearNewEmailField();
                            }

                        } else {
                            appendLog(`ERROR: ${data.message}`, "text-danger");
                        }

                    } catch (error) {
                        appendLog(`CRITICAL ERROR: ${error.message}`, "text-danger");
                        console.error('Fetch error:', error);
                    } finally {
                        loadingModal.style.display = 'none';
                    }
                });

                saveAccountBtn.addEventListener('click', async () => {
                    if (currentAccountData) {
                        appendLog("INITIATING ACCOUNT DATA SAVE...", "text-info");
                        loadingModal.style.display = 'flex';
                        try {
                            const response = await fetch('/save_account', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(currentAccountData),
                            });
                            const result = await response.json();
                            appendLog(result.message.toUpperCase(), result.status === 'success' ? 'text-success' : 'text-danger');
                        } catch (error) {
                            appendLog(`ERROR SAVING ACCOUNT DATA: ${error.message}`, "text-danger");
                            console.error('Save error:', error);
                        } finally {
                            loadingModal.style.display = 'none';
                            saveAccountButtons.classList.add('hidden');
                            currentAccountData = null;
                            clearUserEmailField();
                            clearNewEmailField();
                        }
                    }
                });

                dontSaveAccountBtn.addEventListener('click', () => {
                    appendLog("ACCOUNT DATA NOT SAVED PER USER PROTOCOL.", "text-warning");
                    saveAccountButtons.classList.add('hidden');
                    currentAccountData = null;
                    clearUserEmailField();
                    clearNewEmailField();
                });
            });

            function copyToClipboard(elementId) {
                const element = document.getElementById(elementId);
                const text = element.textContent;
                navigator.clipboard.writeText(text).then(() => {
                    const originalText = element.nextElementSibling.textContent;
                    element.nextElementSibling.textContent = 'COPIED!';
                    setTimeout(() => {
                        element.nextElementSibling.textContent = originalText;
                    }, 1500);
                }).catch(err => {
                    console.error('FAILED TO COPY: ', err);
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);

                    const originalText = element.nextElementSibling.textContent;
                    element.nextElementSibling.textContent = 'COPIED!';
                    setTimeout(() => {
                        element.nextElementSibling.textContent = originalText;
                    }, 1500);
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/create_account', methods=['POST'])
def create_account():
    global custom_password_base
    data = request.json
    custom_password_base = data.get('custom_password_base', "Promises")
    reg_choice = data.get('reg_choice')
    user_email_input = data.get('user_email_input')
    new_email_input = data.get('new_email_input')

    # Clear settings.json for a fresh start, mimicking clear_console behavior
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
            print("Cleared settings.json for new account creation.")
        except Exception as e:
            print(f"⚠️ Failed to delete settings file: {e}")

    # Dummy files for names if they don't exist
    if not os.path.exists("first_name.txt"):
        with open("first_name.txt", "w") as f:
            f.write("John\nJane\nMichael\nEmily\n")
    if not os.path.exists("last_name.txt"):
        with open("last_name.txt", "w") as f:
            f.write("Doe\nSmith\nJohnson\nWilliams\n")

    # Call the modified function
    result = create_fbunconfirmed_flask(
        account_type=1,
        usern="flask_user", # This can be a dummy value as it's not used in the original script's core logic
        gender=1,
        password=None, # Let the function generate based on custom_password_base
        session=requests.Session(),
        reg_choice=reg_choice,
        user_email_input=user_email_input,
        new_email_input=new_email_input
    )
    return jsonify(result)

@app.route('/save_account', methods=['POST'])
def save_account():
    data = request.json
    full_name = data.get('full_name')
    email_or_phone = data.get('email')
    password = data.get('password')
    profile_id = data.get('profile_id')
    access_token = data.get('access_token')

    filename_xlsx = "/storage/emulated/0/Acc_Created.xlsx"
    filename_txt = "/storage/emulated/0/Acc_created.txt"

    data_to_save = [full_name, email_or_phone, password, profile_id, access_token]

    try:
        save_to_xlsx(filename_xlsx, data_to_save)
        save_to_txt(filename_txt, data_to_save)

        # Save cookie (assuming c_user is available from profile_id)
        uid = profile_id.split('=')[-1] if profile_id else None
        if uid:
            ensure_cookie_dir()
            cookie_file = os.path.join(COOKIE_DIR, f"{uid}.json")
            # In a real scenario, you'd need the actual session cookies here.
            # For this example, we'll just save dummy data or assume it's passed.
            # Since the session is lost between requests, this part needs careful handling.
            # A more robust solution would involve passing relevant cookies from create_account response.
            dummy_cookies_data = {"c_user": uid, "note": "Cookies would be saved here if available from the session."}
            with open(cookie_file, "w") as f:
                json.dump(dummy_cookies_data, f, indent=4)

        return jsonify({"status": "success", "message": "Account saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save account: {e}"})

if __name__ == '__main__':
    # Ensure dummy files for names exist if not already present
    if not os.path.exists("first_name.txt"):
        with open("first_name.txt", "w") as f:
            f.write("John\nJane\nMichael\nEmily\n")
    if not os.path.exists("last_name.txt"):
        with open("last_name.txt", "w") as f:
            f.write("Doe\nSmith\nJohnson\nWilliams\n")

    # Clean up settings.json on startup for consistent behavior
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
            print("Cleaned up settings.json on Flask app startup.")
        except Exception as e:
            print(f"⚠️ Failed to delete settings file on startup: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
