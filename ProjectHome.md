This project implements a simple way to control a Foscam camera in Python. Using Foscam's CGI interface, implemented functionality includes:

  1. Moving the pan/tilt
  1. Taking JPEG snapshots of imagery
  1. Parsing the MJPEG video stream and extracting each JPEG frame

This project is designed for Python2. I'm using Python 2.7.

To run the test viewer application, you will need to have also installed:

  1. PyQt4
  1. PIL - the Python Imaging Library

Refer to the Python Package Index (https://pypi.python.org/pypi) to obtain these packages. If you have to build PIL from source, be sure to have installed libjpeg before you build PIL.