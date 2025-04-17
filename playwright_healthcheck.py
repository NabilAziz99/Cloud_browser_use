#!/usr/bin/env python3
"""
A simple script to check if Playwright can run in the current environment.
Add this to your project root directory.
"""

import sys
from playwright.sync_api import sync_playwright

def check_playwright():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('about:blank')
            browser.close()
        print("✅ Playwright is working correctly")
        return True
    except Exception as e:
        print(f"❌ Playwright error: {e}")
        return False

if __name__ == "__main__":
    success = check_playwright()
    sys.exit(0 if success else 1)