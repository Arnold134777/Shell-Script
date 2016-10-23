#!/bin/sh 
#功能:文件解密 
if [ $# -ne 2 ] 
then
  echo "用法:$0 要解密的文件名 解密后的文件名"
  echo "例如:$0 hello.en hello.de"
  exit 1 
fi
flag=0 
KEYFILE="enc.key"
INFILE=$1 
OUTFILE=$2 
if [ -f $INFILE ] 
then
  echo "开始解密$INFILE"
else
  echo "error:文件不存在！！！"
  exit 1 
fi
if [ "$INFILE" = "$OUTFILE" ] 
then
  OUTFILE=$2.TMP 
  flag=1 
fi
#对文件进行解密 
openssl enc -d -aes-128-cbc -kfile $KEYFILE -in $INFILE -out $OUTFILE 
if [ $? -eq 0 ] 
then
    if [ flag -eq 1 ] 
    then
      mv $OUTFILE $INFILE 
      echo "解密完成！生成解密文件为$INFILE"
    else
      echo "解密完成！生成解密文件为$OUTFILE"
    fi
else
    echo "error:解密失败！！！"
fi
exit 0
