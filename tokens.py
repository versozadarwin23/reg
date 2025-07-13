import string
import random
import requests
import hashlib

api_key = "882a8490361da98702bf97a021ddc14d"
secret = "62f8ce9f74b12f84c123cc23437a4a32"

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

        try:
            response = requests.get("https://api.facebook.com/restserver.php", params=params, headers=headers, timeout=10)
            data = response.json()
        except Exception as e:
            result = f"Request failed: {str(e)}"
        else:
            if "access_token" in data:
                result = data["access_token"]
            elif "error_msg" in data:
                result = data["error_msg"]
            elif "error_title" in data:
                result = data["error_title"]
            else:
                result = f"Unknown error: {data}"

        print(f"\033[92m✅ | {result} |\033[0m")

    except KeyboardInterrupt:
        print("\nExiting by user request.")
        break
