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
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) vivo Y93 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/138.0.0.0 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/496.0.0.45.65;IABMV/1;]',
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
        'Content-Length': str(random.randrange(1500, 2000)),
        'cache-control': "private, no-cache, no-store, must-revalidate",
        "facebook-api-version": "v1.0",
        "pragma": "no-cache",
        "priority": "u=0,i",
        "strict-transport-security": "max-age=15552000; preload",
        "vary": "Accept-Encoding",
        "x-fb-connection-quality": "GOOD; q=0.7, rtt=73, rtx=0, c=23, mss=1232, tbw=5012, tp=10, tpl=0, uplat=405, ullat=0",
        "x-fb-debug": "g/lwUlHD6vXZly0pnMoWnhifQ8PoyIuzDnUKVk5ZWru6+2XT2yaUB9Y/TSXbt0/637lElrllnUhGyXNJLheBKA==",
        "x-fb-request-id": "AEJauAi2IHwyhd_zl3pC-4E",
        "x-fb-rev": "1025308755",
        "x-fb-trace-id": "C/GnaBOOeUa",
        "x-frame-options": "DENY"
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
        'fb4a_shared_phone_cpl_experiment': 'fb4a_shared_phone_nonce_cpl_at_risk_v3',
        'fb4a_shared_phone_cpl_group': 'enable_v3_at_risk',
        'enroll_misauth': False,
        'generate_session_cookies': '1',
        'error_detail_type': 'button_with_disabled',
        'source': 'login',
        'machine_id': ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(24)]),
        'jazoest': str(random.randrange(22000, 23000)),
        'meta_inf_fbmeta': 'V2_UNTAGGED',
        'advertiser_id': str(uuid.uuid4()),
        'currently_logged_in_userid': '1',
        'locale': 'fil_PH',
        'client_country_code': 'PH',
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
        if 'error' in pos:
            print(f'{COLOR_RED}Error Message:{COLOR_RESET} {pos["error"]["error_user_title"]}')
        else:
            print(f'{COLOR_RED}Unknown error format:{COLOR_RESET} {pos}')
    print("-" * 30)  # Separator for readability


# Main loop
while True:
    print(f'{COLOR_YELLOW}When you create an account, get the token right away{COLOR_RESET}')
    print(f'{COLOR_YELLOW}before you start doing tasks"{COLOR_RESET}')
    print(f'{COLOR_YELLOW}If you cant get the token, or if the credentials are wrong"{COLOR_RESET}')
    print(f'{COLOR_YELLOW}just switch to a new account or create a new one."{COLOR_RESET}')
    print('')
    print('')
    print(f'{COLOR_YELLOW}If youre always getting a wrong credentials error, you can try these steps:"{COLOR_RESET}')
    print(f'{COLOR_YELLOW}Clear all data for Facebook Lite or the Facebook app.{COLOR_RESET}')
    print(f'{COLOR_YELLOW}Restart your phone."{COLOR_RESET}')
    print(f'{COLOR_YELLOW}If the issue persists, wait a few minutes before trying again."{COLOR_RESET}')


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
