#!/bin/sh
wget -qO- https://raw.githubusercontent.com/buildout/buildout/master/bootstrap/bootstrap.py | env python2 - --setuptools-version=40.0.0 --buildout-version=2.12.1

