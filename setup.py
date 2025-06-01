from setuptools import setup, find_packages

setup(
    name='pkg',
    version='1.0.0',
    description='Helper package (actually malicious)',
    author='Attacker',
    packages=find_packages(),
    install_requires=[
        'PyGithub',
        'requests',
    ],
)