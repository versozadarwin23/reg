session = requests.Session()
    cookie_file = f"/storage/emulated/0/cookie/{username}.json"

    reused_session = False

    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, "r") as f:
                cookies = json.load(f)
            session.cookies = cookiejar_from_dict(cookies)

            home_check = session.get("https://m.facebook.com/home.php", headers=windows_headers, timeout=60)
            if "c_user" in session.cookies:
                with lock:
                    success_count += 1
                uid = session.cookies.get("c_user")
                print(f"\033[92m[✓] {name} Keep-alive OK: {uid} |  (session reused)\033[0m")
                reused_session = True
        except:
            pass
