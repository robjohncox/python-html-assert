from distutils.core import setup
import os


REQUIREMENTS = [
    'beautifulsoup4'
]


PACKAGES = [
    'pha',
]


CLASSIFIERS = [
    'Development Status :: Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Testing',
    'Topic :: Utilities',
]

setup(
    author='Robert Cox',
    author_email='robjohncox@gmail.com',
    name='python-html-assert',
    version='0.1',
    description='partial matching of html using a tree-based specification',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.txt')).read(),
    url='https://github.com/robjohncox/python-html-assert',
    license='MIT License',
    platforms=['MacOS x', 'Linux'],
    classifiers=CLASSIFIERS,
    requires=REQUIREMENTS,
    packages=PACKAGES,
)

