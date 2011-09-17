# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

import le_social


setup(
    name='django-le-social',
    version=le_social.__version__,
    author='Bruno Renié',
    author_email='bruno@renie.fr',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/brutasse/django-le-social',
    license='BSD licence, see LICENCE file',
    description='External registration / authentication for Django',
    long_description=open('README.rst').read(),
    install_requires=[
        'Django',
        'twitter>=1.6.1',
        'python-openid>=2.2.5',
        'itsdangerous>=0.11',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    test_suite='runtests.runtests',
    zip_safe=False,
)
