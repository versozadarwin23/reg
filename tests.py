import string
from openpyxl import Workbook, load_workbook
import os
import requests
from bs4 import BeautifulSoup
import time
import random

os.system("clear")

# 🎯 STEP 1: Mag-generate ng random username
rchjtrchjb = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
email_address = f"{rchjtrchjb}@harakirimail.com"
drtyghbj5hgcbv = f"https://harakirimail.com/inbox/{rchjtrchjb}"

windows_headers = {
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Referer': 'https://m.facebook.com/',
    'Content-Type': 'application/x-www-form-urlencoded'
}


def save_to_xlsx(filename, data):
    while True:
        try:
            if os.path.exists(filename):
                wb = load_workbook(filename)
                ws = wb.active
            else:
                wb = Workbook()
                ws = wb.active
                ws.append(['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK'])
            ws.append(data)
            wb.save(filename)
            break
        except Exception as e:
            print(f"Error saving to {filename}: {e}. Retrying...")


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
    if account_type == 1:
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
    number = f"9{third}{forth}{random_number}"
    return number


def generate_random_password():
    base = 'Promises'
    six_digit = str(random.randint(100000, 999999))
    return base + six_digit


def generate_user_details(account_type, gender, password=None):
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    if password is None:
        password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password


custom_password_base = None


def create_fbunconfirmed(account_type, usern, gender, password=None, session=None):
    global custom_password_base, profile_id
    if password is None:
        if custom_password_base:
            six_digit = str(random.randint(100000, 999999))
            password = custom_password_base + six_digit
        else:
            password = generate_random_password()

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
                print('😢 No internet. Check data or toggle airplane mode.')

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

    if session is None:
        session = requests.Session()

    while True:
        form = check_page_loaded(url, headers)
        if form:
            break

    while True:
        try:
            response = session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")
            break
        except:
            pass

    if form:
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
                data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

        response = session.post(action_url, headers=headers, data=data)

        if "c_user" not in session.cookies:
            print("\033[1;91m⚠️ Create Account Failed. Try toggling airplane mode or use another email.\033[0m")
            time.sleep(3)
            return

        uid = session.cookies.get("c_user")
        profile_id = f'https://www.facebook.com/profile.php?id={uid}'

        form = soup.find('form', action=lambda x: x and 'checkpoint' in x)
        if form:
            print("\033[1;91m⚠️ Created account blocked. Try toggling airplane mode or clearing Facebook Lite data.\033[0m")
            time.sleep(3)
            os.system("clear")
            return

        os.system("clear")
        # 🎯 STEP 2: Maghintay sa subject
        found = False
        while True:
            try:
                dtryvghjuijhn = requests.get(drtyghbj5hgcbv, timeout=30)
                dtryvghjuijhn.raise_for_status()

                soup = BeautifulSoup(dtryvghjuijhn.text, "html.parser")
                table = soup.find("table", class_="table table-hover table-striped")

                if table:
                    subject_link = table.find("tbody", id="mail_list_body").find("a") if table.find("tbody",
                                                                                                    id="mail_list_body") else None
                    if subject_link:
                        subject_div = subject_link.find("div") if subject_link else None
                        if subject_div:
                            subject = subject_div.get_text(strip=True)
                            jbkj = subject.replace(" is your confirmation code",'')

                            if jbkj:
                                break

            except Exception as e:
                print(f"❗ Error sa request: {e}")

            time.sleep(5)
        print(f"\033[1;92m✅ Email: {email_address} | Pass: {password} | {jbkj}\033[0m")

        while True:
            try:
                user_input = input("Type 'b' if blocked, or press Enter to continue: ")
                if user_input.lower() == 'b':
                    print("\033[1;91m⚠️ Creating another account because the last one was blocked.\033[0m")
                    time.sleep(3)
                    os.system("clear")
                    return
                break
            except:
                pass

        filename = "/storage/emulated/0/Acc_Created.xlsx"
        full_name = f"{firstname} {lastname}"
        data_to_save = [full_name, email_address, password, profile_id]
        save_to_xlsx(filename, data_to_save)
        os.system("clear")
        print(f"\033[1;92m✅ Account saved: {firstname} {lastname} | Pass: {password}\033[0m")
        time.sleep(3)


def NEMAIN():
    os.system("clear")
    max_create = 1
    account_type = 1
    gender = 1
    session = requests.Session()

    global custom_password_base
    if custom_password_base is None:
        inp = 'promises'
        custom_password_base = inp if inp else "promises"

    for i in range(max_create):
        usern = "ali"
        create_fbunconfirmed(account_type, usern, gender, session=session)


if __name__ == "__main__":
    while True:
        NEMAIN()
