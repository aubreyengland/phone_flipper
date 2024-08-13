from setuptools import setup, find_packages

setup(
    name="Phone Flipper",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "pytest",
        "configparser",
        "greenlet",
        "iniconfig",
        "packagin",
        "playwright",
        "pluggy",
        "pyee",
        "pytest",
        "setuptools",
        "typing_extensions",
    ],
    entry_points={
        "console_scripts": [
            "phoneflipper=phoneflipper.main:main",
        ],
    },
    author="Aubrey England",
    author_email="aubreng@cdw.com",
    description="A tool for factory resetting and provisioning phones.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aubreyengland/phone_flipper",  # Replace with your GitHub URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
