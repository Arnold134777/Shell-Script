#!/bin/bash

for i in `find . -name "*.png" -o -name "*.jpg"`; do 
    file=`basename -s .jpg "$i" | xargs basename -s .png | xargs basename -s @2x`
    result=`ack -i "$file"`
    if [ -z "$result" ]; then
        echo "$i"
    fi
done

# Ex: to remove from git
# for i in `./script/unused_images.sh`; do git rm "$i"; done