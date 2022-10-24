from setuptools import find_packages
from setuptools import setup

setup(
    packages=find_packages(exclude=["tests*"]),
    author="David Marin",
    author_email="dm@davidmarin.org",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    description="Convert a set of dates into a compact list of globs",
    install_requires=[],
    license="Apache",
    long_description=open("README.rst").read(),
    name="dateglob",
    url="http://github.com/Yelp/dateglob",
    version="1.1.1",
    package_data={
        "dateglob": ["py.typed"],
    },
)
