# GPL-3.0 license
"""
    PyAte/pyate.py
    
    Copyright (C) 2025  Febra S
"""

import sys
import time
import os
import pyperclip
from cli.parser import setupArgParse
from utils.terminal import clearTerminal, banner
from utils.file_handler import loadAccounts
from utils.qr_decoder import getOtpUriFromQrcode
from core.ykman_exporter import generateYkmanCommands
from utils.migration import getOTPAuthPerLineFromOPTAuthMigration

def main():
    args = setupArgParse()
    
    clearTerminal()
    banner()

    accounts = []

    # Determine output file for imports
    outputFile = args.output_file if args.output_file else args.read

    if args.import_migration:
        uriOrPath = args.import_migration
        
        # New logic to handle both otpauth-migration:// and otpauth://
        if uriOrPath.startswith("otpauth-migration://"):
            uri = uriOrPath
            otpUris = getOTPAuthPerLineFromOPTAuthMigration(uri)
            if otpUris:
                try:
                    with open(outputFile, 'a') as f:
                        for otpUri in otpUris:
                            f.write(otpUri + '\n')
                    print(f"Migration URIs successfully added to '{outputFile}'.")
                except Exception as e:
                    print(f"Failed to write URIs to file: {e}")
            else:
                print("No valid OTP URIs found in the migration data.")
                
        elif uriOrPath.startswith("otpauth://"):
            # If it's a single otpauth:// URI, add it directly.
            try:
                with open(outputFile, 'a') as f:
                    f.write(uriOrPath + '\n')
                print(f"OTP URI successfully added to '{outputFile}'.")
            except Exception as e:
                print(f"Failed to write URI to file: {e}")
        
        elif os.path.isfile(uriOrPath):
            # Existing logic to handle a QR code image path
            uri = getOtpUriFromQrcode(uriOrPath)
            if uri:
                # Assuming the QR code contains a migration URI
                if uri.startswith("otpauth-migration://"):
                    otpUris = getOTPAuthPerLineFromOPTAuthMigration(uri)
                    if otpUris:
                        try:
                            with open(outputFile, 'a') as f:
                                for otpUri in otpUris:
                                    f.write(otpUri + '\n')
                            print(f"Migration URIs successfully added to '{outputFile}'.")
                        except Exception as e:
                            print(f"Failed to write URIs to file: {e}")
                    else:
                        print("No valid OTP URIs found in the QR code.")
                
                # Added logic to handle a single otpauth:// URI
                elif uri.startswith("otpauth://"):
                    try:
                        with open(outputFile, 'a') as f:
                            f.write(uri + '\n')
                        print(f"OTP URI from QR code successfully added to '{outputFile}'.")
                    except Exception as e:
                        print(f"Failed to write URI to file: {e}")
                else:
                    print("The QR code does not contain a valid OTP URI.")
        else:
            print("Invalid --import-migration argument. Please provide a migration or single OTP URI string or a QR code image file path.")
        
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
