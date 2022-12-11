
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="DSreader",
    version="0.0.1",
    description="Read data from Digital Standard vegetation mapping projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tdmeij/DSreader",
    author="Thomas de Meij",
    author_email="thomasdemeij@gmail.com",
    license="MIT",
    packages=["DSreader"],
    install_requires=[
        'pandas','numpy','geopandas','plotly','fiona','pyodbc',
        ],
    include_package_data=True,
    package_data={'': ['data/*.csv']},
)
