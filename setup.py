#!/usr/bin/env python

from distutils.core import setup

setup(name='PyKinectTk',
      version='0.1',
      description='Microsoft Kinect Service Data Extractor',
      author='Ryan Kirkbride',
      author_email='sc10rpk@leeds.ac.uk',
      packages=['PyKinectTk',
                'PyKinectTk.Capture',
                'PyKinectTk.Playback',
                'PyKinectTk.Analysis',
                'PyKinectTk.utils',
                'PyKinectTk.utils.PyKinect2'],
      package_data={'PyKinectTk.utils':['Settings/*']} )
