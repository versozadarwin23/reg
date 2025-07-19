import os
import string
import random
import time

import requests
import hashlib

RED = "\033[91m"    # ANSI code for red
GREEN = "\033[92m"  # ANSI code for green
YELLOW = "\033[93m"  # ANSI code for yellow
RESET = "\033[0m"   # ANSI code to reset color
WARNING_EMOJI = "⚠️" # Unicode warning emoji
ERROR_EMOJI = "❌" # Unicode X emoji
CHECK_EMOJI = "✅" # Unicode checkmark emoji


api_key = "882a8490361da98702bf97a021ddc14d"
secret = "62f8ce9f74b12f84c123cc23437a4a32"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear') # Cross-platform clear

def main():
    while True:
        try:
            # ====== INPUT ======
            while True:
                RAW_CREDENTIALS = input("\nPaste your email and password : ").strip()
                if not RAW_CREDENTIALS:
                    pass
                parts = RAW_CREDENTIALS.split()
                if len(parts) < 2:
                    print("❌ Invalid input. Make sure you paste: email password")
                    continue
                email, password = parts[0], parts[1]
                break

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

            display_color = RED # Default to red for potential errors
            display_emoji = ERROR_EMOJI # Default to error emoji

            try:
                response = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers, timeout=10)
                data = response.json()
            except Exception as e:
                result = f"Request failed: {str(e)}"
            else:
                print(f"{RESET}")
                if "access_token" in data:
                    result = data["access_token"]
                    display_color = GREEN
                    display_emoji = CHECK_EMOJI
                elif "error_msg" in data:
                    result = data["error_msg"]
                    time.sleep(3)
                    clear_console()
                elif "error_title" in data:
                    result = data["error_title"]
                    time.sleep(3)
                    clear_console()
                else:
                    result = f"Unknown error: {data}"
                    time.sleep(3)
                    clear_console()

            print(f"{display_color}{display_emoji} | {result} |{RESET}")

        except KeyboardInterrupt:
            print("\nExiting by user request.")
            break

if __name__ == "__main__":
    print(f"{YELLOW}{WARNING_EMOJI} Please get the token immediately after successful creation.{RESET}")
    print(f"{YELLOW}{WARNING_EMOJI} Don't delay, or you won't be able to retrieve it.{RESET}")
    print(f"{YELLOW}{WARNING_EMOJI} And it will show as a 'wrong password'.{RESET}")
    while True:
        main()
