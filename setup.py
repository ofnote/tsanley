#!/usr/bin/env python

import os
import setuptools

def get_long_description():
    filename = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(filename) as f:
        return f.read()

setuptools.setup(name='tsanley',
      version='0.1.0',
      description="Tsanley: Understanding Tensor Programs",
      long_description=get_long_description(),
      long_description_content_type="text/markdown",
      author='Nishant Sinha',
      author_email='nishant@offnote.co',
      url='https://github.com/ofnote/tsanley',
      license='Apache 2.0',
      platforms=['POSIX'],
      packages=setuptools.find_packages(),
      #entry_points={},
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
          ],
      setup_requires=['sympy', 'typed_ast', 'easydict', 'astpretty', 'tsalib'],
      install_requires=['sympy', 'typed_ast', 'easydict', 'astpretty', 'tsalib'],
      )