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
    ProjectName='FFProject' # 自己定定义projectName

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
   
    
