#!/bin/bash

xfce4-terminal -e 'speedometer -r enp7s0 -t enp7s0' --geometry=130x50 &
xfce4-terminal -e 'nmon' --geometry=130x50 &
