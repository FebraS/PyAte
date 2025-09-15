# GPL-3.0 license
"""
    PyAte/pyate.py
    
    Copyright (C) 2025  Febra S
"""

import sys
import time
import os
import pyperclip
from colorama import init, Fore, Style
from cli.parser import setupArgParse
from utils.terminal import clearTerminal, banner
from utils.file_handler import loadAccounts
from utils.qr_utils import getOtpUriFromQrcode, generateQrcodeFromUri
from core.ykman_exporter import generateYkmanCommands
from utils.migration import getOTPAuthPerLineFromOPTAuthMigration

def main():
    # Initialize colorama
    init()
    args = setupArgParse()
    
    clearTerminal()
    banner()

    accounts = []

    # Determine output file for imports
    outputFile = args.output_file if args.output_file else args.read

    if args.import_migration:
        # Loop through each URI or file path provided
        for uriOrPath in args.import_migration:
            
            # New logic to handle both otpauth-migration:// and otpauth://
            if uriOrPath.startswith("otpauth-migration://"):
                uri = uriOrPath
                otpUris = getOTPAuthPerLineFromOPTAuthMigration(uri)
                if otpUris:
                    try:
                        with open(outputFile, 'a') as f:
                            for otpUri in otpUris:
                                f.write(otpUri + '\n')
                        print(f"Migration URIs from '{Fore.GREEN}URI{Style.RESET_ALL}' successfully added to '{Fore.LIGHTMAGENTA_EX}{outputFile}{Style.RESET_ALL}'.")
                    except Exception as e:
                        print(f"{Fore.RED}Failed to write URIs to file: {e}{Style.RESET_ALL }")
                else:
                    print(f"{Fore.RED}No valid OTP URIs found in the migration data from URI.{Style.RESET_ALL}")
                    
            elif uriOrPath.startswith("otpauth://"):
                # If it's a single otpauth:// URI, add it directly.
                try:
                    with open(outputFile, 'a') as f:
                        f.write(uriOrPath + '\n')
                    print(f"OTP URI successfully added from '{Fore.GREEN}URI{Style.RESET_ALL}' to '{Fore.LIGHTMAGENTA_EX}{outputFile}{Style.RESET_ALL}'.")
                except Exception as e:
                    print(f"{Fore.RED}Failed to write URI to file: {e}{Style.RESET_ALL}")
            
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
                                print(f"Migration URIs from '{Fore.CYAN}{uriOrPath}{Style.RESET_ALL}' successfully added to '{Fore.LIGHTMAGENTA_EX}{outputFile}{Style.RESET_ALL}'.")
                            except Exception as e:
                                print(f"{Fore.RED}Failed to write URIs to file: {e}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}No valid OTP URIs found in the QR code.{Style.RESET_ALL}")
                    
                    # Added logic to handle a single otpauth:// URI
                    elif uri.startswith("otpauth://"):
                        try:
                            with open(outputFile, 'a') as f:
                                f.write(uri + '\n')
                            print(f"OTP URI from QR code '{Fore.CYAN}{uriOrPath}{Style.RESET_ALL}' successfully added to '{Fore.LIGHTMAGENTA_EX}{outputFile}{Style.RESET_ALL}'.")
                        except Exception as e:
                            print(f"{Fore.RED}Failed to write URI to file: {e}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}The QR code does not contain a valid OTP URI.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid --import-migration argument: '{uriOrPath}'. Please provide a valid URI or a file path.{Style.RESET_ALL}")
        
        # We process all imports and then exit
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
    
    if args.export:
        
        inputFileExport = args.export
        print(f"Exporting accounts from '{Fore.LIGHTMAGENTA_EX}{inputFileExport}{Style.RESET_ALL}' to QR codes.")

        outputDir = "export"  # Directory to save QR codes
        os.makedirs(outputDir, exist_ok=True) # Create directory if it doesn't exist

        exported_count = 0
        try:
            with open(inputFileExport, 'r') as f: # Gunakan inputFileExport di sini
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line.startswith("otpauth://"):
                    try:
                        import urllib.parse
                        parsedUri = urllib.parse.urlparse(line)
                        queryParams = urllib.parse.parse_qs(parsedUri.query)
                        label = parsedUri.path.strip('/')
                        issuer = queryParams.get('issuer', [label])[0]

                        safeIssuer = "".join(c if c.isalnum() else "_" for c in issuer)
                        safeLabel = "".join(c if c.isalnum() else "_" for c in label)

                        fileNamePrefix = f"{safeIssuer}_{safeLabel}"
                        outputFileName = os.path.join(outputDir, f"qrcode_{fileNamePrefix}.png")

                        if generateQrcodeFromUri(line, outputFileName):
                            exported_count += 1
                    except Exception as e:
                        print(f"{Fore.RED}Warning: Could not parse URI '{line}'. Skipping. Error: {e}{Style.RESET_ALL}")

            if exported_count > 0:
                print(f"\n{Fore.GREEN}Successfully exported {exported_count} QR codes to the {Fore.LIGHTMAGENTA_EX}'{outputDir}'{Fore.LIGHTGREEN_EX}directory.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}No valid 'otpauth://' URIs found to export.{Style.RESET_ALL}")

        except FileNotFoundError:
            print(f"{Fore.RED}Error: File '{inputFileExport}' not found.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}An error occurred during export: {e}{Style.RESET_ALL}")

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

    print(f"{len(accounts)} accounts loaded from '{Fore.LIGHTMAGENTA_EX}{args.read}{Style.RESET_ALL}'.\n")

    currentOtps = {}
    previousOtps = {}
    
    try:
        if args.interactive:
            # Interactive mode
            print("Interactive Mode Enabled. Choose an account to copy its OTP.\n")
            
            # Find the maximum length of account names for alignment
            maxNameLen = 0
            if accounts:
                maxNameLen = max(len(acc['name']) for acc in accounts)
            
            # Print accounts with aligned OTPs
            for i, account in enumerate(accounts):
                currentOtps[account['name']] = account['totpObj'].now()
                # Use ljust() to pad the account name for perfect alignment
                paddedName = f"[{i+1}] {account['name']}".ljust(maxNameLen + 5)
                print(f"{paddedName}: {currentOtps[account['name']]}")

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
            
            # Find the maximum length of account names for alignment
            maxNameLen = 0
            if accounts:
                maxNameLen = max(len(acc['name']) for acc in accounts)
                
            while True:
                remainingSeconds = 30 - (int(time.time()) % 30)
                
                currentOtps = {acc['name']: acc['totpObj'].now() for acc in accounts}
                otpChanged = any(currentOtps.get(name) != previousOtps.get(name) for name in currentOtps)
                
                if otpChanged:
                    clearTerminal()
                    banner()
                    print(f"{len(accounts)} accounts loaded from '{Fore.LIGHTMAGENTA_EX}{args.read}{Style.RESET_ALL}'.\n")
                    
                    for account in accounts:
                        # Use ljust() to pad the name for perfect alignment
                        paddedName = f"[{account['name']}]".ljust(maxNameLen + 3)
                        print(f"{paddedName} OTP: {Fore.LIGHTGREEN_EX}{currentOtps[account['name']]}{Style.RESET_ALL}")

                    sys.stdout.write("\n")
                    
                    if accounts:
                        pyperclip.copy(accounts[0]['totpObj'].now())
                    previousOtps = currentOtps
                
                sys.stdout.write(f"\rRemaining Time: {remainingSeconds}s{' ' * 10}")
                sys.stdout.flush()
                
                time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}Program stopped.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n\n{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()