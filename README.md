# 日常开发中写的脚本
一直想抽时间学习一下shell编程，一直给自己找借口，万事开头难写的第一个日常工作用到的脚本。

## 1.杀掉端口的所有进程

```
#!/bin/sh
if [ $# -lt 1 ]; then
	echo "need 1 argument!"
	exit 0
fi
for info in "$(sudo lsof -i tcp:$1)"
do
	index=0
    for element in ${info}   
	do  
		let index=index+1
		if [ $index -eq 11 ]; then
			echo "$(sudo kill -9 $element)"
			break
		fi
	done 
done
```

使用例子：

```
./kill_port.sh 8081
```

## 2.合并当前目录下模拟器，真机的静态库
```
#!/bin/sh
if [ $# -lt 3 ]; then
    echo "need 3 arguments!"
    exit 0
fi

lipo -create $1 $2 -output $3
lipo -info $3
```
使用
```
./lib_merge.sh xxx1.a xxx2.a xxx.a
```

## 3.扫描图片size大于限制size的图片

```
#!/bin/sh
if [ $# -lt 1 ]; then
    echo "请输入限制图片大小"
    exit 0
fi

find . -type f -size +$1k -name *.png > result.txt
open ./result.txt
```

使用 限制size 70k
```
./filter_large_size_images.sh 70
```

## 4.扫描项目中未使用的图片资源(支持RN)
```
# -*- coding: utf-8 *-

import os
import os.path
import copy
import datetime
import time
import sys
import ConfigParser

import re

def cur_file_dir():
     #获取脚本路径
     path = sys.path[0]
     #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)


def get_file_lists(rootdir, resource_pattern, applyFliter):   # 获取文件列表
    file_lists = []
    sum = 0
    for parent,dirnames,filenames in os.walk(rootdir):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字

        for filename in filenames:                        #输出文件信息
            fullpath = os.path.join(parent,filename)
            if (applyFliter):
                if ('.framework' in fullpath) or ('react_native' in fullpath) or ('Pods' in fullpath):
                    continue
            ext = filename.split('.')[-1]

            filename = filename.split('.')[0]
            if '@' in filename:
                filename = filename.split('@')[0]

            if ' '+ ext +' ' in resource_pattern:
                file_lists.append([filename, fullpath, 0]) # 0 用于标记资源是否被使用的状态，后面会使用

    return file_lists




def process_resources(resource_lists): # 去除第三方库的资源

    new_resource_lists = []

    for resource_list in resource_lists:
        path = resource_list[1]
        #print path
        if (not '.framework' in path) and (not 'react_native' in path) and (not 'Pods' in path):
            #print path
            new_resource_lists.append(resource_list)

    return new_resource_lists

def rn_process_resource(rn_resource_lists): # 去除RN中的基础库

    rn_new_resource_lists = []
    for rn_resource_list in rn_resource_lists:
        path = rn_resource_list[1]
        if (not 'node_modules' in path):
            rn_new_resource_lists.append(rn_resource_list)

    return rn_new_resource_lists

def get_unused_resources(resource_lists, code_lists):   #检查未使用的资源

    unused_resource_lists = []

    for code_list in code_lists:
        filePath = code_list[1]
        if os.path.exists(filePath) == False:
        	continue;
        fileObj = open(filePath, 'r')  
        lines = fileObj.read()
        
        for index, resource_list in enumerate(resource_lists):
            resource = resource_list[0]
            if resource in lines:
                resource_lists[index] = [resource_list[0], resource_lists[1], 1]

        fileObj.close()


    for resource_list in resource_lists:
        if resource_list[2] == 0:
            unused_resource_lists.append(resource_list)

    return unused_resource_lists




def check_package_info(resource_lists, proj_file, pod_file): #检查资源是否被打包
    
    unused_resource_list = []

    fileObj1 = open(proj_file, 'r')  
    lines1 = fileObj1.read()
    fileObj2 = open(pod_file, 'r')  
    lines2 = fileObj2.read()

    for resource_list in resource_lists:

        resource = resource_list[0]

        if  resource in lines1 or resource in lines2:
            #print resource
            unused_resource_list.append(resource_list)
        # else:
        #     print '%s is not packaged' % resource
    
    return unused_resource_list



def Print_to_file(file_lists,LogFile):    # 打印到日志文件
    print LogFile
    fileObj = open(LogFile, 'w') 
    print >> fileObj, "The unused resource lists: " 

    for file_list in file_lists:
        print >> fileObj, file_list[1]
    
    fileObj.close()


if __name__=="__main__":

    currenttime=datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    LogPath=cur_file_dir()+'/Logs/UnusedResources-' + currenttime

    if not os.path.exists(LogPath):
        os.makedirs(LogPath)
    UnusedResource_Log=LogPath+"/native_ununsed.txt"
    RN_UnusedResource_Log=LogPath+"/rn_unused.txt"

    

    match_resource_pattern=' png jpg ' #前后必须有一个空格  待检查的资源文件类型
    match_code_pattern=' h m xib mm plist ' #前后必须有一个空格 
    rn_match_code_pattern=' js '


    #### 设置参量
    ProjPath=cur_file_dir()
    ProjectName='FFProject' # 自己定定义projectName
    xcodeprojPath=cur_file_dir()+'/' + ProjectName + '/' + ProjectName + '.xcodeproj/project.pbxproj'
    PodsprojPath=cur_file_dir()+'/' + ProjectName + '/Pods/Pods.xcodeproj/project.pbxproj'
    RNPath=cur_file_dir()+'/react_native'

    # 获得资源文件列表
    print '获得Native资源文件列表...'
    resource_lists = get_file_lists(ProjPath, match_resource_pattern,True)
    resource_lists = process_resources(resource_lists)

    # 获得代码文件列表
    print '获得Native代码文件列表...'
    code_lists = get_file_lists(ProjPath,match_code_pattern,True)

    # 检查资源是否被工程所使用
    print '检查Native资源是否被工程所使用...'
    unused_resource_list = get_unused_resources(resource_lists, code_lists)

    # 检查未被使用的资源是否被打包
    print '检查Native未被使用的资源是否被打包...'
    unused_package_resource_list = check_package_info(unused_resource_list, xcodeprojPath, PodsprojPath)

    # 打印到日志
    print '打印Native未被使用的资源到日志...'
    Print_to_file(unused_package_resource_list, UnusedResource_Log)

    ######################################### RN ############################################
    # 获取RN资源文件列表
    print '获得RN资源文件列表...'
    rn_resource_lists = get_file_lists(RNPath, match_resource_pattern,False)
    rn_resource_lists = rn_process_resource(rn_resource_lists)

    # 获取RN代码文件列表
    print '获得RN代码文件列表...'
    rn_code_lists = get_file_lists(RNPath,rn_match_code_pattern,False)

    #检查RN资源是否被工程所使用
    print '检查RN资源是否被工程所使用...'
    rn_unused_resource_list = get_unused_resources(rn_resource_lists, rn_code_lists)

    # 打印到日志
    print '打印RN未被使用的资源到日志...'
    Print_to_file(rn_unused_resource_list, RN_UnusedResource_Log)
```

