from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#     long_description = f.read()

with open("requirements.txt") as f:
    dependencies = f.read().splitlines()

setup(
    name='instagrow',
    version='0.1.0',
    description='An Instagram Automation Tool',
    # long_description=long_description,
    # long_description_content_type='text/markdown',
    # url='https://github.com/yanxichen/instagrow',
    author='Yanxi Chen',
    # author_email='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Other/Nonlisted Topic :: Automation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='instagram',
    packages=['instagrow'],
    package_data={
        'instagrow': ['preset.csv'],
    },
    # py_modules=['instagrow'],
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'instagrow=instagrow.example:main',
        ],
    },
)
