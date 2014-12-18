# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(name='Products.Plinn',
      version='3.0',
      descripton='Plinn content management framework',
      author="Benoît Pin – MINES ParisTech – Armines"
      license="GPL",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False
      )
