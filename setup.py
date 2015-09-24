from setuptools import setup


REQUIREMENTS = [
    'beautifulsoup4<=4.3.2']


PACKAGES = [
    'pha']


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Testing',
    'Topic :: Utilities']

setup(
    author='Robert Cox',
    author_email='robjohncox@gmail.com',
    name='python-html-assert',
    version=0.1,
    description='partial matching of html using a tree-based specification',
    url='https://github.com/robjohncox/python-html-assert',
    license='MIT License',
    platforms=['MacOS x', 'Linux'],
    classifiers=CLASSIFIERS,
    requires=REQUIREMENTS,
    packages=PACKAGES)

