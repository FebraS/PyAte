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
import argparse

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

def banner():
    print(f"{pyfiglet.figlet_format('PyAte', font='slant')}")
    print("Python Authenticator Token Extractor")
    print("https://github.com/FebraS/PyAte")
    print("\n")

def setupArgParse():
    # Manage command line arguments
    # Create the parser
    parser = argparse.ArgumentParser(description=banner())

    # Adding argument --read or -r
    parser.add_argument('-r', '--read', 
                        type=str, 
                        default='accounts.txt', 
                        help='Specify the file to read account URIs from. (e.g., --read accounts.txt)')
    
    # Adding argument --interactive or -i
    parser.add_argument('-i', '--interactive',
                        action='store_true',
                        help='Enable interactive mode to select which OTP to copy.')
    
    # Adding argument --search or -s
    parser.add_argument('-s', '--search',
                        type=str,
                        help='Search for accounts by name.')
    
    return parser.parse_args()

def main():
    args = setupArgParse()
    
    clearTerminal()
    banner()

    accounts = loadAccounts(args.read)
    
    if not accounts:
        print(f"No accounts loaded. Make sure '{args.read}' exists and is not empty.")
        return

    # Filter accounts if search term is provided
    if args.search:
        searchTerm = args.search.lower()
        accounts = [acc for acc in accounts if searchTerm in acc['name'].lower()]
        
        if not accounts:
            print(f"No accounts found matching '{args.search}'.")
            return

    print(f"{len(accounts)} accounts loaded from '{args.read}'.\n")

    currentOtps = {}
    previousOtps = {}
    
    try:
        if args.interactive:
            # Interactive mode
            print("Interactive Mode Enabled. Choose an account to copy its OTP.\n")
            for i, account in enumerate(accounts):
                currentOtps[account['name']] = account['toptObj'].now()
                print(f"[{i+1}] {account['name']} : {currentOtps[account['name']]}")

            while True:
                try:
                    choice = int(input("\nEnter account number to copy OTP (or 0 to exit): "))
                    if choice == 0:
                        print("\nExiting interactive mode.")
                        break
                    if 1 <= choice <= len(accounts):
                        selectedOtp = accounts[choice-1]['toptObj'].now()
                        pyperclip.copy(selectedOtp)
                        print(f"\nOTP for '{accounts[choice-1]['name']}' ({selectedOtp}) copied to clipboard!")
                    else:
                        print("Invalid choice. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        
        else:
            # Normal mode
            while True:
                remainingSeconds = 30 - (int(time.time()) % 30)
                
                currentOtps = {acc['name']: acc['toptObj'].now() for acc in accounts}
                otpChanged = any(currentOtps.get(name) != previousOtps.get(name) for name in currentOtps)
                
                if otpChanged:
                    clearTerminal()
                    banner()
                    print(f"{len(accounts)} accounts loaded from '{args.read}'.\n")
                    
                    for account in accounts:
                        print(f"[{account['name']}] OTP: {currentOtps[account['name']]}")

                    sys.stdout.write("\n")
                    
                    if accounts:
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