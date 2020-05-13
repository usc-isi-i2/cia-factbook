# -*- coding: utf-8 -*-
"""
Created on Wed May  6 16:09:02 2020

@author: mhari
"""

import json
from flatten_dict import flatten
from flatten_dict import unflatten
from csv import writer
import os 
from fnmatch import fnmatch

EMPTYCELL = " "

def merge_dicts(dic1, dic2):
    flatten_1, flatten_2 = flatten(dic1), flatten(dic2)
    flatten_1.update(flatten_2)
    return unflatten(flatten_1)

def getTree(datum):
    datType = type(datum)
    if datType is dict:
        temp_array = dict()
        for key in datum:
            temp_array[key] = getTree(datum[key])
        return temp_array
    elif datType is list:
        returnable = dict()
        for datindex in datum:
            ind_tree = getTree(datindex)
            if not returnable:
                returnable = ind_tree
            elif returnable != ind_tree:
                returnable = merge_dicts(returnable, ind_tree)
        return returnable
    else:
       return None               

def mergeTrees(master, tester):
    masterType = type(master)
    testerType = type(tester)
    if masterType != testerType:
        if not master:
            return tester
        elif not tester:
            return master
        else:
            print ("Error")
            print (master, tester)
            return
    if masterType is dict:
        for key in tester:
            if key not in master:
                master[key] = tester[key]
            else:
                master[key] = mergeTrees(master[key], tester[key])
    return master

def get_spacings(datum, level):
    datType = type(datum)
    if datType is dict:
        temp_array = dict()
        total_count = 0
        for key in datum:
            temp = dict()
            child_level, count, temp[key] = get_spacings(datum[key], level+1)
            temp_array[key] = child_level, count, temp[key]
            total_count+=count
        return level, total_count, temp_array
    else:
       return level, 1, None

def seggregateLevels(datum, index):
    datType = type(datum)
    if datType is tuple:
       print("error")
    elif datType is dict:
        temp_appendee = list()
        my_index = index
        for element in datum:
            level, spacing, child = datum[element]
            seggregateLevels(child, my_index)
            temp_appendee.append((element, spacing))
            my_index += spacing
        appendee = (index, temp_appendee)
        if level in levelDict:
            levelDict[level].append(appendee)
        else:
            levelDict[level] = [appendee]
    else:
        return
def getPath(level, index):
    if (level, index) in tempLevInd:
        return tempLevInd[(level,index)]
    
    parentLevel = level -1
    if parentLevel <0:
        tempLevInd[(level,index)] = result[level][index]
    else:
        candidates = result[parentLevel]
        thatIndex = index
        for i in range(index, -1, -1):
            if candidates[i] != EMPTYCELL:
                thatIndex = i
                break
        tempLevInd[(level,index)] = tempLevInd[(parentLevel,thatIndex)] + "." + result[level][index]
    
    return tempLevInd[(level,index)]

def file_writer(data, file_name):
    with open(file_name, 'w', newline='\n', encoding="utf8") as write_obj:
        csv_writer = writer(write_obj, delimiter=',')
        for record in data:
            csv_writer.writerow(record)

def recFlatten(fdict):
    temp = flatten(fdict)
    for k,v in temp.items():
        if type(v) is list:
            tempList = list()
            for item in v:
                if type(item) is dict:
                    flatItem = recFlatten(item)
                    tempList.append(flatItem)
                else:
                    tempList.append(item)
            temp[k] = tempList
    return temp

def mainFunc(filepath, filename):
    global levelDict
    global result
    global columnLookup
    global tempLevInd
    
    with open(filepath, encoding='utf-8') as fileptr:
        jsonData = json.load(fileptr)
        
    country_list = list()
    
    jsonData = jsonData['countries']
    
    for country in jsonData.values():
        country_list.append(country)
        
    structree = dict()
    
    for i, country in enumerate(country_list):
        sidetree = getTree(country)
        structree = mergeTrees(structree, sidetree)
    
    spacer = get_spacings(structree, -1)
    
    levelDict = dict()
       
    init_level, cells, content = spacer
    
    seggregateLevels(content, 0)     
    
    template = [EMPTYCELL] * cells
    
    result = [template[:] for i in range(len(levelDict))]
    
    for level, data in levelDict.items():
        for entitySet in data:
            start_index, eset = entitySet
            for text, spacing in eset:
                if result[level][start_index] != EMPTYCELL:
                    print(level, start_index)
                result[level][start_index] = text
                start_index += spacing
            
    for res in result:
        res.insert(0,EMPTYCELL)
        
    result[0][0] = 'country'
    
    columnLookup= dict()
    tempLevInd= dict()
    
    for lev in range(len(result)):
        for ind in range(len(result[lev])):
            if result[lev][ind] != EMPTYCELL:
                path = getPath(lev, ind)    
                columnLookup[path] = ind
    
    new_file_dir = (output_dir_path + filename).replace('.json','\\')
    if not os.path.exists(new_file_dir):
        os.makedirs(new_file_dir)
        
    for country, countryData in jsonData.items():
        max_len = 1
        flat_country = recFlatten(countryData)
        for val in flat_country.values():
            if type(val) is list:
                l = len(val)
                if max_len < l:
                    max_len = l
        newRecord = [[EMPTYCELL] + template[:] for i in range(max_len)]
        newRecord[0][0] = country
        for key, val in flat_country.items():
            skey = ".".join(key)
            if type(val) is not list:
                newRecord[0][columnLookup[skey]] = val
            else:
                if val:
                    if type(val[0]) is not dict:
                        for v, vel in enumerate(val):
                            newRecord[v][columnLookup[skey]] = vel
                    else:
                        for iv, vl in enumerate(val):
                            for vk, vv in vl.items():
                                sskey = ".".join(key+vk)
                                if sskey in columnLookup:
                                    newRecord[iv][columnLookup[sskey]] = vv
        write_result = result + newRecord
        output_path = new_file_dir+country+".csv"
        file_writer(write_result, output_path)

input_dir_path = "D:\\USC\\ISI\\JSON_CSV\\weekly_json\\"
output_dir_path = "D:\\USC\\ISI\\JSON_CSV\\weekly_csv\\"

if not os.path.exists(output_dir_path):
   os.makedirs(output_dir_path)
        
pattern = "*.json"
for path, subdirs, files in os.walk(input_dir_path):
    for i, name in enumerate(files):
        if i%20 == 0:
            print(i, "files processed")
        if fnmatch(name, pattern):
            filepath = os.path.join(path, name)
            mainFunc(filepath, name)
