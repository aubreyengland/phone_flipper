from PyInstaller.utils.hooks import collect_all, copy_metadata
from pathlib import Path
import playwright

# Collect all necessary files and modules for Playwright
datas, binaries, hiddenimports = collect_all("playwright")

# Collect Playwright metadata (necessary for browser installation)
datas += copy_metadata("playwright")


# Custom function to include Playwright browsers
def include_playwright_browsers():
    browser_path = (
        Path(playwright.__file__).parent / "driver" / "package" / ".local-browsers"
    )
    if browser_path.exists():
        # Append browser binaries to datas for inclusion in the package
        datas.append((str(browser_path), ".local-browsers"))


# Execute the custom function to include browsers
include_playwright_browsers()

# Ensure the binaries list is not empty
if not binaries:
    binaries = []

# Combine all the collected files into the final PyInstaller hook
