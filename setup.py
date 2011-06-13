try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import dateglob

setup(
    author='David Marin',
    author_email='dave@yelp.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.3',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    description='Use globs to represent sets of dates compactly',
    license='Apache',
    long_description=open('README.rst').read(),
    name='dateglob',
    py_modules=['dateglob'],
    url='http://github.com/Yelp/dateglob',
    version=dateglob.__version__,
)
