from setuptools import find_packages, setup


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
    name='python-html-assert',
    version='0.1.3',
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    author='Robert Cox',
    author_email='robjohncox@gmail.com',
    description='partial matching of html using a tree-based specification',
    license='MIT License',
    url='https://github.com/robjohncox/python-html-assert',
    classifiers=CLASSIFIERS)
