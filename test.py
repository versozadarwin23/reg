import csv
import os
import requests
from bs4 import BeautifulSoup
import random
import string
from multiprocessing.dummy import Pool as ThreadPool  # Using threads instead of processes!

def load_names_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def get_names(account_type, gender):
    male_first_names = load_names_from_file("first_name.txt")
    last_names = load_names_from_file("last_name.txt")
    firstname = random.choice(male_first_names)
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
    symbols = '!@#$%^&*()_+-='
    extra = random.choice(symbols)
    password = base + extra + six_digit
    return password

def generate_user_details(account_type, gender):
    firstname, lastname = get_names(account_type, gender)
    year = random.randint(1978, 2001)
    date = random.randint(1, 28)
    month = random.randint(1, 12)
    password = generate_random_password()
    phone_number = generate_random_phone_number()
    return firstname, lastname, date, year, month, phone_number, password

def save_to_csv(filename, data):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(filename) == 0:
            writer.writerow(['NAME', 'USERNAME', 'PASSWORD', 'ACCOUNT LINK'])
        writer.writerow(data)

def create_fbunconfirmed(args):
    account_type, gender, email = args
    firstname, lastname, date, year, month, phone_number, password = generate_user_details(account_type, gender)

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36 [FBAN/EMA;FBLC/en_US;FBAV/444.0.0.0.110;]'
    }

    url = "https://m.facebook.com/reg"
    try:
        response = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find("form")
        if not form:
            print(f"[THREAD] ⚠️ Form not found. Skipping.")
            return
        action_url = requests.compat.urljoin(url, form["action"])
        inputs = form.find_all("input")
        data = {
            "firstname": firstname,
            "lastname": lastname,
            "birthday_day": str(date),
            "birthday_month": str(month),
            "birthday_year": str(year),
            "reg_email__": email,
            "sex": str(gender),
            "encpass": password,
            "submit": "Sign Up"
        }
        for inp in inputs:
            if inp.has_attr("name") and inp["name"] not in data:
                data[inp["name"]] = inp["value"] if inp.has_attr("value") else ""

        post_response = session.post(action_url, headers=headers, data=data, timeout=10)
        if "c_user" in session.cookies:
            uid = session.cookies.get("c_user")
            profile_link = f"https://m.facebook.com/profile.php?id={uid}"
            full_name = f"{firstname} {lastname}"
            save_to_csv("/storage/emulated/0/Acc_Created.csv", [full_name, email, password, profile_link])
            print(f"[THREAD] ✅ Account created: {full_name} | {email} | {password}")
        else:
            print(f"[THREAD] ⚠️ Failed to create account.")
    except Exception as e:
        print(f"[THREAD] ❌ Error: {str(e)}")

    confimation_code = 'https://www.facebook.com/confirmemail.php'
    # Step 1: GET the form page first to get hidden inputs (like fb_dtsg and jazoest)
    response = session.get(confimation_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract hidden inputs
    form = soup.find('form', name='code')
    hidden_inputs = form.find_all('input', type='hidden')

    post_data = {}
    for hidden_input in hidden_inputs:
        post_data[hidden_input['name']] = hidden_input['value']

    # Add the confirmation code (the 5-digit code you received)
    confirmation_codes = "12345"  # replace with your actual code
    post_data['code'] = confirmation_codes

    # Add the other inputs (confirm button is disabled, so no need to include it)

    # Step 2: POST the data
    post_response = session.post(confimation_code, data=post_data)

    print(post_response.status_code)
    print(post_response.text)  # to check if submission was successful or if there's an error

def main():
    os.system("clear")
    email = input("Enter your email (same for all threads): ").strip()
    account_type = 1
    gender = 1

    # Prepare args for 5 threads
    worker_args = [(account_type, gender, email) for _ in range(5)]

    with ThreadPool(5) as pool:  # Using threads to avoid Termux multiprocessing issues!
        pool.map(create_fbunconfirmed, worker_args)

if __name__ == "__main__":
    main()
