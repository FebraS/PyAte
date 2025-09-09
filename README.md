# PyAte (Python Authenticator Token Extractor)
PYATE is a lightweight and efficient Command-Line Interface (CLI) application, built with Python, that serves as a replacement for Google Authenticator. It lets you manage and generate Time-based One-Time Passwords (TOTP) for various accounts directly from your terminal. Instead of manually scanning a QR code, PYATE reads a list of `otpauth://` addresses from a text file (accounts.txt), allowing you to manage multiple accounts at once.

## Key Features
Multi-Account Support: Manage multiple TOTP accounts from one place using a simple list in a text file.

* **Clean CLI Display**: The terminal output automatically refreshes every 30 seconds to show a valid OTP code.

* **Dynamic Time Updates**: A countdown of the remaining time updates every second on the same line, providing an experience similar to the original app.

* **Automatic Screen Clearing**: The terminal screen is cleared and fully refreshed when the OTP code changes, ensuring no old text is left behind.

* **Automatic Copy**: The OTP code for the first account is automatically copied to the clipboard for easy pasting.

* **Cross-Platform Compatibility**: Works seamlessly on Windows, macOS, and Linux.

* **Migration Import**: Automatically imports all accounts from a Google Authenticator migration QR code, simplifying the setup process.

* **YubiKey Support**: Can generate ykman commands directly from a migration URI, making it easy to import TOTP accounts to a YubiKey device.

## Additional (Argument-Based) Features
PyAte has been updated to include argument-based features, providing more control and flexibility.

## How to Use
Make sure you have installed the required libraries.

```bash
pip install -r requirements.txt
```
Create an Accounts File: Create a file named accounts.txt in the same directory as the program. Enter the `otpauth://` address for each account on a separate line.

### Example of accounts.txt content
otpauth://totp/GitHub:your-username?secret=ANOTHER_SECRET_KEY&issuer=GitHub

## Run the Application:

### Normal Mode
Displays all OTPs and automatically copies the first one.
```bash
python pyate.py
```

### Import Migration
This feature allows you to import multiple TOTP accounts at once from a Google Authenticator migration QR code. This is extremely useful for transferring all accounts from your Google Authenticator app on your phone.

```bash
python pyate.py --import-migration path/to/qrcode.png
```
`--import-migration`: Use this argument followed by the path to the migration QR code image file. PyAte will scan the image, extract all OTP URIs, and add them to the accounts.txt file.

### Save to a Custom File
You can combine `--import-migration` with `--output-file` to save the imported URIs to a different file, like `new_accounts.txt`.

```bash
python pyate.py --import-migration path/to/qrcode.png --output-file new_accounts.txt
```

### Generate YubiKey Manager (ykman) Commands
This feature converts the migration URI extracted from a QR code or a direct URI into ready-to-run ykman commands. This is ideal for users who want to import their TOTP accounts from Google Authenticator directly to their YubiKey device.

```bash
python pyate.py --generate-ykman path/to/qrcode.png
```
This command will scan the QR code, extract the OTP URIs, and print a series of ykman commands to the terminal. You can simply copy and paste these commands to import your accounts into your YubiKey.

### Interactive Mode
Choose which account's OTP to copy.

```bash
python pyate.py --interactive
```

### Search Mode
The `--search` argument allows you to filter accounts and only display the OTP for accounts that match the keyword you enter. This is very useful when you have many accounts in your file and only want to see one or a few specific ones.

```bash
python pyate.py --search "google"
```
Example: If your `accounts.txt` file contains accounts for Google and GitHub, the command python pyate.py `--searc`h "google" will filter the list and only show the OTP for the Google account. This command will produce an output like this:

```
1 accounts loaded from 'accounts.txt'.

[Google: your-email] OTP: 123456

Remaining Time: 25s
```

### Use a Custom File
By default, PyAte will read accounts from the accounts.txt file. However, with the --read argument, you can specify another text file to load OTP accounts from. This allows you to manage multiple sets of accounts separately without having to change the main file.
Example: If you have a file named auth.txt and you want PyAte to load accounts from there, use the command:

```bash
python pyate.py --read auth.txt
```

### View Help Page
The `--help` argument displays a brief description of the program and all available arguments, complete with explanations. This is a quick way to get a summary of all the features supported by PyAte directly in your terminal.

**Example**
```
python pyate.py --help
```
