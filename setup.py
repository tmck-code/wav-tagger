#!/usr/bin/env python3
'The Punsy pip package'

import setuptools

def readme():
    'Return README.md as a string'
    with open('README.md', 'r') as istream:
        return istream.read()

setuptools.setup(
    name='wav-tagger',
    version='0.0.1',
    author='Tom McKeesick',
    author_email='tmck01@gmail.com',
    description='A utility to tag .wav tunes, backed by ffmpeg',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/tmck-code/wav-tagger',
    packages=setuptools.find_packages(),
    package_data={},
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'wav_tagger = wav_tagger:run',
        ],
    },
    install_requires=['ffmpeg-python']
)
