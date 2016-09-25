#!/bin/sh
if [ $# -lt 2 ]; then
	echo "需要项目build app文件路径＋Crash文件路径"
	exit 0
fi

BUILD_APP_PATH=$1 # 编译生成的app文件
BUILD_APP_FILENAME=${BUILD_APP_PATH##*/} # 编译生成的app文件名
BUILD_APP_FILENAME=${BUILD_APP_FILENAME%%.*}  # 去掉后缀
CRASH_FILE_PATH=$2 # 待解析的Crash 路径

DSYM_UTIL_PATH="/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/dsymutil"
GENERATE_DSYM_PATH="generate.DSYM" # 中间生成的DSYM文件
RESULT_CRASH_FILE_PATH="result.log" # 解析生成的结果

# 拷贝symbolicatecrash
echo "搜索symbolicatecrash..."
SYMBOLICATE_CARSH_PATH=$(find /Applications/Xcode.app -name symbolicatecrash -type f)
if [ ! -f $SYMBOLICATE_CARSH_PATH ]; then
	echo "symbolicatecrash文件不存在"
	exit 0
fi
	
# 根据App文件生成.dSYM文件
$DSYM_UTIL_PATH $BUILD_APP_PATH/$BUILD_APP_FILENAME -o $GENERATE_DSYM_PATH
if [ $? -ne 0 ];then
	echo "生成的DSYM文件失败"
	exit 0
fi
echo "生成的DSYM文件完毕"

# 生成分析结果文件
if [ ! -f "$CRASH_FILE_PATH" ]; then
	echo "待分析的文件不存在,请检查后重试"
	exit 0
fi

export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"
$SYMBOLICATE_CARSH_PATH $CRASH_FILE_PATH $GENERATE_DSYM_PATH > $RESULT_CRASH_FILE_PATH
open $RESULT_CRASH_FILE_PATH
#rm -rf $GENERATE_DSYM_PATH 
echo "结束"