>* 1.ProjectName='XXX'  指定项目名
>* 2.cd 到项目根目录下执行`python check_all_rn_interfaces.py`即可，结果在根目录`Logs`文件中。

## 5.扫描项目中所有的RN Module以及接口属性
```
# -*- coding: utf-8 *-

import os
import os.path
import copy
import datetime
import time
import sys
import ConfigParser

import re

def cur_file_dir():
     #获取脚本路径
     path = sys.path[0]
     #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)


def get_file_lists(rootdir, resource_pattern):   # 获取文件列表
    file_lists = []
    for parent,dirnames,filenames in os.walk(rootdir):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字

        for filename in filenames:                        #输出文件信息
            fullpath = os.path.join(parent,filename)
            if ('react-native' in fullpath) or ('Pods' in fullpath) or ('Example' in fullpath):
                continue
            ext = filename.split('.')[-1]

            filename = filename.split('.')[0]
            if '@' in filename:
                filename = filename.split('@')[0]

            if ' '+ ext +' ' in resource_pattern:
                file_lists.append([filename, fullpath, 0]) # 0 用于标记资源是否被使用的状态，后面会使用

    return file_lists


def check_package_info(resource_lists, proj_file, pod_file): #检查资源是否被打包
    
    used_resource_list = []

    fileObj1 = open(proj_file, 'r')  
    lines1 = fileObj1.read()
    fileObj2 = open(pod_file, 'r')  
    lines2 = fileObj2.read()

    for resource_list in resource_lists:
        resource = resource_list[0]
        if  resource in lines1 or resource in lines2:
            used_resource_list.append(resource_list)
    
    return used_resource_list

def filter_all_include_rn_interface_list(resource_lists, include_module_keyWords,include_interface_keyWords,export_interface_keyWords):
    all_include_rn_interface_list = []

    for resource_list in resource_lists:

        fullpath = resource_list[1]
        fileObj = open(fullpath, 'r')
        lines = fileObj.read()

        for module_keyword in include_module_keyWords:
            if module_keyword in lines: ### module存在
                insert_file = []
                insert_file.append(fullpath)

                find_current_index = 0
                while find_current_index < len(lines):
                    find_item_start = -1
                    find_item_keyWord = ''
                    for interface_keyWord in include_interface_keyWords:
                        temp_find_item_start = lines.find(interface_keyWord,find_current_index)
                        if temp_find_item_start != -1: ### 找到关键字的起始位置
                            if find_item_start == -1:
                                find_item_start = temp_find_item_start
                                find_item_keyWord = interface_keyWord
                            elif temp_find_item_start < find_item_start:
                                find_item_start = temp_find_item_start
                                find_item_keyWord = interface_keyWord

                    if find_item_start == -1: ### 如果找不到直接退出
                        break;

                    if find_item_keyWord in export_interface_keyWords:
                        find_item_end = lines.find(')',find_item_start + 1) ### 部分关键字的调用没有'{}'
                        find_item_end = find_item_end + 1;
                    else:
                    	find_item_end = lines.find('{',find_item_start + 1)
                    	find_item_end = find_item_end - 1

                    if find_item_end != -1:
                        insert_string = lines[find_item_start:find_item_end - 1]
                        
                        if '@' not in insert_string:
                            insert_file.append('           ' + lines[find_item_start:find_item_end])
                       
                    find_current_index = find_item_end + 1  

                all_include_rn_interface_list.append(insert_file)  
                break

    return all_include_rn_interface_list 
        
def Print_to_file(file_lists,LogFile):    # 打印到日志文件
    print LogFile
    fileObj = open(LogFile, 'w') 
    print >> fileObj, "result lists: " 

    for file_list in file_lists:
        for item in file_list:
            print >> fileObj, item
        print  >> fileObj,'\n'
        print  >> fileObj,'\n' 
    
    fileObj.close()




if __name__=="__main__":

    currenttime=datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    LogPath=cur_file_dir()+'/all_used_rn_interfaces_' + currenttime
    ProjectName='XXX' # 自己定定义projectName

    if not os.path.exists(LogPath):
        os.makedirs(LogPath)
    resultPath=LogPath+"/result.txt"

    match_code_pattern=' m mm ' #前后必须有一个空格 
    filter_module_keyWords = ['RCT_EXPORT_MODULE']
    filter_interface_keyWords = ['RCT_CUSTOM_VIEW_PROPERTY','RCT_EXPORT_METHOD','RCT_EXPORT_VIEW_PROPERTY','RCT_REMAP_VIEW_PROPERTY']
    filter_export_interface_keyWords = ['RCT_EXPORT_VIEW_PROPERTY','RCT_REMAP_VIEW_PROPERTY']

    #### 设置参量
    ProjPath=cur_file_dir()
    xcodeprojPath=cur_file_dir()+'/' + ProjectName + '/' + ProjectName +'.xcodeproj/project.pbxproj'
    PodsprojPath=cur_file_dir()+'/' + ProjectName + '/Pods/Pods.xcodeproj/project.pbxproj'

     # 获得代码文件列表
    print '获得Native代码文件列表...'
    code_lists = get_file_lists(ProjPath,match_code_pattern)

    # 过滤掉项目中未使用的类
    print '过滤掉项目中未使用的类...'
    code_lists = check_package_info(code_lists, xcodeprojPath, PodsprojPath)

    # 过滤含有RN接口或属性的类
    print '过滤含有RN接口或属性的类...'
    code_lists = filter_all_include_rn_interface_list(code_lists, filter_module_keyWords,filter_interface_keyWords,filter_export_interface_keyWords)


    Print_to_file(code_lists, resultPath)
   
```

使用：
>* 1.ProjectName='XXX'  指定项目名
>* 2.cd 到项目根目录下执行`python unused_resource_check.py`即可，结果在根目录`all_used_rn_interfaces`开头的文件中。

## 6.直接根据.app与Crash文件解析Crash (执行脚本第二次才能解析出来，有待解决)

```
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

```