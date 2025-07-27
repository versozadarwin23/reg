import requests, random, json, hashlib, uuid, time

# ANSI escape codes for colors
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_YELLOW = '\033[93m'
COLOR_CYAN = '\033[96m'  # New color for exit message
COLOR_RESET = '\033[0m'  # Resets the color to default


def Login(email: str, password: str):
    r = requests.Session()

    # Define headers
    head = {
        'Host': 'b-graph.facebook.com',
        'X-Fb-Connection-Quality': 'EXCELLENT',
        'Authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; RMX3740 Build/QP1A.190711.020) [FBAN/FB4A;FBAV/417.0.0.33.65;FBPN/com.facebook.katana;FBLC/in_ID;FBBV/480086274;FBCR/Corporation Tbk;FBMF/realme;FBBD/realme;FBDV/RMX3740;FBSV/7.1.2;FBCA/x86:armeabi-v7a;FBDM/{density=1.0,width=540,height=960};FB_FW/1;FBRV/483172840;]',
        'X-Tigon-Is-Retry': 'false',
        'X-Fb-Friendly-Name': 'authenticate',
        'X-Fb-Connection-Bandwidth': str(random.randrange(70000000, 80000000)),
        'Zero-Rated': '0',
        'X-Fb-Net-Hni': str(random.randrange(50000, 60000)),
        'X-Fb-Sim-Hni': str(random.randrange(50000, 60000)),
        'X-Fb-Request-Analytics-Tags': '{"network_tags":{"product":"350685531728","retry_attempt":"0"},"application_tags":"unknown"}',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Fb-Connection-Type': 'WIFI',
        'X-Fb-Device-Group': str(random.randrange(4700, 5000)),
        'Priority': 'u=3,i',
        'Accept-Encoding': 'gzip, deflate',
        'X-Fb-Http-Engine': 'Liger',
        'X-Fb-Client-Ip': 'true',
        'X-Fb-Server-Cluster': 'true',
        'Content-Length': str(random.randrange(1500, 2000))
    }

    # Define data payload
    data = {
        'adid': str(uuid.uuid4()),
        'format': 'json',
        'device_id': str(uuid.uuid4()),
        'email': email,
        'password': f'#PWD_FB4A:0:{str(time.time())[:10]}:{password}',
        'generate_analytics_claim': '1',
        'community_id': '',
        'linked_guest_account_userid': '',
        'cpl': True,
        'try_num': '1',
        'family_device_id': str(uuid.uuid4()),
        'secure_family_device_id': str(uuid.uuid4()),
        'credentials_type': 'password',
        'account_switcher_uids': [],
        'fb4a_shared_phone_cpl_experiment': 'fb4a_shared_phone_nonce_cpl_at_risk_v3',
        'fb4a_shared_phone_cpl_group': 'enable_v3_at_risk',
        'enroll_misauth': False,
        'generate_session_cookies': '1',
        'error_detail_type': 'button_with_disabled',
        'source': 'login',
        'machine_id': ''.join(
            [random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(24)]),
        'jazoest': str(random.randrange(22000, 23000)),
        'meta_inf_fbmeta': 'V2_UNTAGGED',
        'advertiser_id': str(uuid.uuid4()),
        'encrypted_msisdn': '',
        'currently_logged_in_userid': '0',
        'locale': 'id_ID',
        'client_country_code': 'ID',
        'fb_api_req_friendly_name': 'authenticate',
        'fb_api_caller_class': 'Fb4aAuthHandler',
        'api_key': '882a8490361da98702bf97a021ddc14d',
        'sig': hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:32],
        'access_token': '350685531728|62f8ce9f74b12f84c123cc23437a4a32'
    }

    pos = r.post('https://b-graph.facebook.com/auth/login', data=data, headers=head).json()

    if ('session_key' in str(pos)) and ('access_token' in str(pos)):
        token = pos['access_token']
        print(f'{COLOR_YELLOW}Token  :{COLOR_RESET} {token}')
    else:
        if 'error' in pos and 'message' in pos['error']:
            print(f'{COLOR_RED}Error Message:{COLOR_RESET} {pos["error"]["message"]}')
        else:
            print(f'{COLOR_RED}Unknown error format:{COLOR_RESET} {pos}')
    print("-" * 30)  # Separator for readability


# Main loop
while True:
    user_input = input(f'{COLOR_GREEN}Paste your email and password: {COLOR_RESET}')

    if user_input.lower() == 'exit':
        print(f'{COLOR_CYAN}Exiting the program. Goodbye!{COLOR_RESET}')
        break  # Exit the while loop

    email = ""
    password = ""
    # Try splitting by tab first
    if '\t' in user_input:
        try:
            email, password = user_input.split('\t', 1)  # Split only on the first tab
        except ValueError:
            pass  # This case should ideally not happen if a tab is present, but good for robustness
    # If no tab, try splitting by the first space
    elif ' ' in user_input:
        try:
            email, password = user_input.split(' ', 1)  # Split only on the first space
        except ValueError:
            pass  # Same as above
    elif '	' in user_input:
        try:
            email, password = user_input.split(' ', 1)  # Split only on the first space
        except ValueError:
            pass  # Same as above

    if email and password:
        Login(email=email.strip(), password=password.strip())  # Use .strip() to remove leading/trailing whitespace
    else:
        print(
            f'{COLOR_RED}Invalid input format. Please use "email@example.com\\tpassword" or "email@example.com password" or type "exit".{COLOR_RESET}')
