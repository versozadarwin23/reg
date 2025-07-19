import os
import re
import string
import random
import requests
import hashlib

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

api_key = "882a8490361da98702bf97a021ddc14d"
secret = "62f8ce9f74b12f84c123cc23437a4a32"
os.system("clear")  # Clear console when script starts


while True:
    try:
        print(f"{CYAN}\n📧 Enter Facebook Credentials:{RESET}")
        email = input("✉️  Paste your Email: ").strip()
        password = input("🔐 Paste your Password: ").strip()

        # ====== HEADERS (fresh adid) ======
        headers = {
            'x-fb-friendly-name': 'Authenticate',
            'x-fb-connection-type': 'Unknown',
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/x-www-form-urlencoded',
            'x-fb-http-engine': 'Liger',
            'fb_api_req_friendly_name': 'authenticate',
            'generate_machine_id': '0',
            'generate_session_cookies': '0',
            'enroll_misauth': 'false',
            'error_detail_type': 'button_with_disabled',
            'source': 'login',
            'credentials_type': 'password',
            'generate_analytics_claims': '0',
            'adid': ''.join(random.choices(string.hexdigits, k=16)),
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1903 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/136.0.7103.60 Mobile Safari/537.36[FBAN/EMA;FBLC/pt_PT;FBAV/444.2.0.9.110;FBCX/modulariab;]'
        }

        # ====== REQUEST ======
        params = {
            "api_key": api_key,
            "email": email,
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

        print(f"{YELLOW}\n🔄 Sending request to Facebook API...{RESET}")
        try:
            response = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers, timeout=10)
            data = response.json()
        except Exception as e:
            print(f"{RED}❌ Request failed: {str(e)}{RESET}")
        else:
            if "access_token" in data:
                print(f"{GREEN}✅ Success! Access Token:\n🔑 {data['access_token']}{RESET}")
            elif "error_msg" in data:
                print(f"{RED}❌ Error Message: {data['error_msg']}{RESET}")
            elif "error_title" in data:
                print(f"{RED}❌ Error Title: {data['error_title']}{RESET}")
            else:
                print(f"{RED}❌ Unknown response:\n{data}{RESET}")

    except KeyboardInterrupt:
        print(f"\n\n{CYAN}👋 Exiting by user request. Goodbye!{RESET}")
        break
