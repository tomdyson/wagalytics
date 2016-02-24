from setuptools import setup, find_packages
from wagalytics import __version__
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wagalytics',
    version=__version__,
    description='Show Google Analytics data in Wagtail.',
    long_description=long_description,
    url='https://github.com/tomdyson/wagalytics',
    author='Tom Dyson',
    author_email='tom+wagalytics@torchbox.com',
    license='MIT',
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Topic :: Internet :: WWW/HTTP',
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='development',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "wagtail>=0.8.7",
        "Django>=1.7.1",
        "google-api-python-client==1.5.0",
        "oauth2client==1.5.2",
        "wagtailfontawesome"
    ],
)
