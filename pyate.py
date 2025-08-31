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
from pyzbar.pyzbar import decode
from PIL import Image
from utils import migration

UPDATE_SECONDS = 5

def parseOtpUri(uri):
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
                    totpObj, name = parseOtpUri(uri)
                    if totpObj:
                        accounts.append({'totpObj': totpObj, 'name': name})
                    else:
                        print(f"Warning: Skipping invalid line -> {uri}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None
    
    return accounts

def getOtpUriFromQrcode(imagePath):
    try:
        # Check if the file path exists and is not a directory
        if not os.path.isfile(imagePath):
            print(f"Error: File '{imagePath}' not found or is a directory.")
            return None

        img = Image.open(imagePath)
        decodedObjects = decode(img)

        for obj in decodedObjects:
            uri = obj.data.decode('utf-8')
            if uri.startswith("otpauth-migration://"):
                print(f"Successfully read QR Code from: {imagePath}")
                return uri

        print(f"No OTP URI found in the QR Code file: {imagePath}")
        return None

    except FileNotFoundError:
        print(f"Error: File '{imagePath}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while processing the QR code file: {e}")
        return None
    
def generateYkmanCommands(migrationUri: str) -> list:
    commands = []
    try:
        otpUris = migration.getOTPAuthPerLineFromOPTAuthMigration(migrationUri)
    except Exception as e:
        print(f"Error parsing migration URI: {e}")
        return commands

    for uri in otpUris:
        try:
            parsedUri = urlparse(uri)
            queryParams = parse_qs(parsedUri.query)
            
            # Initialize the base command
            ykargs = ["oath", "add"]

            # Add type
            otpType = parsedUri.netloc.lower()
            if otpType == "totp":
                ykargs.extend(["-o", "TOTP", "-p", "30"])
            elif otpType == "hotp":
                ykargs.extend(["-o", "HOTP"])
            else:
                continue # Skip unsupported types

            # Add digits
            digits = queryParams.get("digits", ["6"])[0]
            ykargs.extend(["-d", digits])

            # Add algorithm
            algorithm = queryParams.get("algorithm", ["SHA1"])[0].upper()
            ykargs.extend(["-a", algorithm])

            # Add counter for HOTP
            if otpType == "hotp":
                counter = queryParams.get("counter", ["0"])[0]
                ykargs.extend(["-c", counter])

            # Add issuer
            issuer = queryParams.get("issuer", [""])[0]
            if len(issuer) > 0:
                ykargs.extend(["-i", f'"{issuer}"'])
            
            # Add name (account) and secret
            accountName = unquote(parsedUri.path.strip('/'))
            secret = queryParams.get("secret", [""])[0]
            
            # Handle issuer in name if it's not provided separately
            if not issuer and accountName.find(':') > 0:
                parts = accountName.split(':')
                issuer = parts[0]
                accountName = parts[1]
                ykargs.extend(["-i", f'"{issuer}"'])
            
            ykargs.append(f'"{accountName}"')
            ykargs.append(secret)

            commands.append("ykman " + " ".join(ykargs))
            
        except (IndexError, KeyError):
            continue
            
    return commands

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
    
    # Adding argument --interactive or -t
    parser.add_argument('-t', '--interactive',
                        action='store_true',
                        help='Enable interactive mode to select which OTP to copy.')
    
    # Adding argument --search or -s
    parser.add_argument('-s', '--search',
                        type=str,
                        help='Search for accounts by name.')
    
    # Adding argument --import or -i
    parser.add_argument('-i', '--import-migration',
                        type=str,
                        help='Help import OTPs from a migration QR code. (e.g., --import-migration path/to/qrcode.png )')
    
    # Adding argument --import-migration
    parser.add_argument('-o', '--output-file',
                        type=str,
                        help='Specify the output file to write the decoded URIs. Overrides --read for import operations.')
    
    # Adding argument --generate-ykman or -g
    parser.add_argument('-g', '--generate-ykman',
                        type=str, # Changed type to str to accept QR code path
                        metavar='QR_CODE_PATH',
                        help='Generate and print YubiKey Manager (ykman) commands directly from a migration QR code or URI. (e.g., --generate-ykman path/to/qrcode.png)')
    
    return parser.parse_args()

def main():
    args = setupArgParse()
    
    clearTerminal()
    banner()

    accounts = []

    # Determine output file for imports
    outputFile = args.output_file if args.output_file else args.read

    if args.import_migration:
        if os.path.isfile(args.import_migration):
            uri = getOtpUriFromQrcode(args.import_migration)
            if uri:
                
                otpUris = migration.getOTPAuthPerLineFromOPTAuthMigration(uri)
                if otpUris:
                    try:
                        with open(outputFile, 'a') as f:
                            for otpUri in otpUris:
                                f.write(otpUri + '\n')
                        print(f"Migration URIs successfully added to '{args.read}'.")
                    except Exception as e:
                        print(f"Failed to write URIs to file: {e}")
                else:
                    print("No valid OTP URIs found in the migration data.")
            else:
                return
        elif args.import_migration.startswith("otpauth-migration://"):
            print("Migration URIs are not directly supported in this version. Please use a QR code.")
            return
        else:
            print("Invalid --import-migration argument. Please provide a QR code image file path.")
            return
    
    elif args.generate_ykman:
        uriOrPath = args.generate_ykman
        
        # Check if the input is a file path or a URI string
        if os.path.isfile(uriOrPath):
            uri = getOtpUriFromQrcode(uriOrPath)
            if not uri:
                return
        elif uriOrPath.startswith("otpauth-migration://"):
            uri = uriOrPath
        else:
            print("Invalid --generate-ykman argument. Please provide a QR code image file path or a migration URI string.")
            return
        
        if uri:
            print("YubiKey Manager (ykman) commands for the loaded accounts:")
            print("-" * 50)
            ykmanCommands = generateYkmanCommands(uri)
            if ykmanCommands:
                for cmd in ykmanCommands:
                    print(cmd)
            else:
                print("No valid OTP URIs found in the migration data.")
            print("-" * 50)
        
        # Exit after generating ykman commands
        return
            
    # Load accounts from the file after all imports are complete
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
                currentOtps[account['name']] = account['totpObj'].now()
                print(f"[{i+1}] {account['name']} : {currentOtps[account['name']]}")

            while True:
                try:
                    choice = int(input("\nEnter account number to copy OTP (or 0 to exit): "))
                    if choice == 0:
                        print("\nExiting interactive mode.")
                        break
                    if 1 <= choice <= len(accounts):
                        selectedOtp = accounts[choice-1]['totpObj'].now()
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
                
                currentOtps = {acc['name']: acc['totpObj'].now() for acc in accounts}
                otpChanged = any(currentOtps.get(name) != previousOtps.get(name) for name in currentOtps)
                
                if otpChanged:
                    clearTerminal()
                    banner()
                    print(f"{len(accounts)} accounts loaded from '{args.read}'.\n")
                    
                    for account in accounts:
                        print(f"[{account['name']}] OTP: {currentOtps[account['name']]}")

                    sys.stdout.write("\n")
                    
                    if accounts:
                        pyperclip.copy(accounts[0]['totpObj'].now())
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