"""
this script is the main script to be executed,
involve dataset extraction and sku loop
I created a function scrape() for scraping part, please refer to func.py
"""
from pandas import read_excel
import re
from script.func import scrape,time

#read dataset,cleansing and get all the unique sku no
df=read_excel('./data/Question 1 Dataset.xlsx')
col=list(filter(lambda x:not re.search('unnamed',x,re.IGNORECASE),df.columns))
df=df[col]
df=df.dropna(how='all')
df['Article Number']=df['Article Number'].astype(int).astype(str)
max=max(df['Article Number'].apply(len))
df['Article Number']=df['Article Number'].apply(lambda x:x.rjust(max,'0'))

#loop each sku for web scrape
for each_sku in df['Article Number'].unique():
    print(f'running {each_sku}')
    result=scrape(each_sku)
    print(result)