"""Script to install exam papers downloader."""
import os
from setuptools import setup, find_packages

# Read the content of the README file
with open(
    os.path.join(os.path.dirname(__file__), 'README.md'),
    encoding='utf-8'
) as f:
    long_description = f.read()

setup(
    name='exam_downloader',
    version='0.2.0',
    description='A premium full-stack platform for downloading CAIE and Edexcel exam papers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fam007e/examquest',
    author='Faisal Ahmed Moshiur',
    author_email='faisalmoshiur+gitpy@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'beautifulsoup4>=4.9.3',
        'aiohttp>=3.8.1',
        'fastapi>=0.127.0',
        'uvicorn>=0.35.0',
    ],
    entry_points={
        'console_scripts': [
            'exam-downloader=o_and_a_lv_qp_sdl:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Education',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
    ],
    keywords='education, exams, cambridge, edexcel, igcse, a-level, papacambridge, xtremepapers',
    python_requires='>=3.6',
)
