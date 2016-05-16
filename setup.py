import dateglob

try:
    from setuptools import setup
    setup  # shh, pyflakes

    setuptools_kwargs = {
        'provides': ['dateglob'],
        'test_suite': 'tests',
    }
except ImportError:
    from distutils.core import setup
    setuptools_kwargs = {}

setup(
    author='David Marin',
    author_email='dm@davidmarin.org',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    description='Convert a set of dates into a compact list of globs',
    license='Apache',
    long_description=open('README.rst').read(),
    name='dateglob',
    py_modules=['dateglob'],
    url='http://github.com/Yelp/dateglob',
    version=dateglob.__version__,
    **setuptools_kwargs
)
