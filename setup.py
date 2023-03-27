from setuptools import setup, find_packages

setup(
    name="logcleanaudit",
    version="0.1.0",
    description="A simple and efficient decorator-based package for auditing and debugging Python programs",
    author="8ByteSword",
    author_email="8bytesword@gmail.com",
    url="https://github.com/8bytesword/logcleanaudit",
    packages=find_packages(),
    install_requires=[
        "coloredlogs",
        "colorama"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
