#PyAte/utils/migration.py

import base64
import urllib.parse

# Ported and adapted from Authenticator extension
# Ref:  https://github.com/Authenticator-Extension/Authenticator/blob/dev/src/models/migration.ts

def byteArrayToBase32(bytes_data: list) -> str:
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    lenData = len(bytes_data)
    result = ""
    low = 0
    sh = 0
    hasDataInLow = False

    for i in range(lenData):
        hasDataInLow = True
        currentByte = bytes_data[i]

        # Process each byte based on its position
        if i % 5 == 0:
            high = 0xF8 & currentByte
            result += chars[high >> 3]
            low = 0x07 & currentByte
            sh = 2
        elif i % 5 == 1:
            high = 0xC0 & currentByte
            result += chars[(low << 2) | (high >> 6)]
            result += chars[(0x3E & currentByte) >> 1]
            low = currentByte & 0x01
            sh = 4
        elif i % 5 == 2:
            high = 0xF0 & currentByte
            result += chars[(low << 4) | (high >> 4)]
            low = 0x0F & currentByte
            sh = 1
        elif i % 5 == 3:
            high = 0x80 & currentByte
            result += chars[(low << 1) | (high >> 7)]
            result += chars[(0x7C & currentByte) >> 2]
            low = currentByte & 0x03
            sh = 3
        elif i % 5 == 4:
            hasDataInLow = False
            high = 0xE0 & currentByte
            result += chars[(low << 3) | (high >> 5)]
            result += chars[0x1F & currentByte]
            low = 0
            sh = 0
    
    if hasDataInLow:
        result += chars[low << sh]

    # Handle padding
    padlen = 8 - (len(result) % 8)
    if padlen < 8:
        result += "=" * padlen
    
    return result

def getOTPAuthPerLineFromOPTAuthMigration(migrationUri: str):
    if not migrationUri.startswith("otpauth-migration:"):
        return []
    
    try:
        # Step 1: URL-decode the string
        urlDecodedUri = urllib.parse.unquote(migrationUri)
        
        # Step 2: Split and get the Base64 data
        base64Data = urlDecodedUri.split("data=")[1]
        
        # Step 3: Base64 decode the clean data
        byteData = base64.b64decode(base64Data)

    except (IndexError, base64.binascii.Error):
        return []

    lines = []
    offset = 0

    # Parse the byte data
    while offset < len(byteData):
        if byteData[offset] != 10:
            break
        
        # Read lengths and values
        try:
            lineLength = byteData[offset + 1]
            secretLength = byteData[offset + 3]
            secretBytes = byteData[offset + 4 : offset + 4 + secretLength]
            
            # Fix Unnecessary '=' in secret key for ykman commands bug
            # Change characters from '=' to null
            secret = byteArrayToBase32(secretBytes).replace("=", "")

            accountLength = byteData[offset + 4 + secretLength + 1]
            accountBytes = byteData[offset + 4 + secretLength + 2 : offset + 4 + secretLength + 2 + accountLength]
            account = accountBytes.decode('utf-8')

            issuerLength = byteData[offset + 4 + secretLength + 2 + accountLength + 1]
            issuerBytes = byteData[offset + 4 + secretLength + 2 + accountLength + 2 : offset + 4 + secretLength + 2 + accountLength + 2 + issuerLength]
            issuer = issuerBytes.decode('utf-8')

            algorithmIndex = byteData[offset + 4 + secretLength + 2 + accountLength + 2 + issuerLength + 1]
            algorithm = ["SHA1", "SHA1", "SHA256", "SHA512", "MD5"][algorithmIndex]
            
            digitsIndex = byteData[offset + 4 + secretLength + 2 + accountLength + 2 + issuerLength + 3]
            digits = [6, 6, 8][digitsIndex]
            
            typeIndex = byteData[offset + 4 + secretLength + 2 + accountLength + 2 + issuerLength + 5]
            typeName = ["totp", "hotp", "totp"][typeIndex]

        except IndexError:
            break
        
        # Construct the otpauth URI
        line = f"otpauth://{typeName}/{account}?secret={secret}&issuer={issuer}&algorithm={algorithm}&digits={digits}"

        if typeName == "hotp":
            counterOffset = offset + 4 + secretLength + 2 + accountLength + 2 + issuerLength + 7
            if counterOffset < offset + lineLength + 2:
                counter = byteData[counterOffset]
                line += f"&counter={counter}"
        
        lines.append(line)
        offset += lineLength + 2

    return lines
