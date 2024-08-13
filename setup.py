from setuptools import setup, find_packages

setup(
    name='yawn-api',
    version='0.1.2',
    author='Jack Manners',
    author_email='jack.manners@flinders.edu.au',
    description='A Python package for interacting with the SNAPI API, YawnLabs, and various other health device APIs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jackmanners/yawn-api',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'requests',
        'dotenv'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
