from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os

# --- Configuration para sa Chromium ---
# Mahalaga ang mga options na ito para sa headless execution sa Termux
chrome_options = Options()
chrome_options.add_argument("--headless=new") # Modern headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu") # Kadalasan ay kailangan ito sa headless environments
chrome_options.add_argument("--window-size=1920,1080") # Set window size for consistent screenshots

# Kung hindi auto-detected ang chromedriver, maaaring kailanganin mong tukuyin ang path
# Halimbawa: chrome_driver_path = '/data/data/com.termux/files/usr/bin/chromedriver'
# driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)

print("Nagsisimula ang Selenium script...")

try:
    # --- Magbukas ng website ---
    url = "https://www.google.com"
    print(f"Bumibisita sa: {url}")
    driver.get(url)

    print(f"Ang pamagat ng pahina ay: {driver.title}")

    # --- Maghanap ng element at mag-interact (hal. search bar) ---
    search_box = driver.find_element(By.NAME, "q")
    search_term = "Selenium Termux Python"
    print(f"Naghahanap ng: '{search_term}'")
    search_box.send_keys(search_term)
    search_box.submit()

    # Maghintay nang kaunti para mag-load ang resulta (opsyonal, para sa mas reliable na output)
    driver.implicitly_wait(5) # Maghihintay hanggang 5 segundo

    # --- Kumuha ng screenshot ---
    screenshot_path = "/sdcard/Download/selenium_termux_screenshot.png"
    # Siguraduhin na mayroon kang permission sa storage sa Termux (termux-setup-storage)
    # Maaari kang lumikha ng direktoryo kung wala pa:
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to: {screenshot_path}")

    # --- Kumuha ng ilang text mula sa pahina ng resulta ---
    print("\nIlang resulta mula sa search page:")
    search_results = driver.find_elements(By.CSS_SELECTOR, "h3")
    for i, result in enumerate(search_results[:5]): # Kumuha ng top 5 results
        print(f"{i+1}. {result.text}")

except Exception as e:
    print(f"May error na nangyari: {e}")

finally:
    # --- Isara ang browser ---
    print("\nIsinasara ang browser...")
    driver.quit()
    print("Tapos na ang script.")
