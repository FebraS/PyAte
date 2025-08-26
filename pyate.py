# GPL-3.0 license
"""
    PyAte/pyate.py
    
    Copyright (C) 2025  Febra S
"""

import os
import platform
import time
import sys
import pyperclip
from urllib.parse import urlparse, parse_qs, unquote
import pyotp
import pyfiglet

UPDATE_SECONDS = 5

def parseOtpUrl(uri):
    if not uri.startswith("otpauth://"):
        return None, None

    parsedUrl = urlparse(uri)
    params = parse_qs(parsedUrl.query)
    
    secret = params.get('secret', [None])[0]
    if not secret:
        return None, None

    issuer = params.get('issuer', [None])[0]
    accountPath = unquote(parsedUrl.path.strip('/'))

    if ':' in accountPath:
        pathParts = accountPath.split(':', 1)
        if not issuer:
            issuer = pathParts[0]
        account = pathParts[1]
    else:
        account = accountPath
    
    if not issuer:
        issuer = "Unknown Issuer"

    return pyotp.TOTP(secret), f"{issuer}: {account}"

def loadAccounts(filename="accounts.txt"):
    accounts = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                uri = line.strip()
                if uri:
                    toptObj, name = parseOtpUrl(uri)
                    if toptObj:
                        accounts.append({'toptObj': toptObj, 'name': name})
                    else:
                        print(f"Warning: Skipping invalid line -> {uri}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None
    
    return accounts

def clearTerminal():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
    """
    Membersihkan seluruh output di terminal.
    # Kode ANSI untuk membersihkan layar dari kursor ke bawah
    print("\033[2J\033[H", end="", flush=True)
    """

def banner():
    print(f"{pyfiglet.figlet_format('PyAte', font='slant')}")
    print("Python Authenticator Token Extractor")
    print("https://github.com/FebraS/PyAte")
    print("---------------------------------")

def main():
    clearTerminal()
    banner()

    accounts = loadAccounts()
    
    if not accounts:
        print("No accounts loaded. Make sure 'accounts.txt' exists and is not empty.")
        return

    print(f"{len(accounts)} accounts loaded.\n")

    currentOtps = {}
    previousOtps = {}
    
    try:
        while True:
            remainingSeconds = 30 - (int(time.time()) % 30)
            
            currentOtps = {acc['name']: acc['toptObj'].now() for acc in accounts}
            otpChanged = any(currentOtps.get(name) != previousOtps.get(name) for name in currentOtps)
            
            if otpChanged:
                clearTerminal()
                banner()
                print(f"{len(accounts)} accounts loaded.\n")
                
                for account in accounts:
                    print(f"[{account['name']}] OTP: {currentOtps[account['name']]}")

                sys.stdout.write("\n")
                
                pyperclip.copy(accounts[0]['toptObj'].now())
                previousOtps = currentOtps
            
            sys.stdout.write(f"\rRemaining Time: {remainingSeconds}s{' ' * 10}")
            sys.stdout.flush()
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nProgram stopped.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
