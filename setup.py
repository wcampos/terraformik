from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="terraformik",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A collection of AWS provisioners for Terraform backend configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/terraformik",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "terraformik-cli=provisioners.cli.provision:main",
            "terraformik-boto3=provisioners.boto3.provision:main",
        ],
    },
    install_requires=[
        "boto3>=1.26.0",
    ],
) 