#!/bin/bash

for dir in $(find . -maxdepth 1 -mindepth 1 -type d)
do
  echo "processing $dir"
  cd "$dir" || exit
  net.label -custom ../SWaT2019-attacks.csv
  cd ..
done