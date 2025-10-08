#!/usr/bin/env python3
"""
Test script for db.py module.
"""

import logging
import tempfile
import db

# Set up logging to temp file
temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(temp_log.name),
        logging.StreamHandler()  # Also to console
    ]
)

print(f"Logging to temp file: {temp_log.name}")

if __name__ == "__main__":
    if db.test_connection():
        db.describe_schema()
    else:
        print("Cannot proceed with schema inspection due to connection failure")

    print(f"\nLog file saved to: {temp_log.name}")
    temp_log.close()  # Close but don't delete