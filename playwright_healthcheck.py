#!/usr/bin/env python3
"""
An enhanced script to check if Playwright can run in the current environment.
Provides detailed diagnostics for troubleshooting.
"""

import sys
import os
import platform
import subprocess
import traceback
from playwright.sync_api import sync_playwright


def get_system_info():
    """Collect system information for diagnostics"""
    info = {
        "Platform": platform.platform(),
        "Python Version": platform.python_version(),
        "Architecture": platform.machine(),
        "System": platform.system(),
    }

    # Check if running in Docker
    in_docker = os.path.exists('/.dockerenv')
    info["In Docker"] = in_docker

    # Check available memory
    try:
        if platform.system() == "Linux":
            mem_info = subprocess.check_output(['free', '-h']).decode('utf-8')
            info["Memory Info"] = mem_info
    except Exception as e:
        info["Memory Info Error"] = str(e)

    # Check for DISPLAY variable (X11)
    info["DISPLAY"] = os.environ.get("DISPLAY", "Not set")

    # Check for required libraries on Linux
    if platform.system() == "Linux":
        try:
            libs_output = subprocess.check_output(['ldconfig', '-p']).decode('utf-8')
            required_libs = [
                'libX11', 'libXcomposite', 'libXcursor', 'libXdamage',
                'libXext', 'libXi', 'libXtst', 'libXrandr', 'libXScrnSaver',
                'libgbm', 'libasound', 'libatk-1.0', 'libatspi'
            ]

            missing_libs = []
            for lib in required_libs:
                if lib not in libs_output:
                    missing_libs.append(lib)

            if missing_libs:
                info["Missing Libraries"] = ", ".join(missing_libs)
            else:
                info["Required Libraries"] = "All present"
        except Exception as e:
            info["Libraries Check Error"] = str(e)

    return info


def print_diagnostics(info):
    """Print diagnostic information in a formatted way"""
    print("\n" + "=" * 50)
    print(" SYSTEM DIAGNOSTICS ")
    print("=" * 50)
    for key, value in info.items():
        if isinstance(value, str) and '\n' in value:
            print(f"{key}:\n{value}")
        else:
            print(f"{key}: {value}")
    print("=" * 50 + "\n")


def check_playwright():
    """Try to launch browser with Playwright and report results"""
    system_info = get_system_info()

    try:
        with sync_playwright() as p:
            # Try to launch browser
            print("Attempting to launch browser...")
            launch_args = {
                "headless": True
            }

            # Add args for containerized environments
            if system_info.get("In Docker", False):
                print("Detected container environment, adding special args...")
                launch_args["args"] = [
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--disable-software-rasterizer"
                ]

            browser = p.chromium.launch(**launch_args)
            print("Browser launched successfully!")

            # Try to create a page and navigate
            print("Creating page and navigating to about:blank...")
            page = browser.new_page()
            page.goto('about:blank')
            print("Navigation successful!")

            # Get browser version
            version = browser.version
            system_info["Browser Version"] = version

            # Clean up
            browser.close()
            print("Browser closed successfully.")

        print("\n✅ Playwright is working correctly!")
        print_diagnostics(system_info)
        return True
    except Exception as e:
        print(f"\n❌ Playwright error: {e}")
        print("\nDetailed traceback:")
        traceback.print_exc()

        # Add error info to diagnostics
        system_info["Playwright Error"] = str(e)
        print_diagnostics(system_info)
        return False


if __name__ == "__main__":
    success = check_playwright()
    sys.exit(0 if success else 1)