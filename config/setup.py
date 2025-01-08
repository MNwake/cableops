from setuptools import setup, find_packages

with open('../requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='cableops',
    version='0.1',
    author='Theo Koester',
    author_email='theopkoester@icloud.com',
    description='Holds all the database files and the entire backend of our applications.',
    url='https://github.com/MNwake/cableops.git',
    packages=find_packages(),  # Update with your actual package name
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

