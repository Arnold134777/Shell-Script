#!/bin/sh
if [ $# -lt 3 ]; then
	echo "need 3 arguments!"
	exit 0
fi

lipo -create $1 $2 -output $3
lipo -info $3