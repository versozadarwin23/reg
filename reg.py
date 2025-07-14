from flask import Flask, render_template_string, request, jsonify
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

app = Flask(__name__)

# --- Original reg.py functions (modified for Flask context) ---

COOKIE_DIR = "/storage/emulated/0/cookie"  # Keep original cookie directory
CONFIG_FILE = "/storage/emulated/0/settings.json"  # Keep original settings file for choices


def random_device_model():
    models = [
        "Google-Pixel-7",
        "Google-Pixel-6a",
        "Google-Pixel-5"
    ]
    return random.choice(models)


def random_device_id():
    ids = [
        "15526637-0441-2553-4664-888888888048",
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
    "Mozilla/5.0 (Linux; Android 10; SM-A908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/300.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 11; Google Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/301.0.0.0.0;]",
    "Mozilla/5.0 (Linux; Android 12; SM-G990U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/302.0.0.0.0;]"
]


def delete_config_file():
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
            print("Settings file deleted on exit.")
        except Exception as e:
            print(f"⚠️ Failed to delete settings file: {e}")


atexit.register(delete_config_file)


def save_user_choice(key, value):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
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
        except json.JSONDecodeError:
            return None


def clear_console():
    # Not relevant for Flask web interface
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
    # This assumes first_name.txt and last_name.txt are in the same directory as the script
    script_dir = os.path.dirname(__file__)
    full_file_path = os.path.join(script_dir, file_path)
    try:
        with open(full_file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: {full_file_path} not found. Please ensure name files are present.")
        return ["Unknown"]  # Provide a fallback to prevent errors


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
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    if password is None:
        password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password


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


# Global variable to store results to be displayed in the log
# This is a simple approach; for production, consider a database or more robust state management
current_results_log = []

# Pass `results_callback` to send updates to the Flask app
def create_fbunconfirmed(account_type, usern, gender, password=None, session=None, reg_choice=None, custom_email=None,
                         results_callback=None):
    agent = random.choice(ua)

    if password is None:
        password = generate_random_password()

    firstname, lastname, date, year, month, phone_number, used_password = generate_user_details(account_type, gender,
                                                                                                password)

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
                response = session.get(url, headers=headers, timeout=60)
                soup = BeautifulSoup(response.text, "html.parser")
                form = soup.find("form")
                if form:
                    return form, response.text
            except requests.exceptions.RequestException as e:
                results_callback(f"😢 Failed to connect to network: {e}. Retrying...", "error")
                time.sleep(3)

    form, initial_response_text = get_registration_form()

    is_phone_choice = (reg_choice == '2')
    email_or_phone = ""

    if reg_choice == '1':  # Enter Email
        email_or_phone = custom_email
        if not email_or_phone:
            results_callback("❌ Email cannot be empty. Aborting.", "error")
            return "FAILED_INVALID_EMAIL"
    else:  # Use Random Phone Number
        email_or_phone = phone_number

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
            response = session.post(action_url, headers=headers, data=data, timeout=60)
        except requests.exceptions.RequestException as e:
            results_callback(f"😢 Failed to post registration data: {e}. Aborting.", "error")
            return "FAILED_POST"
    else:
        results_callback("❌ Could not find registration form. Aborting.", "error")
        return "FAILED_NO_FORM"

    if "c_user" not in session.cookies:
        results_callback(f"⚠️ Create Account Failed. No c_user cookie found. Try again or use another email/phone.",
                         "error")
        return "FAILED_NO_C_USER"

    # Change email if generated with phone
    if is_phone_choice:
        # Ensure that `custom_email` is available and not empty for the change
        if not custom_email:
            results_callback("❌ New email cannot be empty for email change. Skipping email change.", "error")
        else:
            new_email = custom_email  # Use the custom_email provided in the form

            if "c_user" not in session.cookies:
                results_callback("Session expired or invalid, cannot change email.", "error")
                return

            change_email_url = "https://m.facebook.com/changeemail/"
            try:
                response = session.get(change_email_url, headers=headers, timeout=60)
            except requests.exceptions.RequestException as e:
                results_callback(f"❌ Error getting email change form: {e}. Skipping.", "error")
                # break Removed break as it was in a while True loop that is now removed.

            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")

            if not form:
                results_callback("❌ Could not load email change form. Skipping.", "error")
                # break Removed break as it was in a while True loop that is now removed.
            else:
                action_url = requests.compat.urljoin(change_email_url, form.get("action", change_email_url))
                data = {}
                for inp in form.find_all("input"):
                    if inp.has_attr("name"):
                        data[inp["name"]] = inp.get("value", "")

                data["new"] = new_email
                data["submit"] = "Add"

                try:
                    response = session.post(action_url, headers=headers, data=data, timeout=60)
                except requests.exceptions.RequestException as e:
                    results_callback(f"❌ Error submitting email change: {e}. Skipping.", "error")
                    # break Removed break as it was in a while True loop that is now removed.

                if "email" in response.text.lower():
                    results_callback(f"✅ Email: {custom_email}", "success", email=custom_email)
                else:
                    results_callback("⚠️ Email change may not have succeeded. Check your account manually.", "warning")

                email_or_phone = new_email

    full_name = f"{firstname} {lastname}"
    results_callback(f"Account Created | Password: {password}", "success", password=password)
    results_callback(f"Info | Full Name: {full_name}", "success")

    uid = session.cookies.get("c_user")
    profile_id = f'https://www.facebook.com/profile.php?id={uid}'
    filename_xlsx = "/storage/emulated/0/Acc_Created.xlsx"
    filename_txt = "/storage/emulated/0/Acc_created.txt"

    if has_access_token_in_xlsx(filename_xlsx, email_or_phone):
        results_callback("Account already saved with an access token.", "info")
        return "ALREADY_SAVED"

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

    access_token = ""
    try:
        resp = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers, timeout=60)
        data = resp.json()
        access_token = data.get("access_token", "")
        if "error_title" in data:
            results_callback(f"Facebook API Error: {data['error_title']}", "error")
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        results_callback(f"Error getting access token from API: {e}", "error")

    if access_token.strip():
        data_to_save = [full_name, email_or_phone, password, profile_id, access_token]
        save_to_xlsx(filename_xlsx, data_to_save)
        save_to_txt(filename_txt, data_to_save)

        # Save cookies
        ensure_cookie_dir()
        cookie_file = os.path.join(COOKIE_DIR, f"{uid}.json")
        cookie_names = ["c_user", "datr", "fr", "noscript", "sb", "xs"]
        cookies_data = {name: session.cookies.get(name, "") for name in cookie_names}
        try:
            with open(cookie_file, "w", encoding="utf-8") as f:
                json.dump(cookies_data, f, indent=4)
        except IOError as e:
            results_callback(f"❌ Failed to save cookie file: {e}", "error")

    else:
        results_callback("❌ No access token acquired on this attempt.", "warning")
        results_callback("Manual intervention (like airplane mode toggle) might be needed for access token.", "info")

    # Attempt to log out
    if response and response.text:
        soup = BeautifulSoup(response.text, "html.parser")
        logout_link = soup.find("a", href=lambda href: href and "/logout.php" in href)
        if logout_link:
            logout_url = requests.compat.urljoin("https://m.facebook.com/", logout_link["href"])
            try:
                session.get(logout_url, headers=headers, timeout=30)
            except requests.exceptions.RequestException as e:
                results_callback(f"❌ Failed to log out: {e}", "warning")
    return "SUCCESS"


