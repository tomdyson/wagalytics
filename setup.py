from os import path

from setuptools import setup, find_packages

try:
    from wagtail.utils.setup import sdist
    cmdclass = {
        'sdist': sdist
    }
except ModuleNotFoundError:
    cmdclass = {}

from wagalytics import __version__


testing_extras = [
    'pytest==5.3.1',
    'pytest-django==3.7.0',
    'wagtail-factories==2.0.0',
    'factory-boy==2.11.0',
]

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
        "wagtail>=2.0",
        "Django>=2.0.13",
        "oauth2client",
        "wagtailfontawesome>=1.1.2",
        "pyexcel-ods==0.5.3"
    ],
    cmdclass=cmdclass,
    extras_require={
        'testing': testing_extras,
    },
)
