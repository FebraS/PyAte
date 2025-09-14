import os
import platform
import pyfiglet
from colorama import init, Fore, Style
import random

def clearTerminal():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def banner():
    # Fix colorama issue on Windows
    init()

    print(f"\n{Fore.LIGHTYELLOW_EX}{pyfiglet.figlet_format('PyAte', font='dos_rebel')}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}Python Authenticator Token Extractor{Style.RESET_ALL}")
    print(f"https://github.com/FebraS/PyAte")
    print("\n")
