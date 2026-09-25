"""
PocketSmart AI - __init__.py
Ithu than package ah Python ku theriyavaikkuthu da Swetha
"""

import os
from dotenv import load_dotenv

# .env file ah load pannu
load_dotenv()

# Project root path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"📁 PocketSmart Base: {BASE_DIR}")
print(f"📁 App Dir: {APP_DIR}")

# Version
__version__ = "1.0.0"
__author__ = "Swetha"

# Ithu iruntha dhan `from app import ...` work aagum da