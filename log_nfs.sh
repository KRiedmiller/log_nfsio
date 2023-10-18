#! /bin/bash

date >> ~/nfsstat.log
date >> ~/nfsiostat.log

nfsstat >> ~/nfsstat.log
nfsiostat >> ~/nfsiostat.log

echo "##########" >> ~/nfsstat.log
echo "##########" >> ~/nfsiostat.log
