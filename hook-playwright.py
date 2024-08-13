# hook-playwright.py
from PyInstaller.utils.hooks import collect_all, copy_metadata
from pathlib import Path
import os
import playwright

# Collect all necessary files and modules for playwright
datas, binaries, hiddenimports = collect_all("playwright")

# Add the Playwright metadata
datas += copy_metadata("playwright")

# Ensure Playwright uses the specific path for browsers
browsers_path = Path("C:/Users/Admin/AppData/Local/ms-playwright/")


def include_playwright_browsers():
    if browsers_path.exists():
        binaries.append((str(browsers_path), "ms-playwright"))


include_playwright_browsers()
