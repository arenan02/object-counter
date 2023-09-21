from setuptools import setup, find_packages
# from setuptools.req import parse_requirements

# Parse requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='object_counter',  # Replace with your package name
    version='0.1',  # Replace with your package version
    packages=find_packages(),
    install_requires=requirements,  # Use the parsed requirements
    author='Vishwesh',  # Replace with your name
    # author_email='your.email@example.com',  # Replace with your email
    description='Description of your package',
    long_description=open('README.md').read(),
    # long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',  # Replace with your Python version(s)
        'Programming Language :: Python :: 3.8',  # Add more as needed
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
