import os
from pyzbar.pyzbar import decode
from PIL import Image

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
            
            # Updated to handle both migration and single OTP URIs
            if uri.startswith("otpauth-migration://") or uri.startswith("otpauth://"):
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
