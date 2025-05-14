from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="sortmate",
    version="0.1.0",
    author="Amaan",
    author_email="your.email@example.com",  # Replace with your email
    description="A smart Gmail organization tool that automatically categorizes emails using date-based labels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amaan-19/SortMate",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Email",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sortmate=sortmate.cli:main",  # Assumes you rename testing.py to cli.py
        ],
    },
    keywords="gmail, email, organization, automation, labels, google, api",
    project_urls={
        "Bug Reports": "https://github.com/amaan-19/SortMate/issues",
        "Source": "https://github.com/amaan-19/SortMate",
    },
    include_package_data=True,
    zip_safe=False,
)