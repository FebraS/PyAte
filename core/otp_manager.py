# GPL-3.0 license
"""
    PyAte/core/otp_manager.py
    
    Copyright (C) 2025 Febra S
"""
from urllib.parse import urlparse, parse_qs, unquote
import pyotp

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
