# GPL-3.0 license
"""
    PyAte/core/ykman_exporter.py
    
    Copyright (C) 2025 Febra S
"""

from urllib.parse import urlparse, parse_qs, unquote
import utils.migration as migration

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
