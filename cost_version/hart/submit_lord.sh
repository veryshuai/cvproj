#!/bin/sh
# This script submits many jobs to the high performance computing servers

N=5  #number of jobs to submit

for i in $(seq 1 1 $N)
do
  echo $i
  qsub submit.pbs
  sleep 1
done
