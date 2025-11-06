FB Auto-Reg Tool (Termux Version)
A Python-based automated tool designed for creating Facebook accounts directly from Termux on Android. This tool handles the registration process, attempts to fetch the Graph API access token (EAAAAU...), and saves credentials automatically to your device's internal storage.

⚠️ DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY. Automating Facebook account creation violates their Terms of Service. The author is not responsible for any misused accounts or banned devices resulting from the use of this tool. Use at your own risk.

🔥 Features
Automated Registration Loop: Runs continuously to create multiple accounts in one session.

Realistic Device Fingerprinting: Randomizes device models, user agents, and system fingerprints to mimic real Android devices.

Auto Token Fetcher: Attempts to automatically log in and retrieve the EAAAAU... access token after successful registration.

Retry Logic: Includes built-in retries for network timeouts and failed token fetches.

Auto-Save: Saves account details (Name, UID, Password, Cookie/Profile Link, Token) to both .txt and .xlsx formats in your internal storage.

🛠️ Requirements
Android Device with Termux installed.

Python 3.x

Internet connection (Mobile Data allows for easier IP rotation via Airplane mode).

📥 Installation
Setup Termux Storage (Important for saving output files):

Bash

termux-setup-storage
Allow the permission when prompted.

Update Termux and install Python:

Bash

pkg update && pkg upgrade -y
pkg install python git -y

🚀 Usage
Run the script using Python:

Bash

python reg.py
Interactive Prompts:
Password: You will be asked to set a base password (e.g., if you type "Pass", passwords will be like "Pass123456").

Registration Method:

[1] Enter Email: You manually provide an email for each account.

[2] Random Phone Number: The tool generates a random number (Warning: These accounts may get checkpointed easily if not verified).

Token Fetching: After registration, confirm if you want the tool to attempt fetching the access token immediately.

📂 Output Location
Successfully created accounts are saved directly to your phone's internal root storage for easy access:

Excel: /storage/emulated/0/Acc_Created.xlsx

Text: /storage/emulated/0/Acc_created.txt

🛑 Troubleshooting
Registration Failed (No 'c_user' cookie): Facebook likely flagged your IP. Try turning Airplane Mode ON for 5 seconds, then OFF to get a new IP address (if using mobile data), then try again.

Token Fetch Failed: Sometimes newly created accounts need a few minutes before they can use the Graph login. The script has a retry option; if it still fails, you may need to log in manually later.

Permission Denied Error: Make sure you ran termux-setup-storage and granted storage permissions so the script can save the .xlsx file.
