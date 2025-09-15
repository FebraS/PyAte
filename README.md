# PyAte (Python Authenticator Token Extractor)
PyAte is a lightweight and efficient Command-Line Interface (CLI) application built with Python. It serves as a powerful replacement for Google Authenticator, allowing you to manage and generate Time-based One-Time Passwords (TOTP) directly from your terminal.

Instead of manually scanning QR codes, PyAte reads a list of `otpauth://` addresses from a text file (accounts.txt), making it easy to manage multiple accounts at once.

## ✨ Key Features
* **Multi-Account Support**: Manage all your TOTP accounts from one central place.

* **Clean CLI Display**: The terminal output automatically refreshes every 30 seconds to show a valid OTP code.

* **Dynamic Time Updates**: A countdown of the remaining time updates every second, providing an experience similar to the original app.

* **Automatic Copy**: The OTP code for the first account is automatically copied to your clipboard for easy pasting.

* **Cross-Platform Compatibility**: Works seamlessly on Windows, macOS, and Linux.

* **Migration Import**: Automatically imports all accounts from a Google Authenticator migration QR code, simplifying the setup process.

* **YubiKey Support**: Generates ykman commands directly from a migration URI, making it easy to import TOTP accounts to a YubiKey device.

* **Export to QR Codes**: **(New!)** Generates individual QR code images for accounts from a specified file, saving them to a qrcodes directory for backup or transfer.

## 🛠️ How to Use
**1. Installation**
First, make sure you have Python installed. Then, install the required libraries:

```bash
pip install -r requirements.txt
```

**2. Setup**
Create a file named accounts.txt in the same directory as the program. Add the otpauth:// address for each of your accounts on a separate line.
Example accounts.txt content:

`otpauth://totp/GitHub:your-username?secret=ANOTHER_SECRET_KEY&issuer=GitHub`

**3. Run the Application**
Run the application with the basic command:

```bash
python pyate.py
```
This will display all your OTPs and automatically copy the first one to your clipboard.

## 🚀 Advanced Features (Arguments)
PyAte includes various arguments for more control and flexibility.

| Argumen | Description |
|---|---|
|`--import-migration <path_to_image>`	| Scans a Google Authenticator migration QR code and adds all URIs to accounts.txt. |
|`--output-file <filename.txt>`	| Use with --import-migration to save the imported URIs to a custom file. |
|`--generate-ykman <path_to_image>`	| Converts URIs from a QR code into ready-to-run ykman commands for YubiKey. |
|`--export <filename.txt>`	| Generates individual QR code images for each account in the specified file (defaults to accounts.txt). |
|`--interactive`	| Runs in interactive mode, allowing you to choose which account's OTP to copy. |
|`--search <keyword>`	| Filters and displays the OTP only for accounts that match your keyword. |
|`--read <filename.txt>`	| Loads accounts from a custom file instead of accounts.txt. |
|`--help`	| Displays a brief description of the program and all available arguments. |

## 🤝 Contribution
If you're interested in contributing, please check out the CONTRIBUTING.md file or feel free to open an issue on our GitHub repository.