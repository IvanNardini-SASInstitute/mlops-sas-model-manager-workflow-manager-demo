try:
    from setuptools import setup
except:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='viyapy',
    version='0.0.1',
    author='SAS Institute',
    author_email='Yi Jian Ching <YiJian.Ching@sas.com>, Thierry Jossermoz <Thierry.Jossermoz@sas.com>',
    url="https://gitlab.sas.com/SAS-AP/viya-py-api",
    description="Package simplifying using the SAS Viya API functions",
    long_description=long_description,
    install_requires=[
        'requests',
        'inflection'
    ],
    packages=["viyapy", "viyapy.services"],
    license="TBD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
