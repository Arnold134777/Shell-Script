#!/bin/sh
if [ $# -lt 1 ]; then
	echo "need 1 argument!"
	exit 0
fi
for info in "$(sudo lsof -i tcp:$1)"
do
	echo ${info}
	index=0
    for element in ${info}   
	do  
		let index=index+1
		if [ $index -eq 11 ]; then
			echo "sudo kill -9 $element"
			echo "$(sudo kill -9 $element)"
			break
		fi
	done 
done



