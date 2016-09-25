#!/bin/bash

#!/bin/sh
if [ $# -lt 1 ]; then
    echo "请输入限制图片大小"
    exit 0
fi

find . -type f -size +$1k -name *.png > result.txt
open ./result.txt