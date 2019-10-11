#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 16:32:52 2019

@author: MrMndFkr
"""

import xlrd
import pandas as pd
import numpy as np
import os
from time import strptime
import datetime


# =============================================================================
# book = xlrd.open_workbook('/Users/MrMndFkr/Desktop/EDA/Monthly-Traffic-Volume-Analysis/Datasets/19jultvt.xls')
# print(book.nsheets)
# print(book.sheet_names())
# first_sheet = book.sheet_by_index(0)
# print(first_sheet.row_values(0))
# cell = first_sheet.cell(4,0)
# print(cell)
# print(cell.value)
# print(first_sheet.row_slice(rowx=59,start_colx=3,end_colx=9))
# =============================================================================

def get_arterial(file_path,category):
    """ 
    variable path is the path of the xls workbook and category is "rural" / "urban" / "all",  
    returns dataframe containing the values for given category for each state
    """
    book = xlrd.open_workbook(file_path)
    file_name = os.path.basename(file_path)
    year = str(20) + "".join([str(s) for s in file_name if s.isdigit()]) ## gets the year from filename
    Month = strptime(file_name[2:5],'%b').tm_mon ## gets month no
    mydate = datetime.date(int(year),Month, 1) ## first day of the month and year
    mydate_1 = mydate - datetime.timedelta(days=1) ## interested in last month of this year as data corresponds to last month and same year
    mydate_2 = mydate - datetime.timedelta(days=368) ## interested in last month of last year as data corresponds to last month and last year 
    #monthid1 = str(mydate_1.strftime("%Y")) + str(mydate_1.strftime("%m")) ## 200706 for July 2007 file
    monthid2 = str(mydate_2.strftime("%Y")) + str(mydate_2.strftime("%m")) ## 200606 for July 2007 file
    try:
        if category.lower() == "rural":
            index = 3
        elif category.lower() == "urban":
            index = 4
        else:
            index = 5
        sheet = book.sheet_by_index(index)
        list_states = sheet.col_values(0)
        xstart = list_states.index('Connecticut')
        xend = list_states.index('TOTALS')
        #list1 = sheet.col_slice(colx= 8,start_rowx=xstart,end_rowx= xend - 1)
        #list1 = [w.value for w in list1]
        list2 = sheet.col_slice(colx= 9,start_rowx=xstart,end_rowx= xend - 1)
        list2 = [w.value for w in list2]
        list3 = sheet.col_slice(colx= 0,start_rowx=xstart,end_rowx= xend - 1)
        list3 = [w.value.lower() for w in list3] ## take lowercase for direct match later
        df = pd.concat([pd.DataFrame(list3),pd.DataFrame(list2)], axis = 1) # ,pd.DataFrame(list1)
        #col_name_1 = category + '_Arterial_' + monthid1
        col_name_2 = category + '_Arterial_' + monthid2
        df.columns = ['State', col_name_2 ] # col_name_1, 
        df[col_name_2].replace('', np.nan, inplace=True) ## removes rows with blank records ( zonal categories)
        df['State'].replace('', np.nan, inplace=True)
        curr_monthid = str(mydate.strftime("%Y")) + str(mydate.strftime("%m")) ## 200707 for July 2007 file
        df['data_monthid'] = curr_monthid
        df.dropna(subset=[col_name_2], inplace=True)
        df.dropna(subset=['State'], inplace=True)
        df = df[~df.State.str.contains("subtotal")] ### causes problems on joins, there in most files
        df = df[df.State != "total"] ## causes problems on joins, is there only in specific files
        df['State'] = df.State.str.strip() ## removes leading and lagging white spaces if any
        df2 = pd.melt(df,id_vars=['State','data_monthid'],var_name=['category'], value_name='Million_Vehicle_Miles')
        return df2
    except:
        print("error in file ",os.path.basename(file_path))


# =============================================================================
# year = str(20) + "".join([str(s) for s in "19jultvt" if s.isdigit()]) ## gets the year from filename
# Month = strptime("19jultvt"[2:5],'%b').tm_mon
# mydate = datetime.date(int(year),Month, 1)
# mydate_1 = mydate - datetime.timedelta(days=1)
# mydate_2 = mydate - datetime.timedelta(days=366)
# monthid1 = str(mydate_1.strftime("%Y")) + str(mydate_1.strftime("%m"))
# monthid2 = str(mydate_2.strftime("%Y")) + str(mydate_2.strftime("%m"))
# print(monthid1, monthid2)
# =============================================================================

## get all the files
def filelist(root):
    """Return a fully-qualified list of filenames under root directory"""
    allfiles = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.find("xls") >= 0:
                allfiles.append(os.path.join(path, name))
    return allfiles
    
file_list = filelist('/Users/MrMndFkr/Desktop/Monthly-Traffic-Volume-Analysis/Datasets')


### check function get_arterial and append dataframes for Dataset 1
for file in file_list:
    try:
        df1 = get_arterial(file,"Rural")
        df2 = get_arterial(file,"Urban")
        df3 = get_arterial(file,"All")
        df_final = pd.concat([df1,df2,df3], axis = 0)
        #df_temp = pd.merge(df1,df2, how = 'inner', on = 'State')
        #df_final = pd.merge(df_temp,df3, how = 'inner', on = 'State')
        #assert df_final.shape[0] == df3.shape[0]
        #assert df_final.shape[0] == df_temp.shape[0]
    except:
        print('error encountered at ' + os.path.basename(file))

## get view of all columns and rows
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

## appending these dataframes
df1 = get_arterial(file_list[0],"Rural")
df2 = get_arterial(file_list[0],"Urban")
df3 = get_arterial(file_list[0],"All")
df_final = pd.concat([df1,df2,df3], axis = 0)
#df_temp = pd.merge(df1,df2, how = 'inner', on = 'State')
#df_final = pd.merge(df_temp,df3, how = 'inner', on = 'State')
for file in file_list[1:]:
    try:
        df1 = get_arterial(file,"Rural")
        df2 = get_arterial(file,"Urban")
        df3 = get_arterial(file,"All")
        df_final = pd.concat([df_final,df1,df2,df3], axis = 0)
        #df_temp = pd.merge(df1,df2, how = 'inner', on = 'State')
        #df_temp2 = pd.merge(df_temp,df3, how = 'inner', on = 'State')
        #df_final = pd.merge(df_final,df_temp2, how = 'inner', on = 'State')
        #assert df_final.shape[0] == df_temp.shape[0]
        #assert df_final.shape[0] == df_temp2.shape[0]
    except:
        print('error encountered at ' + os.path.basename(file))


## only change is that the values are in cols 7 and 8 for Dataset III ( in Dataset I, they are in cols 9 and 10)
def get_arterial(file_path,category):
    """ 
    variable path is the path of the xls workbook and category is "rural" / "urban" / "all",  
    returns dataframe containing the values for given category for each state
    """
    book = xlrd.open_workbook(file_path)
    file_name = os.path.basename(file_path)
    year = str(20) + "".join([str(s) for s in file_name if s.isdigit()]) ## gets the year from filename
    Month = strptime(file_name[2:5],'%b').tm_mon ## gets month no
    mydate = datetime.date(int(year),Month, 1) ## first day of the month and year
    #mydate_1 = mydate - datetime.timedelta(days=1) ## interested in last month of this year as data corresponds to last month and same year
    mydate_2 = mydate - datetime.timedelta(days=368) ## interested in last month of last year as data corresponds to last month and last year 
    #monthid1 = str(mydate_1.strftime("%Y")) + str(mydate_1.strftime("%m")) ## 200706 for July 2007 file
    monthid2 = str(mydate_2.strftime("%Y")) + str(mydate_2.strftime("%m")) ## 200606 for July 2007 file
    try:
        if category.lower() == "rural":
            index = 3
        elif category.lower() == "urban":
            index = 4
        else:
            index = 5
        sheet = book.sheet_by_index(index)
        list_states = sheet.col_values(0)
        xstart = list_states.index('Connecticut')
        xend = list_states.index('TOTALS')
        #list1 = sheet.col_slice(colx= 6,start_rowx=xstart,end_rowx= xend - 1)
        #list1 = [w.value for w in list1]
        list2 = sheet.col_slice(colx= 7,start_rowx=xstart,end_rowx= xend - 1)
        list2 = [w.value for w in list2]
        list3 = sheet.col_slice(colx= 0,start_rowx=xstart,end_rowx= xend - 1)
        list3 = [w.value.lower() for w in list3] ## take lowercase for direct match later
        df = pd.concat([pd.DataFrame(list3),pd.DataFrame(list2)], axis = 1) # pd.DataFrame(list1),
        #col_name_1 = category + '_Arterial_' + monthid1
        col_name_2 = category + '_Arterial_' + monthid2
        df.columns = ['State',  col_name_2 ] ## col_name_1,
        df[col_name_2].replace('', np.nan, inplace=True) ## removes rows with blank records ( zonal categories)
        df['State'].replace('', np.nan, inplace=True)
        curr_monthid = str(mydate.strftime("%Y")) + str(mydate.strftime("%m")) ## 200707 for July 2007 file
        df['data_monthid'] = curr_monthid
        df.dropna(subset=[col_name_2], inplace=True)
        df.dropna(subset=['State'], inplace=True)
        df = df[~df.State.str.contains("subtotal")] ### causes problems on joins, there in most files
        df = df[df.State != "total"] ## causes problems on joins, is there only in specific files
        df['State'] = df.State.str.strip() ## removes leading and lagging white spaces if any
        df2 = pd.melt(df,id_vars=['State','data_monthid'],var_name=['category'], value_name='Million_Vehicle_Miles')
        return df2
    except:
        print("error in file ",os.path.basename(file_path))

# get new filelist from dataset III
file_list = filelist('/Users/MrMndFkr/Desktop/Monthly-Traffic-Volume-Analysis/Datasets_III')

## get collated dataset
#df1 = get_arterial(file_list[0],"Rural")
#df2 = get_arterial(file_list[0],"Urban")
#df3 = get_arterial(file,"All")
#df_temp = pd.merge(df1,df2, how = 'inner', on = 'State')
#df_final = pd.merge(df_temp,df3, how = 'inner', on = 'State')
for file in file_list[1:]:
    try:
        df1 = get_arterial(file,"Rural")
        df2 = get_arterial(file,"Urban")
        df3 = get_arterial(file,"All")
        df_final = pd.concat([df_final,df1,df2,df3], axis = 0)
        #df_temp = pd.merge(df1,df2, how = 'inner', on = 'State')
        #df_temp2 = pd.merge(df_temp,df3, how = 'inner', on = 'State')
        #df_final = pd.merge(df_final,df_temp2, how = 'inner', on = 'State')
        #assert df_final.shape[0] == df_temp.shape[0]
        #assert df_final.shape[0] == df_temp2.shape[0]
    except:
        print('error encountered at ' + os.path.basename(file))


## get different column for category
df_final.loc[df_final.category.str.find("Rural") >= 0,'area'] = 'rural'
df_final.loc[df_final.category.str.find("Urban") >= 0,'area'] = 'urban'
df_final.loc[df_final.category.str.find("All") >= 0,'area'] = 'all'
#df_final.iloc[0:10,]

## get different column for monthid
df_final['monthid'] = df_final.category.str[-6:]
#df_final.iloc[0:10,]

## QC - check dups
QC = df_final.groupby(['State','monthid','category']).agg({'Million_Vehicle_Miles':['count']}).reset_index()
QC.columns = ['State','monthid','category','value']
QC.iloc[0:10,]
QC.loc[(QC.value > 1)]

## save it to disk
df_final.to_csv("/Users/MrMndFkr/Desktop/Monthly-Traffic-Volume-Analysis/data_reshaped.csv")


# =============================================================================
# file = '/Users/MrMndFkr/Desktop/EDA/Monthly-Traffic-Volume-Analysis/08maytvt.xls'
# df1 = get_arterial(file,"Rural")
# df2 = get_arterial(file,"Urban")
# df_final = pd.merge(df1,df2, how = 'inner', on = 'State')
# df_final.shape[0]
# df1.shape[0]
# df1.shape
# =============================================================================

# =============================================================================
# book = xlrd.open_workbook('/Users/MrMndFkr/Desktop/Monthly-Traffic-Volume-Analysis/Datasets/19jultvt.xls')
# fourth_sheet = book.sheet_by_index(3)
# #print(fourth_sheet.row_values(1))
# list_states = fourth_sheet.col_values(0)
# xstart = list_states.index('Connecticut')
# xend = list_states.index('TOTALS')
# #list1 = fourth_sheet.col_slice(colx= 8,start_rowx=xstart,end_rowx= xend - 1)
# #list1 = [w.value for w in list1]
# list2 = fourth_sheet.col_slice(colx= 9,start_rowx=xstart,end_rowx= xend - 1)
# list2 = [w.value for w in list2]
# list3 = fourth_sheet.col_slice(colx= 0,start_rowx=xstart,end_rowx= xend - 1)
# list3 = [w.value.lower() for w in list3]
# #col1 = pd.DataFrame(list1)
# col2 = pd.DataFrame(list2)
# col3 = pd.DataFrame(list3)
# #col1
# df = pd.concat([col3,col2], axis = 1) # col1,
# df.columns = ['State','Rural_Arterial_201806'] # 'Rural_Arterial_201906',
# df['Rural_Arterial_201806'].replace('', np.nan, inplace=True)
# df.dropna(subset=['Rural_Arterial_201806'], inplace=True)
# df = df[~df.State.str.contains("subtotal")]
# df['State'] = df.State.str.strip()
# df2= pd.melt(df,id_vars=['State'],var_name=['category'], value_name='Million_Vehicle_Miles')
# 
# fifth_sheet = book.sheet_by_index(4)
# list_states = fifth_sheet.col_values(0)
# xstart = list_states.index('Connecticut')
# xend = list_states.index('TOTALS')
# list1 = fifth_sheet.col_slice(colx= 8,start_rowx=xstart,end_rowx= xend - 1)
# list1 = [w.value for w in list1]
# list2 = fifth_sheet.col_slice(colx= 9,start_rowx=xstart,end_rowx= xend - 1)
# list2 = [w.value for w in list2]
# list3 = fifth_sheet.col_slice(colx= 0,start_rowx=xstart,end_rowx= xend - 1)
# list3 = [w.value.lower() for w in list3]
# col1 = pd.DataFrame(list1)
# col2 = pd.DataFrame(list2)
# col3 = pd.DataFrame(list3)
# df2 = pd.concat([col3,col1,col2], axis = 1)
# df2.columns = ['State','Urban_Arterial_201906','Urban_Arterial_201806']
# df2['Urban_Arterial_201906'].replace('', np.nan, inplace=True)
# df2.dropna(subset=['Urban_Arterial_201906'], inplace=True)
# df2 = df2[~df2.State.str.contains("subtotal")]
# df2['State'] = df2.State.str.strip()
# 
# df_final = pd.merge(df,df2, how = 'inner', on = 'State')
# =============================================================================
