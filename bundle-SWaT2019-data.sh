#!/bin/bash

dir="SWaT2019-netcap-labeled"

rm -rf "$dir"

echo "creating $dir"
mkdir -p "$dir"

for f in $(find . -iname *_labeled.csv.gz)
do
  folder=$(dirname "$f")
  path=${dir}${folder#"."}

  mkdir -p "$path"

  echo "moving $f to $path"
  mv "$f" "$path"
done

echo "done"

du -h $dir