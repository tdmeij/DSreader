
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="DSreader",
    version="0.0.1",
    description="Read data from Digital Standard vegetation mapping projects",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tdmeij/DSreader",
    author="Thomas de Meij",
    author_email="thomasdemeij@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["DSreader"],
    include_package_data=True,
    install_requires=["pandas", ""],
    #entry_points={
    #    "console_scripts": [
    #        "realpython=reader.__main__:main",
    #    ]
    #},
)
