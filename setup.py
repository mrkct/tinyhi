from setuptools import setup, find_packages


setup(
    name='TinyHi',
    version='0.1.0',
    description='An interpreter for the TinyHI programming language',
    author='Marco Cutecchia',
    author_email='marco.cutecchia@studenti.unimi.it',
    url='https://github.com/mapio-teaching/LET20-Cutecchia-Marco',
    packages=find_packages(exclude=('tests', 'docs'))
)