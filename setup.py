#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("requirements.txt", "r") as reqs:
    requirements = reqs.readlines()

setup(
    name="python-actor",
    version="0.0.1",
    description="Python actor system",
    author="Philip Bove",
    install_requires=requirements,
    author_email="phil@bove.online",
    packages=find_packages(),
    scripts=[],
)
