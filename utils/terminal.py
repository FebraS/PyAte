import os
import platform
import pyfiglet

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