# --- Flask Application Routes and HTML ---

@app.route("/", methods=["GET", "POST"])
def index():
    global current_results_log # Declare as global to modify the list

    def append_result(message, type="info", password=None, email=None):
        result_item = {"message": message, "type": type}
        if password:
            result_item["password"] = password
        if email:
            result_item["email"] = email
        current_results_log.append(result_item) # Append to the global log

    if request.method == "POST":
        custom_password_base = request.form.get("password_base", "Promises")
        reg_choice = request.form.get("reg_choice", "2")  # Default to phone number
        gender = request.form.get("gender", "1")  # Default to male (assuming 1 is male)
        custom_email = request.form.get("email_input", "").strip()

        # Server-side validation for email if "Enter Email" is chosen or if phone-registered needs email change
        if reg_choice == '1' and not custom_email:
            append_result("Please provide an email address when 'Enter Email' is selected.", "error")
            max_create = 0  # Prevent account creation
        elif reg_choice == '2' and not custom_email:
            append_result(
                "Please provide an email address in the 'Custom Email' field. This will be used to change the email after phone registration.",
                "warning")
            # Do not set max_create to 0 here, but the email change will fail later.

        try:
            max_create = 1
        except ValueError:
            append_result("Invalid number of accounts. Please enter a valid number.", "error")
            max_create = 0

        if max_create > 0:
            append_result(f"Starting account creation for {max_create} account(s)...", "info")
            for i in range(max_create):
                append_result(f"--- Creating account {i + 1}/{max_create} ---", "info")
                session = requests.Session()
                # Pass custom_email and reg_choice from form
                generated_password = custom_password_base + str(random.randint(100000, 999999))
                status = create_fbunconfirmed(1, "ali", int(gender),
                                              password=generated_password,
                                              session=session, reg_choice=reg_choice, custom_email=custom_email,
                                              results_callback=append_result)
                append_result(f"Account creation finished with status: {status}", "info")
                # Small delay between creations
                time.sleep(random.uniform(2, 5))
            append_result("All account creation attempts completed.", "success")
        else:
            append_result("No accounts to create or validation failed.", "info")

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Account Creator</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                color: #1c1e21;
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .container {
                background-color: #fff;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 600px;
                margin-bottom: 20px;
            }
            h1 {
                color: #1877f2;
                text-align: center;
                margin-bottom: 25px;
            }
            form {
                display: flex;
                flex-direction: column;
            }
            label {
                margin-bottom: 8px;
                font-weight: bold;
                color: #606770;
            }
            input[type="text"],
            input[type="number"],
            input[type="email"],
            select {
                padding: 12px;
                margin-bottom: 20px;
                border: 1px solid #dddfe2;
                border-radius: 6px;
                font-size: 1rem;
                width: calc(100% - 24px);
            }
            input[type="radio"] {
                margin-right: 5px;
            }
            .radio-group {
                margin-bottom: 20px;
            }
            .radio-group label {
                margin-right: 15px;
                font-weight: normal;
            }
            button {
                background-color: #42b72a;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 1.1rem;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #36a420;
            }
            .results-box {
                background-color: #e9ebee;
                border: 1px solid #ccd0d5;
                border-radius: 8px;
                padding: 20px;
                width: 100%;
                max-width: 600px;
                max-height: 400px;
                overflow-y: auto;
            }
            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .results-header h2 {
                margin: 0;
            }
            .clear-button {
                background-color: #f02849;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 6px;
                font-size: 0.9rem;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .clear-button:hover {
                background-color: #d1213f;
            }
            .result-item {
                padding: 8px 0;
                border-bottom: 1px dashed #c0c0c0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap; /* Allow items to wrap */
            }
            .result-item span {
                flex-grow: 1; /* Allow message to take available space */
            }
            .result-item:last-child {
                border-bottom: none;
            }
            .result-item.info { color: #1877f2; }
            .result-item.success { color: #42b72a; font-weight: bold; }
            .result-item.warning { color: #f2c200; }
            .result-item.error { color: #eb4d4b; font-weight: bold; }
            #emailInputContainer {
                display: none; /* Hidden by default */
            }
            .copy-button {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                cursor: pointer;
                margin-left: 10px;
                font-size: 0.85rem;
                transition: background-color 0.2s ease;
            }
            .copy-button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Facebook Account Creator By Dars: V1</h1>
            <form method="POST" onsubmit="changeButtonText()">
                <label for="password_base">Password: </label>
                <input type="text" id="password_base" name="password_base" placeholder="Type your Password: ">

                <label>Registration Method:</label>
                <div class="radio-group">
                    <input type="radio" id="reg_email" name="reg_choice" value="1" onclick="toggleEmailInput()">
                    <label for="reg_email">Enter Email</label>
                    <input type="radio" id="reg_phone" name="reg_choice" value="2" checked onclick="toggleEmailInput()">
                    <label for="reg_phone">Use Random Phone Number</label>
                </div>

                <div id="emailInputContainer">
                    <label for="email_input">Email Address: </label>
                    <input type="email" id="email_input" name="email_input" placeholder="e.g., your_email@example.com">
                </div>

                <label for="gender">Gender:</label>
                <select id="gender" name="gender">
                    <option value="1">Male</option>
                    <option value="2">Female</option>
                </select>

                <button type="submit" id="start_button">Start Creating Accounts</button>
            </form>
        </div>

        <div class="results-box">
            <div class="results-header">
                <h2>Activity Log</h2>
                <button class="clear-button" onclick="clearActivityLog()">Clear Log</button>
            </div>
            <div id="results">
                {% for result in results %}
                    <p class="result-item {{ result.type }}">
                        <span>{{ result.message }}</span>
                        {% if result.password %}
                            <button class="copy-button" onclick="copyToClipboard('{{ result.password }}', this)">Copy Password</button>
                        {% endif %}
                        {% if result.email %}
                            <button class="copy-button" onclick="copyToClipboard('{{ result.email }}', this)">Copy Email</button>
                        {% endif %}
                    </p>
                {% endfor %}
            </div>
        </div>

        <script>
            function toggleEmailInput() {
                var emailRadio = document.getElementById('reg_email');
                var emailInput = document.getElementById('email_input');
                var emailInputContainer = document.getElementById('emailInputContainer');

                if (emailRadio.checked) {
                    emailInputContainer.style.display = 'block';
                    emailInput.setAttribute('required', 'required'); // Make it required
                    emailInput.placeholder = 'Paste your Email: ';
                } else {
                    emailInputContainer.style.display = 'block'; // Keep visible but not required
                    emailInput.removeAttribute('required'); // Not strictly required but highly recommended
                    emailInput.placeholder = 'Paste your Email: ';
                }
            }

            function copyToClipboard(text, buttonElement) {
                navigator.clipboard.writeText(text).then(function() {
                    var originalText = buttonElement.innerText;
                    buttonElement.innerText = 'Copied!';
                    setTimeout(function() {
                        buttonElement.innerText = originalText;
                    }, 2000);
                }).catch(function(err) {
                    console.error('Could not copy text: ', err);
                    alert('Failed to copy. Please copy manually: ' + text);
                });
            }

            function changeButtonText() {
                var submitButton = document.getElementById('start_button');
                submitButton.innerText = 'Creating your account. Please be patient';
                // You might also want to disable the button to prevent multiple submissions
                submitButton.disabled = true;
            }

            function clearActivityLog() {
                fetch('/clear_log', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('results').innerHTML = '<p class="result-item info"><span>Activity log cleared.</span></p>';
                    } else {
                        alert('Failed to clear activity log: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while clearing the log.');
                });
            }

            // Call on page load to set initial state
            document.addEventListener('DOMContentLoaded', toggleEmailInput);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content, results=current_results_log)

@app.route("/clear_log", methods=["POST"])
def clear_log():
    global current_results_log
    current_results_log = [] # Clear the global list
    return jsonify({"status": "success", "message": "Activity log cleared."})


if __name__ == "__main__":
    if not os.path.exists("first_name.txt"):
        with open("first_name.txt", "w") as f:
            f.write("John\nJane\nMichael\nEmily\n")
            print("Created placeholder 'first_name.txt'. Please populate it with names.")
    if not os.path.exists("last_name.txt"):
        with open("last_name.txt", "w") as f:
            f.write("Smith\nJohnson\nWilliams\nBrown\n")
            print("Created placeholder 'last_name.txt'. Please populate it with names.")

    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
            print("Removed existing settings.json on startup.")
        except Exception as e:
            print(f"Warning: Could not remove settings.json on startup: {e}")

    # To suppress the default Flask message, set `debug=False` and `use_reloader=False`
    # Then print your custom message.
    print("copy this paste to google chrome:  |  http://127.0.0.1:5000   |")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
