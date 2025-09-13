# GPL-3.0 license
"""
    PyAte/utils/file_handler.py
    
    Copyright (C) 2025 Febra S
"""

import os
import sys
from core.otp_manager import parseOtpUri

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

def saveAccounts(fileName, otpUris):
    try:
        with open(fileName, 'a') as f:
            for otpUri in otpUris:
                f.write(otpUri + '\n')
        print(f"Migration URIs successfully added to '{fileName}'.")
    except Exception as e:
        print(f"Failed to write URIs to file: {e}")
