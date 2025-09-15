# GPL-3.0 license
"""
    PyAte/cli/parser.py
    
    Copyright (C) 2025 Febra S
"""

import argparse
from utils.terminal import banner

def setupArgParse():
    # Manage command line arguments
    # Create the parser
    banner()

    parser = argparse.ArgumentParser(
        description="Manage OTP accounts and extract TOTP codes from authenticator apps.",
        formatter_class=argparse.RawTextHelpFormatter)

    # Adding argument --read or -r
    parser.add_argument('-r', '--read',
                        type=str,
                        default='accounts.txt',
                        help='Specify the file to read account URIs from.')

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
                        # Fix issue inefficient import of multiple arguments
                        nargs='+',
                        help='''Import accounts from a QR code image file (e.g., path/to/qrcode.png), 
a migration URI string (e.g., "otpauth-migration://..."), 
or a single OTP URI string (e.g., "otpauth://...").''')

    # Adding argument --output-file
    parser.add_argument('-o', '--output-file',
                        type=str,
                        help='Specify the output file to write the decoded URIs. Overrides --read for import operations.')

    # Adding argument --generate-ykman or -g
    parser.add_argument('-g', '--generate-ykman',
                        type=str,
                        metavar='QR_CODE_PATH',
                        help='''Generate and print YubiKey Manager (ykman) commands directly 
from a migration QR code or URI.''')
    
    # Adding agrument --export or -e
    parser.add_argument('-e', '--export',
                        type=str,
                        default='accounts.txt',
                        help='Specify the file to read account URIs from. Default is accounts.txt.')

    return parser.parse_args()
