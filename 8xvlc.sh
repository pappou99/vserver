#!/bin/bash

ip="239.230.225.255"
startport=5001
width=300
height=300
xpos=0
ypos=0

for input in {1..8}
do
    port=$((startport -1 + input))
    echo $port
    vlc --autoscale --width=400 --height=300 --canvas-width=400 --canvas-height=300 --canvas-padd rtp://@$ip:$port &
    xpos=$((xpos + width))
    ypos=$((ypos + height))
    echo $xpos
done