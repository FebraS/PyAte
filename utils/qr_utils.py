import os
from pyzbar.pyzbar import decode
from PIL import Image
import qrcode
from colorama import init, Fore, Style

def getOtpUriFromQrcode(imagePath):
    # Initialize colorama
    init()

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

def generateQrcodeFromUri(uri, outputPath):
    # Initialize colorama
    init()
    
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save image to specified path
        img.save(outputPath)
        print(f"QR Code generated and saved to: {Fore.LIGHTMAGENTA_EX}{outputPath}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"An error occurred while generating the QR code: {e}")
        return False

