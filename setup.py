from os import path

from setuptools import setup, find_packages
from wagtail.utils.setup import sdist
from wagalytics import __version__

setup(
    name='wagalytics',
    version=__version__,
    description='Show Google Analytics data in Wagtail.',
    long_description='See https://github.com/tomdyson/wagalytics for details',
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
    zip_safe=False,
    install_requires=[
        "wagtail>=0.8.7",
        "Django>=1.7.1",
        "oauth2client",
        "wagtailfontawesome>=1.0.2",
        "pyexcel-ods==0.5.3"
    ],
    cmdclass={
        'sdist': sdist
    }
)
