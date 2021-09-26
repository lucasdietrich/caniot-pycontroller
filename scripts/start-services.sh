#!/usr/bin/env bash

sudo systemctl enable canhttpserver.service
sudo systemctl enable cancontroller.service

sudo systemctl start canhttpserver.service
sudo systemctl start cancontroller.service
