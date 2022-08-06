#!/bin/bash

cd /home/pi/dev/cat-feeder
source ./venv/bin/activate
python3 ./CatFeeder.py
deactivate
