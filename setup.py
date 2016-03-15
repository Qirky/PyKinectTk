#!/usr/bin/env python

from distutils.core import setup

setup(name='PyKinectXEF',
      version='0.1',
      description='Microsoft Kinect Service Data Extractor',
      author='Ryan Kirkbride',
      author_email='sc10rpk@leeds.ac.uk',
      packages=['PyKinectXEF',
                'PyKinectXEF.Capture',
                'PyKinectXEF.Playback',
                'PyKinectXEF.utils',
                'PyKinectXEF.utils.PyKinect2',
                'PyKinectXEF.utils.SQL'],
      package_data={'PyKinectXEF.utils.SQL':['config']} )
