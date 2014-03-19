#! /bin/bash

echo "Adding @allnodes nodes list to SGE env"

qconf -dhgrp @allnodes

echo "group_name @allnodes" > allnodes.txt
echo -n "hostlist " >> allnodes.txt
cat /etc/hosts | grep node0 | cut -f 2 -d " " | tr '\n' ' ' >> allnodes.txt
echo "" >> allnodes.txt 

qconf -Ahgrp allnodes.txt

