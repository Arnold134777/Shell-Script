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
    ProjectName='XX' # 自己定定义projectName
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