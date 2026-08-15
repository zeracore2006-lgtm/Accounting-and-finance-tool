#!/usr/bin/env python3
"""
ApexFinance Enterprise SME Accounting Suite - Main Server Entry Point
Enforces dynamic $PORT binding for Render cloud deployment and serves all static UI files and REST API endpoints.
"""

import sys
import os

# Add backend directory to module lookup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(BASE_DIR, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import main

if __name__ == '__main__':
    main()
