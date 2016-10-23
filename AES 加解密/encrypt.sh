#!/bin/sh 
#功能:文件加密 
if [ $# -ne 2 ] 
then
  echo "用法:$0 要加密的文件名 加密后的文件名"
  echo "例如:$0 hello hello.en"
  exit 1 
fi
#flag为输入的加密文件名与加密后的文件名是否一样，1为相同文件名 
flag=0 
KEYFILE="enc.key"
INFILE=$1 
OUTFILE=$2 
if [ -f $INFILE ] 
then
  echo "开始加密$INFILE"
else
  echo "error:文件不存在！！！"
  exit 1 
fi
if [ "$INFILE" = "$OUTFILE" ] 
then
  OUTFILE=$2.TMP 
  flag=1 
fi
#对文件进行加密 
openssl enc -e -aes-128-cbc -kfile $KEYFILE -in $INFILE -out $OUTFILE 
if [ $? -eq 0 ] 
then
    if [ $flag -eq 1 ] 
    then
      mv $OUTFILE $INFILE 
      echo "加密完成！生成加密文件为$INFILE"
    else
      echo "加密完成！生成加密文件为$OUTFILE"
    fi
else
    echo "error:加密失败！！！"
fi
exit 0
