#!/bin/bash
echo "RUNNING"
python setup.py build_ext --inplace
python samplerbox2.py